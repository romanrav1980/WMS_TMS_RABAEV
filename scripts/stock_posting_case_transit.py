"""Switch CASE picking out of the bin into dedicated transit without allocating it twice."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path+" "+old[:45])
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/160_case_pick_command.sql"
edit(path,"n number:=0;v_cell varchar2(60);","n number:=0;v_cell varchar2(60);target_cell varchar2(60);")
edit(path,"remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;",
 "remaining:=fact-nvl(l.PICKED_QTY,0);v_cell:=l.CELL_CODE;target_cell:='CASE_TRANSIT_'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.WARE_ID);")
edit(path,"x.get_string('article'),x.get_string('cell'),v_cell);",
 "x.get_string('article'),x.get_string('cell'),target_cell);")
edit(path,"sr.UID_PALLET,l.ARTICUL,v_cell,v_cell);","sr.UID_PALLET,l.ARTICUL,v_cell,target_cell);")
edit(path,"v.put('cell',v_cell);v.put('article',l.ARTICUL);","v.put('cell',v_cell);v.put('transit_cell',target_cell);v.put('article',l.ARTICUL);")
edit(path,"article varchar2(160);\n  qty number;","article varchar2(160);target_cell varchar2(60);\n  qty number;")
edit(path,"article:=v.get_string('article');","article:=v.get_string('article');target_cell:=v.get_string('transit_cell');")
# Existing contents are already in transit, not in the next SKU's shelf bin.
edit(path,"   if x.get_string('cell')!=v_cell then","   if x.get_string('cell')!=target_cell then")
edit(path,"RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),v_cell,",
 "RRL_STOCK_TRANSFER_CORE.move(uid,uid,x.get_string('cell'),target_cell,")
edit(path,"base,ver,ware,p_actor,line_no);","base,ver,ware,p_actor,line_no,null,null,null,null,null,'CASE_TRANSIT');")
edit(path,"RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,v_cell,",
 "RRL_STOCK_TRANSFER_CORE.move(uid,target,v_cell,target_cell,")
edit(path,"else null end,new_sid);","else null end,new_sid,null,null,'CASE_TRANSIT');")
edit(path,"set CURRENT_CELL=v_cell,CONTENT_VERSION=CONTENT_VERSION+1,",
 "set CURRENT_CELL=target_cell,CONTENT_VERSION=CONTENT_VERSION+1,")
edit(path,"v.put('cell',v_cell);v.put('lots',facts);","v.put('cell',target_cell);v.put('picked_from_cell',v_cell);v.put('lots',facts);")
path="db/migrations/2026-10-08_stock_posting_core/032_transfer_core.sql"
edit(path,"v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;","v_r RRL_STOCK_RESERVATION%rowtype;v_result_reservation number;v_system number;v_command varchar2(80);v_operation varchar2(100);")
edit(path,"  if p_location_mode='PUTAWAY' then",
 """  select count(*) into v_sum from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if v_sum>0 then
   v_operation:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
   select COMMAND_TYPE into v_command from RRL_STOCK_OPERATION where OPERATION_ID=v_operation;
   if v_command not in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN') then raise_application_error(-20886,'CASE_MEMBER_REQUIRES_CARRIER_COMMAND');end if;
  end if;
  if p_location_mode='CASE_TRANSIT' then
   if p_to!='CASE_TRANSIT_'||RRL_STOCK_PLAN_HELPER.decimal_text(p_warehouse) then raise_application_error(-20886,'CASE_TRANSIT_TARGET_REQUIRED');end if;
   select IS_SYSTEM into v_system from RRL_CELLS where CELL=p_to;
   if v_system is null or v_system!=1 then raise_application_error(-20886,'CASE_TRANSIT_SYSTEM_LOCATION_REQUIRED');end if;
   if p_from=p_to then RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,p_warehouse);
   else RRL_STOCK_LOCATION_CORE.assert_ordinary(p_from,nvl(p_source_warehouse,p_warehouse),'SOURCE');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_to,p_warehouse);
  elsif p_location_mode='PUTAWAY' then""")
print(json.dumps(files,ensure_ascii=True))
