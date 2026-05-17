-- 2026-05-17-006-rights-admin-page-permissions
-- Purpose: add separate legacy RIGHTS permissions for the rights administration page.

declare
  procedure ensure_right(p_group varchar2, p_right varchar2, p_descr varchar2) is
    v_count number;
    v_id number;
  begin
    select count(*)
      into v_count
      from RIGHTS
     where USER_GROUP = p_group
       and upper(RIGHT1) = upper(p_right);

    if v_count = 0 then
      select nvl(max(ID), 0) + 1 into v_id from RIGHTS;
      insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
      values (upper(p_right), p_group, v_id, p_descr);
    else
      update RIGHTS
         set DESCR = p_descr
       where USER_GROUP = p_group
         and upper(RIGHT1) = upper(p_right);
    end if;
  end;
begin
  ensure_right('GLOBAL_ADMIN', 'RIGHTS_ADMIN_VIEW', 'View WMS users, groups, and legacy RIGHTS');
  ensure_right('GLOBAL_ADMIN', 'RIGHTS_ADMIN_EDIT', 'Edit WMS user groups and legacy RIGHTS');
end;
/
