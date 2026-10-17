"""Source/ledger readback; does not claim business acceptance."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway

def norm(s):
    return re.sub(r"^create\s+or\s+replace\s+","",s.replace("\r","").strip(),flags=re.I).rstrip("/").strip()

def main():
    g=OracleGateway();folder=ROOT/"db/migrations/2026-10-15_assembly_intent_abandon";checks=[]
    items=[("spec.sql","RRL_ASM_INTENT_API","PACKAGE"),("body.sql","RRL_ASM_INTENT_API","PACKAGE BODY"),("guards.sql","RRL_ASM_INTENT_GUARD","TRIGGER"),("assembly_body.sql","RRL_ASSEMBLY_SCALE_API","PACKAGE BODY")]
    for file,name,kind in items:
        expected=(folder/file).read_text(encoding="utf-8-sig").split("\n/",1)[0]
        actual="".join(x["text"]for x in g.fetch_all("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",{"n":name,"t":kind}))
        assert norm(actual)==norm(expected),(name,"SOURCE_MISMATCH")
        assert not g.fetch_all("select TEXT from USER_ERRORS where NAME=:n",{"n":name})
        checks.append(dict(name=name,kind=kind,exact=True,sha256=hashlib.sha256(norm(actual).encode()).hexdigest()))
    invalid=g.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]["n"];assert invalid==0
    ledger=g.fetch_all("select STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-assembly-intent-abandon'");assert ledger==[{"status":"APPLIED"}]
    out=ROOT/"reports/retailcase/2026-10-15/assembly-intent";out.mkdir(parents=True,exist_ok=True)
    report=dict(status="PASS",checks=checks,invalid=invalid,ledger=ledger,scope="Source and DDL; native business separate")
    (out/"oracle-verification.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__":main()
