from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-forecast.html");s=p.read_text(encoding="utf-8")
start=s.index('<section class="wf-panel wf-resources"');end=s.index('</section>',start)+len('</section>')
s=s[:start]+"""<section class="wf-panel wf-resources" aria-labelledby="wfResTitle">
<h2 id="wfResTitle">Трудозатраты по нормам участка</h2>
<div id="wfLabourResult" aria-live="polite"><p>Рассчитайте прогноз, чтобы увидеть часы и основания.</p></div>
<p class="wf-note">Расчёт рекомендательный: количество / действующая норма. Часы по строке округляются вверх до 9 десятичных знаков. Численность людей, техника и слоты требуют доступных смен, перерывов и квалификации; здесь не назначаются.</p>
<details><summary>Настроить связь вида работы с участком</summary>
<p>Связь относится к выбранным выше складу и виду работы. Нормы SKU и базовых единиц ведутся в <a href="resource-workload.html">нагрузке и выходе персонала</a>.</p>
<button id="wfNormLoad" type="button">Прочитать настройки участка</button>
<p id="wfNormCurrent">Настройки ещё не прочитаны.</p>
<div class="wf-form">
<label for="wfNormSites">Участок норм<select id="wfNormSites"></select></label>
<label class="wf-check"><input type="checkbox" id="wfNormActive" checked><span>Связь действует</span></label>
<label for="wfNormReason">Основание изменения<input id="wfNormReason" maxlength="500" minlength="3" placeholder="Почему выбран этот участок"></label>
</div>
<button id="wfNormSave" type="button" disabled>Сохранить связь с участком</button>
<button id="wfNormRetry" type="button" hidden>Повторить сохранённую настройку</button>
<button id="wfNormArchive" type="button" hidden>Архивировать повреждённый запрос</button>
<p id="wfNormMessage" role="status"></p>
</details>
</section>"""+s[end:]
s=s.replace('<script src="warehouse-forecast-explain.js', '<script src="wave-command-intent.js"></script><script src="warehouse-forecast-labour.js?v=20261014-1331"></script><script src="warehouse-forecast-explain.js')
p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-forecast.js");s=p.read_text(encoding="utf-8").replace('    renderRows();\n    el("wfResult")','    renderRows();\n    window.warehouseForecastLabour?.render(r);\n    el("wfResult")').replace('    result = null;\n    el("wfResult")','    result = null;\n    window.warehouseForecastLabour?.clear();\n    el("wfResult")').replace('  el("wfRead").addEventListener("click", calculate);','  el("wfRead").addEventListener("nicora-invalidate", invalidate);\n  el("wfRead").addEventListener("click", calculate);')
p.write_text(s,encoding="utf-8")
