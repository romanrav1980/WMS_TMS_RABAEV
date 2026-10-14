import json
from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
point='<section class="panel order-picking-panel" id="orderWavePlanning"'
assert point in s
panel="""<article id="preparedLayoutPanel" class="panel order-picking-panel">
 <h2>Укладка подготовленной СТ</h2><p>Перенос целой строки между местами одной СТ. Уже связанные с фактическим товаром места изменяются в процессе пересборки.</p>
 <button id="plRead" type="button">Показать текущую укладку</button>
 <div class="rights-table-wrap"><table class="rights-table"><thead><tr><th>Место СТ</th><th>Товар</th><th>Количество</th><th>Ед.</th><th>Коробки</th><th>Масса</th></tr></thead><tbody id="plCurrentRows"></tbody></table></div>
 <div class="rights-toolbar"><label>Строка для переноса<select id="plRow"></select></label><label>В место СТ<select id="plTarget"></select></label><button id="plPreview" type="button">Сравнить укладку</button></div>
 <div id="plComparison" hidden><h3>До изменения</h3><div class="rights-table-wrap"><table class="rights-table"><thead><tr><th>Место СТ</th><th>Товар</th><th>Количество</th><th>Ед.</th><th>Коробки</th><th>Масса</th></tr></thead><tbody id="plBeforeRows"></tbody></table></div>
 <h3>После изменения</h3><div class="rights-table-wrap"><table class="rights-table"><thead><tr><th>Место СТ</th><th>Товар</th><th>Количество</th><th>Ед.</th><th>Коробки</th><th>Масса</th></tr></thead><tbody id="plAfterRows"></tbody></table></div></div>
 <label>Причина изменения<input id="plReason" maxlength="500" placeholder="Например, согласование с отбором целых паллет"></label>
 <button id="plMove" type="button" disabled>Подтвердить перенос строки</button><button id="plArchive" type="button" hidden>Сохранить отказ в архив и перечитать</button>
 <p id="plStatus" role="status" aria-live="polite">Выберите заказ и покажите укладку.</p>
</article>
"""
s=s.replace(point,panel+point,1)
point='<script src="order-wave-planning.js'
start=s.index(point);end=s.index('</script>',start)+len('</script>')
s=s[:end]+'<script src="order-prepared-layout.js"></script>'+s[end:]
print(json.dumps({str(p):s}))
