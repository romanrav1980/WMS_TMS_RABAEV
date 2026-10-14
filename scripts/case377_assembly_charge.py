exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.oracle_gateway import OracleGateway
svc=LogisticsCosts(OracleGateway());source=json.loads(Path("tmp/context376.json").read_text());ware=source["warehouse"];trip=source["trip"];p=Path("tmp/context377.json");ctx=json.loads(p.read_text())if p.exists()else{}
def save():p.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
if "policy"not in ctx:
 ctx["policy"]=svc.configure_period("POLICY377.CASE:"+str(ware),ware,"CASE_ASSEMBLY","Pacific/Kiritimati",0,"Own synthetic timezone boundary fixture, not RETAILCASE warehouse geography","DEV377.CALENDAR","admin");save()
preview=svc.assembly_period(trip,ware,"Pacific/Kiritimati","admin");assert preview["complete"]and preview["single_period"]and len(preview["lines"])==1,preview
day=preview["business_dates"][0]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_char(cast(sys_extract_utc(LOADED_AT)as date),'YYYY-MM-DD')from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=source["load_operation_id"]);loaded_day=q.fetchone()[0]
assert day!=loaded_day,(day,loaded_day)
if "old_rate"not in ctx:ctx["old_rate"]=svc.rate(ware,"GEL","2",loaded_day,0,"Own377 loadedUTC comparison date","DEV377.OLD","admin");save()
if "assembly_rate"not in ctx:ctx["assembly_rate"]=svc.rate(ware,"GEL","3",day,1,"Own377 actual CASE business date rate","DEV377.ACTUAL","admin");save()
result=svc.calculate("COST377.ASSEMBLY:"+str(trip),trip,ware,"GEL","admin");assert result["amount"]=="3.00"and result["lines"][0]["rate_date"]==day and result["lines"][0]["period_mode"]=="CASE_ASSEMBLY"and result["lines"][0]["version"]==2,result
assert svc.calculate("COST377.ASSEMBLY:"+str(trip),trip,ware,"GEL","admin")==result
rows=svc.trip(trip,"admin")["lines"];row=next(x for x in rows if x["operation_id"]==result["operation_id"]);assert row["rate_date"]==day and row["period_time_zone"]=="Pacific/Kiritimati",row
ctx.update(result=result,preview=preview,loaded_utc_date=loaded_day,assembly_date=day,source=source);save()
print("PASS377 newly assembled markedCASE7/14codes/awarestart/explicitsyntheticcalendar day differs fromloadedUTC ->actualnewrate3 notold2/oneBOX3.00/nativeperiodproof/replay/frozenbilldate/no second stock")
