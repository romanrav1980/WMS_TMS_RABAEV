set define off
set serveroutput on

prompt [clean-install] minimal runtime settings

alter session set current_schema = RABAEV;

merge into RRL_WARES d
using (
  select 1 ID,
         'WARE_1' NAME,
         'OVERFLOW' OVERFLOW_CELL_NAME,
         'C' PREFIX,
         'Z0001' FAKE_ART,
         'OVERFLOW' SPIS_IF_HRAN_NO_EMPTY,
         1 ORD2
    from dual
) s
on (d.ID = s.ID)
when matched then update set
  d.NAME = s.NAME,
  d.OVERFLOW_CELL_NAME = s.OVERFLOW_CELL_NAME,
  d.PREFIX = s.PREFIX,
  d.FAKE_ART = s.FAKE_ART,
  d.SPIS_IF_HRAN_NO_EMPTY = s.SPIS_IF_HRAN_NO_EMPTY,
  d.ORD2 = s.ORD2
when not matched then insert (
  ID, NAME, OVERFLOW_CELL_NAME, PREFIX, FAKE_ART, SPIS_IF_HRAN_NO_EMPTY, ORD2
) values (
  s.ID, s.NAME, s.OVERFLOW_CELL_NAME, s.PREFIX, s.FAKE_ART, s.SPIS_IF_HRAN_NO_EMPTY, s.ORD2
);

merge into USER_GROUP d
using (select 'GLOBAL_ADMIN' ID, 'Global Admin' NAME from dual) s
on (d.ID = s.ID)
when matched then update set d.NAME = s.NAME
when not matched then insert (ID, NAME) values (s.ID, s.NAME);

declare
  procedure ensure_right(p_right varchar2, p_descr varchar2) is
    v_id number;
  begin
    select count(*)
      into v_id
      from RIGHTS
     where USER_GROUP = 'GLOBAL_ADMIN'
       and upper(RIGHT1) = upper(p_right);

    if v_id = 0 then
      select nvl(max(ID), 0) + 1 into v_id from RIGHTS;
      insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
      values (upper(p_right), 'GLOBAL_ADMIN', v_id, p_descr);
    else
      update RIGHTS
         set DESCR = p_descr
       where USER_GROUP = 'GLOBAL_ADMIN'
         and upper(RIGHT1) = upper(p_right);
    end if;
  end;
begin
  ensure_right('WMS_ADMIN_LOGIN', 'WMS admin shell login');
  ensure_right('API_AUDIT_VIEW', 'View API call audit journal and details');
  ensure_right('API_AUDIT_REPLAY', 'Replay API calls from audit journal');
  ensure_right('RIGHTS_ADMIN_VIEW', 'View WMS users, groups, and legacy RIGHTS');
  ensure_right('RIGHTS_ADMIN_EDIT', 'Edit WMS user groups and legacy RIGHTS');
  ensure_right('TRANSPORT_VIEW', 'View transport module');
  ensure_right('TRANSPORT_EDIT', 'Edit transport module');
  ensure_right('TRANSPORT_FLEET_EDIT', 'Edit transport fleet dictionaries');
end;
/

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

merge into RRL_VERSIONS d
using (select 'xp12' VERSION, 1 ALLOW from dual) s
on (d.VERSION = s.VERSION)
when matched then update set d.ALLOW = s.ALLOW
when not matched then insert (VERSION, ALLOW) values (s.VERSION, s.ALLOW);

merge into RRL_CONSTANTS d
using (
  select 'EXT_BASE_CONNECTION_STRING' NAME,
         'Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=127.0.0.1)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=orcl)));User ID=SUPERMAG;Password=SUPERMAG' VALUE
    from dual
  union all select 'load_logopar_from_supermag', '0' from dual
  union all select 'storeloc', '1' from dual
) s
on (d.NAME = s.NAME)
when matched then update set d.VALUE = s.VALUE
when not matched then insert (NAME, VALUE) values (s.NAME, s.VALUE);

merge into RRL_WARE_MASKS d
using (select 'C----' WARE_MASK, '1' WARE_MASK_IDS, 1 ORD_ID from dual) s
on (d.WARE_MASK = s.WARE_MASK)
when matched then update set
  d.WARE_MASK_IDS = s.WARE_MASK_IDS,
  d.ORD_ID = s.ORD_ID
when not matched then insert (WARE_MASK, WARE_MASK_IDS, ORD_ID)
values (s.WARE_MASK, s.WARE_MASK_IDS, s.ORD_ID);

commit;

prompt [clean-install] minimal runtime settings done
