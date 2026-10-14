from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
panel="""<section class="panel" data-permission="transport_dispatch_edit"><h2>Перенос неотобранной СТ</h2>
<p>Переносятся все паллеты одной СТ на существующий спланированный рейс. Исходные даты и объём заказа сохраняются.</p>
<label>Номер СТ<input id="sdSt" maxlength="100"></label><button id="sdRead">Прочитать исходную СТ</button>
<label>Номер целевого рейса<input id="sdTarget" inputmode="numeric"></label>
<label>Причина<textarea id="sdReason" maxlength="500"></textarea></label>
<label>Ссылка на решение<input id="sdReference" maxlength="500"></label>
<button id="sdSave" disabled>Перенести всю СТ</button><button id="sdRetry" disabled>Повторить сохранённую команду</button>
<p id="sdPending" role="status"></p><p id="sdMessage" role="status"></p>
<button id="sdHistory">История переносов</button><button id="sdHistoryNext" disabled>Следующие записи</button>
<table><thead><tr><th>Версия</th><th>Исходный рейс</th><th>Новый рейс</th><th>Исходная дата</th><th>Новая дата</th><th>Причина</th><th>Основание</th><th>Диспетчер</th></tr></thead><tbody id="sdHistoryRows"></tbody></table></section>"""
s=s.replace("</main>",panel+"</main>").replace("</body>",'<script src="st-deferral.js"></script></body>')
print(json.dumps({str(p):s},ensure_ascii=True))
