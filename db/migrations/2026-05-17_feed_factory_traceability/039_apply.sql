prompt [migration 2026-05-20-039] topology gate distance matrix - apply

declare
  procedure ensure_table(p_table varchar2, p_sql clob) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_table);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
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
  ensure_table('RRL_TOPOLOGY_GATE', q'[
    create table RRL_TOPOLOGY_GATE (
      TOPOLOGY_GATE_ID number not null,
      TOPOLOGY_ID number not null,
      WARE_ID number not null,
      GATE_CODE varchar2(40) not null,
      GATE_NAME varchar2(200),
      GATE_KIND varchar2(30) default 'SHIPPING' not null,
      STAGING_ZONE_CODE varchar2(40),
      VEHICLE_CLASS varchar2(40),
      X number default 0 not null,
      Y number default 0 not null,
      WIDTH number default 2.8 not null,
      HEIGHT number default 3.2 not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPOLOGY_GATE_PK primary key (TOPOLOGY_GATE_ID),
      constraint RRL_TOPOLOGY_GATE_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPOLOGY_GATE_U1 unique (TOPOLOGY_ID, GATE_CODE),
      constraint RRL_TOPOLOGY_GATE_CHK1 check (GATE_KIND in ('RECEIVING', 'SHIPPING', 'BOTH')),
      constraint RRL_TOPOLOGY_GATE_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_TOPOLOGY_CELL_GATE_DIST', q'[
    create table RRL_TOPOLOGY_CELL_GATE_DIST (
      CELL_GATE_DISTANCE_ID number not null,
      TOPOLOGY_ID number not null,
      TOPOLOGY_CELL_ID number not null,
      TOPOLOGY_GATE_ID number not null,
      FLOW_KIND varchar2(20) default 'BOTH' not null,
      DISTANCE_M number not null,
      TRAVEL_TIME_SEC number,
      ROUTE_KIND varchar2(30) default 'TOPOLOGY_ESTIMATE' not null,
      CALC_METHOD varchar2(30) default 'MANHATTAN' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPO_CELL_GATE_DIST_PK primary key (CELL_GATE_DISTANCE_ID),
      constraint RRL_TOPO_CELL_GATE_DIST_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPO_CELL_GATE_DIST_FK2 foreign key (TOPOLOGY_CELL_ID) references RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID),
      constraint RRL_TOPO_CELL_GATE_DIST_FK3 foreign key (TOPOLOGY_GATE_ID) references RRL_TOPOLOGY_GATE (TOPOLOGY_GATE_ID),
      constraint RRL_TOPO_CELL_GATE_DIST_U1 unique (TOPOLOGY_CELL_ID, TOPOLOGY_GATE_ID, FLOW_KIND),
      constraint RRL_TOPO_CELL_GATE_DIST_CHK1 check (FLOW_KIND in ('INBOUND', 'OUTBOUND', 'BOTH')),
      constraint RRL_TOPO_CELL_GATE_DIST_CHK2 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_sequence('RRL_TOPOLOGY_GATE_SQ',
    'create sequence RRL_TOPOLOGY_GATE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPO_CELL_GATE_DIST_SQ',
    'create sequence RRL_TOPO_CELL_GATE_DIST_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_TOPOLOGY_GATE_I1',
    'create index RRL_TOPOLOGY_GATE_I1 on RRL_TOPOLOGY_GATE (TOPOLOGY_ID, GATE_KIND, ACTIVE)');
  ensure_index('RRL_TOPO_CELL_GATE_DIST_I1',
    'create index RRL_TOPO_CELL_GATE_DIST_I1 on RRL_TOPOLOGY_CELL_GATE_DIST (TOPOLOGY_ID, TOPOLOGY_CELL_ID, ACTIVE)');
  ensure_index('RRL_TOPO_CELL_GATE_DIST_I2',
    'create index RRL_TOPO_CELL_GATE_DIST_I2 on RRL_TOPOLOGY_CELL_GATE_DIST (TOPOLOGY_ID, TOPOLOGY_GATE_ID, FLOW_KIND, ACTIVE)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-20-039-topology-gate-distance-matrix' migration_id,
         'Topology gates and cell-to-gate distance matrix for inbound and outbound travel-time planning' description,
         '039_apply.sql' script_name,
         '039_rollback.sql' rollback_script
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

prompt [migration 2026-05-20-039] apply done
