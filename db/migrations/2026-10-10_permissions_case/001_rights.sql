create or replace function RRL_HAS_WRIGHT(user_id varchar2,wright_name varchar2) return int is
 group_id varchar2(255);n number;
begin
 if user_id is null or wright_name is null then return 0;end if;
 select count(*),max(USER_GROUP) into n,group_id from RUSERS where ID=user_id and nvl(DELETED,0)=0;
 if n!=1 then return 0;end if;
 if upper(trim(group_id))='GLOBAL_ADMIN' then return 1;end if;
 select count(*) into n from RIGHTS where USER_GROUP=group_id and upper(trim(RIGHT1))=upper(trim(wright_name));
 if n>0 then return 1;end if;return 0;
exception when others then return 0;
end;
/
