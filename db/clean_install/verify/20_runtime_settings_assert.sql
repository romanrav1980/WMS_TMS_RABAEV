set define off

prompt [verify] runtime settings

declare
  v_count number;
  procedure assert_row(p_count number, p_name varchar2) is
  begin
    if p_count = 0 then
      raise_application_error(-20911, 'Missing runtime setting: ' || p_name);
    end if;
  end;

begin
  select count(*) into v_count from RABAEV.RUSERS
   where lower(ID) = 'admin'
     and PASS = 'admin123'
     and USER_GROUP = 'GLOBAL_ADMIN'
     and nvl(DELETED, 0) = 0;
  assert_row(v_count, 'admin/admin123 GLOBAL_ADMIN user');

  select count(*) into v_count from RABAEV.USER_GROUP where ID = 'GLOBAL_ADMIN';
  assert_row(v_count, 'GLOBAL_ADMIN group');

  select count(*) into v_count from RABAEV.RRL_VERSIONS where VERSION = 'xp12' and ALLOW = 1;
  assert_row(v_count, 'xp12 allowed version');

  select count(*) into v_count from RABAEV.RRL_CONSTANTS where NAME = 'storeloc';
  assert_row(v_count, 'storeloc constant');

  select count(*) into v_count from RABAEV.RRL_WARES where ID = 1;
  assert_row(v_count, 'warehouse 1');
end;
/

prompt [verify] runtime settings ok
