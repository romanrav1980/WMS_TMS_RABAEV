from pathlib import Path
import json
p="scripts/check1102_qc_damaged.js";s=Path(p).read_text(encoding="utf-8")
s=s.replace('  querySelectorAll(){return [...map.values()];}addEventListener(n,f){this.events[n]=f;}','  querySelectorAll(){return [...map.values()];}addEventListener(n,f){this.events[n]=f;}focus(){}',1)
needle=' const current=setup();'
assert needle in s
s=s.replace(needle,""" const scans=setup();answer(scans);await flush();scans.el('item-code').value='EAN:own';scans.el('add-item').onclick();
 assert.equal(JSON.parse(scans.storage.get(scans.key+':scans')).entries.length,1);
 function button(node){if(node.textContent==='Удалить')return node;for(const child of node.children){const found=button(child);if(found)return found;}return null;}
 button(scans.el('scan-list')).events.click();assert.equal(JSON.parse(scans.storage.get(scans.key+':scans')).entries.length,0);
 scans.el('item-code').value='EAN:own';scans.el('add-item').onclick();scans.el('errors').value='0';scans.el('scan').onclick();
 const frozen=scans.requests.at(-1).options.body,originalScans=scans.storage.get(scans.key+':scans');assert.equal(JSON.parse(frozen).item_scans.length,1);
 answer(scans,{detail:'unknown'},false);await flush();const remove=button(scans.el('scan-list'));assert(remove.disabled);
 remove.events.click();assert.equal(scans.storage.get(scans.key+':scans'),originalScans);
 scans.el('load').onclick();assert.equal(scans.requests.at(-1).options.body,frozen);
 answer(scans,{detail:'unknown'},false);await flush();
"""+needle,1)
s=s.replace('strict contract\\\');','strict contract/currentPLANread/scan correction and frozen pending\\\');')
print(json.dumps({p:s},ensure_ascii=True))
