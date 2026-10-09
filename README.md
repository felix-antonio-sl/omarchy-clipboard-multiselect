# Omarchy Clipboard Multi-select

Select several saved text clips and paste them as one block, in the order you
marked them. This plugin extends Omarchy's native clipboard picker while keeping
its search, preview, history capture, and individual image/file actions.

[Instrucciones en español](docs/uso-es.md).

## Install

Tested with **Omarchy 4.0.4**. Requires the native Omarchy Shell clipboard helpers,
Quickshell, `wl-clipboard`, and `wtype` provided by that installation. Compatibility
with later shell APIs must be checked when they change.

```bash
omarchy plugin add https://github.com/felix-antonio-sl/omarchy-clipboard-multiselect.git --enable
```

The plugin ID is `felix-antonio-sl.clipboard-multiselect`. Its manifest declares
`omarchy.clonedFrom: omarchy.clipboard`, so Omarchy uses it as a local replacement
and routes the normal clipboard shortcut to it.

If you already customized the native clipboard plugin, keep a backup of that
copy before enabling this replacement.

## Use

| Action | Result |
| --- | --- |
| Super + Ctrl + V | Open clipboard history |
| Ctrl + click | Mark or unmark a text entry |
| Arrow keys, then Ctrl + Space | Mark or unmark the focused text entry |
| Enter | Paste the marked texts as one block |
| Shift + Enter | Copy the block without pasting |
| Escape | Clear the search first; close when the search is empty |

Numbers beside marked entries show the marking order. Texts are joined with one
newline separator, preserving their existing whitespace and full contents. The
preview is bounded to keep large clips responsive; the copied block is complete.
Searching preserves marks, and reopening the picker clears them.

Images and file entries are selected individually. When an image or file row is
focused, Enter and Shift + Enter use that row's native action. Other text rows,
including an empty search result, can submit the marked text block.

The new footer hints are currently in Spanish. On a Mac-style keyboard, Super is
usually the Command key.

## Updates and persistence

Omarchy installs third-party plugins under `~/.config/omarchy/plugins/`. Normal
package updates preserve that user-owned copy; this plugin does not patch
`/usr/share/omarchy/`.

Update this plugin separately with:

```bash
omarchy plugin update felix-antonio-sl.clipboard-multiselect
```

Local edits can prevent a fast-forward update. Major Omarchy changes may require
a compatible plugin release; keeping a local copy prevents overwrite but cannot
guarantee compatibility with every future shell API.

To return to the original clipboard while keeping this plugin installed:

```bash
omarchy plugin disable felix-antonio-sl.clipboard-multiselect
```

## Tests

From the repository directory, run the portable selection tests with Node.js:

```bash
node --test tests/selection.test.cjs
```

On a machine with Omarchy and Quickshell installed, also run:

```bash
python3 tests/check-qml.py
```

The Qt check runs the actual plugin functions, keyboard handler, mouse callback,
and clipboard Process/Timer blocks in an isolated offscreen engine. External
clipboard and keyboard commands are replaced with file receivers, so the test
checks complete text payloads and command arguments without sending desktop
input. It covers marking order, unmarking, search, history reordering, Ctrl-click,
copy-only, combined paste dispatch, and individual image/file actions.

The plugin was also loaded and visually inspected in the live Omarchy Shell.
These tests do not establish paste compatibility with every application.

## Source and license

Derived from the native clipboard plugin shipped in Omarchy 4.0.4, under the MIT
license. The original license is preserved in [LICENSE](LICENSE), and source
provenance is documented in [NOTICE.md](NOTICE.md).

This repository contains source code, documentation, and synthetic tests.
Clipboard history and machine configuration are not part of the distribution.
