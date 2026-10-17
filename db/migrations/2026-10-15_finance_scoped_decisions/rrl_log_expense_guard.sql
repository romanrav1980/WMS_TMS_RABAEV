create or replace trigger RRL_LOG_EXPENSE_GUARD before insert or update or delete on RRL_LOGISTICS_EXPENSE for each row

declare n number;v_total number;v_previous number;

begin

 if not inserting then raise_application_error(-20863,'LOGISTICS_EXPENSE_IMMUTABLE');end if;

 RRL_ACCESS_API.assert_allowed(:new.ACTOR,'edit_bill_tt','WAREHOUSE',to_char(:new.WARE_ID));

 if :new.COST_CORRECTION_OF_OP is not null then
  if :new.CORRECTION_OF_OP is not null then raise_application_error(-20886,'ONE_FINANCIAL_CORRECTION_SOURCE_REQUIRED');end if;
  select count(*)into n from RRL_LOGISTICS_EXP_ARTICLE a where a.CODE=:new.ARTICLE_CODE and a.VERSION_NO=:new.ARTICLE_VERSION
   and a.NAME=:new.ARTICLE_NAME and a.ACTIVE_FLAG=1 and a.INCLUDED_IN_RATE=0 and a.OBJECT_SCOPE in(:new.OBJECT_KIND,'BOTH');
  if n!=1 then raise_application_error(-20886,'LOGISTICS_EXTRA_ACTIVE_ARTICLE_REQUIRED');end if;
  RRL_NORM_COST_CORRECTION.validate_report(:new.COST_CORRECTION_OF_OP,:new.WARE_ID,:new.OBJECT_KIND,:new.OBJECT_ID,:new.CURRENCY,:new.AMOUNT*:new.ADJUSTMENT_SIGN,:new.EXPECTED_CONFIRMED_TOTAL);
 elsif :new.CORRECTION_OF_OP is null then

  if :new.ADJUSTMENT_SIGN!=1 or :new.EXPECTED_CONFIRMED_TOTAL is not null then raise_application_error(-20886,'LOGISTICS_ORDINARY_EXPENSE_POSITIVE_REQUIRED');end if;

  select count(*)into n from RRL_LOGISTICS_EXP_ARTICLE a where a.CODE=:new.ARTICLE_CODE and a.VERSION_NO=:new.ARTICLE_VERSION and a.NAME=:new.ARTICLE_NAME and a.ACTIVE_FLAG=1 and a.INCLUDED_IN_RATE=0 and a.OBJECT_SCOPE in(:new.OBJECT_KIND,'BOTH');

  if n!=1 then raise_application_error(-20886,'LOGISTICS_EXTRA_ACTIVE_ARTICLE_REQUIRED');end if;

 else

  select AMOUNT into v_total from RRL_LOGISTICS_EXPENSE e where e.OPERATION_ID=:new.CORRECTION_OF_OP and e.CORRECTION_OF_OP is null and e.COST_CORRECTION_OF_OP is null

  and e.ARTICLE_CODE=:new.ARTICLE_CODE and e.ARTICLE_VERSION=:new.ARTICLE_VERSION and e.ARTICLE_NAME=:new.ARTICLE_NAME

  and e.WARE_ID=:new.WARE_ID and e.OBJECT_KIND=:new.OBJECT_KIND and e.OBJECT_ID=:new.OBJECT_ID and e.CURRENCY=:new.CURRENCY for update;

  select count(*)into n from RRL_LOGISTICS_EXP_DECISION where EXPENSE_OPERATION_ID=:new.CORRECTION_OF_OP and PHASE='FINANCE' and OUTCOME='APPROVE';if n!=1 then raise_application_error(-20886,'LOGISTICS_CORRECTION_ORIGINAL_APPROVAL_REQUIRED');end if;

  select nvl(sum(c.AMOUNT*c.ADJUSTMENT_SIGN),0)into v_previous from RRL_LOGISTICS_EXPENSE c join RRL_LOGISTICS_EXP_DECISION f on f.EXPENSE_OPERATION_ID=c.OPERATION_ID and f.PHASE='FINANCE' and f.OUTCOME='APPROVE' where c.CORRECTION_OF_OP=:new.CORRECTION_OF_OP;

  v_total:=v_total+v_previous;

  if :new.EXPECTED_CONFIRMED_TOTAL is null or v_total!=:new.EXPECTED_CONFIRMED_TOTAL or v_total+:new.AMOUNT*:new.ADJUSTMENT_SIGN<0 or v_total+:new.AMOUNT*:new.ADJUSTMENT_SIGN>=1000000000000000000 then raise_application_error(-20886,'LOGISTICS_CORRECTION_CURRENT_TOTAL_REQUIRED');end if;

 end if;

 if :new.OBJECT_KIND='TRIP' then select count(*)into n from RRL_TRANSPORT_TASK where ID=:new.OBJECT_ID;

 else select count(*)into n from RRL_TR_VEHICLE where ID=:new.OBJECT_ID;end if;

 if n!=1 then raise_application_error(-20886,'LOGISTICS_EXPENSE_EXISTING_OBJECT_REQUIRED');end if;

exception when no_data_found then raise_application_error(-20886,'LOGISTICS_CORRECTION_ORIGINAL_IDENTITY_REQUIRED');

end;
/
