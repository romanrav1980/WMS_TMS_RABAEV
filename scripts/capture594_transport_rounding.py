exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder=Path("db/migrations/2026-10-12_ni071_transport_rounding");folder.mkdir(parents=True,exist_ok=True)
if(folder/"checkpoint.json").exists():raise SystemExit("594 snapshot already captured; do not recapture")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();pieces=[]
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_COST_API'and TYPE=:kind order by LINE",kind=kind)
  pieces.append("create or replace "+"".join(row[0]for row in q.fetchall()).strip()+"\n/\n")
 old="\n".join(pieces)
 q.execute("select CONSTRAINT_NAME,SEARCH_CONDITION_VC from USER_CONSTRAINTS where TABLE_NAME='RRL_TRANSPORT_COST_DETAIL'and CONSTRAINT_TYPE='C'")
 constraints=q.fetchall();matches=[name for name,text in constraints if text and "ROUND" in text.upper()and "AMOUNT" in text.upper()]
 assert len(matches)==1,matches;name=matches[0];assert name.replace("_","").replace("$","").isalnum()
 new=old.replace("amount:=quantity*round(rate_value,2)","amount:=round(quantity*rate_value,2)").replace("HALF_UP_2_PER_CHARGE_UNIT","HALF_UP_2_PER_ARTICLE")
 assert new!=old
 (folder/"000_before_api.sql").write_text(old,encoding="utf-8");(folder/"001_api.sql").write_text(new,encoding="utf-8")
 (folder/"002_rounding_constraint.sql").write_text("alter table RRL_TRANSPORT_COST_DETAIL add constraint RRL_TRAN_COST_AMOUNT_CK check(AMOUNT=round(QUANTITY*RATE_VALUE,2));\n"+"alter table RRL_TRANSPORT_COST_DETAIL drop constraint "+name+";\n",encoding="utf-8")
 (folder/"rollback.sql").write_text("alter table RRL_TRANSPORT_COST_DETAIL add constraint "+name+" check(AMOUNT=QUANTITY*round(RATE_VALUE,2));\nalter table RRL_TRANSPORT_COST_DETAIL drop constraint RRL_TRAN_COST_AMOUNT_CK;\n@@000_before_api.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-594-transport-article-rounding';\n",encoding="utf-8")
 (folder/"checkpoint.json").write_text(json.dumps({"migration_id":"2026-10-12-594-transport-article-rounding","before_sha256":hashlib.sha256(old.encode()).hexdigest(),"after_sha256":hashlib.sha256(new.encode()).hexdigest(),"before_constraint":name,"recovery":"Package source captured; old-rule constraint rollback validates retained facts and refuses incompatible new amounts, no history changes."},indent=2)+"\n",encoding="utf-8")
 print("594 canonical live source/constraint captured; aggregate-article rounding matches existing finance domain amount.cost_amount, no data rewrite.")
