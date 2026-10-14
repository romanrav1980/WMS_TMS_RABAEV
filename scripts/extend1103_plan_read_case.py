from pathlib import Path
import json
p="scripts/check1102_qc_damaged.js";s=Path(p).read_text(encoding="utf-8")
needle=" const v=s.ctx.window.wmsQualityIntent,good="
assert needle in s
s=s.replace(needle,""" const current=setup();answer(current);await flush();current.el('load').onclick();answer(current);await flush();
 const planned=JSON.parse(current.requests.at(-1).options.body);
 answer(current,{operation_id:planned.operation_id,control_status:status});await flush();
 assert(!current.requests.at(-1).options.method);assert(!current.storage.has(current.key));
 answer(current,{...status,case_content_version:21,composition_signature:'B'.repeat(64)});await flush();
 assert(current.el('summary').textContent.includes('v21'));
"""+needle,1)
s=s.replace('strict contract\\\');','strict contract/current read after cachedPLAN\\\');')
print(json.dumps({p:s},ensure_ascii=True))
