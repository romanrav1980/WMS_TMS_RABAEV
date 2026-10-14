from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
a="""select r.RESULT_JSON from RRL_LOGISTICS_COST_RUN r
         join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID
         where r.TT_ID=:trip and r.WARE_ID=:ware order by r.OPERATION_ID fetch first 2 rows only"""
b="""select r.RESULT_JSON from RRL_TT_VEHICLE_SOURCE s
         join RRL_TRANSPORT_COST_CLAIM c on c.DEPARTURE_OPERATION_ID=s.DEPARTURE_OPERATION_ID
         join RRL_LOGISTICS_COST_RUN r on r.OPERATION_ID=c.OPERATION_ID and r.TT_ID=s.TT_ID
         where s.TT_ID=:trip and r.WARE_ID=:ware fetch first 2 rows only"""
assert a in v;v=v.replace(a,b);p.write_text(v,encoding="utf-8")
print("590 PK source -> claim -> journal read replaces trip scan/sort.")
