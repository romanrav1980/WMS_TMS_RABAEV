from pathlib import Path
s=Path("scripts/continue255.py").read_text(encoding="utf-8")
prefix=s.split(' api("POST","/api/inventory/interwarehouse/unload"',1)[0]
tail=s.split(' # Actual membership invalidates old empty-TT approval;',1)[1]
# Prefix owns environment/cursor/scans; replace absent onward variables with current original binding.
prefix=prefix.replace('from app.oracle_gateway import OracleGateway','from app.oracle_gateway import OracleGateway')
extra=""" from app.modules.transport.public import TransportPreflight,update_existing_trip,generate_existing_operations
 from datetime import datetime
 coordination=TransportPreflight(OracleGateway())
 q.execute("select b.ST_ID,b.ST_IDENTIFIER,p.ST_NUMBER,placement.TASK_ID from RRL_INTERWARE_ONWARD_BIND b join RRL_SBORKA_PALLETS p on p.ID=b.ST_ID join RRL_INTERWARE_PLACEMENT placement on placement.RECEIPT_OPERATION_ID=b.RECEIPT_OPERATION_ID where b.RECEIPT_OPERATION_ID=:rec",rec="IW255.RECEIVE:"+tag)
 sid,st,st_number,task=q.fetchone()
 onward={"st_id":sid,"shipment_identifier":st,"st_number":st_number}
 original=datetime.fromisoformat(ctx["time255"]["operations"][0]["start_at"])
 update_existing_trip(OracleGateway(),ctx["target_trip"],{"shipment_date":original.date().isoformat(),"shipment_time":original.strftime("%H:%M")},"admin")
 # Explicit dispatcher reconfirms known planned date/clock after legacy ST assignment clears it.
"""
Path("tmp/resume255_code.py").write_text(prefix+extra+" # Actual membership invalidates old empty-TT approval;"+tail,encoding="utf-8")
exec(compile(prefix+extra+" # Actual membership invalidates old empty-TT approval;"+tail,"resume255","exec"))
