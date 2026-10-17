"""Read-only exact before/after source verification; not native business acceptance."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway


def normalized(value):
    value=re.sub(r"^create\s+or\s+replace\s+","",value.replace("\r","").strip(),flags=re.I)
    return value.rstrip("/").strip()


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--before",action="store_true");args=parser.parse_args()
    gateway=OracleGateway();folder=ROOT/"db/migrations/2026-10-15_case_scoped_confirmation"
    objects=[("case_access_spec","RRL_CASE_TASK_ACCESS","PACKAGE"),("case_access_body","RRL_CASE_TASK_ACCESS","PACKAGE BODY"),
             ("resource_policy_spec","RRL_CASE_RESOURCE_POLICY","PACKAGE"),("resource_policy_body","RRL_CASE_RESOURCE_POLICY","PACKAGE BODY"),
             ("case_pick_spec","RRL_STOCK_CASE_PICK_CMD","PACKAGE"),("case_pick_body","RRL_STOCK_CASE_PICK_CMD","PACKAGE BODY")]
    checks=[]
    for key,name,kind in objects:
        filename=("before_" if args.before or key in("resource_policy_spec","case_pick_spec")else "")+key+".sql"
        expected=(folder/filename).read_text(encoding="utf-8")
        actual="".join(r["text"]for r in gateway.fetch_all("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",{"n":name,"t":kind}))
        assert normalized(expected)==normalized(actual),(name,kind,"SOURCE_MISMATCH")
        assert not gateway.fetch_all("select LINE,TEXT from USER_ERRORS where NAME=:n",{"n":name}),name
        checks.append({"object":name,"type":kind,"source_exact":True,"sha256":hashlib.sha256(normalized(actual).encode()).hexdigest()})
    invalid=gateway.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]["n"];assert invalid==0
    ledger=gateway.fetch_all("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-scoped-confirmation'")
    if not args.before:assert len(ledger)==1 and ledger[0]["status"]=="APPLIED"
    else:assert not ledger
    slow=gateway.fetch_all("select LOG_ID,ELAPSED_MS,API_PATH,dbms_lob.substr(SQL_TEXT,250,1) SQL_SAMPLE from RRL_SQL_SLOW_LOG where CREATED_AT>=systimestamp-interval'1'hour order by CREATED_AT desc fetch first 12 rows only")
    report={"status":"PASS","mode":"BEFORE"if args.before else"APPLIED","source_checks":checks,"invalid_count":invalid,"ledger":ledger,"recent_slow":slow,
            "scope":"Exact source/errors/ledger only; real current-rights/stock/resource/replay/concurrency proof separate",
            "sql_decision":"CASE-bound identity and line closure retained; inspect attributed long-query plan before index change. No capacity claim."}
    output=ROOT/"reports/retailcase/2026-10-15/scoped-case-audit";output.mkdir(parents=True,exist_ok=True)
    (output/("before-verification.json"if args.before else"oracle-verification.json")).write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","mode":report["mode"],"source_checks":len(checks),"invalid_count":invalid,"slow_count":len(slow)}))


if __name__=="__main__":main()
