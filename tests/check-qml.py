"""Run production selection handlers and clipboard pipe without desktop input.

Only the external clipboard/keyboard commands are replaced with file receivers.
The QML functions, key handler and Process/Timer blocks come from the installed
plugin, so the test checks its actual selection and output code in Qt's engine.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile

base = Path(__file__).resolve().parents[1]
plugin = Path(os.environ.get('CLIPBOARD_PLUGIN_DIR', str(base)))
source = (plugin / 'Clipboard.qml').read_text()

def block_after(marker):
    start = source.index(marker)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

with tempfile.TemporaryDirectory(prefix='clipboard-qml-', dir=os.environ.get('XDG_RUNTIME_DIR')) as directory:
    test_root = Path(directory)
    (test_root / 'Commons').symlink_to(Path(os.environ.get('OMARCHY_PATH', '/usr/share/omarchy')) / 'shell/Commons')
    for name in ['ClipboardHistory.js', 'ClipboardSelection.js']:
        shutil.copy2(plugin / name, test_root / name)
    commands = test_root / 'commands'
    commands.mkdir()
    copy_path = test_root / 'copied.txt'
    copy_args = test_root / 'copy-args.json'
    paste_args = test_root / 'paste-args.json'
    native_calls = test_root / 'native-calls.jsonl'
    native_bin = test_root / 'bin'
    native_bin.mkdir()
    for name in ['omarchy-clipboard-paste-file', 'omarchy-clipboard-paste-text']:
        helper = native_bin / name
        helper.write_text(
            '#!/usr/bin/python3\nimport sys,json\n'
            f'with open({str(native_calls)!r}, "a") as f:\n'
            '    f.write(json.dumps([sys.argv[0].rsplit("/",1)[-1], sys.argv[1:]]) + "\\n")\n'
        )
        helper.chmod(0o700)
    (commands / 'wl-copy').write_text(
        '#!/usr/bin/python3\nimport sys,json\nfrom pathlib import Path\n'
        f'Path({str(copy_path)!r}).write_bytes(sys.stdin.buffer.read())\n'
        f'Path({str(copy_args)!r}).write_text(json.dumps(sys.argv[1:]))\n'
    )
    (commands / 'wtype').write_text(
        '#!/usr/bin/python3\nimport sys,json\nfrom pathlib import Path\n'
        f'Path({str(paste_args)!r}).write_text(json.dumps(sys.argv[1:]))\n'
    )
    for command in commands.iterdir():
        command.chmod(0o700)
    functions = '\n'.join(block_after('function ' + name + '(') for name in [
        'open', 'rebuildDisplay', 'select', 'selectAbsolute', 'setFilter',
        'toggleIndex', 'activateIndex', 'copyIndex', 'applyCombined', 'loadHistory',
        'applySelected', 'copySelected'
    ])
    handler = block_after('Keys.onPressed: function(event)').replace(
        'Keys.onPressed: function(event)', 'function handleKey(event)', 1
    )
    mouse_handler = block_after('onClicked: function(mouse)').replace(
        'onClicked: function(mouse)', 'function mouseClick(mouse)', 1
    )
    copy_process = block_after('Process {\n    id: combinedCopy')
    paste_timer = block_after('Timer {\n    id: combinedPasteTimer')
    qml = '''
import Quickshell
import Quickshell.Io
import QtQuick
import qs.Commons
import "ClipboardHistory.js" as ClipboardHistory
import "ClipboardSelection.js" as ClipboardSelection
Item {
  id: root
  property var history: [
    { type: "text", text: "C — tercer texto" },
    { type: "text", text: "B — segundo texto" },
    { type: "text", text: "A — primer texto" }
  ]
  property var selectedEntries: []
  property bool opened: false
  property bool cursorActive: false
  property int selectedIndex: 0
  property string filterText: ""
  property string selectionMessage: ""
  property string pendingCombinedText: ""
  property bool pendingCopyOnly: false
  property bool clearConfirmOpen: false
  property string omarchyPath: TEST_ROOT
  property int stage: 0
  property int ticks: 0
  property int failures: 0
  property int rowIndex: 0
  function disarmPointer() {}
  function close() { root.opened = false }
  function check(condition, message) {
    if (!condition) {
      root.failures++
      console.log("FAIL: " + message)
    }
  }
  function key(code, modifiers, text) {
    handleKey({ key: code, modifiers: modifiers || 0, text: text || "", accepted: false })
  }
  ListModel { id: displayModel }
  Item { id: resultList; function positionViewAtIndex(index, mode) {} }
  Item { id: keyCatcher }
  QtObject { id: row; property int index: root.rowIndex }
  FileView { id: copyResult; path: COPY_PATH; printErrors: false }
  FileView { id: pasteResult; path: PASTE_PATH; printErrors: false }
  FUNCTIONS
  HANDLER
  MOUSE_HANDLER
  COPY_PROCESS
  PASTE_TIMER
  Component.onCompleted: {
    root.open("{}")
    root.key(Qt.Key_Down)
    root.key(Qt.Key_Space, Qt.ControlModifier)
    root.key(Qt.Key_Down)
    root.key(Qt.Key_Space, Qt.ControlModifier)
    root.key(Qt.Key_Up)
    root.key(Qt.Key_Space, Qt.ControlModifier)
    root.key(Qt.Key_Space, Qt.ControlModifier)
    root.check(ClipboardSelection.join(root.selectedEntries) === "A — primer texto\\nB — segundo texto", "wrong marking/unmarking order")
    root.loadHistory(JSON.stringify([root.history[2], root.history[0], root.history[1]]))
    root.check(ClipboardSelection.join(root.selectedEntries) === "A — primer texto\\nB — segundo texto", "history reorder changed selection order")
    root.history = root.history.concat([
      { type: "image", path: "/tmp/synthetic.png", mime: "image/png" },
      { type: "text", text: "file:///tmp/synthetic.txt" }
    ])
    root.rebuildDisplay()
    root.activateIndex(3)
    root.check(root.pendingCombinedText === "" && root.selectedEntries.length === 2, "marked text intercepted image activation")
    root.copyIndex(3)
    root.check(root.pendingCombinedText === "", "marked text intercepted image copy")
    root.activateIndex(4)
    root.check(root.pendingCombinedText === "", "marked text intercepted file activation")
    root.copyIndex(4)
    root.check(root.pendingCombinedText === "", "marked text intercepted file copy")
    root.history = root.history.slice(0, 3)
    root.rebuildDisplay()
    root.opened = true
    root.key(Qt.Key_Z, 0, "z")
    root.check(displayModel.count === 0 && root.selectedEntries.length === 2, "filter lost selection")
    root.key(Qt.Key_Return, Qt.ShiftModifier)
    root.check(!root.opened, "copy-only did not dismiss picker")
    poll.running = true
  }
  Timer {
    id: poll
    interval: 40
    repeat: true
    onTriggered: {
      root.ticks++
      if (root.ticks > 150) {
        console.log("FAIL: QML clipboard test timed out")
        Qt.quit()
        return
      }
      if (combinedCopy.running || combinedPasteTimer.running) return
      if (root.stage === 0) {
        copyResult.reload()
        if (copyResult.text() !== "A — primer texto\\nB — segundo texto") return
        root.check(root.selectedEntries.length === 0, "copy did not clear selection")
        root.stage = 1
        root.open("{}")
        root.check(root.selectedEntries.length === 0, "opening retained old marks")
        root.rowIndex = 2
        root.mouseClick({ modifiers: Qt.ControlModifier })
        root.rowIndex = 0
        root.mouseClick({ modifiers: Qt.ControlModifier })
        root.key(Qt.Key_Return)
        root.check(!root.opened, "paste did not dismiss picker")
      } else {
        pasteResult.reload()
        if (!pasteResult.text()) return
        copyResult.reload()
        if (copyResult.text() !== "B — segundo texto\\nA — primer texto") return
        root.check(root.selectedEntries.length === 0, "paste did not clear selection")
        if (root.failures === 0) console.log("PASS: Qt key handlers, Ctrl-click, marking order, unmarking, search, history reorder, images/files, copy-only and combined paste pipeline")
        Qt.quit()
      }
    }
  }
}
'''
    replacements = {
        'FUNCTIONS': functions,
        'HANDLER': handler,
        'MOUSE_HANDLER': mouse_handler,
        'COPY_PROCESS': copy_process,
        'PASTE_TIMER': paste_timer,
        'COPY_PATH': json.dumps(str(copy_path)),
        'PASTE_PATH': json.dumps(str(paste_args)),
        'TEST_ROOT': json.dumps(str(test_root)),
    }
    for name in sorted(replacements, key=len, reverse=True):
        qml = qml.replace(name, replacements[name])
    (test_root / 'shell.qml').write_text(qml)
    environment = dict(os.environ, QT_QPA_PLATFORM='offscreen',
                       WAYLAND_DISPLAY='clipboard-test-no-desktop',
                       PATH=str(commands) + ':' + os.environ['PATH'])
    result = subprocess.run(['qs', '-p', str(test_root), '--no-color'],
                            env=environment, capture_output=True, text=True, timeout=12)
    log = result.stdout + result.stderr
    (base / 'qml-validation.log').write_text(log)
    if result.returncode or 'PASS: Qt key handlers' not in log or 'FAIL:' in log:
        print(log)
        raise SystemExit('QML validation failed')
    assert json.loads(copy_args.read_text()) == ['--type', 'text/plain;charset=utf-8']
    assert json.loads(paste_args.read_text()) == ['-M', 'shift', '-k', 'Insert', '-m', 'shift']
    calls = [json.loads(line) for line in native_calls.read_text().splitlines()]
    assert sorted(calls) == sorted([
        ['omarchy-clipboard-paste-file', ['image/png', '/tmp/synthetic.png']],
        ['omarchy-clipboard-paste-file', ['--copy-only', 'image/png', '/tmp/synthetic.png']],
        ['omarchy-clipboard-paste-text', ['--shift-insert', '--history-index', '4']],
        ['omarchy-clipboard-paste-text', ['--copy-only', '--history-index', '4']],
    ])
    print('PASS: actual QML handlers and clipboard stdin, plus native paste invocation; desktop unaffected.')
