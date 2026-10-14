exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
files={};root="db/migrations/2026-10-14_ni022_prepared_row_move/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(x[0]for x in q).replace("\r","").rstrip()+"\n/\n"
 expected=Path(root+"004_root.sql").read_text(encoding="utf-8").strip()
 assert before.strip().lower()==expected.lower(),"Current root drift: inspect before patch"
 files[root+"000_before_fullpal_scope.sql"]=before
 point="g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE')"
 assert before.count(point)==2
 files[root+"006_fullpal_scope.sql"]=before.replace(point,"g_kind in('TASK_COMPLETE','HU_TASK_COMPLETE','PICK_PALLET_BIND_SHIPMENT')")
 p=Path(root+"apply.sql");files[str(p)]=p.read_text(encoding="utf-8")+"@@006_fullpal_scope.sql\n"
 p=Path("wiki/database/retailcase_ni022_prepared_row_move_20261014.md")
 files[str(p)]=p.read_text(encoding="utf-8")+"\n1275:1265 установлена; явный UI перенос строки16727991 ->641508 выполнен операцией ST.LAYOUT:f840ec86-d60f-4308-8d65-b2be2754fade/outbox5206.18+18EA/3+3коробки/12+12кг, прежние ST IDs/рейс33571 сохранены; exact replay и native rollback PASS, stock36/hard36. Подготовлено дополнение006: существующий RRL_WAREHOUSE_TASK_ACCESS.assert_completion применяется также к FULLPAL binding до replay и после fence, без нового механизма авторизации.\n"
 p=Path("wiki/index.md");files[str(p)]="- [Укладка СТ1275](database/retailcase_ni022_prepared_row_move_20261014.md): actual row move18+18/6boxes/24kg, oldST IDs/trip/replay; FULLPAL scope reuse подготовлен.\n"+p.read_text(encoding="utf-8")
 p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 /1275: штатный перенос строки СТ выполнен через UI/Root; rollback+replay подтверждены. Подготовлен reuse task-access для FULLPAL binding; текущий Root captured, изменений физического остатка нет.\n"
print(json.dumps(files))
