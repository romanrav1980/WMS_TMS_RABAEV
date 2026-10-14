create or replace package body RRL_IW_AGG_SCAN as 
 procedure expand(p_metadata clob,p_scans out clob)is 
 m json_object_t:=json_object_t.parse(p_metadata);direct_scans json_array_t:=json_array_t();aggregates json_array_t:=json_array_t(); 
 result_scans json_array_t:=json_array_t();item json_object_t;expanded json_array_t;members clob;expanded_wire clob; 
 v_system_code varchar2(40);v_profile_code varchar2(80);v_digest varchar2(64);v_level_code varchar2(10);v_origin_uid varchar2(200); 
 n number;expected_count number;current_count number;aggregate_version varchar2(40);current_version varchar2(40);scan_mode varchar2(40); 
 begin 
 if m.has('unit_scans')then direct_scans:=m.get_array('unit_scans');end if; 
 if m.has('aggregation_scans')then aggregates:=m.get_array('aggregation_scans');end if; 
 if direct_scans is null or aggregates is null or direct_scans.get_size>20000 or aggregates.get_size>1000 then raise_application_error(-20881,'INTERWARE_SCAN_BOUND');end if; 
 for i in 0..direct_scans.get_size-1 loop result_scans.append(direct_scans.get(i));end loop; 
 for i in 0..aggregates.get_size-1 loop 
 item:=treat(aggregates.get(i)as json_object_t); 
 if item is null or item.get_size!=4 then raise_application_error(-20871,'INTERWARE_AGGREGATION_SCAN_FIELDS');end if; 
 v_system_code:=item.get_string('system_code');v_profile_code:=item.get_string('profile_code');v_digest:=item.get_string('code_hash');v_level_code:=item.get_string('level'); 
 if v_system_code is null or v_profile_code is null or v_digest is null or not regexp_like(v_digest,'^[a-f0-9]{64}$')or v_level_code not in('BOX','PALLET')or v_level_code is null then raise_application_error(-20871,'INTERWARE_AGGREGATION_SCAN_INVALID');end if; 
 select count(*)into n from RRL_WMS_RECEIPT_AGG where RRL_WMS_RECEIPT_AGG.SYSTEM_CODE=v_system_code and RRL_WMS_RECEIPT_AGG.PROFILE_CODE=v_profile_code and CODE_HASH=v_digest and AGG_LEVEL=v_level_code; 
 if n!=1 then raise_application_error(-20886,'INTERWARE_REGISTERED_AGGREGATION_REQUIRED');end if; 
 select UID_PALLET into v_origin_uid from RRL_WMS_RECEIPT_AGG where RRL_WMS_RECEIPT_AGG.SYSTEM_CODE=v_system_code and RRL_WMS_RECEIPT_AGG.PROFILE_CODE=v_profile_code and CODE_HASH=v_digest and AGG_LEVEL=v_level_code; 
 select count(*)into n from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID 
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=used.STOCK_OPERATION_ID and op.STATE='APPLIED' 
 where used.UID_PALLET=v_origin_uid and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code; 
 if n>1 then raise_application_error(-20886,'INTERWARE_AGGREGATION_ORIGIN_AMBIGUOUS');end if;
 if n=1 then
 select a.UNITS_JSON,a.PROFILE_VERSION into members,aggregate_version from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where used.UID_PALLET=v_origin_uid and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 else
 select count(*)into n from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=a.ORDER_ID and rec.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=rec.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where rec.UID_PALLET=v_origin_uid and rec.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 if n!=1 then raise_application_error(-20886,'INTERWARE_APPLIED_AGGREGATION_BIRTH_SOURCE_REQUIRED');end if;
 select a.UNITS_JSON into members from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=a.ORDER_ID and rec.LINE_NUMBER=a.LINE_NUMBER
 where rec.UID_PALLET=v_origin_uid and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 aggregate_version:=null;
 end if;
 select count(*)into n from RRL_SKU_RECEIPT_PROFILE profile join RRL_PALLETS p on p.ARTICUL=profile.ARTICUL 
 where p.UID_PALLET=v_origin_uid and profile.SYSTEM_CODE=v_system_code and profile.PROFILE_CODE=v_profile_code; 
 if n!=1 then raise_application_error(-20886,'INTERWARE_AGGREGATION_CURRENT_PROFILE_REQUIRED');end if; 
 select profile.PROFILE_VERSION,profile.SCAN_MODE into current_version,scan_mode from RRL_SKU_RECEIPT_PROFILE profile join RRL_PALLETS p on p.ARTICUL=profile.ARTICUL 
 where p.UID_PALLET=v_origin_uid and profile.SYSTEM_CODE=v_system_code and profile.PROFILE_CODE=v_profile_code; 
 if current_version is null or(aggregate_version is not null and current_version!=aggregate_version)or scan_mode not in(v_level_code,'UNIT_OR_AGGREGATION')or scan_mode is null then raise_application_error(-20887,'INTERWARE_AGGREGATION_PROFILE_VERSION_OR_MODE');end if; 
 if v_system_code='CRPT'then 
 select count(*)into n from RRL_CRPT_AGGREGATION where UID_PALLET=v_origin_uid and upper(AGGREGATION_STATUS)in('DISAGGREGATED','CANCELLED','DESTROYED','REJECTED'); 
 if n!=0 then raise_application_error(-20886,'INTERWARE_REGULATORY_AGGREGATION_INVALIDATED');end if; 
 end if; 
 expected_count:=json_array_t.parse(members).get_size; 
 if expected_count<1 or expected_count>10000 then raise_application_error(-20881,'INTERWARE_AGGREGATION_MEMBER_BOUND');end if; 
 select count(*),json_arrayagg(json_object('system_code'value v_system_code,'profile_code'value v_profile_code,'code_hash'value code.CODE_HASH)order by u.PHYSICAL_UNIT_KEY returning clob) 
 into current_count,expanded_wire 
 from json_table(members,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id',Q varchar2(60)path '$.quantity',RAW_CODE varchar2(4000)path '$.code'))j 
 join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=v_origin_uid and u.UNIT_ID=j.UNIT_ID 
 join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID and code.SYSTEM_CODE=v_system_code 
 where u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=case when j.Q is not null then RRL_STOCK_MATH.quantity(j.Q) else u.BASE_QTY end 
 and exists(select 1 from json_table(code.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile',C varchar2(4000)path '$.raw_code',V varchar2(40)path '$.version'))proof where proof.P=v_profile_code and proof.C=j.RAW_CODE and proof.V=current_version); 
 if current_count!=expected_count then raise_application_error(-20886,'INTERWARE_AGGREGATION_MEMBERS_CHANGED');end if; 
 expanded:=json_array_t.parse(expanded_wire); 
 for j in 0..expanded.get_size-1 loop result_scans.append(expanded.get(j));end loop; 
 if result_scans.get_size>20000 then raise_application_error(-20881,'INTERWARE_EXPANDED_SCAN_BOUND');end if; 
 end loop; 
 p_scans:=result_scans.to_clob; 
 end; 
end;
/
