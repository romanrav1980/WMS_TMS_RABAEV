"""Two isolated dev addresses for retained B01; no stock DML and no shared-cell reconfiguration."""
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context1238.json").read_text(encoding="utf-8"))
assert ctx["stage"]=="RECEIVING" and len(ctx["receipts"])==1 and ctx["receipts"][0]["status"]>=400
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 cells=[]
 for i in range(2):
  cell="B38"+ctx["tag"][:8]+str(i+1);cells.append(cell)
  q.execute("select count(*)from RRL_CELLS where CELL=:c",c=cell)
  if q.fetchone()[0]:continue
  q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,9807,:x,1,1,0,0,1000,3)",c=cell,x=2+i)
  q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 c.commit()
ctx["storage_cells"]=cells;ctx["first_receipt_refusal"]=ctx.pop("receipts")
ctx["stage"]="STORAGE_READY";Path("tmp/context1238.json").write_text(json.dumps(ctx,indent=2),encoding="utf-8")
print(json.dumps({"stage":ctx["stage"],"cells":cells,"stock_changed":False}))
