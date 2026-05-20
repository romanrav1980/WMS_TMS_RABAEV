prompt [migration 2026-05-20-040] linear pick route order invariants - apply

declare
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
  -- Existing restored schemas keep PICK_SEQUENCE as unconstrained NUMBER.
  -- That already supports decimal ranks and avoids ORA-01440 on populated tables.

  update RRL_PICK_ROUTE
     set STATUS = 'ARCHIVED',
         ACTIVE = 0,
         UPDATED_AT = sysdate,
         UPDATED_BY = '040_LINEAR_ROUTE'
   where PICK_ROUTE_ID in (
     select PICK_ROUTE_ID
       from (
         select r.PICK_ROUTE_ID,
                row_number() over (
                  partition by r.TOPOLOGY_ID
                  order by case r.STATUS
                             when 'PUBLISHED' then 1
                             when 'VALIDATED' then 2
                             when 'DRAFT' then 3
                             else 9
                           end,
                           r.PICK_ROUTE_ID desc
                ) RN
           from RRL_PICK_ROUTE r
          where r.TOPOLOGY_ID is not null
            and r.ROUTE_KIND = 'PICK'
            and r.ACTIVE = 1
            and r.STATUS <> 'ARCHIVED'
       )
      where RN > 1
   );

  update RRL_PICK_ROUTE_CELL
     set ACTIVE = 0,
         UPDATED_AT = sysdate,
         UPDATED_BY = '040_LINEAR_ROUTE'
   where PICK_ROUTE_CELL_ID in (
     select PICK_ROUTE_CELL_ID
       from (
         select rc.PICK_ROUTE_CELL_ID,
                row_number() over (
                  partition by rc.PICK_ROUTE_ID, rc.TOPOLOGY_CELL_ID
                  order by rc.PICK_SEQUENCE, rc.PICK_ROUTE_CELL_ID
                ) RN
           from RRL_PICK_ROUTE_CELL rc
          where rc.ACTIVE = 1
            and rc.TOPOLOGY_CELL_ID is not null
       )
      where RN > 1
   );

  update RRL_PICK_ROUTE_CELL
     set ACTIVE = 0,
         UPDATED_AT = sysdate,
         UPDATED_BY = '040_LINEAR_ROUTE'
   where PICK_ROUTE_CELL_ID in (
     select PICK_ROUTE_CELL_ID
       from (
         select rc.PICK_ROUTE_CELL_ID,
                row_number() over (
                  partition by rc.PICK_ROUTE_ID, rc.PICK_SEQUENCE
                  order by rc.PICK_ROUTE_CELL_ID
                ) RN
           from RRL_PICK_ROUTE_CELL rc
          where rc.ACTIVE = 1
       )
      where RN > 1
   );

  ensure_index('RRL_PICK_ROUTE_UX_ACTIVE_TOPO',
    q'[create unique index RRL_PICK_ROUTE_UX_ACTIVE_TOPO on RRL_PICK_ROUTE (
       case when ACTIVE = 1 and ROUTE_KIND = 'PICK' and STATUS <> 'ARCHIVED' then TOPOLOGY_ID end
    )]');

  ensure_index('RRL_PICK_ROUTE_CELL_UX_SEQ',
    q'[create unique index RRL_PICK_ROUTE_CELL_UX_SEQ on RRL_PICK_ROUTE_CELL (
       case when ACTIVE = 1 then PICK_ROUTE_ID end,
       case when ACTIVE = 1 then PICK_SEQUENCE end
    )]');

  ensure_index('RRL_PICK_ROUTE_CELL_UX_CELL',
    q'[create unique index RRL_PICK_ROUTE_CELL_UX_CELL on RRL_PICK_ROUTE_CELL (
       case when ACTIVE = 1 and TOPOLOGY_CELL_ID is not null then PICK_ROUTE_ID end,
       case when ACTIVE = 1 and TOPOLOGY_CELL_ID is not null then TOPOLOGY_CELL_ID end
    )]');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-20-040-linear-pick-route-order' migration_id,
         'Linear pick-route order invariants: one active route per topology, decimal sequence, unique active route sequence and cell membership' description,
         '040_apply.sql' script_name,
         '040_rollback.sql' rollback_script
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

prompt [migration 2026-05-20-040] apply done
