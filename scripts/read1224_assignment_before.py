exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
target=Path("tmp/context1224.json")
if target.exists():raise RuntimeError("Retained assignment proof exists; continue, do not recreate")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PALLET_UID,TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS where ST_NUMBER='SAP_2135'order by ID");rows=q.fetchall();assert len(rows)==2 and all((r[2]or 0)==0 for r in rows),rows
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=9807");stock=q.fetchone()
 target.write_text(json.dumps({"state":"UNASSIGNED","trip":33571,"st":"SAP_2135","rows":rows,"before_stock":stock},indent=2),encoding="utf-8")
 print(json.dumps({"status":"READY1224","stock":stock,"rows":len(rows)}))
