from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.js");text=p.read_text(encoding="utf-8")
needle='  async function mutate(path, fields) {'
assert text.count(needle)==1
text=text.replace(needle,'''  async function pendingLock(action) {
    const identity = owner();
    const perform = () => { if (identity !== owner()) throw Error("Пользователь или подключение изменились; повторите выбор."); return action(); };
    try {
      if (navigator.locks) return await navigator.locks.request("wmsWorkloadMutation:" + identity, perform);
      return await perform();
    } catch (error) { if (identity === owner()) message(error.message); }
  }
  async function mutate(path, fields) { return pendingLock(() => mutateUnlocked(path, fields)); }
  async function mutateUnlocked(path, fields) {''')
text=text.replace('    await retry();','    await retryUnlocked();',1)
text=text.replace('  async function retry() {','  async function retry() { return pendingLock(retryUnlocked); }\n  async function retryUnlocked() {',1)
text=text.replace('await request(saved.path, "POST", saved.body); localStorage.removeItem(key);','await request(saved.path, "POST", saved.body);\n      if (JSON.parse(localStorage.getItem(key) || "null")?.body?.operation_id === saved.body.operation_id) localStorage.removeItem(key);')
text=text.replace('if (error.status && error.status < 500 && ![401, 403].includes(error.status)) localStorage.removeItem(key);','if (error.status && error.status < 500 && ![401, 403].includes(error.status) && JSON.parse(localStorage.getItem(key) || "null")?.body?.operation_id === saved.body.operation_id) localStorage.removeItem(key);')
print(json.dumps({str(p):text},ensure_ascii=True))
