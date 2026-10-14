create or replace trigger RRL_IW_GROUP_PLAN_GUARD before insert or update or delete on RRL_IW_GROUP_PLAN for each row
declare wire clob;source_value json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_PLAN_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 wire:=RRL_IW_GROUP_SOURCE.source_json(:new.SOURCE_LOAD_OPERATION_ID,:new.ACTOR);source_value:=json_object_t.parse(wire);
 if dbms_lob.compare(wire,:new.SOURCE_JSON)!=0 or source_value.get_number('source_trip_id')!=:new.SOURCE_TT_ID or source_value.get_number('source_warehouse_id')!=:new.SOURCE_WARE_ID or source_value.get_string('physical_place_identifier')!=:new.ROOT_UID then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=:new.INBOUND_DOCK and WARE_ID=:new.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_TARGET_INBOUND_REQUIRED');end if;
 select count(*)into n from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK and d.WARE_ID=:new.TARGET_WARE_ID and nvl(d.DOCK_IS_BLOCKED,0)=0
 where t.ID=:new.TARGET_TT_ID and t.DOCK=:new.OUTBOUND_DOCK and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_TARGET_TRIP_REQUIRED');end if;
end;
/
