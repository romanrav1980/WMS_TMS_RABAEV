from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
section="""<section class="panel" data-permission="transport_dispatch_view"><h2>СТ выбранной даты и занятость зарегистрированных ячеек</h2>
<button id="srLoad">С первой строки</button><button id="srNext" disabled>Следующие строки</button>
<table><thead><tr><th>СТ</th><th>Идентификатор паллеты</th><th>Рейс</th><th>Адрес</th><th>Фактическое состояние</th><th>Корневое место погрузки</th></tr></thead><tbody id="srRows"></tbody></table>
<h3>Зарегистрированные ячейки грузовой зоны</h3>
<table><thead><tr><th>Ячейка</th><th>Строки положительного запаса</th><th>Неотгруженные контейнеры</th><th>Неотгруженные CASE</th><th>Занятость</th></tr></thead><tbody id="srCells"></tbody></table>
<p id="srMessage" role="status"></p></section>
"""
s=s.replace("</main>",section+"</main>",1).replace('<script src="day-review-history.js"></script>','<script src="day-review-history.js"></script><script src="shipping-register.js"></script>')
print(json.dumps({str(p):s},ensure_ascii=True))
