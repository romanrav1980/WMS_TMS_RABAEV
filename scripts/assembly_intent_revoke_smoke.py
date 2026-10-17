"""Retire only owned TEST actor inside caller rollback; no goods commands."""
import json
from assembly_intent_native_smoke import OUT,ACTOR,RID,OracleGateway,oracle_connection,snapshot,deny,wire
def main():
    report=json.loads(OUT.read_text());g=OracleGateway();before=snapshot(g)
    with oracle_connection()as con:
        q=con.cursor()
        try:
            q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
            q.execute("update RUSERS set DELETED=1 where ID=:a",a=ACTOR);assert q.rowcount==1
            read=deny(q,"RRL_ASM_INTENT_API.describe",[RID,ACTOR],"CASE_ACTIVE_USER_REQUIRED")
            replay=deny(q,"RRL_ASM_INTENT_API.abandon",[wire(report["body"]),ACTOR],"CASE_ACTIVE_USER_REQUIRED")
        finally:con.rollback();q.callproc("RRL_STOCK_CONFIG_API.end_change")
    assert snapshot(g)==before
    assert g.fetch_all("select nvl(DELETED,0) N from RUSERS where ID=:a",{"a":ACTOR})==[{"n":0}]
    name="revoked_current_user_denies_read_and_exact_mutation_before_receipt_lookup_metadata_caller_rollback"
    if name not in report["checks"]:report["checks"].append(name)
    report["revocation_caller_rollback"]=dict(read=read,replay=replay,actor_restored=True,source_unchanged=True)
    OUT.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(dict(status="PASS",checks=len(report["checks"]),actor_restored=True,stock_posted=False)))
if __name__=="__main__":main()
