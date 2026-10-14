raise SystemExit("Retired authoring generator: use final221 owners and fresh checkpoint; never overwrite live code")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni063_recovery_lineage");out={}
out["wiki/database/nicora_ni063_recovery_lineage_design_20261011.md"]="""# NI06.3: повторный возврат на одной исходной погрузке
221 extends existing unloading admission from direct HELD replacement to source-unique recovery lineage, max16 links/max200 offer associations. Every edge belongs to same original current load/warehouse/type/physical place/balance; terminal must be HELD and original starting book TRANSFERRED, not merely a pending HELD offer. CANCELLED/missing/cyclic/foreign/overbound chains refuse. All source offer/proof/original book/return/accept/current hold locks already declared; no balance or goods writer added. Fresh source recheck after locks. New recovery uses same existing helper; additionally declares actual original FF/order rows read for FULLPAL proof.
"""
s=(f/"000_before_rrl_stock_unload_cmd.sql").read_text(encoding="utf-8")
anchor=" procedure source_state(p_load";idx=s.index(anchor)
helper=""" function held_recovery(p_load varchar2,p_book varchar2)return number is
  original RRL_TARE_BOOK%rowtype;current_book RRL_TARE_BOOK%rowtype;proof RRL_TARE_LOAD_RECOVERY%rowtype;next_book varchar2(100);seen varchar2(4000):='|';n number;
 begin
  select *into original from RRL_TARE_BOOK where OPERATION_ID=p_book;
  if original.STATUS!='TRANSFERRED'then return 0;end if;current_book:=original;
  for depth in 0..16 loop
   if instr(seen,'|'||current_book.OPERATION_ID||'|')>0 then raise_application_error(-20886,'UNLOAD_TARE_RECOVERY_CYCLE');end if;
   seen:=seen||current_book.OPERATION_ID||'|';
   if current_book.OWNER_WARE_ID!=original.OWNER_WARE_ID or current_book.PALLET_TYPE_ID!=original.PALLET_TYPE_ID or current_book.PLACE_KIND!=original.PLACE_KIND or current_book.PLACE_ID!=original.PLACE_ID or current_book.BALANCE_KEY!=original.BALANCE_KEY or current_book.QUANTITY!=1 then raise_application_error(-20886,'UNLOAD_TARE_RECOVERY_LINEAGE_CONFLICT');end if;
   if current_book.STATUS='HELD'then return 1;end if;
   if current_book.STATUS!='TRANSFERRED'then return 0;end if;
   if depth=16 then raise_application_error(-20881,'UNLOAD_TARE_RECOVERY_DEPTH_16');end if;
   select *into proof from RRL_TARE_LOAD_RECOVERY where ORIGINAL_BOOK_OPERATION_ID=current_book.OPERATION_ID;
   if proof.LOAD_OPERATION_ID!=p_load or proof.WARE_ID!=original.OWNER_WARE_ID or proof.PALLET_TYPE_ID!=original.PALLET_TYPE_ID
    or(original.PLACE_KIND='CASE'and(proof.CASE_PICK_TASK_ID is null or RRL_STOCK_PLAN_HELPER.decimal_text(proof.CASE_PICK_TASK_ID)!=original.PLACE_ID or proof.ROOT_UID is not null))
    or(original.PLACE_KIND='HU'and(proof.ROOT_UID is null or proof.ROOT_UID!=original.PLACE_ID or proof.CASE_PICK_TASK_ID is not null))then raise_application_error(-20886,'UNLOAD_TARE_RECOVERY_ORIGINAL_LOAD_REQUIRED');end if;
   select count(*)into n from RRL_TARE_ACCEPT a join RRL_TARE_OFFER_BOOK ob on ob.OFFER_OPERATION_ID=a.OFFER_OPERATION_ID where a.OPERATION_ID=current_book.CLOSED_OPERATION_ID and ob.BOOK_OPERATION_ID=current_book.OPERATION_ID and ob.LOAD_OPERATION_ID=p_load and a.ACCEPTED_QTY=1 and a.SHORT_QTY=0;
   if n!=1 then raise_application_error(-20886,'UNLOAD_TARE_RECOVERY_ORIGINAL_ACCEPT_REQUIRED');end if;
   next_book:=proof.OPERATION_ID;select *into current_book from RRL_TARE_BOOK where OPERATION_ID=next_book;
  end loop;
  return 0;
 exception when no_data_found then return 0;end;
"""
s=s[:idx]+helper+s[idx:]
start=s.index("  select count(*)into n from RRL_TARE_OFFER_BOOK old_offer");end=s.index("  if kind_name='HU_SHIP'then",start)
s=s[:start]+"""  n:=0;
  for old_offer in(select BOOK_OPERATION_ID from RRL_TARE_OFFER_BOOK ob where LOAD_OPERATION_ID=p_load and not exists(select 1 from RRL_TARE_OFFER_CANCEL c where c.OFFER_OPERATION_ID=ob.OFFER_OPERATION_ID)order by OFFER_OPERATION_ID,BOOK_OPERATION_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'UNLOAD_TARE_ASSOCIATION_BOUND_200');end if;
   if held_recovery(p_load,old_offer.BOOK_OPERATION_ID)!=1 then raise_application_error(-20886,'UNLOAD_TARE_HANDOVER_DECISION_REQUIRED');end if;
  end loop;
"""+s[end:];out[str(f/"001_unload.sql")]=s
s=(f/"000_before_rrl_tare_load_recovery_api.sql").read_text(encoding="utf-8")
s=s.replace("wave_id number;node","wave_id number;ff_id number;order_id number;node",1)
s=s.replace("select count(*),max(PICKED_WAREHOUSE_TASK_ID)into n,task_id","select count(*),max(PICKED_WAREHOUSE_TASK_ID),max(FULFILLMENT_ID),max(CUSTOMER_ORDER_ID)into n,task_id,ff_id,order_id",1)
s=s.replace("j.put('fullpal_task_id',task_id);","j.put('fullpal_fulfillment_id',ff_id);j.put('fullpal_order_id',order_id);j.put('fullpal_task_id',task_id);",1)
anchor="    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK'";idx=s.index(anchor)
s=s[:idx]+"""    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_fulfillment_id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_order_id')));
"""+s[idx:];out[str(f/"002_recovery.sql")]=s
out[str(f/"003_recompile.sql")]="alter package RRL_STOCK_TARE_BOOK_CMD compile body;\nalter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"apply.sql")]="@@001_unload.sql\n@@002_recovery.sql\n@@003_recompile.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT where OPERATION_ID like 'FULL221.%';if n>0 then raise_application_error(-20863,'REPEATED_TARE_UNLOAD_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_unload_cmd.sql
@@000_before_rrl_tare_load_recovery_api.sql
@@003_recompile.sql
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
print(json.dumps(out,ensure_ascii=True))
