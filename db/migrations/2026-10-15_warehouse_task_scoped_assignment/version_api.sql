create or replace package RRL_WTASK_VERSION_API authid definer
 accessible by(trigger RRL_WTASK_ASSIGN_DERIVE,trigger RRL_WTASK_VERSION_GUARD)as
 procedure derive(p_task number,p_initial boolean);
 function writing(p_task number)return number;
end;
/
create or replace package body RRL_WTASK_VERSION_API as
 g_tx varchar2(100);g_task number;
 function writing(p_task number)return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)and g_task=p_task then return 1;end if;return 0;end;
 procedure derive(p_task number,p_initial boolean)is begin
  g_tx:=dbms_transaction.local_transaction_id(true);g_task:=p_task;
  if p_initial then
   insert into RRL_WTASK_ASSIGN_VERSION(TASK_ID,ASSIGNMENT_VERSION)values(p_task,0);
  else
   update RRL_WTASK_ASSIGN_VERSION set ASSIGNMENT_VERSION=ASSIGNMENT_VERSION+1,CHANGED_AT=systimestamp where TASK_ID=p_task;
   if sql%rowcount=0 then insert into RRL_WTASK_ASSIGN_VERSION(TASK_ID,ASSIGNMENT_VERSION)values(p_task,1);end if;
  end if;
  g_tx:=null;g_task:=null;
 exception when others then g_tx:=null;g_task:=null;raise;end;
end;
/
create or replace trigger RRL_WTASK_VERSION_GUARD before insert or update or delete on RRL_WTASK_ASSIGN_VERSION for each row begin
 if deleting or RRL_WTASK_VERSION_API.writing(:new.TASK_ID)!=1 then raise_application_error(-20863,'WTASK_VERSION_SERVER_DERIVED');end if;
 if updating and(:new.TASK_ID!=:old.TASK_ID or :new.ASSIGNMENT_VERSION!=:old.ASSIGNMENT_VERSION+1)then raise_application_error(-20863,'WTASK_VERSION_MONOTONIC');end if;
end;
/
