from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace("r.DISCREPANCY_REFERENCE,\n            o.RESOLVED_PLAN_JSON","r.DISCREPANCY_REFERENCE,\n            o.RESOLVED_PLAN_JSON",1)
needle='        return dict(receipt_operation_id=receipt_id'
extra='''        recovered_keys=set()
        if recovery and recovery[4]:
            cur.execute("""select r.PHYSICAL_UNIT_KEY from RRL_INTERWARE_RECOVERY_UNIT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.RECOVERY_OPERATION_ID
                where r.RECOVERY_OPERATION_ID=:recovery_id and r.LOSS_OPERATION_ID=:loss_id and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'""",
                recovery_id=recovery[4],loss_id=claim[4])
            recovered_keys={r[0]for r in cur.fetchall()}
            unresolved=[k for k in unresolved if k not in recovered_keys]
        for unit in units:unit["recovered"]=unit["key"]in recovered_keys
        cur.execute("""select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE
            where ARTICUL=(select ARTICLE from RRL_INTERWARE_RECEIPT where OPERATION_ID=:receipt_id)
            order by SYSTEM_CODE,PROFILE_CODE fetch first 51 rows only""",receipt_id=receipt_id)
        profiles=[dict(system_code=r[0],profile_code=r[1],profile_version=r[2],scan_mode=r[3])for r in cur.fetchall()]
        if len(profiles)>50:raise StoreReturnReceiveError("INTERWARE_RECOVERY_PROFILE_BOUND","Слишком много профилей маркировки",409)
        recovered_qty=Decimal(str(recovery[6]))if recovery and recovery[6]is not None else Decimal(0)
'''
assert needle in s;s=s.replace(needle,extra+needle,1)
s=s.replace('base_uom=uom,discrepancy_reason=','article=domain.get("article"),profiles=profiles,net_unrecovered_short_quantity=str(shortage-recovered_qty),\n                    currently_missing_units=[u for u in units if not u["recovered"]],\n                    base_uom=uom,discrepancy_reason=',1)
s=s.replace('status="CONFIRMED_CARRIER_SHORTAGE"if claim','status="RECOVERED_PENDING_PLACEMENT"if recovery and recovery[4]else"CONFIRMED_CARRIER_SHORTAGE"if claim',1)
print(json.dumps({p.as_posix():s}))
