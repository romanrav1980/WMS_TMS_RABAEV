from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
section="""<section class="panel" data-permission="transport_dispatch_edit">
<h2>Зафиксировать результат сверки</h2>
<p>Запись сохраняет рассмотренные факты и открытые обязательства. Она не изменяет запас и не подтверждает отсутствующие ответы внешних систем.</p>
<button id="drReviewRead">Прочитать сверку для фиксации</button>
<label>Причина и вывод диспетчера<textarea id="drReviewReason" maxlength="500"></textarea></label>
<button id="drReviewSave" disabled>Зафиксировать</button>
<button id="drReviewRetry" disabled>Повторить сохранённую команду</button>
<button id="drReviewResolve" disabled>Проверить исход команды</button>
<p id="drReviewMessage" role="status"></p></section>
"""
s=s.replace("</main>",section+"</main>",1).replace('<script src="day-reconciliation.js"></script>','<script src="day-reconciliation.js"></script><script src="day-review.js"></script>')
out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
j["packages"].append("RRL_DAY_REVIEW_API");j["components"].append("../2026-10-11_ni072_review/002_api.sql");j["startup_scripts"].append("../2026-10-11_ni072_review/001_schema.sql")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
