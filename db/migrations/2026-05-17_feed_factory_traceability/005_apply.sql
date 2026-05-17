-- 2026-05-17-005-admin-users-db-backed-auth
-- Purpose: keep WMS admin login and API audit permissions in Oracle, not in code.

declare
  procedure ensure_group(p_id varchar2, p_name varchar2) is
  begin
    merge into USER_GROUP d
    using (select p_id ID, p_name NAME from dual) s
       on (d.ID = s.ID)
     when matched then update set d.NAME = s.NAME
     when not matched then insert (ID, NAME) values (s.ID, s.NAME);
  end;

  procedure ensure_right(p_group varchar2, p_right varchar2, p_descr varchar2) is
    v_id number;
  begin
    select count(*)
      into v_id
      from RIGHTS
     where USER_GROUP = p_group
       and lower(RIGHT1) = lower(p_right);

    if v_id = 0 then
      select nvl(max(ID), 0) + 1 into v_id from RIGHTS;
      insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
      values (p_right, p_group, v_id, p_descr);
    else
      update RIGHTS
         set DESCR = p_descr
       where USER_GROUP = p_group
         and lower(RIGHT1) = lower(p_right);
    end if;
  end;
begin
  ensure_group('GLOBAL_ADMIN', 'Global Admin');

  ensure_right('GLOBAL_ADMIN', 'WMS_ADMIN_LOGIN', 'WMS admin shell login');
  ensure_right('GLOBAL_ADMIN', 'API_AUDIT_VIEW', 'View API call audit journal and details');
  ensure_right('GLOBAL_ADMIN', 'API_AUDIT_REPLAY', 'Replay API calls from audit journal');
  ensure_right('GLOBAL_ADMIN', 'REGULATORY_ADAPTER_VIEW', 'View Mercury and Honest Sign adapter journal');
  ensure_right('GLOBAL_ADMIN', 'REGULATORY_ADAPTER_RETRY', 'Retry Mercury and Honest Sign adapter messages');

  merge into RUSERS d
  using (
    select 'admin' ID,
           'Global Administrator' NAME,
           'admin123' PASS,
           'GLOBAL_ADMIN' USER_GROUP
      from dual
  ) s
     on (lower(d.ID) = lower(s.ID))
   when matched then update set
     d.NAME = s.NAME,
     d.PASS = s.PASS,
     d.DELETED = 0,
     d.PRAVO_ADMIN_LOGIN = 1,
     d.USER_GROUP = s.USER_GROUP,
     d.WARE_ID = nvl(d.WARE_ID, 1)
   when not matched then insert (
     ID, NAME, PASS, DELETED, PRAVO_ADMIN_LOGIN, USER_GROUP, WARE_ID
   ) values (
     s.ID, s.NAME, s.PASS, 0, 1, s.USER_GROUP, 1
   );
end;
/
