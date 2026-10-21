create or replace package body RRL_PALLET_FLOOR_READ as
 function scope_warehouse(p_uid varchar2,p_actor varchar2)return number is ware_no number;n number;
 begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'stock_posting_shipping')=1;
  if n!=1 then raise_application_error(-20882,'PALLET_FLOOR_ACTOR_REQUIRED');end if;
  select count(distinct c.WARE_ID),min(c.WARE_ID)into n,ware_no from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
   where r.UID_POLETA=p_uid and r.REMAIN>0;
  if n>1 then raise_application_error(-20886,'PALLET_FLOOR_SINGLE_WARE_REQUIRED');end if;
  if n=0 then
   begin select DECLARED_WARE_ID into ware_no from RRL_PALLET_FLOOR_TYPE where UID_PALLET=p_uid;
   exception when no_data_found then raise_application_error(-20886,'PALLET_FLOOR_CURRENT_SOURCE_REQUIRED');end;
  end if;
  select count(*)into n from RUSERS u join RRL_WARES w on w.ID=ware_no where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=ware_no or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'PALLET_FLOOR_CURRENT_WARE_FORBIDDEN');end if;
  return ware_no;
 end;
 function describe_type(p_uid varchar2,p_actor varchar2)return clob is
  ware_no number:=scope_warehouse(p_uid,p_actor);p RRL_PALLETS%rowtype;meta RRL_PALLET_FLOOR_TYPE%rowtype;
  j json_object_t:=json_object_t();n number;cell_value varchar2(60);type_name varchar2(160);
 begin
  select *into p from RRL_PALLETS where UID_PALLET=p_uid;
  if p.HU_KIND is null or p.HU_KIND!='STOCK'then raise_application_error(-20886,'PALLET_FLOOR_STOCK_CARRIER_REQUIRED');end if;
  select count(*)into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=p_uid and ACTIVE_FLAG=1;
  if n>0 then raise_application_error(-20886,'PALLET_FLOOR_INDEPENDENT_TOP_REQUIRED');end if;
  select count(*)into n from RRL_CASE_CARRIER_LOT where LOT_UID=p_uid;
  if n>0 then raise_application_error(-20886,'PALLET_FLOOR_INDEPENDENT_TOP_REQUIRED');end if;
  select count(*),min(CELL)into n,cell_value from RRL_REMAINS where UID_POLETA=p_uid and REMAIN>0;
  if n>1 then raise_application_error(-20886,'PALLET_FLOOR_SINGLE_PHYSICAL_CELL_REQUIRED');end if;
  j.put('article',p.ARTICUL);j.put('uid',p_uid);j.put('warehouse',ware_no);j.put('kind',p.HU_KIND);j.put('sscc',p.SSCC);j.put('cell',cell_value);
  j.put('has_physical_stock',n=1);j.put('operational_admission',false);j.put('stock_changed',false);
  begin
   select *into meta from RRL_PALLET_FLOOR_TYPE where UID_PALLET=p_uid;
   select PALLET_TYPE_NAME into type_name from RRL_PALLET_TYPE where PALLET_TYPE_ID=meta.PALLET_TYPE_ID;
   j.put('version',meta.TYPE_VERSION);j.put('pallet_type_id',meta.PALLET_TYPE_ID);j.put('current_type_name',type_name);
   j.put('operation_id',meta.LAST_OPERATION_ID);j.put('status','CONFIGURED');
  exception when no_data_found then j.put('version',0);j.put('status','NOT_CONFIGURED');end;
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'PALLET_FLOOR_CURRENT_SOURCE_REQUIRED');
 end;
end;
/
