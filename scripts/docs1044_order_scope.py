from pathlib import Path
import json
files={}
report="""# 23 · Заказы: текущий склад и точные количества

13.10.2026, продолжение по поручению владельца после 20:00. NI03.3 остаётся in_progress.

## Результат
HTTP-список и карточка заказа теперь используют существующий RRL_STORE_ORDER_SCOPE для права customer_order_view и текущего склада RUSERS. GLOBAL_ADMIN сохраняет доступ ко всем складам. Список фильтруется по складу в SQL до лимита, карточка проверяет источник до выдачи данных; весь сценарий в одном READ ONLY snapshot. Новых Oracle объектов и проводок нет.

Исходные SQL извлечены из CustomerOrderService в небольшой fulfillment reader/public factory. Старые in-process методы оставлены как явно доверенные legacy readers; HTTP ими больше не пользуется. Это не новая система заказов.

Карточка возвращает точные десятичные ORDER_QTY/ORDER_WEIGHT/PACK_COUNT строками, сохраняя числовые поля. UI и начальная раскладка SAP используют точные строки. Список показывает сумму только для одинаковой известной единицы; для смешанных/неизвестных единиц — «См. позиции». Историческая числовая сумма в API сохранена для совместимости. Более 2000 строк карточки отклоняются явно, усечённый заказ не выдаётся за полный.

## Фактические проверки
Native1041: старый заказ1931/4EA, текущий2133/12EA, admin limit5, missing и QA172_KRO denied, legacy compatibility — PASS. В базе не найден обычный действующий пользователь с правом customer_order_view/WARE; положительный foreign-WARE сценарий не заявляется.

HTTP1043 после root serv.bat: оба заказа/точные строки, list limit3/UOMmetadata, missing404/invalid409 — PASS. JS1024: поздний ответ другого заказа/смена пользователя не подменяют текущую карточку — PASS. Первый runtime вызов1041 обнаружил конфликт имени list с Python annotation; исправлен postponed annotations до повторной проверки.

Скриншот29 показывает реальную прежнюю строку4/подтверждено3/резерв0/осталось1, открытие через URL. Новых приёмок, движений, SAP-отправок не выполнялось.

SQL1041: detail rows 3.710ms/3.3buffer gets (3exec). Решение: оставить order-key/bound2001; list500 сохранён. Для растущего каталога owner fulfillment: keyset до агрегирования вместо полного агрегирования+rownum, отдельный ticket по фактическому плану. Индекс без подтверждённого плана не добавлялся.
"""
files["reports/retailcase/2026-10-13/23-order-scope-report.md"]=report
e={"native":json.loads(Path("tmp/read1041_customer_order_scope.json").read_text(encoding="utf-8")),"http":json.loads(Path("tmp/http1043_order_scope.json").read_text(encoding="utf-8"))}
files["reports/retailcase/2026-10-13/23-order-scope-evidence.json"]=json.dumps(e,indent=2,ensure_ascii=False)
p="reports/retailcase/2026-10-13/index.html"
t=Path(p).read_text(encoding="utf-8")
t=t.replace("</main>","""<article><h2>23 · Заказы по текущему складу</h2><p>Список и карточка проверяют RUSERS/право/WARE в одном snapshot; точные количества и единицы сохраняются.</p><p><a href="23-order-scope-report.md">Отчёт</a> · <a href="23-order-scope-evidence.json">Данные</a></p><img src="screenshots/29-order-scoped-execution.png" alt="Сохранённый заказ: потребность4, факт3, остаток1"></article></main>""")
files[p]=t
p="wiki/components/retailcase_order_execution_workspace_20261013.md"
files[p]=Path(p).read_text(encoding="utf-8")+"\n## Продолжение1040–1044\n\n"+report.split("## Результат",1)[1]
p="wiki/requirements/retailcase_delivery_v55/implementation_plan.json"
d=json.loads(Path(p).read_text(encoding="utf-8"));d["planRevision"]=45
d["firstChange"]="Continue all remaining functional sprints per owner instruction after20:00, reuse existing modules; do not declare real ERP/Gov/hardware or independent acceptance without evidence."
files[p]=json.dumps(d,indent=2,ensure_ascii=False)+"\n"
p="wiki/requirements/retailcase_delivery_v55/implementation_plan.md"
t=Path(p).read_text(encoding="utf-8").replace("**Revision 44,","**Revision 45,")
files[p]=t+"\nRevision45/checkpoint1044: общий список/карточка заказов подключены к текущему native warehouse scope, exact quantities/UOM UI, report23/screen29; NI03.3 in_progress. Владелец поручил продолжать после20:00 до фактического завершения, прежний срок больше не действует.\n"
p="wiki/requirements/retailcase_delivery_v55/execution/active/ni03_3.md"
files[p]=Path(p).read_text(encoding="utf-8")+"\n1040–1044: original list/detail extracted/scoped native currentWARE, exact quantities and UOM summary, native/HTTP/JS/browser evidence report23. Full status remains in_progress.\n"
p="wiki/runbooks/retailcase_active_work.md"
files[p]="# Продолжение1044 по новому поручению владельца\n\nПрежний срок20:00 отменён: выполнять до фактического завершения всех спринтов. Plan45/currentNI03.3, all18 ещё не завершены. API1043/current, report23/screen29. Новые scope/list/detail/exactquantity readers reuse native existing RRL_STORE_ORDER_SCOPE; noDDL/noStockWrites. Ниже прежние checkpoints исторические. Conditional fullcommit/GitHub only after all complete; no agents/goals/DBcopies.\n\n"+Path(p).read_text(encoding="utf-8")
p="wiki/index.md"
files[p]="- [Продолжение1044: заказы по текущему складу](components/retailcase_order_execution_workspace_20261013.md): scoped list/detail/exactquantity, report23/screen29, plan45; продолжать до завершения.\n"+Path(p).read_text(encoding="utf-8")
p="wiki/log.md"
files[p]=Path(p).read_text(encoding="utf-8")+"\n- 13.10.2026 checkpoint1044 — возобновление по поручению владельца без срока20:00; scoped original order reads/exact UOM UI; plan45/report23/screen29, noStockWrites. NI03.3 остаётся открыт.\n"
files["задания на проведения тестов/NI03.3/1044_склад_заказа_точные_количества.md"]="""# NI03.3 — заказы и точные количества
Проверить новый public CustomerOrderRead/HTTP list-detail: текущая native роль/WARE, GLOBAL_ADMIN, ограничение до500/2000, неизменённые старые факты, exact decimal strings в UI и раскладкеSAP. Подтвердить обычного пользователя своего склада и отказ чужого, не менять права рабочего пользователя. Без повторного создания сохранённых источников и без реальных отправок. QA172_KRO denied — не доказательство чужого склада. Убедиться, что сумма разных UNIT_CODE не отображается как одно количество. Отчёт23 содержит actual evidence; авторские проверки не независимая приёмка. Проводки этих read-only действий отсутствуют. ДолгийSQL требует решения владельца fulfillment.
"""
print(json.dumps(files,ensure_ascii=True))
