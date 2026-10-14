create or replace package body RRL_RETURN_REUSE_API as
 procedure preview(p_receipt varchar2,p_line number,p_quantity varchar2,p_actor varchar2,p_result out clob)is
  n number;qty number;used number;line RRL_STORE_RECEIPT_LINE%rowtype;proof json_object_t;b json_object_t:=json_object_t();reason varchar2(1000);
 begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1;
  if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_APPROVER_REQUIRED');end if;
  if p_receipt is null or lengthb(p_receipt)>100 or p_line is null or p_line<1 or p_line>200 or trunc(p_line)!=p_line then raise_application_error(-20886,'RETURN_REUSE_SOURCE_REQUIRED');end if;
  qty:=RRL_STOCK_MATH.quantity(p_quantity);if qty<=0 then raise_application_error(-20886,'RETURN_REUSE_POSITIVE_QUANTITY_REQUIRED');end if;
  select *into line from RRL_STORE_RECEIPT_LINE where OPERATION_ID=p_receipt and LINE_NO=p_line;
  select nvl(sum(BASE_QTY),0)into used from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=p_receipt and LINE_NO=p_line and RETURN_BASIS='ACCEPTED';
  b.put('receipt_operation_id',p_receipt);b.put('line_no',p_line);b.put('article',line.ARTICLE);b.put('base_uom',line.BASE_UOM);
  b.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));b.put('available_for_approval',RRL_STOCK_PLAN_HELPER.decimal_text(line.ACCEPTED_BASE_QTY-used));
  begin
   RRL_STOCK_RETURN_REUSE.describe_source(line.LOT_UID,line.ARTICLE,line.BASE_UOM,qty,proof);
   b.put('source_eligible',true);b.put('source_proof',proof);b.put_null('source_reason');
   if qty<=line.ACCEPTED_BASE_QTY-used then b.put('currently_approvable',true);else b.put('currently_approvable',false);end if;
  exception when others then
   if sqlcode=-20886 then
    reason:=substr(sqlerrm,instr(sqlerrm,':')+2);b.put('source_eligible',false);b.put('currently_approvable',false);b.put('source_reason',reason);b.put_null('source_proof');
   else raise;end if;
  end;
  b.put('physical_completeness_verified',false);b.put('marked_unit_selection_verified',false);b.put('read_only',true);b.put('stock_changed',false);
  p_result:=b.to_clob;
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_ORIGINAL_LINE_REQUIRED');
 end;
end;

/
