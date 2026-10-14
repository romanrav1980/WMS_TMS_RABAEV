from pathlib import Path
import json
files={}
page="""# NI03.3: рабочее место фактического исполнения волны

860–864 сохраняют существующие GET execution / POST finish-execution и native WAVE_EXECUTION_FINISH. Никакой второй реализации запуска/отгрузки/остатка не вводится.

Wave-execution controller, view и scoped intent разделены. Выбранная волна обновляет панель; прямой wave_id открывает исполнение даже вне первых100 строк очереди. Таблица причин содержит ссылки на реальные warehouse tasks. Потребность planning остаётся отдельно от отгруженного факта. Исторические причины у DONE подписаны как исторические; кнопки нового завершения запрещены.

Read responses сверяются с номером волны и actor/API scope; stale response игнорируется. Saved pending schema whitelist разрешает только wave, operation_id и допустимые disposition/reason. Пока есть pending, новый body/волна не создаются. Cross-tab raw compare и scope compare сохраняют исходник. POST success должен подтвердить ту же wave/operation/DONE/completed; потерянный/неподходящий ответ сохраняет исходный запрос. Повреждённый raw блокирует writes; архив сохраняет исходник до удаления и server reread.

Progress panel теперь показывает таблицу per-SKU BASE: demand/planned/confirmed/unfulfilled/pick remaining/capacity. Selection и identity guards, явный лимит50; отсутствие rows не объявляется исполнением заказа. Панели перенесены внутрь рабочего layout.

Фактический read859 / browser863 для защищённой wave403: DONE, warehouse839 DONE3, cancelled original order1930/line3415 planning1EA. Команды не отправлялись, данные не менялись. Screenshot11 — реальный браузер до финального CSS/подписи historical; не заявлять новый native end-to-end. JS861 PASS intent malformed/other-tab/context/archive. Разработчик, не независимая приёмка спринта.

SQL857 по последнему NI03.2 case: canonical projection17.832ms/136 buffers, cancel12.596ms, partial12.291ms/184 buffers; continuation2.783ms. Более старый projection102ms/241buffers: сохраняем bounded windows, владелец resources; при устойчивом>500ms проверить план/статистику. Новые индексы не обоснованы.
"""
files["wiki/components/nicora_ni033_wave_workspace_20261013.md"]=page
files["reports/nicora/2026-10-13/09-wave-workspace-report.md"]="# Экран исполнения волны\n\n"+page.split('\n',2)[2]+"\n![Реальный экран волны403](screenshots/11-wave-execution.png)\n"
p=Path("reports/nicora/2026-10-13/index.html");files[str(p)]=p.read_text(encoding="utf-8").replace("</main>",'<article><h2>09 · Исполнение волны</h2><p>Фактические задания, причины, потребность и восстановление сохранённого решения.</p><a href="09-wave-workspace-report.md">Отчёт №9</a><img src="screenshots/11-wave-execution.png" alt="Фактическое исполнение волны403"></article></main>')
p=Path("wiki/index.md");files[str(p)]="- [Checkpoint864: исполнение волны](components/nicora_ni033_wave_workspace_20261013.md): existing native/API, scoped pending/recovery, выбор волны и реальные links; read/browser403, report09.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 checkpoint864: NI03.3 existing wave workspace/controller-view-intent split, stale scope guards and exact saved result verification, archive+server reread; table/progress/warehouse links; read403/screenshots10-11/report08-09, no native write. SQL857 retain bounded noindex. Full increment remains open.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"))
inc=next(x for x in plan["increments"]if x["id"]=="NI03.2");inc["pendingSlices"][0]="Other physical split modes, duplicate retained bindings on same selected stock, marked/concurrent independent multi-continuation acceptance"
inc=next(x for x in plan["increments"]if x["id"]=="NI03.3");inc["implementedSlices"].append("860-864 actual execution workspace/selected wave/task links/read-only403; controller-view-intent split, scoped exact pending/recovery, progress table; no new lifecycle engine")
files[str(p)]=json.dumps(plan,ensure_ascii=False,indent=2)
print(json.dumps(files,ensure_ascii=True))
