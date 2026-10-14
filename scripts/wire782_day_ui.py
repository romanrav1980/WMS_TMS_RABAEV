from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");t=p.read_text(encoding="utf-8")
assert 'day-reconciliation.css' not in t
t=t.replace('<link rel="stylesheet" href="styles.css">','<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="day-reconciliation.css">')
t=t.replace('class="auth-pending"','class="auth-pending day-page"')
t=t.replace('<h1>Сверка исполнения</h1>','''<header class="page-heading"><div><div class="eyebrow">RETAILCASE · Управление складом</div><h1>Исполнение и отгрузка</h1><p class="page-description">Факты дня, перенос рейсов и контроль складских заданий</p></div><span class="page-badge">Рабочий интерфейс WMS</span></header>
<nav class="page-tabs" aria-label="Разделы сверки"><a href="#dayOverview">Обзор дня</a><a href="#shippingArea">Грузовая зона</a><a href="#stTransfer">Перенос СТ</a><a href="#waitingArea">Ожидание товара</a></nav>''')
t=t.replace('<section class="panel"><label>Склад','<section class="panel" id="dayOverview"><label>Склад',1)
t=t.replace('<section class="panel" data-permission="transport_dispatch_view"><h2>СТ выбранной даты','<section class="panel" id="shippingArea" data-permission="transport_dispatch_view"><h2>СТ выбранной даты')
old='<section class="panel" data-permission="transport_dispatch_edit"><h2>Перенос неотобранной СТ</h2>'
new='<section class="panel" id="stTransfer" data-permission="transport_dispatch_edit"><h2><span class="flow-step">1</span>Перенос СТ на другой рейс</h2><div id="sdOverview" class="summary-cards" hidden></div>'
assert old in t;t=t.replace(old,new)
a=t.index('<label>Номер СТ<input id="sdSt"');b=t.index('<button id="sdSave"',a)
t=t[:a]+'''<div class="source-line"><label>Номер СТ<input id="sdSt" maxlength="100" placeholder="Введите номер СТ"></label><button id="sdRead">Прочитать СТ</button></div>
<div class="form-grid"><label>Номер целевого рейса<input id="sdTarget" inputmode="numeric" placeholder="Номер существующего рейса"></label>
<label>Основание переноса<input id="sdReference" maxlength="500" placeholder="Документ или согласованное решение"></label>
<label>Причина<textarea id="sdReason" maxlength="500" placeholder="Почему переносим отгрузку"></textarea></label></div>
'''+t[b:]
t=t.replace('<section class="panel"><h2>Перемещение отобранного товара в ожидание</h2>','<section class="panel" id="waitingArea"><h2><span class="flow-step">2</span>Товар в ожидании следующего рейса</h2>')
a=t.index('<label>Решение о переносе СТ<input id="swDecision"');b=t.index('</section>',a)
t=t[:a]+'''<div class="waiting-toolbar"><label>Решение о переносе СТ<input id="swDecision" maxlength="100" placeholder="Выберите решение из истории выше"></label>
<button id="swRead">Обновить задания</button><button id="swPlan">Создать задания</button><button id="swRetry" disabled>Повторить команду</button></div>
<p id="swPending" role="status"></p><p id="swMessage" role="status"></p>
<div id="swEmpty" class="waiting-empty">Выберите решение о переносе, чтобы увидеть задания и их текущий статус.</div>
<table id="swTable" hidden><thead><tr><th>Задание</th><th>Идентификатор паллеты</th><th>Откуда</th><th>Куда</th><th>Количество</th><th>Статус</th></tr></thead><tbody id="swRows"></tbody></table>
<div class="section-note"><span id="swCount"></span><div><button id="swNext" disabled>Следующие задания</button><a href="warehouse-tasks.html">Все складские задания →</a></div></div>
'''+t[b:]
print(json.dumps({str(p):t},ensure_ascii=True))
