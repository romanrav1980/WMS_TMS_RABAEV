prompt [migration 2026-05-17-013] Batch shipment readiness and aging norm - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);

    if n = 0 then
      execute immediate 'alter table ' || p_table || ' add (' || p_sql || ')';
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
  ensure_column('RRL_ARTICULS', 'SHIPMENT_AGING_HOURS', 'SHIPMENT_AGING_HOURS number default 0');
  ensure_column('RRL_ARTICULS', 'SHIPMENT_AGING_COMMENT', 'SHIPMENT_AGING_COMMENT varchar2(1000)');

  ensure_column('RRL_PROD_BATCH', 'AGING_REQUIRED_HOURS', 'AGING_REQUIRED_HOURS number default 0');
  ensure_column('RRL_PROD_BATCH', 'AGING_UNTIL', 'AGING_UNTIL date');
  ensure_column('RRL_PROD_BATCH', 'SHIPMENT_ALLOWED_AT', 'SHIPMENT_ALLOWED_AT date');
  ensure_column('RRL_PROD_BATCH', 'SHIPMENT_RELEASE_STATUS', q'[SHIPMENT_RELEASE_STATUS varchar2(30) default 'READY']');
  ensure_column('RRL_PROD_BATCH', 'SHIPMENT_BLOCK_REASON', 'SHIPMENT_BLOCK_REASON varchar2(1000)');

  ensure_index('RRL_PROD_BATCH_I_SHIP_READY', 'create index RRL_PROD_BATCH_I_SHIP_READY on RRL_PROD_BATCH (SHIPMENT_RELEASE_STATUS, SHIPMENT_ALLOWED_AT)');
  ensure_index('RRL_ARTICULS_I_AGING', 'create index RRL_ARTICULS_I_AGING on RRL_ARTICULS (ACTICUL, SHIPMENT_AGING_HOURS)');
end;
/

create or replace trigger RRL_TRG_PROD_BATCH_SHIP_READY
  before insert or update of ARTICUL, PRODUCED_DATE_FROM, PRODUCED_DATE_TO, QUALITY_STATUS, AGING_REQUIRED_HOURS
  on RRL_PROD_BATCH
  for each row
declare
  v_hours number := 0;
  v_base_date date;
begin
  if :new.ARTICUL is not null then
    select nvl(max(SHIPMENT_AGING_HOURS), 0)
      into v_hours
      from RRL_ARTICULS
     where upper(ACTICUL) = upper(:new.ARTICUL);
  end if;

  if inserting or nvl(:new.AGING_REQUIRED_HOURS, -1) < 0 then
    :new.AGING_REQUIRED_HOURS := nvl(v_hours, 0);
  elsif :new.AGING_REQUIRED_HOURS is null then
    :new.AGING_REQUIRED_HOURS := nvl(v_hours, 0);
  end if;

  v_base_date := nvl(:new.PRODUCED_DATE_TO, nvl(:new.PRODUCED_DATE_FROM, sysdate));
  if :new.SHIPMENT_ALLOWED_AT is null then
    :new.SHIPMENT_ALLOWED_AT := v_base_date + nvl(:new.AGING_REQUIRED_HOURS, 0) / 24;
  end if;

  if :new.AGING_UNTIL is null then
    :new.AGING_UNTIL := :new.SHIPMENT_ALLOWED_AT;
  end if;

  if :new.SHIPMENT_RELEASE_STATUS is null
     or :new.SHIPMENT_RELEASE_STATUS in ('READY', 'WAIT_AGING') then
    if nvl(:new.AGING_REQUIRED_HOURS, 0) > 0 and :new.SHIPMENT_ALLOWED_AT > sysdate then
      :new.SHIPMENT_RELEASE_STATUS := 'WAIT_AGING';
    else
      :new.SHIPMENT_RELEASE_STATUS := 'READY';
    end if;
  end if;
end;
/

update RRL_PROD_BATCH b
   set AGING_REQUIRED_HOURS = nvl((
         select max(nvl(a.SHIPMENT_AGING_HOURS, 0))
           from RRL_ARTICULS a
          where upper(a.ACTICUL) = upper(b.ARTICUL)
       ), 0),
       SHIPMENT_ALLOWED_AT = nvl(
         SHIPMENT_ALLOWED_AT,
         nvl(PRODUCED_DATE_TO, nvl(PRODUCED_DATE_FROM, CREATED_AT)) + nvl((
           select max(nvl(a.SHIPMENT_AGING_HOURS, 0))
             from RRL_ARTICULS a
            where upper(a.ACTICUL) = upper(b.ARTICUL)
         ), 0) / 24
       ),
       AGING_UNTIL = nvl(
         AGING_UNTIL,
         nvl(
           SHIPMENT_ALLOWED_AT,
           nvl(PRODUCED_DATE_TO, nvl(PRODUCED_DATE_FROM, CREATED_AT)) + nvl((
             select max(nvl(a.SHIPMENT_AGING_HOURS, 0))
               from RRL_ARTICULS a
              where upper(a.ACTICUL) = upper(b.ARTICUL)
           ), 0) / 24
         )
       ),
       SHIPMENT_RELEASE_STATUS = case
         when nvl((
           select max(nvl(a.SHIPMENT_AGING_HOURS, 0))
             from RRL_ARTICULS a
            where upper(a.ACTICUL) = upper(b.ARTICUL)
         ), 0) > 0
          and nvl(
            SHIPMENT_ALLOWED_AT,
            nvl(PRODUCED_DATE_TO, nvl(PRODUCED_DATE_FROM, CREATED_AT)) + nvl((
              select max(nvl(a.SHIPMENT_AGING_HOURS, 0))
                from RRL_ARTICULS a
               where upper(a.ACTICUL) = upper(b.ARTICUL)
            ), 0) / 24
          ) > sysdate then 'WAIT_AGING'
         else nvl(SHIPMENT_RELEASE_STATUS, 'READY')
       end
 where SHIPMENT_ALLOWED_AT is null
    or AGING_UNTIL is null
    or AGING_REQUIRED_HOURS is null
    or SHIPMENT_RELEASE_STATUS is null;

create or replace view RRL_PROD_BATCH_READY_V as
select b.PROD_BATCH_ID,
       b.PROD_BATCH_NO,
       b.PRODUCTION_ORDER_ID,
       b.ARTICUL,
       b.WARE_ID,
       b.QUALITY_STATUS,
       b.AGING_REQUIRED_HOURS,
       b.AGING_UNTIL,
       b.SHIPMENT_ALLOWED_AT,
       b.SHIPMENT_RELEASE_STATUS,
       b.SHIPMENT_BLOCK_REASON,
       case
         when nvl(b.QUALITY_STATUS, 'DRAFT') in ('DRAFT', 'BLOCKED', 'QUALITY_HOLD', 'LAB_PENDING', 'REJECTED') then 'BLOCKED'
         when b.SHIPMENT_RELEASE_STATUS in ('BLOCKED', 'QUALITY_HOLD', 'REJECTED') then 'BLOCKED'
         when b.SHIPMENT_ALLOWED_AT is not null and b.SHIPMENT_ALLOWED_AT > sysdate then 'WAIT_AGING'
         else 'READY'
       end SHIPMENT_EFFECTIVE_STATUS,
       case
         when nvl(b.QUALITY_STATUS, 'DRAFT') in ('DRAFT', 'BLOCKED', 'QUALITY_HOLD', 'LAB_PENDING', 'REJECTED') then 0
         when b.SHIPMENT_RELEASE_STATUS in ('BLOCKED', 'QUALITY_HOLD', 'REJECTED') then 0
         when b.SHIPMENT_ALLOWED_AT is not null and b.SHIPMENT_ALLOWED_AT > sysdate then 0
         else 1
       end IS_SHIPMENT_ALLOWED,
       b.CREATED_AT,
       b.UPDATED_AT
  from RRL_PROD_BATCH b;

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'QUALITY_BATCH_VIEW' RIGHT1, 'View batch quality and shipment readiness' DESCR from dual
    union all
    select 'QUALITY_BATCH_EDIT', 'Edit batch quality and shipment readiness' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-013-batch-shipment-readiness' migration_id,
         'Batch quality, aging norm, and shipment readiness fields' description,
         '013_apply.sql' script_name,
         '013_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-013] done
