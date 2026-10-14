import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/tare.py");v=p.read_text(encoding="utf-8")
assert "participant_holders"not in v
v=v.replace("from .tare_damage_custody import damage_custody","from .tare_damage_custody import damage_custody\nfrom .tare_participant_read import participant_holders")
v=v.replace('"select ID,NAME from RRL_WARES order by NAME,ID fetch first 200 rows only"',
""""select w.ID,w.NAME from RRL_WARES w order by case when w.ID in(select WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip union select WARE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=:trip union select WARE_ID from RUSERS where ID=:actor)then 0 else 1 end,w.NAME,w.ID fetch first 200 rows only",{"trip":task_id,"actor":actor}""")
v=v.replace('return {"permissions":permissions,"customers":customers,','return {"participant":participant_holders(self.gateway,task_id,actor),"permissions":permissions,"customers":customers,')
v=v.replace("o.OFFERED_BY,o.OFFERED_AT,a.OPERATION_ID ACCEPT_OPERATION_ID,","o.OFFERED_BY,o.OFFERED_AT,x.DAMAGE_OPERATION_ID,a.OPERATION_ID ACCEPT_OPERATION_ID,")
v=v.replace("left join RRL_TARE_OFFER_CANCEL c on c.OFFER_OPERATION_ID=o.OPERATION_ID","left join RRL_TARE_OFFER_CANCEL c on c.OFFER_OPERATION_ID=o.OPERATION_ID\n              left join RRL_TARE_DAMAGE_OFFER x on x.OFFER_OPERATION_ID=o.OPERATION_ID")
print(json.dumps({str(p):v}))
