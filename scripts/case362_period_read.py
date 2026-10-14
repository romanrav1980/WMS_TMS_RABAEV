exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.finance.infrastructure.logistics_costs import LogisticsCosts
from app.modules.finance.contracts import LogisticsCostError
from app.oracle_gateway import OracleGateway
svc=LogisticsCosts(OracleGateway());ctx=json.loads(Path("tmp/context357.json").read_text())
result=svc.assembly_period(ctx["trip"],ctx["warehouse"],"Asia/Tbilisi","admin")
assert result["state"]=="INCOMPLETE"and result["lines"][0]["case_task_id"]==1112 and result["lines"][0]["legacy_start_present"]and result["lines"][0]["instant"]is None
assert result["financial_posting_performed"]is False and result["legacy_wall_dates_reinterpreted"]is False
try:svc.assembly_period(ctx["trip"],ctx["warehouse"],"NoSuch/Region","admin")
except LogisticsCostError as e:assert e.code=="COST_TIMEZONE_UNKNOWN"and e.status==422
else:raise AssertionError("Invented timezone accepted")
assert svc.calculate(ctx["operation_id"],ctx["trip"],ctx["warehouse"],"GEL","admin")==ctx["result"]
Path("tmp/context362.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print("PASS362 originalCASE1112 naive start explicitly incomplete/no guessed period/invalidregion422/oldfinancialreceipt preserved/no charge")
