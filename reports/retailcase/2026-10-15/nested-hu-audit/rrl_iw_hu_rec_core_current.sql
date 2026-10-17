package body RRL_IW_HU_REC_CORE as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t)is
 source_hu json_object_t;containers json_array_t;links json_array_t;x json_object_t;
 begin
 if not p_domain.has('nested_source')then return;end if;
 source_hu:=p_domain.get_object('nested_source');containers:=source_hu.get_array('containers');links:=source_hu.get_array('links');
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',source_hu.get_string('stock_uid'));
 for i in 0..containers.get_size-1 loop x:=treat(containers.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',x.get_string('uid'));RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PALLETS',x.get_string('uid'));end loop;
 for i in 0..links.get_size-1 loop x:=treat(links.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('new_id')));
 end loop;
 end;
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2)is
 source_hu json_object_t:=p_domain.get_object('nested_source');containers json_array_t:=source_hu.get_array('containers');links json_array_t:=source_hu.get_array('links');x json_object_t;
 v_uid varchar2(200);v_cell varchar2(60):=p_domain.get_string('receive_cell');v_load varchar2(100):=p_domain.get_string('source_load_operation_id');v_version number;
 v_parent varchar2(200);v_child varchar2(200);v_link number;
 begin
 for i in 0..containers.get_size-1 loop
 x:=treat(containers.get(i)as json_object_t);v_uid:=x.get_string('uid');v_version:=x.get_number('version');
 update RRL_PALLETS set HU_CURRENT_CELL=v_cell,HU_SHIPPED_OPERATION=null,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1
 where UID_PALLET=v_uid and HU_KIND='CONTAINER'and HU_CURRENT_CELL is null and HU_SHIPPED_OPERATION=v_load and HU_CONTENT_VERSION=v_version;
 if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: receiving source container');end if;
 end loop;
 for i in 0..links.get_size-1 loop
 x:=treat(links.get(i)as json_object_t);v_parent:=x.get_string('parent');v_child:=x.get_string('child');v_link:=x.get_number('new_id');
 insert into RRL_WMS_HU_LINK(HU_LINK_ID,PARENT_UID,CHILD_PALLET_UID,ACTIVE_FLAG,LINK_VERSION,LINKED_OPERATION_ID,LINKED_BY)
 values(v_link,v_parent,v_child,1,0,p_operation,p_actor);
 end loop;
 end;
end;
