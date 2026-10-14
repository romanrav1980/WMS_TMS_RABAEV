import json
from pathlib import Path
f=Path("db/migrations/2026-10-11_ni042_case_sscc")
root=(f/"000_before_case.sql").read_text(encoding="utf-8")
needle="  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id;"
assert root.count(needle)==1
root=root.replace(needle,needle+"\n  RRL_CASE_SSCC_API.assert_ready(task_id);")
needle="  select * into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=task_id for update;"
assert root.count(needle)==1
root=root.replace(needle,needle+"\n  RRL_CASE_SSCC_API.assert_ready(task_id);")
out={str(f/"005_case.sql"):root,
str(f/"apply.sql"):"@@001_schema.sql\n@@002_allocator.sql\n@@003_api.sql\n@@004_guard.sql\n@@005_case.sql\n",
str(f/"rollback.sql"):"declare n number;begin select count(*)into n from RRL_CASE_SSCC_LABEL;if n>0 then raise_application_error(-20863,'CASE_SSCC_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;\n/\n@@000_before_case.sql\ndrop trigger RRL_CASE_SSCC_ID_GUARD;\ndrop trigger RRL_CASE_SSCC_LABEL_GUARD;\ndrop context RRL_CASE_SSCC_CTX;\ndrop package RRL_CASE_SSCC_API;\ndrop package RRL_SSCC_ALLOCATOR;\ndrop table RRL_CASE_SSCC_LABEL;\n",
str(f/"verify.sql"):"select object_name,object_type,status from user_objects where object_name in('RRL_SSCC_ALLOCATOR','RRL_CASE_SSCC_API','RRL_CASE_SSCC_LABEL_GUARD','RRL_CASE_SSCC_ID_GUARD','RRL_STOCK_CASE_PICK_CMD');\nselect name,type,line,text from user_errors where name not like 'BIN$%';\n",
"wiki/database/nicora_ni042_case_sscc_design_20261011.md":"# NI04.2: SSCC малой коробки\n\nМиграция 2026-10-11-203-case-logistic-sscc. Новый идентификатор выдаётся только пустому CASE до отбора. Общая последовательность приёмки и складской настройки GS1 повторно используется; назначенный компании префикс обязателен. CP сохраняется в неизменяемом архиве. Обновление идентификатора и версии, архив исходной команды и ответа — одна существующая metadata-транзакция CONFIG; количества и резервы не меняются. Повтор той же команды возвращает исходный ответ; другое содержимое отвергается.\n\nПодтверждение требует сканирования прикреплённого SSCC. Тип CONTAINER с FINAL_WEIGHT_REQUIRED требует подтверждения до первого отбора в исходном native CASE, включая повторную проверку под блокировками. Обычные старые места без этого признака сохраняют текущий путь. После выдачи SSCC его замена запрещена. Печать использует существующие GS1-128 SVG/ZPL, без планового количества на этикетке пустой коробки. Это логистическая этикетка; ответ государственной системы агрегации отдельно.\n\nВосстановление: свежие CASE package и labels.py сохранены в 000_before/checkpoint.json; пустые новые объекты обратимы paired rollback. При появлении архива необходима корректирующая миграция с сохранением истории. Копия базы не создаётся.\n"}
print(json.dumps(out,ensure_ascii=True))
