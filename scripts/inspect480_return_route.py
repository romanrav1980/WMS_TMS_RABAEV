exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
case=json.loads(Path("tmp/case211.json").read_text(encoding="utf-16"))
print("CASE211_KEYS",list(case))
receipt=json.loads(Path("tmp/context383.json").read_text(encoding="utf-8"))["body"]["operation_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("""select f.LOAD_OPERATION_ID,l.LOT_UID,l.ARTICLE,l.BASE_UOM,json_value(o.RESOLVED_PLAN_JSON,'$.domain.transport_task_id'returning number),
 json_value(o.RESOLVED_PLAN_JSON,'$.domain.warehouse_id'returning number)from RRL_STORE_RECEIPT_FACT f
 join RRL_STORE_RECEIPT_LINE l on l.OPERATION_ID=f.OPERATION_ID join RRL_STOCK_OPERATION o on o.OPERATION_ID=f.LOAD_OPERATION_ID where f.OPERATION_ID=:op""",op=receipt)
 print("SOURCE",q.fetchall())
 for key in ["tag","warehouse","ware","trip","driver","vehicle","plate","article","shipcell","receive","box_barcode","expiry","supplier_batch"]:
  if key in case:print(key,case[key])
