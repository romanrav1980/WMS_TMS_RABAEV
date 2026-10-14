create or replace trigger RRL_INTERWARE_UNIT_MANIFEST_G before insert or update or delete on RRL_INTERWARE_UNIT_MANIFEST for each row
declare plan RRL_INTERWARE_PLAN%rowtype;wire clob;j json_object_t;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_UNIT_MANIFEST_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=:new.PLAN_OPERATION_ID;
 RRL_INTERWARE_UNIT_SOURCE.assert_scope(plan.SOURCE_LOAD_OPERATION_ID,:new.CREATED_BY);
 wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON);j:=json_object_t.parse(wire);
 if j.get_number('physical_unit_count')=0 or j.get_string('unit_signature')!=:new.UNIT_SIGNATURE or dbms_lob.compare(wire,:new.MANIFEST_JSON)!=0 then raise_application_error(-20863,'INTERWARE_UNIT_MANIFEST_EXACT_SOURCE_REQUIRED');end if;
end;
/
