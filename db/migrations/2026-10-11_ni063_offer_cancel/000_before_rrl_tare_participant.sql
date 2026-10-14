create or replace package RRL_TARE_PARTICIPANT authid definer as
 procedure warehouse_actor(p_actor varchar2,p_owner number);
 procedure holder_actor(p_actor varchar2,p_kind varchar2,p_id varchar2,p_owner number,p_trip RRL_TRANSPORT_TASK%rowtype,p_right varchar2);
end;
/

create or replace package body RRL_TARE_PARTICIPANT as
 procedure warehouse_actor(p_actor varchar2,p_owner number) is n number;
 begin
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=p_owner);
 if n!=1 then raise_application_error(-20882,'TARE_WAREHOUSE_BINDING_REQUIRED');end if;
 end;
 procedure holder_actor(p_actor varchar2,p_kind varchar2,p_id varchar2,p_owner number,p_trip RRL_TRANSPORT_TASK%rowtype,p_right varchar2) is n number;
 begin
 if RRL_HAS_WRIGHT(p_actor,p_right)!=1 then raise_application_error(-20882,'TARE_PARTICIPANT_PERMISSION_REQUIRED');end if;
 if p_kind='WAREHOUSE' then warehouse_actor(p_actor,p_owner);
 elsif p_kind='VEHICLE' then
 select count(*) into n from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID
 where b.DRIVER_ID=p_trip.VODITEL_ID and b.USER_ID=p_actor and b.ACTIVE=1 and nvl(u.DELETED,0)=0 and upper(trim(u.USER_GROUP))!='GLOBAL_ADMIN';
 if n!=1 then raise_application_error(-20882,'TARE_AUTHENTICATED_CURRENT_DRIVER_REQUIRED');end if;
 else RRL_STOCK_STORE_RECEIPT_READ.require_receiver(p_actor,p_id);end if;
 end;
end;
/
