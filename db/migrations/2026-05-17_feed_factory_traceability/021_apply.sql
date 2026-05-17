prompt [migration 2026-05-17-021] Finished goods admin settings - apply

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
  ensure_table('RRL_FINISHED_GOODS_SKU', q'[
    create table RRL_FINISHED_GOODS_SKU (
      ARTICUL varchar2(40) not null,
      IS_FINISHED_GOODS number(1) default 1 not null,
      PRODUCT_GROUP varchar2(100),
      GTIN varchar2(14),
      CRPT_REQUIRED number(1) default 0 not null,
      AGGREGATION_REQUIRED number(1) default 0 not null,
      SSCC_REQUIRED number(1) default 1 not null,
      PALLET_LABEL_REQUIRED number(1) default 1 not null,
      QUALITY_HOLD_REQUIRED number(1) default 0 not null,
      DEFAULT_PALLET_CASE_QTY number,
      DEFAULT_LAYER_QTY number,
      DEFAULT_LAYER_COUNT number,
      TECHNOLOGIST_COMMENT varchar2(1000),
      ACTIVE number(1) default 1 not null,
      CREATED_AT timestamp default systimestamp not null,
      CREATED_BY varchar2(50),
      UPDATED_AT timestamp,
      UPDATED_BY varchar2(50),
      constraint RRL_FINISHED_GOODS_SKU_PK primary key (ARTICUL),
      constraint RRL_FINISHED_GOODS_SKU_CHK1 check (IS_FINISHED_GOODS in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK2 check (CRPT_REQUIRED in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK3 check (AGGREGATION_REQUIRED in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK4 check (SSCC_REQUIRED in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK5 check (PALLET_LABEL_REQUIRED in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK6 check (QUALITY_HOLD_REQUIRED in (0, 1)),
      constraint RRL_FINISHED_GOODS_SKU_CHK7 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_index('RRL_FINISHED_GOODS_SKU_I1',
    'create index RRL_FINISHED_GOODS_SKU_I1 on RRL_FINISHED_GOODS_SKU (ACTIVE, IS_FINISHED_GOODS, PRODUCT_GROUP)');
end;
/

merge into RRL_FINISHED_GOODS_SKU d
using (
  select upper(substr(a.ACTICUL, 1, 40)) ARTICUL,
         max(b.GTIN) GTIN,
         max(nvl(b.CRPT_REQUIRED, 0)) CRPT_REQUIRED
    from (
      select ACTICUL
        from RRL_ARTICULS
       where upper(ACTICUL) like 'FG-%'
      union
      select ARTICUL
        from RRL_PROD_BATCH
       where ARTICUL is not null
      union
      select p.ARTICUL
        from RRL_PALLETS p
        join RRL_REMAINS r on r.UID_POLETA = p.UID_PALLET
        join RRL_CELLS c on c.CELL = r.CELL
        join RRL_WARES w on w.ID = c.WARE_ID
       where p.ARTICUL is not null
         and (nvl(w.FLAG_FINISHED_GOODS, 0) = 1 or nvl(w.FLAG_PRODUCTION_BUFFER, 0) = 1)
         and nvl(r.REMAIN, 0) <> 0
    ) a
    left join RRL_PROD_BATCH b on upper(b.ARTICUL) = upper(a.ACTICUL)
   group by upper(substr(a.ACTICUL, 1, 40))
) s
on (upper(d.ARTICUL) = s.ARTICUL)
when matched then update set
  d.IS_FINISHED_GOODS = 1,
  d.GTIN = nvl(d.GTIN, s.GTIN),
  d.CRPT_REQUIRED = greatest(nvl(d.CRPT_REQUIRED, 0), nvl(s.CRPT_REQUIRED, 0)),
  d.UPDATED_AT = systimestamp,
  d.UPDATED_BY = '021_apply'
when not matched then insert (
  ARTICUL, IS_FINISHED_GOODS, GTIN, CRPT_REQUIRED,
  AGGREGATION_REQUIRED, SSCC_REQUIRED, PALLET_LABEL_REQUIRED,
  QUALITY_HOLD_REQUIRED, ACTIVE, CREATED_BY, CREATED_AT
) values (
  s.ARTICUL, 1, s.GTIN, nvl(s.CRPT_REQUIRED, 0),
  0, 1, 1, 0, 1, '021_apply', systimestamp
);

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'FINISHED_GOODS_VIEW' RIGHT1, 'View finished goods admin page' DESCR from dual
    union all
    select 'FINISHED_GOODS_EDIT', 'Edit finished goods SKU settings' from dual
    union all
    select 'FINISHED_GOODS_STOCK_VIEW', 'View finished goods stock and pallets' from dual
    union all
    select 'FINISHED_GOODS_BATCH_VIEW', 'View finished goods production batches' from dual
    union all
    select 'FINISHED_GOODS_EXPORT', 'Export finished goods lists and stock' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-021-finished-goods-admin' migration_id,
         'Finished goods SKU settings and admin rights' description,
         '021_apply.sql' script_name,
         '021_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-021] done
