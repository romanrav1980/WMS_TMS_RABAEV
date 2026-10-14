create or replace package RRL_STOCK_TARE_RESOLVE authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_TARE_RESOLVE as
 procedure read_balance(p_key raw,p_qty out number,p_version out number) is
 begin select QUANTITY,BALANCE_VERSION into p_qty,p_version from RRL_TARE_BALANCE where BALANCE_KEY=p_key;
 exception when no_data_found then p_qty:=0;p_version:=0;end;
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
 v_owner number;v_type number;v_holder varchar2(12);v_id varchar2(255);v_qty number;v_from raw(32);v_to raw(32);v_from_qty number;v_from_version number;v_to_qty number;v_to_version number;
 v_delivery varchar2(100);v_damage varchar2(100);v_outstanding number;v_used number;v_reason varchar2(32767):=m.get_string('reason');v_ref varchar2(32767):=m.get_string('decision_reference');
 v_tt number;v_vehicle number;v_plate varchar2(50);n number;trip RRL_TRANSPORT_TASK%rowtype;damage RRL_TARE_RESOLUTION%rowtype;
 begin
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'TARE_ACTIVE_ACTOR_REQUIRED');end if;
 if trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_ref) is null or lengthb(v_ref)>255 then raise_application_error(-20886,'TARE_RESOLUTION_REASON_DECISION_REQUIRED');end if;
 if not regexp_like(m.get_string('quantity'),'^[0-9]{1,18}$') then raise_application_error(-20886,'TARE_INTEGER_QUANTITY_REQUIRED');end if;
 v_qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
 if kind='TARE_WRITE_OFF' then
  if RRL_HAS_WRIGHT(p_actor,'tare_writeoff')!=1 then raise_application_error(-20882,'TARE_TRANSPORT_WRITEOFF_DECISION_REQUIRED');end if;
  v_damage:=s.get_string('damage_operation_id');select * into damage from RRL_TARE_RESOLUTION where OPERATION_ID=v_damage and RESOLUTION_KIND='DAMAGE';
  if damage.ACTOR=p_actor then raise_application_error(-20882,'TARE_INDEPENDENT_DAMAGE_DECISION_REQUIRED');end if;
  v_owner:=damage.OWNER_WARE_ID;v_type:=damage.PALLET_TYPE_ID;v_holder:=damage.CUSTODIAN_KIND;v_id:=damage.CUSTODIAN_ID;v_delivery:=damage.DELIVERY_ACCEPT_OPERATION_ID;
  select nvl(sum(QUANTITY),0) into v_used from RRL_TARE_RESOLUTION where DAMAGE_OPERATION_ID=v_damage and RESOLUTION_KIND='WRITE_OFF';
  if v_qty>damage.QUANTITY-v_used then raise_application_error(-20886,'TARE_DAMAGE_DECISION_QUANTITY_EXCEEDED');end if;
 else
  v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_holder:=m.get_string('custodian_kind');v_id:=m.get_string('custodian_id');
  if v_owner is null or v_type is null or v_holder is null or v_holder not in('WAREHOUSE','VEHICLE','STORE') or v_id is null then raise_application_error(-20886,'TARE_RESOLUTION_HOLDER_REQUIRED');end if;
  if v_holder='WAREHOUSE' and v_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_owner)then raise_application_error(-20886,'TARE_CURRENT_HOLDER_ID_REQUIRED');end if;
  if v_holder='VEHICLE' then
   v_tt:=s.get_number('task_id');select * into trip from RRL_TRANSPORT_TASK where ID=v_tt and nvl(DELETED,0)=0;
   select ID,NUM into v_vehicle,v_plate from RRL_TR_VEHICLE where NUM=trip.TRANSPORT and nvl(DELETED,0)=0 and nvl(BLOCKED,0)=0;
   if v_id!=RRL_STOCK_PLAN_HELPER.decimal_text(v_vehicle) or m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=v_plate then raise_application_error(-20886,'TARE_DAMAGE_CURRENT_VEHICLE_SCAN_REQUIRED');end if;
  end if;
  RRL_TARE_PARTICIPANT.holder_actor(p_actor,v_holder,v_id,v_owner,trip,'tare_damage');
  if v_holder='STORE' then v_delivery:=s.get_string('delivery_accept_operation_id');end if;
 end if;
 select count(*) into n from RRL_WARES where ID=v_owner;if n!=1 then raise_application_error(-20886,'TARE_OWNER_WAREHOUSE_REQUIRED');end if;
 select count(*) into n from RRL_PALLET_TYPE where PALLET_TYPE_ID=v_type and ACTIVE=1;if n!=1 then raise_application_error(-20886,'TARE_ACTIVE_EXISTING_PALLET_TYPE_REQUIRED');end if;
 if v_holder='STORE' then
  select OUTSTANDING_QTY into v_outstanding from RRL_TARE_STORE_DEBT where CLAIM_KEY=case when kind='TARE_DAMAGE' then v_delivery else v_damage end
   and OWNER_WARE_ID=v_owner and PALLET_TYPE_ID=v_type and STORE_ADDR=v_id and CONDITION_CODE=case when kind='TARE_DAMAGE' then 'GOOD' else 'DAMAGED' end;
  if v_qty>v_outstanding then raise_application_error(-20886,'TARE_ORIGINAL_STORE_DEBT_QUANTITY_EXCEEDED');end if;
 end if;
 v_from:=RRL_TARE_BALANCE_KEY(v_owner,v_type,case when kind='TARE_DAMAGE' then 'GOOD' else 'DAMAGED' end,v_holder,v_id);read_balance(v_from,v_from_qty,v_from_version);
 if v_qty>v_from_qty then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
 if kind='TARE_DAMAGE' then v_to:=RRL_TARE_BALANCE_KEY(v_owner,v_type,'DAMAGED',v_holder,v_id);read_balance(v_to,v_to_qty,v_to_version);end if;
 p_domain:=json_object_t();p_domain.put('owner_ware_id',v_owner);p_domain.put('pallet_type_id',v_type);p_domain.put('custodian_kind',v_holder);p_domain.put('custodian_id',v_id);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
 p_domain.put('from_key',rawtohex(v_from));p_domain.put('from_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_from_qty));p_domain.put('from_version',v_from_version);
 p_domain.put('to_key',rawtohex(v_to));p_domain.put('to_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_to_qty));p_domain.put('to_version',v_to_version);
 p_domain.put('delivery_accept_operation_id',v_delivery);p_domain.put('damage_operation_id',v_damage);p_domain.put('store_outstanding',v_outstanding);p_domain.put('previously_written_off',v_used);
 p_domain.put('task_id',v_tt);p_domain.put('vehicle_id',v_vehicle);p_domain.put('vehicle_number',v_plate);p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);
 exception when no_data_found then raise_application_error(-20886,'TARE_ORIGINAL_DAMAGE_DELIVERY_OR_HOLDER_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_command(p_request,d.get_string('actor'),v);RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('from_key'));if v.get_string('to_key') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('to_key'));end if;
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_RESOLUTION',p_operation);
 if v.get_string('damage_operation_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_RESOLUTION',v.get_string('damage_operation_id'));end if;
 if v.get_string('delivery_accept_operation_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',v.get_string('delivery_accept_operation_id'));end if;
 if v.get_number('task_id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_owner number;v_type number;v_holder varchar2(12);v_id varchar2(255);v_qty number;v_from raw(32);v_to raw(32);v_after number;v_delivery varchar2(100);v_damage varchar2(100);v_reason varchar2(2000);v_ref varchar2(255);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');v_from:=hextoraw(v.get_string('from_key'));v_to:=hextoraw(v.get_string('to_key'));
 for row_record in(select BALANCE_KEY from RRL_TARE_BALANCE where BALANCE_KEY in(v_from,v_to)order by BALANCE_KEY for update)loop null;end loop;
 if v.get_number('task_id') is not null then
  n:=v.get_number('task_id');select ID into n from RRL_TRANSPORT_TASK where ID=n for update;n:=v.get_number('vehicle_id');select ID into n from RRL_TR_VEHICLE where ID=n for update;
 end if;
 describe_command(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare resolution');end if;
 v_owner:=v.get_number('owner_ware_id');v_type:=v.get_number('pallet_type_id');v_holder:=v.get_string('custodian_kind');v_id:=v.get_string('custodian_id');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 v_delivery:=v.get_string('delivery_accept_operation_id');v_damage:=v.get_string('damage_operation_id');v_reason:=v.get_string('reason');v_ref:=v.get_string('decision_reference');
 update RRL_TARE_BALANCE set QUANTITY=QUANTITY-v_qty,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp where BALANCE_KEY=v_from and QUANTITY>=v_qty;
 if sql%rowcount!=1 then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;
 if kind='TARE_DAMAGE' then
  v_after:=to_number(v.get_string('to_quantity'))+v_qty;
  merge into RRL_TARE_BALANCE b using(select v_to BALANCE_KEY from dual)s on(b.BALANCE_KEY=s.BALANCE_KEY)
  when matched then update set QUANTITY=v_after,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp
  when not matched then insert(BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,CUSTODIAN_KIND,CUSTODIAN_ID,QUANTITY,BALANCE_VERSION,LAST_OPERATION_ID)values(v_to,v_owner,v_type,'DAMAGED',v_holder,v_id,v_after,1,op);
 end if;
 insert into RRL_TARE_RESOLUTION(OPERATION_ID,RESOLUTION_KIND,OWNER_WARE_ID,PALLET_TYPE_ID,CUSTODIAN_KIND,CUSTODIAN_ID,FROM_BALANCE_KEY,TO_BALANCE_KEY,QUANTITY,DELIVERY_ACCEPT_OPERATION_ID,DAMAGE_OPERATION_ID,REASON_TEXT,DECISION_REFERENCE,ACTOR)
 values(op,case when kind='TARE_DAMAGE' then 'DAMAGE' else 'WRITE_OFF' end,v_owner,v_type,v_holder,v_id,v_from,v_to,v_qty,v_delivery,v_damage,v_reason,v_ref,p_actor);
 j.put('operation_id',op);j.put('quantity',v.get_string('quantity'));j.put('status','POSTED');j.put('resolution_kind',case when kind='TARE_DAMAGE' then 'DAMAGE' else 'WRITE_OFF' end);j.put('total_tare_changed',kind='TARE_WRITE_OFF');j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
