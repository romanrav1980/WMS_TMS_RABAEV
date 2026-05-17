prompt [migration 2026-05-17-020] Raw material admin settings - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      begin
        execute immediate p_sql;
      exception
        when others then
          if sqlcode = -1408 then
            null;
          else
            raise;
          end if;
      end;
    end if;
  end;
begin
  ensure_table('RRL_RAW_MATERIAL_SKU', q'[
    create table RRL_RAW_MATERIAL_SKU (
      ARTICUL varchar2(40) not null,
      IS_RAW_MATERIAL number(1) default 1 not null,
      RAW_GROUP varchar2(100),
      MERCURY_REQUIRED number(1) default 0 not null,
      LOT_REQUIRED number(1) default 1 not null,
      EXPIRY_REQUIRED number(1) default 1 not null,
      MIN_STOCK_QTY number,
      TARGET_STOCK_QTY number,
      ALLOWED_WARE_IDS varchar2(1000),
      ALLOWED_ZONE_CODES varchar2(1000),
      TECHNOLOGIST_COMMENT varchar2(1000),
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(50),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(50),
      constraint RRL_RAW_MATERIAL_SKU_PK primary key (ARTICUL),
      constraint RRL_RAW_MATERIAL_SKU_CHK1 check (IS_RAW_MATERIAL in (0, 1)),
      constraint RRL_RAW_MATERIAL_SKU_CHK2 check (MERCURY_REQUIRED in (0, 1)),
      constraint RRL_RAW_MATERIAL_SKU_CHK3 check (LOT_REQUIRED in (0, 1)),
      constraint RRL_RAW_MATERIAL_SKU_CHK4 check (EXPIRY_REQUIRED in (0, 1)),
      constraint RRL_RAW_MATERIAL_SKU_CHK5 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_index('RRL_RAW_MATERIAL_SKU_I1',
    'create index RRL_RAW_MATERIAL_SKU_I1 on RRL_RAW_MATERIAL_SKU (ACTIVE, IS_RAW_MATERIAL, RAW_GROUP)');
end;
/

merge into RRL_RAW_MATERIAL_SKU d
using (
  select upper(substr(a.ACTICUL, 1, 40)) ARTICUL,
         case
           when upper(a.ACTICUL) like 'RM-MEAT%' then 'MEAT'
           when upper(a.ACTICUL) like 'RM-PACK%' then 'PACKAGING'
           when upper(a.ACTICUL) like 'RM-ADD%' then 'ADDITIVE'
           else 'RAW'
         end RAW_GROUP,
         case when upper(a.ACTICUL) like 'RM-MEAT%' then 1 else 0 end MERCURY_REQUIRED
    from RRL_ARTICULS a
   where upper(a.ACTICUL) like 'RM-%'
      or exists (
        select 1
          from RRL_PALLETS p
          join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
          join RRL_CELLS c on c.CELL = r.CELL
          join RRL_WARES w on w.ID = c.WARE_ID
         where upper(p.ARTICUL) = upper(a.ACTICUL)
           and nvl(w.FLAG_RAW_MATERIAL, 0) = 1
           and nvl(r.REMAIN, 0) <> 0
      )
) s
on (upper(d.ARTICUL) = s.ARTICUL)
when matched then update set
  d.IS_RAW_MATERIAL = 1,
  d.RAW_GROUP = nvl(d.RAW_GROUP, s.RAW_GROUP),
  d.MERCURY_REQUIRED = greatest(nvl(d.MERCURY_REQUIRED, 0), s.MERCURY_REQUIRED),
  d.UPDATED_AT = systimestamp,
  d.UPDATED_BY = '020_apply'
when not matched then insert (
  ARTICUL, IS_RAW_MATERIAL, RAW_GROUP, MERCURY_REQUIRED,
  LOT_REQUIRED, EXPIRY_REQUIRED, ACTIVE, CREATED_BY, CREATED_AT
) values (
  s.ARTICUL, 1, s.RAW_GROUP, s.MERCURY_REQUIRED,
  1, 1, 1, '020_apply', systimestamp
);

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'RAW_MATERIAL_VIEW' RIGHT1, 'View raw material admin page' DESCR from dual
    union all
    select 'RAW_MATERIAL_EDIT', 'Edit raw material SKU settings' from dual
    union all
    select 'RAW_MATERIAL_STOCK_VIEW', 'View raw material stock' from dual
    union all
    select 'RAW_MATERIAL_EXPORT', 'Export raw material lists and stock' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-020-raw-material-admin' migration_id,
         'Raw material SKU settings and admin rights' description,
         '020_apply.sql' script_name,
         '020_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set
  d.DESCRIPTION = s.DESCRIPTION,
  d.SCRIPT_NAME = s.SCRIPT_NAME,
  d.ROLLBACK_SCRIPT = s.ROLLBACK_SCRIPT,
  d.APPLIED_AT = sysdate,
  d.APPLIED_BY = user
when not matched then insert (
  MIGRATION_ID, DESCRIPTION, SCRIPT_NAME, ROLLBACK_SCRIPT, APPLIED_AT, APPLIED_BY
) values (
  s.MIGRATION_ID, s.DESCRIPTION, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, sysdate, user
);

commit;

prompt [migration 2026-05-17-020] done
