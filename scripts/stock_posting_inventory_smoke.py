"""Post-cutover inventory smoke; refuses PREPARED and uses tagged command history."""
import json
import sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
    c.call_timeout=15000
    q=c.cursor()
    try:
        q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
        assert q.fetchone()==("RABAEV","orcl")
        q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        assert q.fetchone()==("ACTIVE",), "Run only after the complete cutover"
        q.execute("select (select count(*) from RRL_REMAINS),(select count(*) from RRL_EVENTS),(select count(*) from RRL_STOCK_OPERATION) from dual")
        assert q.fetchone()==(0,0,0)
        q.execute("""select p.UID_PALLET,p.ARTICUL from RRL_PALLETS p
          where exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=p.ARTICUL and u.INPUT_UOM='EA' and u.BASE_UOM='EA' and u.NUMERATOR=1 and u.DENOMINATOR=1)
           and not exists(select 1 from RRL_SKU_RECEIPT_POLICY x where x.ARTICUL=p.ARTICUL and x.MARKING_REQUIRED=1)
           and not exists(select 1 from RRL_SKU_RECEIPT_PROFILE x where x.ARTICUL=p.ARTICUL)
           and not exists(select 1 from RRL_FINISHED_GOODS_SKU x where x.ARTICUL=p.ARTICUL and x.CRPT_REQUIRED=1)
          order by p.UID_PALLET fetch first 1 row only""")
        uid,article=q.fetchone()
        q.execute("""select CELL,WARE_ID from RRL_CELLS where WARE_ID is not null
           and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0
           order by WARE_ID,CELL fetch first 1 row only""")
        cell,ware=q.fetchone()
        revision=q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"])
        c.commit()  # Metadata-only revision created before the command transaction.
        def post(operation, quantity, version):
            payload=json.dumps({"contract_version":2,"operation_id":operation,"command_type":"INVENTORY_COUNT","actor":"admin",
                "source":{"revision_id":int(revision)},"lines":[],"units":[],
                "metadata":{"reason":"Committed cutover inventory case","counts":[{"uid":uid,"cell":cell,"article":article,
                    "unit":"EA","quantity":quantity,"expected_stock_version":version,"unit_keys":[]}]}},sort_keys=True,separators=(",",":"))
            inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,payload);out=q.var(oracledb.DB_TYPE_CLOB)
            q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
            replay=out.getvalue()
            if replay is None:
                q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
            result=out.getvalue();result=json.loads(result.read() if hasattr(result,"read") else result)
            c.commit()
            q.callproc("RRL_STOCK_POSTING_API.reset_connection")
            return result,replay is not None
        operation="SMOKE.INVENTORY:"+uuid4().hex
        result,replay=post(operation,"1",0);assert not replay
        q.execute("select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell)
        physical,hard,version=q.fetchone();assert (physical,hard)==(1,0)
        repeated,replay=post(operation,"1",0);assert replay and repeated==result
        count_zero,replay=post("SMOKE.INVENTORY:"+uuid4().hex,"0",int(version));assert not replay
        q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell)
        assert q.fetchone()==(0,0)
        q.execute("select count(*) from RRL_EVENTS");assert q.fetchone()==(2,)
        print("PASS: count 0->1, identical replay without extra movement, count 1->0")
    finally:
        c.rollback()
        q.callproc("RRL_STOCK_POSTING_API.reset_connection")
    q.execute("select STATE,(select count(*) from RRL_REMAINS),(select count(*) from RRL_EVENTS),(select count(*) from RRL_STOCK_OPERATION) from RRL_STOCK_RELEASE where RELEASE_ID=1")
    assert q.fetchone()==("ACTIVE",1,2,2)
    print("PASS: zero quantity, two append-only movements and two committed operations; release stays ACTIVE")
