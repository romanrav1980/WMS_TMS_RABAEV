from pathlib import Path
import json
out={};page="wiki/database/nicora_ni081_cluster_retry_20261010.md"
out[page]="""# NI08.1 — устойчивый повтор создания кластера,139

Исходный API /api/admin/transport/clusters/{raion}/create-task, поиск района и native TT/ST writers сохранены. ClusterCreateTaskRequest теперь требует operation_id (ASCII1..100). Существующий React caller создаёт ID до отправки, сохраняет body/район в localStorage по API+username без пароля; сетевой сбой/5xx/401/403 сохраняет исходную операцию. Изменённые параметры при неизвестном исходе отклоняются с исходными параметрами; подтверждённый бизнес/input отказ400/404/409/422 снимает pending для исправления. TypeScript typecheck PASS; интерактивное независимое UI acceptance остаётся открытым.

Migration2026-10-10-139-idempotent-existing-cluster APPLIED8/0: RRL_CLUSTER_CREATE_RESULT(request hash/body/actor/original TT FK/result/TZ created), guarded native RRL_CLUSTER_CREATE_API. Уникальный ключ операции сериализует одинаковый повтор; one UOW включает прежнее создание, изменение, общую capacity-проверку и назначение. Права активного RUSERS+transport_dispatch_edit и warehouse scope проверяются перед эффектом/при повторе. Записанный состав СТ и warehouse_ids отражает фактическое назначение после заблокированных проверок, не новый список доступности при retry.

Native SAVEPOINT RRL_CLUSTER139 откатывает все собственные изменения при ошибке, даже если внешний PL/SQL-код перехватывает её и фиксирует остальную транзакцию. Сам пакет не commit, не проводит P/H и не вызывает второй алгоритм распределения. До200 СТ/65536chars sourceJSON/2000chars request; API request bytes<=4000. Результат immutable; прямой update/delete не разрешён. Rollback migration после истории запрещён, исправления forward.

scripts/ni081_cluster_retry_existing_case.py переиспользовал только прежние136 частные источники: ошибка10kg машины не оставила TT/operation; два concurrent запроса CLUSTER139:b40b0303ee3b вернули один33528, точный source snapshot2; changed body409, прямой proof update20863. Свой33528 отменён, машины снова неактивны. Повтор с пустым найденным списком возвращает сохранённый отменённый TT как историю, не создаёт новый.
scripts/ni081_cluster_http_replay_case.py: настоящий прежний HTTP endpoint после отмены вернул точный saved33528, missing operation422. После перекомпиляции native package первый pooled lease дал503; исходный повтор того жеID дал сохранённый200 без нового TT.
scripts/ni081_cluster_caught_error_case.py: внешний PL/SQL поймал ошибку неактивной машины и сделал commit; own savepoint оставил0 новых TT и0 proof. Независимая приёмка не объявлена.

Oracle new package/spec/body/guard + stock root/transport136/137 liveVALID. Native cluster cursor mean27.473ms/7 executions; сохранить ограниченные исходные выборки/ключевые индексы, не объявлять throughput. Inventory receiving metadata extraction138 replay preserved original result/events; архитектурные циклы0, прочий общий debt остаётся FAIL.

Дальше NI08.1: окна времени/текущий водитель/тара и согласованное изменение волны-рейса, затем NS59 динамические зоны с approval/drain. Этот срез не закрывает весь NI08.1 или внешние интеграции.
"""
out["wiki/index.updated.tmp"]="- [Устойчивое создание кластера](database/nicora_ni081_cluster_retry_20261010.md):139 native operation/source snapshot/concurrent one TT33528/replay after cancellation/savepoint/React pending.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:139 cluster operation mandatory/durable UI pending API+actor/native immutable result/private operation-TX guard. APPLIED8/0/liveVALID; original136 sources concurrent sameID→one33528/changed409/direct20863/retired metadata, actual HTTP empty-source saved replay/missingID422. Native savepoint outer caught failure+commit left no TT/proof. Post recompile pooled503→sameID200, no new operation. Native mean27.473ms/7 retain bounds/keyed indices; UI typecheck PASS, independent timing/capacity acceptance open."),
 ("wiki/requirements/nikora_delivery_v55/implementation_plan.md","NI08.1 author139: existing cluster one native UOW/current scope/immutable original TT/source/idempotent operation and client pending. Concurrent sameID creates one33528, changed request409, native caught error rollback; full timing/coordination/NS59/independent acceptance remain open.")
]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("138/139 atomic original cluster/current warehouse/source snapshot/durable operation/replay/UI pending")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_139_timing_coordination_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
m["packages"].append("RRL_CLUSTER_CREATE_API")
m["components"].append("../2026-10-10_ni081_cluster_retry/002_api.sql")
m["additional_scripts"].extend(["../2026-10-10_ni081_cluster_retry/001_schema.sql","../2026-10-10_ni081_cluster_retry/003_guard.sql"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/139_устойчивый_повтор_кластера.md"]="""# Qwen —139

Читайте wiki/database/nicora_ni081_cluster_retry_20261010.md и design. Не создавать товар; собственный33528 уже отменён,136 машины retired. Авторские кейсы указаны в wiki; свежий case создаёт только TT-метаданные, предпочтительнее read/replay.

Проверьте native операция→машины→новый TT→упорядоченные СТ, одна транзакция прежних writers, duplicate wait/recheck/current rights+scope. Состав только первого применения; replay даже после отмены сохраняет историю, другой body/actor запрещён. Пакет без commit, свой savepoint откатывает даже при outer catch+commit. Result guard private operation+TX, mutation denied, history rollback запрещён.

HTTP обязательный ID/missing422; UI до fetch сохраняет исходный request с ID по API+username без пароля. Network/5xx/auth-loss сохраняет pending, changed form не подменяет неизвестную операцию. Успех очищает pending до read-only reload; confirmed4xx business/input разрешает корректировку. Проверьте восстановление после reload, отключения и успеха сервера до потери ответа. Typecheck не считается UI acceptance.

Нельзя считать планирование физическим допуском груза или закрывать NI08.1: временные окна, driver/tare и approval wave/TT ещё впереди.
"""
print(json.dumps(out,ensure_ascii=True))
