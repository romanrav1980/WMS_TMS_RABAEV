create or replace trigger RRL_LOG_RATE_HISTORY_GUARD before insert or update or delete on RRL_LOGISTICS_RATE_HISTORY for each row
declare n number;j json_object_t;base_value number;common_amount number;boxes number;v_share number;total_rate number;month_text varchar2(7);
begin
 if not inserting then raise_application_error(-20863,'LOGISTICS_RATE_HISTORY_IMMUTABLE');end if;
 select count(*)into n from RRL_LOGISTICS_RATE_HEAD h join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where h.RATE_KEY=:new.RATE_KEY and h.VERSION_NO=:new.VERSION_NO and(u.WARE_ID=h.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'create_tt_price')=1;
 if n!=1 then raise_application_error(-20882,'LOGISTICS_RATE_CURRENT_BOUND_FINANCE_REQUIRED');end if;
 if :new.COMPONENTS_JSON is not null then
  j:=json_object_t.parse(:new.COMPONENTS_JSON);base_value:=j.get_number('picking_rate');common_amount:=j.get_number('common_work_amount');boxes:=j.get_number('basis_boxes');v_share:=j.get_number('common_work_rate');total_rate:=j.get_number('combined_rate');month_text:=j.get_string('month');
  if j.get_size!=7 or base_value is null or common_amount is null or boxes is null or v_share is null or total_rate is null or month_text is null or j.get_string('basis_provenance')is null or j.get_string('basis_provenance')!='DECLARED_MONTHLY_BOX_BASE'
   or base_value<0 or common_amount<0 or common_amount!=round(common_amount,2)or boxes<=0 or boxes!=trunc(boxes)or boxes>999999999999 or v_share!=round(common_amount/boxes,9)or total_rate!=base_value+v_share or total_rate!=:new.RATE_VALUE or total_rate>=1e18
   or month_text!=to_char(:new.EFFECTIVE_FROM,'YYYY-MM')or :new.EFFECTIVE_FROM!=trunc(:new.EFFECTIVE_FROM,'MM')then raise_application_error(-20886,'LOGISTICS_MONTHLY_RATE_EXACT_COMPONENTS_REQUIRED');end if;
 end if;

end;
/
