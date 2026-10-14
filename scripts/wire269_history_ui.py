from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
section="""<section class="panel" data-permission="transport_dispatch_view"><h2>Журнал рассмотренных сверок</h2>
<button id="drReviewHistoryLoad">С первой записи</button><button id="drReviewHistoryNext" disabled>Следующие записи</button>
<table><thead><tr><th>Версия</th><th>Время рассмотренных фактов</th><th>Диспетчер</th><th>Вывод</th></tr></thead><tbody id="drReviewHistoryRows"></tbody></table>
<p id="drReviewHistoryMessage" role="status"></p><div id="drReviewHistoryDetail"></div></section>
"""
s=s.replace("</main>",section+"</main>",1).replace('<script src="day-review.js"></script>','<script src="day-review.js"></script><script src="day-review-history.js"></script>')
print(json.dumps({str(p):s},ensure_ascii=True))
