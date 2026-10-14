from pathlib import Path
import json
out={}
f=Path("db/migrations/2026-10-10_ni062_reuse_boxes")
p=f/"002_reuse.sql";s=p.read_text(encoding="utf-8-sig").replace("p_batch_source varchar2,p_proof","p_batch_source varchar2,p_ware number,p_proof")
s=s.replace("v_quantity number;v_good boolean;","v_quantity number;v_good boolean;v_min_days number;",1)
s=s.replace(" v_count:=RRL_STOCK_MATH.quantity"," select nvl(max(MIN_SHELF_DAYS),0)into v_min_days from RRL_RECEIPT_SKU_RULE where ARTICUL=p_approval.ARTICLE and WARE_ID=p_ware;\n if to_date(p_metadata.get_string('expiry_date'),'FXYYYY-MM-DD')<trunc(sysdate)+v_min_days then raise_application_error(-20886,'RETURN_REUSE_SHELF_LIFE_REQUIRED');end if;\n v_count:=RRL_STOCK_MATH.quantity",1)
s=s.replace("v_cell_max number;","v_cell_max number;v_mix number;v_planned_count number:=0;v_key varchar2(1000);",1)
s=s.replace(" RRL_STOCK_REPL_ADMISSION.assert_target",""" select nvl(max(ALLOW_PICK_BATCH_MIX),0) into v_mix from RRL_RECEIPT_SKU_RULE where WARE_ID=p_receipt.WARE_ID and ARTICUL=p_receipt.ARTICLE;
 v_key:=RRL_STOCK_REPL_ADMISSION.lot_key(p_receipt.UID_PALLET);
 for planned in(select wt.UID_PALLET,pp.ARTICUL from RRL_WAREHOUSE_TASK wt join RRL_PALLETS pp on pp.UID_PALLET=wt.UID_PALLET
  where wt.TO_CELL=p_target and wt.STATUS not in('DONE','CANCELLED') and wt.UID_PALLET!=p_receipt.UID_PALLET)loop
  v_planned_count:=v_planned_count+1;if v_planned_count>200 then raise_application_error(-20881,'RETURN_REUSE_PLANNED_TARGET_BOUND_200');end if;
  if planned.ARTICUL!=p_receipt.ARTICLE or(v_mix!=1 and RRL_STOCK_REPL_ADMISSION.lot_key(planned.UID_PALLET)!=v_key)then raise_application_error(-20886,'RETURN_REUSE_PLANNED_TARGET_SKU_BATCH_CONFLICT');end if;
 end loop;
 RRL_STOCK_REPL_ADMISSION.assert_target""",1);out[str(p)]=s
p=f/"003_receiving.sql";out[str(p)]=p.read_text(encoding="utf-8-sig").replace("m,v_scan_uom,v_batch_source,v_proof","m,v_scan_uom,v_batch_source,sap.WARE_ID,v_proof",1)
p=f/"005_guards.sql";out[str(p)]=p.read_text(encoding="utf-8-sig").replace("if :new.OPERATION_ID!=op","if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or :new.OPERATION_ID!=op",1)
p=Path("db/migrations/2026-10-08_stock_posting_core/422_before107_repl_policy.sql");s=p.read_text(encoding="utf-8-sig").replace(" function reason("," function lot_key(p_uid varchar2) return varchar2;\n function reason(",1);out[str(f/"006_repl_policy.sql")]=s
p=f/"apply.sql";s=p.read_text(encoding="utf-8-sig").replace("@@002_reuse.sql","@@006_repl_policy.sql\n@@002_reuse.sql",1);out[str(p)]=s
out[str(f/"refine.sql")]="@@006_repl_policy.sql\n@@002_reuse.sql\n@@003_receiving.sql\n@@005_guards.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n"
print(json.dumps(out,ensure_ascii=True))
