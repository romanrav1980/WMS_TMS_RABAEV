create or replace trigger RRL_INTERWARE_PLAN_GUARD before insert or update or delete on RRL_INTERWARE_PLAN for each row
declare n number;unit_wire clob;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_PLAN_SOURCE_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RUSERS u where u.ID=:new.ACTOR and nvl(u.DELETED,0)=0 and(u.WARE_ID=:new.SOURCE_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1;
 if n!=1 then raise_application_error(-20882,'INTERWARE_SOURCE_DISPATCHER_REQUIRED');end if;
 select count(*)into n from RRL_TT_HU_LOAD_FACT f join RRL_TT_HU_LOAD_ST m on m.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID and m.ACTIVE_FLAG=1
 join RRL_SBORKA_PALLETS s on s.ID=m.SBORKA_PALLET_ID join RRL_PALLETS p on p.UID_PALLET=:new.ROOT_UID
 where f.LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and f.TT_ID=:new.SOURCE_TT_ID and f.WARE_ID=:new.SOURCE_WARE_ID
 and f.ROOT_UID=nvl(:new.SOURCE_PLACE_UID,:new.ROOT_UID) and m.SBORKA_PALLET_ID=:new.SOURCE_ST_ID and f.STATUS='DEPARTED' and f.ROOT_CASE_TASK_ID is null
 and nvl(p.HU_KIND,'STOCK')='STOCK'and s.RETURN_SUPPLIER_ID is null and dbms_lob.compare(f.COMPOSITION_JSON,:new.SOURCE_COMPOSITION_JSON)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_EXACT_EXISTING_SINGLE_LOAD_REQUIRED');end if;
 if :new.ROOT_UID!=RRL_IW_HU_SOURCE.stock_uid(:new.SOURCE_LOAD_OPERATION_ID)then raise_application_error(-20886,'INTERWARE_FROZEN_STOCK_LEAF_REQUIRED');end if;
 RRL_IW_HU_SOURCE.assert_context(:new.SOURCE_LOAD_OPERATION_ID,:new.SOURCE_HU_JSON);
 if (:new.SOURCE_HU_JSON is null and :new.SOURCE_PLACE_UID is not null)or(:new.SOURCE_HU_JSON is not null and(:new.SOURCE_PLACE_UID is null or :new.SOURCE_PLACE_UID=:new.ROOT_UID))then raise_application_error(-20886,'INTERWARE_PHYSICAL_PLACE_STOCK_KEYS_REQUIRED');end if;

 select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and ACTIVE_FLAG=1;
 if n!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_ST_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=:new.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
 if n!=0 then raise_application_error(-20886,'INTERWARE_SOURCE_STOCK_ALREADY_PRESENT');end if;
 unit_wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(:new.SOURCE_LOAD_OPERATION_ID,:new.ROOT_UID,:new.SOURCE_COMPOSITION_JSON);
 select count(*)into n from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID;if n!=0 then raise_application_error(-20886,'INTERWARE_ALREADY_ACCEPTED_BY_STORE');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=:new.INBOUND_DOCK and WARE_ID=:new.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;if n!=1 then raise_application_error(-20886,'INTERWARE_TARGET_INBOUND_DOCK_REQUIRED');end if;
 select count(*)into n from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK and d.WARE_ID=:new.TARGET_WARE_ID and nvl(d.DOCK_IS_BLOCKED,0)=0
 where t.ID=:new.TARGET_TT_ID and t.DOCK=:new.OUTBOUND_DOCK and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_EXISTING_TARGET_PLANNED_TRIP_REQUIRED');end if;
end;
/
