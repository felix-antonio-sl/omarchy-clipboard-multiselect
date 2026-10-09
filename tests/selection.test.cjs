const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const modulePath = path.resolve(process.env.CLIPBOARD_PLUGIN_DIR || path.resolve(__dirname, '..'), 'ClipboardSelection.js');
const selection = fs.existsSync(modulePath) ? require(modulePath) : {};
const first = { type: 'text', text: 'Primer párrafo' };
const second = { type: 'text', text: 'Segundo párrafo' };
const ready = typeof selection.toggle === 'function';

test('can mark text entries for a combined paste', () => {
  assert.equal(typeof selection.toggle, 'function', 'multiple selection is missing');
  assert.deepEqual(selection.toggle([], first), [first]);
});

test('keeps marking order even when history is reordered', { skip: !ready }, () => {
  let marked = selection.toggle([], second);
  marked = selection.toggle(marked, first);
  marked = selection.retain(marked, [first, second]);
  assert.equal(selection.join(marked), 'Segundo párrafo\nPrimer párrafo');
  assert.equal(selection.position(marked, first), 1);
});

test('unmarks a duplicate and appends it when marked again', { skip: !ready }, () => {
  const marked = selection.toggle(selection.toggle([], first), second);
  const unmarked = selection.toggle(marked, { ...first });
  assert.deepEqual(unmarked, [second]);
  assert.deepEqual(marked, [first, second]);
  assert.equal(selection.join(selection.toggle(unmarked, first)), 'Segundo párrafo\nPrimer párrafo');
});

test('drops a deleted entry without losing the remaining order', { skip: !ready }, () => {
  assert.deepEqual(selection.remove([second, first], first), [second]);
  assert.deepEqual(selection.retain([second, first], [first]), [first]);
});

test('does not concatenate images or blank entries', { skip: !ready }, () => {
  assert.deepEqual(selection.toggle([first], { type: 'image', path: '/tmp/image.png' }), [first]);
  assert.deepEqual(selection.toggle([first], { type: 'text', text: '   ' }), [first]);
});

test('preserves unicode, whitespace and shell syntax literally', { skip: !ready }, () => {
  const entries = [
    { type: 'text', text: '  áéíóú 🐺\nsegunda línea\n' },
    { type: 'text', text: '`whoami` $(id) "comillas" \\ ruta' }
  ];
  assert.equal(selection.join(entries), '  áéíóú 🐺\nsegunda línea\n\n`whoami` $(id) "comillas" \\ ruta');
});

test('bounds the preview while retaining the complete paste', { skip: !ready }, () => {
  const entries = [{ type: 'text', text: 'abcdef' }, { type: 'text', text: 'ghijkl' }];
  assert.equal(selection.preview(entries, 9), 'abcdef\ngh');
  const large = [{ type: 'text', text: 'x'.repeat(200000) }, second];
  assert.equal(selection.preview(large, 8192).length, 8192);
  assert.equal(selection.join(large).length, 200000 + 1 + second.text.length);
});
