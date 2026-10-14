exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
receipt=json.loads(Path("tmp/context383.json").read_text(encoding="utf-8"))["body"]["operation_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select cell.WARE_ID,w.NAME,w.DEFAULT_RECEIVE_CELL,tt.ID,tt.VODITEL_ID,v.ID,v.NUM,v.PALLETS,v.MAX_WEIGHT_KG
 from RRL_STORE_RECEIPT_FACT f join RRL_CELLS cell on cell.CELL=json_value(f.COMPOSITION_JSON,'$.cell')
 join RRL_WARES w on w.ID=cell.WARE_ID join RRL_TT_HU_LOAD_FACT load on load.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
 join RRL_TRANSPORT_TASK tt on tt.ID=load.TT_ID join RRL_TR_VEHICLE v on v.NUM=tt.TRANSPORT
 where f.OPERATION_ID=:op""",op=receipt);print(q.fetchall())
