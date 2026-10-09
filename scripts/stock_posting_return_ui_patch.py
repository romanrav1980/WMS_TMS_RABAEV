import json
from pathlib import Path
out={};d=Path("wiki-raw/wms_admin_ui_reference")
p=d/"case-pick-tsd.html";s=p.read_text(encoding="utf-8")
needle='        <section class="tsd-actions" data-permission="case_pick_execute">'
assert s.count(needle)==1
s=s.replace(needle,'''        <section data-permission="case_pick_manage"><div id="cpTsdReturnDestinations"></div><button id="cpTsdReturnCarrier" type="button">Вернуть весь состав в исходные ячейки</button><button id="cpTsdRetryReturn" type="button" hidden>Повторить возврат</button></section>
'''+needle,1)
s=s.replace('    <script src="case-shipment-binding.js"></script>','    <script src="case-shipment-binding.js"></script>\n    <script src="case-carrier-return.js"></script>',1)
out[str(p)]=s
for name in ("case-pick-posting.js","case-carrier-move.js"):
 p=d/name;s=p.read_text(encoding="utf-8");needle="      storageKey=key();" if name=="case-carrier-move.js" else "      storageKey = key();"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n      if(localStorage.getItem(JSON.stringify(['nicora.caseCarrierReturn',cpTsdApiBase(),cpTsdUser()])))throw new Error('Сначала повторите сохранённый возврат.');",1);out[str(p)]=s
p=d/"case-shipment-binding.js";s=p.read_text(encoding="utf-8").replace('["nicora.casePickIntent", "nicora.caseCarrierMove"]','["nicora.casePickIntent", "nicora.caseCarrierMove", "nicora.caseCarrierReturn"]',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
