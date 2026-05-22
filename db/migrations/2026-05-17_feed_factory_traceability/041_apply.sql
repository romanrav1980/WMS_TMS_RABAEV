prompt [migration 2026-05-22-041] warehouse map canvas and cell slots - apply

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

  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_constraint(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_constraints
     where constraint_name = upper(p_name);
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
  ensure_column('RRL_TOPOLOGY_CELL', 'SLOT_LAYER_KIND',
    'alter table RRL_TOPOLOGY_CELL add SLOT_LAYER_KIND varchar2(30)');
  ensure_column('RRL_TOPOLOGY_CELL', 'WAREHOUSE_MAP_CAMERA_ID',
    'alter table RRL_TOPOLOGY_CELL add WAREHOUSE_MAP_CAMERA_ID number');
  ensure_column('RRL_PICK_ROUTE_CELL', 'CELL_SLOT_ID',
    'alter table RRL_PICK_ROUTE_CELL add CELL_SLOT_ID number');
  ensure_column('RRL_STOCK_RESERVATION', 'CELL_SLOT_ID',
    'alter table RRL_STOCK_RESERVATION add CELL_SLOT_ID number');
  ensure_column('RRL_WAREHOUSE_TASK', 'FROM_CELL_SLOT_ID',
    'alter table RRL_WAREHOUSE_TASK add FROM_CELL_SLOT_ID number');
  ensure_column('RRL_WAREHOUSE_TASK', 'TO_CELL_SLOT_ID',
    'alter table RRL_WAREHOUSE_TASK add TO_CELL_SLOT_ID number');

  ensure_table('RRL_WAREHOUSE_MAP_CANVAS', q'[
    create table RRL_WAREHOUSE_MAP_CANVAS (
      CANVAS_ID number not null,
      WARE_ID number not null,
      TOPOLOGY_ID number,
      CANVAS_CODE varchar2(80) not null,
      CANVAS_NAME varchar2(200),
      VERSION_NO number default 1 not null,
      STATUS varchar2(20) default 'DRAFT' not null,
      RENDERER_KIND varchar2(20) default 'CANVAS_2D' not null,
      UNIT_CODE varchar2(20) default 'METER' not null,
      GRID_CELL_WIDTH_M number default 1.2 not null,
      GRID_CELL_DEPTH_M number default 0.8 not null,
      LEVELS number default 1 not null,
      VIEWPORT_JSON clob,
      RENDERER_STATE_JSON clob,
      SOURCE_CANVAS_ID number,
      ACTIVE number(1) default 1 not null,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      PUBLISHED_AT date,
      PUBLISHED_BY varchar2(50),
      constraint RRL_WH_MAP_CANVAS_PK primary key (CANVAS_ID),
      constraint RRL_WH_MAP_CANVAS_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_WH_MAP_CANVAS_FK2 foreign key (SOURCE_CANVAS_ID) references RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID),
      constraint RRL_WH_MAP_CANVAS_CHK_STATUS check (STATUS in ('DRAFT', 'VALIDATED', 'PUBLISHED', 'ARCHIVED')),
      constraint RRL_WH_MAP_CANVAS_CHK_RENDER check (RENDERER_KIND in ('CANVAS_2D', 'WEBGL')),
      constraint RRL_WH_MAP_CANVAS_CHK_UNIT check (UNIT_CODE = 'METER'),
      constraint RRL_WH_MAP_CANVAS_CHK_SIZE check (GRID_CELL_WIDTH_M > 0 and GRID_CELL_DEPTH_M > 0 and LEVELS > 0),
      constraint RRL_WH_MAP_CANVAS_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_WAREHOUSE_MAP_CAMERA', q'[
    create table RRL_WAREHOUSE_MAP_CAMERA (
      CAMERA_ID number not null,
      CANVAS_ID number not null,
      WARE_ID number not null,
      CAMERA_CODE varchar2(80) not null,
      CAMERA_NAME varchar2(200) not null,
      CAMERA_KIND varchar2(30) default 'DRY' not null,
      ORIGIN_X_M number default 0 not null,
      ORIGIN_Y_M number default 0 not null,
      ORIGIN_Z_M number default 0 not null,
      WIDTH_M number not null,
      DEPTH_M number not null,
      HEIGHT_M number not null,
      GRID_CELL_WIDTH_M number default 1.2 not null,
      GRID_CELL_DEPTH_M number default 0.8 not null,
      LEVELS number default 1 not null,
      BOUNDARY_JSON clob,
      DEFAULT_PASSAGE_WIDTH_M number default 3 not null,
      DEFAULT_AISLE_SPACING_M number,
      STATUS varchar2(20) default 'DRAFT' not null,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_WH_MAP_CAMERA_PK primary key (CAMERA_ID),
      constraint RRL_WH_MAP_CAMERA_FK1 foreign key (CANVAS_ID) references RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID),
      constraint RRL_WH_MAP_CAMERA_CHK_KIND check (CAMERA_KIND in ('DRY', 'COLD', 'FREEZER', 'DOCK', 'SERVICE', 'MIXED')),
      constraint RRL_WH_MAP_CAMERA_CHK_STATUS check (STATUS in ('DRAFT', 'ACTIVE', 'ARCHIVED')),
      constraint RRL_WH_MAP_CAMERA_CHK_SIZE check (
        WIDTH_M > 0 and DEPTH_M > 0 and HEIGHT_M > 0 and
        GRID_CELL_WIDTH_M > 0 and GRID_CELL_DEPTH_M > 0 and
        LEVELS > 0 and DEFAULT_PASSAGE_WIDTH_M > 0 and
        (DEFAULT_AISLE_SPACING_M is null or DEFAULT_AISLE_SPACING_M > 0)
      ),
      constraint RRL_WH_MAP_CAMERA_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_WAREHOUSE_MAP_OBJECT', q'[
    create table RRL_WAREHOUSE_MAP_OBJECT (
      MAP_OBJECT_ID number not null,
      CANVAS_ID number not null,
      CAMERA_ID number not null,
      TOPOLOGY_CELL_ID number,
      OBJECT_CODE varchar2(100),
      OBJECT_KIND varchar2(40) not null,
      OBJECT_NAME varchar2(200),
      LEVEL_NO number,
      X_M number default 0 not null,
      Y_M number default 0 not null,
      Z_M number default 0 not null,
      WIDTH_M number,
      DEPTH_M number,
      HEIGHT_M number,
      ANGLE_DEG number default 0 not null,
      GEOMETRY_JSON clob,
      STYLE_JSON clob,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_WH_MAP_OBJECT_PK primary key (MAP_OBJECT_ID),
      constraint RRL_WH_MAP_OBJECT_FK1 foreign key (CANVAS_ID) references RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID),
      constraint RRL_WH_MAP_OBJECT_FK2 foreign key (CAMERA_ID) references RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID),
      constraint RRL_WH_MAP_OBJECT_FK_CELL foreign key (TOPOLOGY_CELL_ID) references RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID),
      constraint RRL_WH_MAP_OBJECT_CHK_KIND check (OBJECT_KIND in (
        'CELL_BLOCK', 'WALL', 'COLUMN', 'PASSAGE', 'ZONE', 'LABEL', 'MEASURE', 'DOCK', 'SERVICE', 'BACKGROUND_REF'
      )),
      constraint RRL_WH_MAP_OBJECT_CHK_SIZE check (
        (WIDTH_M is null or WIDTH_M > 0) and
        (DEPTH_M is null or DEPTH_M > 0) and
        (HEIGHT_M is null or HEIGHT_M > 0)
      ),
      constraint RRL_WH_MAP_OBJECT_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_WAREHOUSE_MAP_PASSAGE', q'[
    create table RRL_WAREHOUSE_MAP_PASSAGE (
      PASSAGE_ID number not null,
      CANVAS_ID number not null,
      CAMERA_ID number not null,
      PASSAGE_CODE varchar2(80) not null,
      PASSAGE_NAME varchar2(200),
      PASSAGE_KIND varchar2(40) default 'PICK_AISLE' not null,
      X1_M number default 0 not null,
      Y1_M number default 0 not null,
      Z1_M number default 0 not null,
      X2_M number default 0 not null,
      Y2_M number default 0 not null,
      Z2_M number default 0 not null,
      WIDTH_M number default 3 not null,
      AISLE_SPACING_M number,
      GEOMETRY_JSON clob,
      ALLOWED_RESOURCE_MASK varchar2(200),
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_WH_MAP_PASSAGE_PK primary key (PASSAGE_ID),
      constraint RRL_WH_MAP_PASSAGE_FK1 foreign key (CANVAS_ID) references RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID),
      constraint RRL_WH_MAP_PASSAGE_FK2 foreign key (CAMERA_ID) references RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID),
      constraint RRL_WH_MAP_PASSAGE_CHK_KIND check (PASSAGE_KIND in (
        'PICK_AISLE', 'CROSS_AISLE', 'MAIN_TRANSPORT', 'DOCK_PASSAGE', 'SERVICE'
      )),
      constraint RRL_WH_MAP_PASSAGE_CHK_SIZE check (WIDTH_M > 0 and (AISLE_SPACING_M is null or AISLE_SPACING_M > 0)),
      constraint RRL_WH_MAP_PASSAGE_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_table('RRL_WAREHOUSE_MAP_CAMERA_LINK', q'[
    create table RRL_WAREHOUSE_MAP_CAMERA_LINK (
      CAMERA_LINK_ID number not null,
      CANVAS_ID number not null,
      FROM_CAMERA_ID number not null,
      TO_CAMERA_ID number not null,
      LINK_CODE varchar2(80) not null,
      LINK_KIND varchar2(40) default 'DOOR' not null,
      FROM_POINT_X_M number default 0 not null,
      FROM_POINT_Y_M number default 0 not null,
      FROM_POINT_Z_M number default 0 not null,
      TO_POINT_X_M number default 0 not null,
      TO_POINT_Y_M number default 0 not null,
      TO_POINT_Z_M number default 0 not null,
      DISTANCE_M number default 0 not null,
      TRAVEL_TIME_SEC number,
      DIRECTION_CODE varchar2(20) default 'BOTH' not null,
      ALLOWED_RESOURCE_MASK varchar2(200),
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_WH_MAP_CAMERA_LINK_PK primary key (CAMERA_LINK_ID),
      constraint RRL_WH_MAP_CAMERA_LINK_FK1 foreign key (CANVAS_ID) references RRL_WAREHOUSE_MAP_CANVAS (CANVAS_ID),
      constraint RRL_WH_MAP_CAMERA_LINK_FK2 foreign key (FROM_CAMERA_ID) references RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID),
      constraint RRL_WH_MAP_CAMERA_LINK_FK3 foreign key (TO_CAMERA_ID) references RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID),
      constraint RRL_WH_MAP_LINK_CHK_KIND check (LINK_KIND in ('DOOR', 'CORRIDOR', 'GATE', 'LIFT', 'STAGING_PASSAGE', 'SERVICE')),
      constraint RRL_WH_MAP_LINK_CHK_DIR check (DIRECTION_CODE in ('BOTH', 'FROM_TO', 'TO_FROM')),
      constraint RRL_WH_MAP_LINK_CHK_SIZE check (
        FROM_CAMERA_ID <> TO_CAMERA_ID and
        DISTANCE_M >= 0 and
        (TRAVEL_TIME_SEC is null or TRAVEL_TIME_SEC >= 0)
      ),
      constraint RRL_WH_MAP_LINK_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_constraint('RRL_TOPO_CELL_CHK_SLOT_LAYER',
    q'[alter table RRL_TOPOLOGY_CELL add constraint RRL_TOPO_CELL_CHK_SLOT_LAYER
       check (SLOT_LAYER_KIND is null or SLOT_LAYER_KIND in ('PICK_FACE_SLOT', 'STORAGE_SLOT', 'MIXED'))]');
  ensure_constraint('RRL_TOPO_CELL_UK_SLOT_LAYER',
    'alter table RRL_TOPOLOGY_CELL add constraint RRL_TOPO_CELL_UK_SLOT_LAYER unique (TOPOLOGY_CELL_ID, SLOT_LAYER_KIND)');
  ensure_constraint('RRL_TOPOLOGY_CELL_FK_MAP_CAM',
    'alter table RRL_TOPOLOGY_CELL add constraint RRL_TOPOLOGY_CELL_FK_MAP_CAM foreign key (WAREHOUSE_MAP_CAMERA_ID) references RRL_WAREHOUSE_MAP_CAMERA (CAMERA_ID)');

  ensure_table('RRL_TOPOLOGY_CELL_SLOT', q'[
    create table RRL_TOPOLOGY_CELL_SLOT (
      CELL_SLOT_ID number not null,
      TOPOLOGY_ID number not null,
      TOPOLOGY_CELL_ID number not null,
      PARENT_SLOT_LAYER_KIND varchar2(30) not null,
      SLOT_KIND varchar2(30) not null,
      SLOT_CODE varchar2(100) not null,
      SLOT_NAME varchar2(200),
      FRACTION_COUNT number default 1 not null,
      FRACTION_INDEX number default 1 not null,
      SUB_LEVEL_NO number,
      SUB_COLUMN_NO number,
      PICK_ORDER number,
      STORAGE_ORDER number,
      CAPACITY_QTY number,
      CAPACITY_VOLUME_M3 number,
      CAPACITY_WEIGHT_KG number,
      X_OFFSET_M number default 0 not null,
      Y_OFFSET_M number default 0 not null,
      Z_OFFSET_M number default 0 not null,
      WIDTH_M number,
      DEPTH_M number,
      HEIGHT_M number,
      CANVAS_OBJECT_ID number,
      ACTIVE number(1) default 1 not null,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_TOPO_CELL_SLOT_PK primary key (CELL_SLOT_ID),
      constraint RRL_TOPO_CELL_SLOT_FK1 foreign key (TOPOLOGY_ID) references RRL_WAREHOUSE_TOPOLOGY (TOPOLOGY_ID),
      constraint RRL_TOPO_CELL_SLOT_FK2 foreign key (TOPOLOGY_CELL_ID) references RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID),
      constraint RRL_TOPO_CELL_SLOT_FK_LAYER foreign key (TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND)
        references RRL_TOPOLOGY_CELL (TOPOLOGY_CELL_ID, SLOT_LAYER_KIND),
      constraint RRL_TOPO_CELL_SLOT_FK_OBJECT foreign key (CANVAS_OBJECT_ID) references RRL_WAREHOUSE_MAP_OBJECT (MAP_OBJECT_ID),
      constraint RRL_TOPO_CELL_SLOT_CHK_KIND check (
        PARENT_SLOT_LAYER_KIND in ('PICK_FACE_SLOT', 'STORAGE_SLOT', 'MIXED') and
        SLOT_KIND in ('PICK_FACE_SLOT', 'STORAGE_SLOT') and
        (PARENT_SLOT_LAYER_KIND = 'MIXED' or PARENT_SLOT_LAYER_KIND = SLOT_KIND)
      ),
      constraint RRL_TOPO_CELL_SLOT_CHK_FRACT check (
        FRACTION_COUNT between 1 and 9 and
        FRACTION_INDEX between 1 and FRACTION_COUNT
      ),
      constraint RRL_TOPO_CELL_SLOT_CHK_ORD check (
        (SLOT_KIND = 'PICK_FACE_SLOT' and STORAGE_ORDER is null) or
        (SLOT_KIND = 'STORAGE_SLOT' and PICK_ORDER is null)
      ),
      constraint RRL_TOPO_CELL_SLOT_CHK_SIZE check (
        (WIDTH_M is null or WIDTH_M > 0) and
        (DEPTH_M is null or DEPTH_M > 0) and
        (HEIGHT_M is null or HEIGHT_M > 0) and
        (CAPACITY_QTY is null or CAPACITY_QTY >= 0) and
        (CAPACITY_VOLUME_M3 is null or CAPACITY_VOLUME_M3 >= 0) and
        (CAPACITY_WEIGHT_KG is null or CAPACITY_WEIGHT_KG >= 0)
      ),
      constraint RRL_TOPO_CELL_SLOT_CHK_ACTIVE check (ACTIVE in (0, 1))
    )
  ]');

  ensure_sequence('RRL_WH_MAP_CANVAS_SQ',
    'create sequence RRL_WH_MAP_CANVAS_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_WH_MAP_CAMERA_SQ',
    'create sequence RRL_WH_MAP_CAMERA_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_WH_MAP_OBJECT_SQ',
    'create sequence RRL_WH_MAP_OBJECT_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_WH_MAP_PASSAGE_SQ',
    'create sequence RRL_WH_MAP_PASSAGE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_WH_MAP_CAM_LINK_SQ',
    'create sequence RRL_WH_MAP_CAM_LINK_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_TOPO_CELL_SLOT_SQ',
    'create sequence RRL_TOPO_CELL_SLOT_SQ start with 1 increment by 1 nocache');

  ensure_constraint('RRL_PICK_ROUTE_CELL_FK_SLOT',
    'alter table RRL_PICK_ROUTE_CELL add constraint RRL_PICK_ROUTE_CELL_FK_SLOT foreign key (CELL_SLOT_ID) references RRL_TOPOLOGY_CELL_SLOT (CELL_SLOT_ID)');
  ensure_constraint('RRL_STOCK_RES_FK_CELL_SLOT',
    'alter table RRL_STOCK_RESERVATION add constraint RRL_STOCK_RES_FK_CELL_SLOT foreign key (CELL_SLOT_ID) references RRL_TOPOLOGY_CELL_SLOT (CELL_SLOT_ID)');
  ensure_constraint('RRL_WH_TASK_FK_FROM_SLOT',
    'alter table RRL_WAREHOUSE_TASK add constraint RRL_WH_TASK_FK_FROM_SLOT foreign key (FROM_CELL_SLOT_ID) references RRL_TOPOLOGY_CELL_SLOT (CELL_SLOT_ID)');
  ensure_constraint('RRL_WH_TASK_FK_TO_SLOT',
    'alter table RRL_WAREHOUSE_TASK add constraint RRL_WH_TASK_FK_TO_SLOT foreign key (TO_CELL_SLOT_ID) references RRL_TOPOLOGY_CELL_SLOT (CELL_SLOT_ID)');

  ensure_index('RRL_WH_MAP_CANVAS_UX_CODE',
    q'[create unique index RRL_WH_MAP_CANVAS_UX_CODE on RRL_WAREHOUSE_MAP_CANVAS (
       case when ACTIVE = 1 then WARE_ID end,
       case when ACTIVE = 1 then upper(CANVAS_CODE) end
    )]');
  ensure_index('RRL_WH_MAP_CAMERA_UX_CODE',
    q'[create unique index RRL_WH_MAP_CAMERA_UX_CODE on RRL_WAREHOUSE_MAP_CAMERA (
       case when ACTIVE = 1 then CANVAS_ID end,
       case when ACTIVE = 1 then upper(CAMERA_CODE) end
    )]');
  ensure_index('RRL_WH_MAP_OBJECT_I1',
    'create index RRL_WH_MAP_OBJECT_I1 on RRL_WAREHOUSE_MAP_OBJECT (CANVAS_ID, CAMERA_ID, OBJECT_KIND, ACTIVE)');
  ensure_index('RRL_WH_MAP_PASSAGE_UX_CODE',
    q'[create unique index RRL_WH_MAP_PASSAGE_UX_CODE on RRL_WAREHOUSE_MAP_PASSAGE (
       case when ACTIVE = 1 then CAMERA_ID end,
       case when ACTIVE = 1 then upper(PASSAGE_CODE) end
    )]');
  ensure_index('RRL_WH_MAP_LINK_UX_CODE',
    q'[create unique index RRL_WH_MAP_LINK_UX_CODE on RRL_WAREHOUSE_MAP_CAMERA_LINK (
       case when ACTIVE = 1 then CANVAS_ID end,
       case when ACTIVE = 1 then upper(LINK_CODE) end
    )]');
  ensure_index('RRL_TOPO_CELL_SLOT_UX_CODE',
    q'[create unique index RRL_TOPO_CELL_SLOT_UX_CODE on RRL_TOPOLOGY_CELL_SLOT (
       case when ACTIVE = 1 then TOPOLOGY_ID end,
       case when ACTIVE = 1 then upper(SLOT_CODE) end
    )]');
  ensure_index('RRL_TOPO_CELL_SLOT_UX_POS',
    q'[create unique index RRL_TOPO_CELL_SLOT_UX_POS on RRL_TOPOLOGY_CELL_SLOT (
       case when ACTIVE = 1 then TOPOLOGY_CELL_ID end,
       case when ACTIVE = 1 then SLOT_KIND end,
       case when ACTIVE = 1 then nvl(SUB_LEVEL_NO, -1) end,
       case when ACTIVE = 1 then nvl(SUB_COLUMN_NO, -1) end,
       case when ACTIVE = 1 then FRACTION_INDEX end
    )]');
  ensure_index('RRL_TOPO_CELL_SLOT_I1',
    'create index RRL_TOPO_CELL_SLOT_I1 on RRL_TOPOLOGY_CELL_SLOT (TOPOLOGY_CELL_ID, SLOT_KIND, ACTIVE)');
  ensure_index('RRL_TOPO_CELL_SLOT_I2',
    'create index RRL_TOPO_CELL_SLOT_I2 on RRL_TOPOLOGY_CELL_SLOT (TOPOLOGY_ID, SLOT_KIND, ACTIVE)');
  ensure_index('RRL_PICK_ROUTE_CELL_I_SLOT',
    'create index RRL_PICK_ROUTE_CELL_I_SLOT on RRL_PICK_ROUTE_CELL (CELL_SLOT_ID, ACTIVE)');
  ensure_index('RRL_STOCK_RES_I_CELL_SLOT',
    'create index RRL_STOCK_RES_I_CELL_SLOT on RRL_STOCK_RESERVATION (CELL_SLOT_ID, STATUS)');
  ensure_index('RRL_WH_TASK_I_FROM_SLOT',
    'create index RRL_WH_TASK_I_FROM_SLOT on RRL_WAREHOUSE_TASK (FROM_CELL_SLOT_ID, STATUS)');
  ensure_index('RRL_WH_TASK_I_TO_SLOT',
    'create index RRL_WH_TASK_I_TO_SLOT on RRL_WAREHOUSE_TASK (TO_CELL_SLOT_ID, STATUS)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-22-041-warehouse-map-canvas-slots' migration_id,
         'Saved warehouse map canvas/camera geometry, passages, camera links, and generalized pick/storage child cell slots' description,
         '041_apply.sql' script_name,
         '041_rollback.sql' rollback_script
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

prompt [migration 2026-05-22-041] apply done
