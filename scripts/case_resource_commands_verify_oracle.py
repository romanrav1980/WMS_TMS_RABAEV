"""Read-only before/after exact-source/schema/ledger verification, not business proof."""
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
    gateway=OracleGateway();folder=ROOT/"db/migrations/2026-10-15_case_resource_commands"
    if args.before:
        with gateway.transaction("Read-only exact CASE metadata before")as cursor:
            cursor.execute("set transaction read only");cursor.execute((folder/"before.sql").read_text(encoding="utf-8").split("\n/",1)[0])
        print(json.dumps({"status":"PASS","before_sources":5,"namespace_empty":True,"assignment_version_absent":True,"invalid":0}));return
    objects=[("case_access_spec.sql","RRL_CASE_TASK_ACCESS","PACKAGE"),("case_access_body.sql","RRL_CASE_TASK_ACCESS","PACKAGE BODY"),
        ("before_resource_policy_spec.sql","RRL_CASE_RESOURCE_POLICY","PACKAGE"),("resource_policy_body.sql","RRL_CASE_RESOURCE_POLICY","PACKAGE BODY"),
        ("start_guard.sql","RRL_CASE_START_TIME_GUARD","TRIGGER"),("spec.sql","RRL_CASE_ASSIGNMENT_API","PACKAGE"),("body.sql","RRL_CASE_ASSIGNMENT_API","PACKAGE BODY")]
    checks=[]
    for filename,name,kind in objects:
        expected=(folder/filename).read_text(encoding="utf-8").split("\n/",1)[0]
        actual="".join(row["text"]for row in gateway.fetch_all("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",{"n":name,"t":kind}))
        assert normalized(expected)==normalized(actual),(name,"SOURCE_MISMATCH")
        assert not gateway.fetch_all("select LINE,TEXT from USER_ERRORS where NAME=:n",{"n":name}),name
        checks.append({"name":name,"type":kind,"source_exact":True,"sha256":hashlib.sha256(normalized(actual).encode()).hexdigest()})
    for expected in re.findall(r"create or replace trigger .*?\n/",(folder/"version_guard.sql").read_text(encoding="utf-8"),flags=re.S|re.I):
        name=re.search(r"trigger\s+(\w+)",expected,re.I).group(1).upper()
        actual="".join(row["text"]for row in gateway.fetch_all("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",{"n":name}))
        assert normalized(actual)==normalized(expected),name
        assert not gateway.fetch_all("select LINE,TEXT from USER_ERRORS where NAME=:n",{"n":name}),name
        checks.append({"name":name,"type":"TRIGGER","source_exact":True,"sha256":hashlib.sha256(normalized(actual).encode()).hexdigest()})
    invalid=gateway.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]["n"];assert invalid==0
    ledger=gateway.fetch_all("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-case-resource-commands'");assert ledger==[{"migration_id":"2026-10-15-case-resource-commands","status":"APPLIED"}]
    column=gateway.fetch_all("select COLUMN_NAME,DATA_TYPE,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK'and COLUMN_NAME='ASSIGNMENT_VERSION'");assert column==[{"column_name":"ASSIGNMENT_VERSION","data_type":"NUMBER","nullable":"N"}]
    default=gateway.fetch_all("select DATA_DEFAULT from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK'and COLUMN_NAME='ASSIGNMENT_VERSION'")[0]["data_default"];assert default.strip()=="0"
    index=gateway.fetch_all("select INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME='RRL_CASE_RESOURCE_TASK_IX'");assert index==[{"index_name":"RRL_CASE_RESOURCE_TASK_IX","status":"VALID"}]
    constraints=gateway.fetch_all("select CONSTRAINT_NAME,STATUS,VALIDATED from USER_CONSTRAINTS where TABLE_NAME='RRL_CASE_RESOURCE_COMMAND'order by CONSTRAINT_NAME")
    assert constraints and all(row["status"]=="ENABLED"and row["validated"]=="VALIDATED"for row in constraints)
    runtime=ROOT/"reports/retailcase/2026-10-15/case-resource-commands/context-runtime-proof.json"
    proof=json.loads(runtime.read_text(encoding="utf-8"));assert proof["status"]=="PASS"and proof["caller_rollback"]is True
    context={"verification":"Separate trusted API native caller-rollback runtime proof", "report":str(runtime.relative_to(ROOT)),"catalog_note":"ALL_CONTEXT shows session values, not namespace catalog"}
    report={"status":"PASS","source_checks":checks,"ledger":ledger,"column":column,"constraints":constraints,"context":context,"invalid":invalid,"scope":"Exact source/schema only; native business/receipt/revoke/concurrency and HTTP separate"}
    output=ROOT/"reports/retailcase/2026-10-15/case-resource-commands";output.mkdir(parents=True,exist_ok=True)
    (output/"oracle-verification.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","source_checks":len(checks),"invalid":invalid,"ledger":"APPLIED"}))


if __name__=="__main__":main()
