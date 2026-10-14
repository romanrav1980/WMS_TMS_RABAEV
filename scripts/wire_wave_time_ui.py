from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/resource-workload.html");s=p.read_text(encoding="utf-8-sig")
section='''<section class="panel" id="wtPanel" hidden><h2>Утверждение окна комплектации</h2>
<p>Меняет план существующей волны. Начатые задания переносить нельзя. Вместимость персонала и связь с рейсом проверяются отдельно.</p>
<label>Волна<input id="wtWave" type="number" min="1"></label><button id="wtLoad">Прочитать актуальную волну</button><p id="wtContext"></p>
<label>Часовой пояс плана<select id="wtZone"><option value="UTC">UTC</option><option value="Asia/Tbilisi">Тбилиси UTC+4</option><option value="Europe/Moscow">Москва UTC+3</option></select></label>
<label>Начало<input id="wtStart" type="datetime-local" step="1"></label><label>Окончание<input id="wtFinish" type="datetime-local" step="1"></label>
<label>Основание утверждения<input id="wtReason" maxlength="500"></label><button id="wtApprove" disabled>Утвердить окно комплектации</button>
<button id="wtRetry" hidden>Повторить сохранённое утверждение</button><p id="wtMessage" role="status"></p></section>
'''
s=s.replace('<p>Плановый выход и текущие активные сессии',section+'<p>Плановый выход и текущие активные сессии')
s=s.replace('<script src="resource-workload.js"></script>','<script src="resource-workload.js"></script><script src="resource-wave-time.js"></script>')
print(json.dumps({str(p):s},ensure_ascii=True))
