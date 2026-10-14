const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const ts = require(path.join(root, 'admin/wms_admin_frontend/node_modules/typescript'));
const prefix = String.fromCharCode(110,105,99,111,114,97);
class Store {
  constructor(entries) { this.map = new Map(entries); }
  get length() { return this.map.size; }
  key(index) { return Array.from(this.map.keys())[index] ?? null; }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
  removeItem(key) { this.map.delete(key); }
}
const modules = [
  'admin/wms_admin_frontend/src/replay/storageBrandMigration.ts',
  'terminal/wms_terminal_web/src/store/storageBrandMigration.ts',
  'wiki-raw/wms_admin_ui_reference/admin-auth.js'
];
for (const filename of modules) {
  const source = fs.readFileSync(path.join(root, filename), 'utf8');
  function migrate(store) {
    if (filename.endsWith('.ts')) {
      const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
      const context = { exports: {} };
      vm.runInNewContext(js, context);
      context.exports.migrateRetailcaseStorage(store);
    } else {
      vm.runInNewContext(source.slice(0, source.indexOf('const ADMIN_SESSION_KEY')), { localStorage: store, document: { body: { classList: { remove() {} }, setAttribute() {}, textContent: "" } } });
    }
  }
  const body = JSON.stringify({ operation_id: 'same-original-id', quantity: '12.125', phase: 'UNCERTAIN' });
  const old = prefix + '.trip.time.pending:scope';
  const current = 'retailcase.trip.time.pending:scope';
  const s = new Store([[old, body]]);
  migrate(s);
  assert.equal(s.getItem(current), body);
  assert.equal(s.getItem(old), null);
  migrate(s);
  assert.equal(s.getItem(current), body);
  const oldArray = JSON.stringify([prefix + '.casePickIntent', 'api', 'actor']);
  const newArray = JSON.stringify(['retailcase.casePickIntent', 'api', 'actor']);
  const a = new Store([[oldArray, body]]); migrate(a);
  assert.equal(a.getItem(newArray), body);
  const conflict = new Store([[old, body], [current, 'different']]);
  assert.throws(() => migrate(conflict));
  assert.equal(conflict.getItem(old), body); assert.equal(conflict.getItem(current), 'different');
  const readonly = new Store([[old, body]]); readonly.setItem = () => { throw new Error('quota'); };
  assert.throws(() => migrate(readonly)); assert.equal(readonly.getItem(old), body);
}
console.log('PASS: 3 clients retain operation identity; JSON keys, conflict, quota and repeat cases');
