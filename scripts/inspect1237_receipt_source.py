exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
x=json.loads(Path("tmp/context1118.json").read_text(encoding="utf-8"))
print(json.dumps({"articles":x["articles"],"tag":x["tag"]}))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for title,sql,bind in [
 ("warehouse","select ID,DEFAULT_RECEIVE_CELL from RRL_WARES where ID=9807",{}),
 ("cells","select CELL,WARE_ID,OTBOR,X,Y,Z from RRL_CELLS where CELL like 'DS-BASE-%' order by CELL",{}),
 ("articles","select ACTICUL,CELL,NORMA_UKLADKI from RRL_ARTICULS where ACTICUL in(:a,:b)",dict(a=x["articles"][0],b=x["articles"][1])),
 ("rules","select * from RRL_RECEIPT_SKU_RULE where WARE_ID=9807 and ARTICUL in(:a,:b)",dict(a=x["articles"][0],b=x["articles"][1]))]:
  try:q.execute(sql,bind);print(json.dumps({"kind":title,"columns":[i[0]for i in q.description],"rows":q.fetchmany(30)},default=str))
  except oracledb.Error as e:print(json.dumps({"kind":title,"error":str(e).split("\n")[0]}))
