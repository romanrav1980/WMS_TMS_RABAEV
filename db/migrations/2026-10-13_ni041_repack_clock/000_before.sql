create or replace package body RRL_HU_PACK_CLOCK as

 g_writing boolean:=false;

 function writing return boolean is begin return g_writing;end;

 procedure begin_empty_box(p_uid varchar2,p_operation varchar2,p_actor varchar2)is

 p RRL_PALLETS%rowtype;n number;ware number;kind varchar2(80);state varchar2(20);actor nvarchar2(50);

 begin

  if nvl(sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'),'~')!=p_operation or

   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or

   sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)

   then raise_application_error(-20863,'BOX_PACKING_ROOT_CONTEXT_REQUIRED');end if;

  select COMMAND_TYPE,STATE,ACTOR into kind,state,actor from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;

  if kind not in('HU_ATTACH','HU_REPACK')or state!='IN_FLIGHT'or actor!=p_actor then raise_application_error(-20863,'BOX_PACKING_ATTACH_REQUIRED');end if;

  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));

  select *into p from RRL_PALLETS where UID_PALLET=p_uid;

  if p.HU_KIND!='CONTAINER'or p.HU_TYPE!='BOX'then return;end if;

  select count(*)into n from RRL_WMS_HU_LINK where PARENT_UID=p_uid and ACTIVE_FLAG=1;

  if n!=0 then return;end if;

  select WARE_ID into ware from RRL_CELLS where CELL=p.HU_CURRENT_CELL;

  g_writing:=true;

  insert into RRL_HU_PACK_CYCLE(PARENT_UID,START_CONTENT_VERSION,START_OPERATION_ID,WARE_ID,ACTOR,STARTED_AT_INSTANT)

  values(p_uid,p.HU_CONTENT_VERSION+1,p_operation,ware,p_actor,systimestamp);

  g_writing:=false;

 exception when others then g_writing:=false;raise;

 end;

 function clock_json(p_uid varchar2,p_version number)return json_object_t is

 j json_object_t;r RRL_HU_PACK_CYCLE%rowtype;

 begin

  select *into r from RRL_HU_PACK_CYCLE where PARENT_UID=p_uid and START_CONTENT_VERSION<=p_version

   order by START_CONTENT_VERSION desc fetch first 1 row only;

  j:=json_object_t();j.put('operation_id',r.START_OPERATION_ID);j.put('content_version',r.START_CONTENT_VERSION);

  j.put('warehouse',r.WARE_ID);

  j.put('instant',to_char(r.STARTED_AT_INSTANT,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));

  return j;

 exception when no_data_found then return null;

 end;

end;


/
