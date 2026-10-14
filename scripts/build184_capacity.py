from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-11_ni042_box_capacity");s=(f/"000_before_capacity.sql").read_text(encoding="utf-8")
needle=" begin\n  select count(*),max(coalesce"
assert s.count(needle)==1
s=s.replace(needle," begin\n  if RRL_WEIGHT_BOX_CAPACITY.enabled(p_article)=1 then return RRL_WEIGHT_BOX_CAPACITY.kg_volume_upper_bound(p_cell,p_article);end if;\n  select count(*),max(coalesce")
s=s.replace("for r in(select p.ARTICUL,s.REMAIN from RRL_REMAINS","for r in(select p.ARTICUL,s.REMAIN,s.UID_POLETA from RRL_REMAINS")
s=s.replace("   v_occupied:=v_occupied+r.REMAIN*volume_for(r.ARTICUL);","   if RRL_WEIGHT_BOX_CAPACITY.enabled(r.ARTICUL)=1 then v_occupied:=v_occupied+RRL_WEIGHT_BOX_CAPACITY.physical_volume(r.UID_POLETA,p_cell,r.REMAIN);\n   else v_occupied:=v_occupied+r.REMAIN*volume_for(r.ARTICUL);end if;")
s=s.replace("for r in(select rt.ARTICUL,rt.QTY,","for r in(select rt.ARTICUL,rt.QTY,rt.SOURCE_RESERVATION_ID,")
s=s.replace("   v_arriving:=v_arriving+greatest(0,r.QTY-r.ARRIVED)*volume_for(r.ARTICUL);","   if RRL_WEIGHT_BOX_CAPACITY.enabled(r.ARTICUL)=1 then v_arriving:=v_arriving+RRL_WEIGHT_BOX_CAPACITY.reservation_volume(r.SOURCE_RESERVATION_ID,greatest(0,r.QTY-r.ARRIVED));\n   else v_arriving:=v_arriving+greatest(0,r.QTY-r.ARRIVED)*volume_for(r.ARTICUL);end if;")
s=s.replace("for r in(select p.ARTICUL,\n","for r in(select p.ARTICUL,p.UID_PALLET,t.FROM_CELL,\n")
s=s.replace("   v_arriving:=v_arriving+r.BASE_QTY*volume_for(r.ARTICUL);","   if RRL_WEIGHT_BOX_CAPACITY.enabled(r.ARTICUL)=1 then v_arriving:=v_arriving+RRL_WEIGHT_BOX_CAPACITY.physical_volume(r.UID_PALLET,r.FROM_CELL,r.BASE_QTY,0);\n   else v_arriving:=v_arriving+r.BASE_QTY*volume_for(r.ARTICUL);end if;")
out={str(f/"002_capacity_contract.sql"):s,str(f/"002_capacity_body.sql"):s[s.index("create or replace package body"):],
str(f/"apply.sql"):"-- MIGRATION_ID:2026-10-11-184-weight-box-volume-budget\n@@001_weighted.sql\n@@002_capacity_body.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"rollback.sql"):"@@000_before_capacity.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n",
str(f/"verify.sql"):"select object_name,object_type,status from user_objects where object_name in('RRL_STOCK_REPL_CAPACITY','RRL_WEIGHT_BOX_CAPACITY');\nselect name,line,text from user_errors where name in('RRL_STOCK_REPL_CAPACITY','RRL_WEIGHT_BOX_CAPACITY');\n"}
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-184-weight-box-volume-budget","sha256":{p:hashlib.sha256(v.encode()).hexdigest()for p,v in out.items()},"before_sha256":hashlib.sha256((f/"000_before_capacity.sql").read_bytes()).hexdigest(),"recovery":"fresh same-signature capacity package rollback; additive read-only helper; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
