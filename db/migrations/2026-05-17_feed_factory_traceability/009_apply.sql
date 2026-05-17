prompt [migration 2026-05-17-009] BOM production block - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
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
  ensure_table('RRL_BOM', q'[
    create table RRL_BOM (
      BOM_ID number not null,
      BOM_CODE varchar2(100) not null,
      BOM_NAME varchar2(255),
      TARGET_ARTICUL varchar2(40) not null,
      TARGET_MOD_ID number,
      TARGET_GTIN varchar2(14),
      BOM_KIND varchar2(30) default 'FINISHED_GOODS' not null,
      BASE_QTY number not null,
      BASE_UNIT_CODE varchar2(20) not null,
      IS_PRIMARY number(1) default 0 not null,
      STATUS varchar2(30) default 'DRAFT' not null,
      VALID_FROM date not null,
      VALID_TO date,
      WARE_ID number,
      PRODUCTION_LINE varchar2(100),
      VERSION_NO number default 1 not null,
      PARENT_BOM_ID number,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      APPROVED_AT date,
      APPROVED_BY varchar2(50),
      constraint RRL_BOM_PK primary key (BOM_ID),
      constraint RRL_BOM_U1 unique (BOM_CODE),
      constraint RRL_BOM_FK1 foreign key (PARENT_BOM_ID)
        references RRL_BOM (BOM_ID),
      constraint RRL_BOM_CHK1 check (BOM_KIND in ('FINISHED_GOODS', 'SEMIFINISHED')),
      constraint RRL_BOM_CHK2 check (BASE_QTY > 0),
      constraint RRL_BOM_CHK3 check (IS_PRIMARY in (0, 1)),
      constraint RRL_BOM_CHK4 check (STATUS in ('DRAFT', 'APPROVED', 'ACTIVE', 'BLOCKED', 'ARCHIVED')),
      constraint RRL_BOM_CHK5 check (VALID_TO is null or VALID_TO >= VALID_FROM)
    )
  ]');

  ensure_table('RRL_BOM_LINE', q'[
    create table RRL_BOM_LINE (
      BOM_LINE_ID number not null,
      BOM_ID number not null,
      LINE_NO number not null,
      COMPONENT_TYPE varchar2(30) not null,
      COMPONENT_ARTICUL varchar2(40),
      COMPONENT_MOD_ID number,
      COMPONENT_NAME varchar2(255),
      QTY_PER_BASE number,
      UNIT_CODE varchar2(20),
      LOSS_PERCENT number default 0 not null,
      MIN_TOLERANCE_PCT number,
      MAX_TOLERANCE_PCT number,
      IS_REQUIRED number(1) default 1 not null,
      SUBSTITUTION_GROUP varchar2(100),
      REPLACEMENT_RATIO number,
      COMMENT_TEXT varchar2(1000),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date,
      UPDATED_BY varchar2(50),
      constraint RRL_BOM_LINE_PK primary key (BOM_LINE_ID),
      constraint RRL_BOM_LINE_U1 unique (BOM_ID, LINE_NO),
      constraint RRL_BOM_LINE_FK1 foreign key (BOM_ID)
        references RRL_BOM (BOM_ID),
      constraint RRL_BOM_LINE_CHK1 check (COMPONENT_TYPE in ('RAW', 'SEMIFINISHED', 'PACKAGING', 'ADDITIVE', 'SERVICE')),
      constraint RRL_BOM_LINE_CHK2 check (QTY_PER_BASE is null or QTY_PER_BASE > 0),
      constraint RRL_BOM_LINE_CHK3 check (IS_REQUIRED in (0, 1)),
      constraint RRL_BOM_LINE_CHK4 check (LOSS_PERCENT >= 0)
    )
  ]');

  ensure_table('RRL_BOM_AUDIT', q'[
    create table RRL_BOM_AUDIT (
      BOM_AUDIT_ID number not null,
      BOM_ID number,
      ACTION_TYPE varchar2(50) not null,
      OLD_STATUS varchar2(30),
      NEW_STATUS varchar2(30),
      MESSAGE varchar2(1000),
      PAYLOAD_JSON clob,
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      constraint RRL_BOM_AUDIT_PK primary key (BOM_AUDIT_ID),
      constraint RRL_BOM_AUDIT_FK1 foreign key (BOM_ID)
        references RRL_BOM (BOM_ID)
    )
  ]');

  ensure_sequence('RRL_BOM_SQ', 'create sequence RRL_BOM_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_BOM_LINE_SQ', 'create sequence RRL_BOM_LINE_SQ start with 1 increment by 1 nocache');
  ensure_sequence('RRL_BOM_AUDIT_SQ', 'create sequence RRL_BOM_AUDIT_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_BOM_I1', 'create index RRL_BOM_I1 on RRL_BOM (TARGET_ARTICUL, STATUS, VALID_FROM, VALID_TO)');
  ensure_index('RRL_BOM_I2', 'create index RRL_BOM_I2 on RRL_BOM (TARGET_ARTICUL, IS_PRIMARY, STATUS)');
  ensure_index('RRL_BOM_I3', 'create index RRL_BOM_I3 on RRL_BOM (PARENT_BOM_ID)');
  ensure_index('RRL_BOM_LINE_I1', 'create index RRL_BOM_LINE_I1 on RRL_BOM_LINE (BOM_ID, LINE_NO)');
  ensure_index('RRL_BOM_LINE_I2', 'create index RRL_BOM_LINE_I2 on RRL_BOM_LINE (COMPONENT_ARTICUL, COMPONENT_TYPE)');
  ensure_index('RRL_BOM_AUDIT_I1', 'create index RRL_BOM_AUDIT_I1 on RRL_BOM_AUDIT (BOM_ID, CREATED_AT)');
end;
/

create or replace package RRL_BOM_API as
  function create_bom(
    p_bom_code         varchar2,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default 'FINISHED_GOODS',
    p_base_qty         number,
    p_base_unit_code   varchar2 default 'KG',
    p_is_primary       number default 0,
    p_valid_from       date,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_created_by       varchar2 default null
  ) return number;

  procedure update_bom(
    p_bom_id           number,
    p_bom_code         varchar2 default null,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2 default null,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default null,
    p_base_qty         number default null,
    p_base_unit_code   varchar2 default null,
    p_is_primary       number default null,
    p_valid_from       date default null,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_updated_by       varchar2 default null
  );

  function add_line(
    p_bom_id             number,
    p_line_no            number default null,
    p_component_type     varchar2 default 'RAW',
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default 0,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default 1,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number;

  procedure update_line(
    p_bom_line_id        number,
    p_line_no            number default null,
    p_component_type     varchar2 default null,
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default null,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default null,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_updated_by         varchar2 default null
  );

  procedure delete_line(
    p_bom_line_id number,
    p_deleted_by  varchar2 default null
  );

  procedure approve_bom(
    p_bom_id      number,
    p_approved_by varchar2 default null
  );

  procedure block_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  );

  procedure archive_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  );

  procedure make_primary(
    p_bom_id     number,
    p_updated_by varchar2 default null
  );

  function clone_bom(
    p_source_bom_id number,
    p_bom_code      varchar2,
    p_valid_from    date,
    p_valid_to      date default null,
    p_created_by    varchar2 default null
  ) return number;

  function find_primary_bom(
    p_target_articul  varchar2,
    p_planned_date    date default null,
    p_target_mod_id   number default null,
    p_ware_id         number default null,
    p_production_line varchar2 default null
  ) return number;
end RRL_BOM_API;
/

create or replace package body RRL_BOM_API as
  procedure write_audit(
    p_bom_id       number,
    p_action_type  varchar2,
    p_old_status   varchar2 default null,
    p_new_status   varchar2 default null,
    p_message      varchar2 default null,
    p_payload_json clob default null,
    p_created_by   varchar2 default null
  ) is
    v_id number;
    v_trace_id number;
  begin
    select RRL_BOM_AUDIT_SQ.nextval into v_id from dual;

    insert into RRL_BOM_AUDIT (
      BOM_AUDIT_ID, BOM_ID, ACTION_TYPE, OLD_STATUS, NEW_STATUS,
      MESSAGE, PAYLOAD_JSON, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_bom_id, substr(upper(p_action_type), 1, 50),
      substr(p_old_status, 1, 30), substr(p_new_status, 1, 30),
      substr(p_message, 1, 1000), p_payload_json, sysdate, substr(p_created_by, 1, 50)
    );

    begin
      v_trace_id := RRL_TRACEABILITY_API.add_trace_event(
        p_event_type => p_action_type,
        p_entity_type => 'BOM',
        p_entity_id => to_char(p_bom_id),
        p_source_system => 'WMS_API',
        p_payload_json => p_payload_json,
        p_created_by => p_created_by
      );
    exception
      when others then
        null;
    end;
  end write_audit;

  procedure assert_draft(p_bom_id number) is
    v_status RRL_BOM.STATUS%type;
  begin
    select STATUS into v_status
      from RRL_BOM
     where BOM_ID = p_bom_id;

    if v_status <> 'DRAFT' then
      raise_application_error(-20090, 'BOM can be edited only in DRAFT status.');
    end if;
  exception
    when no_data_found then
      raise_application_error(-20091, 'BOM not found.');
  end assert_draft;

  procedure assert_primary_available(p_bom_id number) is
    v_target_articul RRL_BOM.TARGET_ARTICUL%type;
    v_target_mod_id RRL_BOM.TARGET_MOD_ID%type;
    v_ware_id RRL_BOM.WARE_ID%type;
    v_production_line RRL_BOM.PRODUCTION_LINE%type;
    v_valid_from RRL_BOM.VALID_FROM%type;
    v_valid_to RRL_BOM.VALID_TO%type;
    v_count number;
  begin
    select TARGET_ARTICUL, TARGET_MOD_ID, WARE_ID, PRODUCTION_LINE, VALID_FROM, VALID_TO
      into v_target_articul, v_target_mod_id, v_ware_id, v_production_line, v_valid_from, v_valid_to
      from RRL_BOM
     where BOM_ID = p_bom_id;

    select count(*)
      into v_count
      from RRL_BOM b
     where b.BOM_ID <> p_bom_id
       and b.TARGET_ARTICUL = v_target_articul
       and nvl(b.TARGET_MOD_ID, -1) = nvl(v_target_mod_id, -1)
       and nvl(b.WARE_ID, -1) = nvl(v_ware_id, -1)
       and nvl(upper(b.PRODUCTION_LINE), '~') = nvl(upper(v_production_line), '~')
       and b.IS_PRIMARY = 1
       and b.STATUS in ('APPROVED', 'ACTIVE')
       and nvl(b.VALID_TO, date '2999-12-31') >= v_valid_from
       and nvl(v_valid_to, date '2999-12-31') >= b.VALID_FROM;

    if v_count > 0 then
      raise_application_error(-20092, 'Another primary BOM already exists for this product and period.');
    end if;
  end assert_primary_available;

  procedure validate_period(p_valid_from date, p_valid_to date) is
  begin
    if p_valid_from is null then
      raise_application_error(-20093, 'BOM valid_from is required.');
    end if;
    if p_valid_to is not null and p_valid_to < p_valid_from then
      raise_application_error(-20094, 'BOM valid_to cannot be earlier than valid_from.');
    end if;
  end validate_period;

  procedure validate_line(
    p_component_type varchar2,
    p_component_articul varchar2,
    p_component_name varchar2,
    p_qty_per_base number
  ) is
    v_type varchar2(30) := upper(nvl(p_component_type, 'RAW'));
  begin
    if v_type not in ('RAW', 'SEMIFINISHED', 'PACKAGING', 'ADDITIVE', 'SERVICE') then
      raise_application_error(-20095, 'Unsupported BOM component type.');
    end if;

    if p_component_articul is null and p_component_name is null then
      raise_application_error(-20096, 'BOM line component articul or name is required.');
    end if;

    if v_type <> 'SERVICE' and nvl(p_qty_per_base, 0) <= 0 then
      raise_application_error(-20097, 'BOM material line qty_per_base must be greater than zero.');
    end if;
  end validate_line;

  function create_bom(
    p_bom_code         varchar2,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default 'FINISHED_GOODS',
    p_base_qty         number,
    p_base_unit_code   varchar2 default 'KG',
    p_is_primary       number default 0,
    p_valid_from       date,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_created_by       varchar2 default null
  ) return number is
    v_id number;
    v_code varchar2(100) := upper(trim(p_bom_code));
  begin
    if v_code is null then
      raise_application_error(-20098, 'BOM code is required.');
    end if;
    if p_target_articul is null then
      raise_application_error(-20099, 'Target articul is required.');
    end if;
    if nvl(p_base_qty, 0) <= 0 then
      raise_application_error(-20100, 'BOM base quantity must be greater than zero.');
    end if;
    validate_period(p_valid_from, p_valid_to);

    begin
      select BOM_ID into v_id
        from RRL_BOM
       where BOM_CODE = v_code;
      return v_id;
    exception
      when no_data_found then null;
    end;

    select RRL_BOM_SQ.nextval into v_id from dual;

    insert into RRL_BOM (
      BOM_ID, BOM_CODE, BOM_NAME, TARGET_ARTICUL, TARGET_MOD_ID, TARGET_GTIN,
      BOM_KIND, BASE_QTY, BASE_UNIT_CODE, IS_PRIMARY, STATUS, VALID_FROM,
      VALID_TO, WARE_ID, PRODUCTION_LINE, VERSION_NO, COMMENT_TEXT,
      CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(v_code, 1, 100), substr(p_bom_name, 1, 255),
      substr(upper(trim(p_target_articul)), 1, 40), p_target_mod_id,
      substr(p_target_gtin, 1, 14), substr(upper(nvl(p_bom_kind, 'FINISHED_GOODS')), 1, 30),
      p_base_qty, substr(upper(nvl(p_base_unit_code, 'KG')), 1, 20),
      case when nvl(p_is_primary, 0) = 1 then 1 else 0 end,
      'DRAFT', p_valid_from, p_valid_to, p_ware_id, substr(p_production_line, 1, 100),
      1, substr(p_comment_text, 1, 1000), sysdate, substr(p_created_by, 1, 50)
    );

    write_audit(v_id, 'BOM_CREATED', null, 'DRAFT', 'BOM draft created', null, p_created_by);
    return v_id;
  end create_bom;

  procedure update_bom(
    p_bom_id           number,
    p_bom_code         varchar2 default null,
    p_bom_name         varchar2 default null,
    p_target_articul   varchar2 default null,
    p_target_mod_id    number default null,
    p_target_gtin      varchar2 default null,
    p_bom_kind         varchar2 default null,
    p_base_qty         number default null,
    p_base_unit_code   varchar2 default null,
    p_is_primary       number default null,
    p_valid_from       date default null,
    p_valid_to         date default null,
    p_ware_id          number default null,
    p_production_line  varchar2 default null,
    p_comment_text     varchar2 default null,
    p_updated_by       varchar2 default null
  ) is
    v_valid_from date;
    v_valid_to date;
  begin
    assert_draft(p_bom_id);

    select nvl(p_valid_from, VALID_FROM), nvl(p_valid_to, VALID_TO)
      into v_valid_from, v_valid_to
      from RRL_BOM
     where BOM_ID = p_bom_id;
    validate_period(v_valid_from, v_valid_to);

    update RRL_BOM
       set BOM_CODE = nvl(substr(upper(trim(p_bom_code)), 1, 100), BOM_CODE),
           BOM_NAME = nvl(substr(p_bom_name, 1, 255), BOM_NAME),
           TARGET_ARTICUL = nvl(substr(upper(trim(p_target_articul)), 1, 40), TARGET_ARTICUL),
           TARGET_MOD_ID = nvl(p_target_mod_id, TARGET_MOD_ID),
           TARGET_GTIN = nvl(substr(p_target_gtin, 1, 14), TARGET_GTIN),
           BOM_KIND = nvl(substr(upper(p_bom_kind), 1, 30), BOM_KIND),
           BASE_QTY = nvl(p_base_qty, BASE_QTY),
           BASE_UNIT_CODE = nvl(substr(upper(p_base_unit_code), 1, 20), BASE_UNIT_CODE),
           IS_PRIMARY = nvl(case when p_is_primary is null then null when p_is_primary = 1 then 1 else 0 end, IS_PRIMARY),
           VALID_FROM = v_valid_from,
           VALID_TO = v_valid_to,
           WARE_ID = nvl(p_ware_id, WARE_ID),
           PRODUCTION_LINE = nvl(substr(p_production_line, 1, 100), PRODUCTION_LINE),
           COMMENT_TEXT = nvl(substr(p_comment_text, 1, 1000), COMMENT_TEXT),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where BOM_ID = p_bom_id;

    write_audit(p_bom_id, 'BOM_UPDATED', 'DRAFT', 'DRAFT', 'BOM draft updated', null, p_updated_by);
  end update_bom;

  function add_line(
    p_bom_id             number,
    p_line_no            number default null,
    p_component_type     varchar2 default 'RAW',
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default 0,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default 1,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_created_by         varchar2 default null
  ) return number is
    v_id number;
    v_line_no number;
    v_type varchar2(30) := upper(nvl(p_component_type, 'RAW'));
  begin
    assert_draft(p_bom_id);
    validate_line(v_type, p_component_articul, p_component_name, p_qty_per_base);

    if p_line_no is null then
      select nvl(max(LINE_NO), 0) + 10 into v_line_no
        from RRL_BOM_LINE
       where BOM_ID = p_bom_id;
    else
      v_line_no := p_line_no;
    end if;

    select RRL_BOM_LINE_SQ.nextval into v_id from dual;

    insert into RRL_BOM_LINE (
      BOM_LINE_ID, BOM_ID, LINE_NO, COMPONENT_TYPE, COMPONENT_ARTICUL,
      COMPONENT_MOD_ID, COMPONENT_NAME, QTY_PER_BASE, UNIT_CODE, LOSS_PERCENT,
      MIN_TOLERANCE_PCT, MAX_TOLERANCE_PCT, IS_REQUIRED, SUBSTITUTION_GROUP,
      REPLACEMENT_RATIO, COMMENT_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, p_bom_id, v_line_no, v_type, substr(upper(trim(p_component_articul)), 1, 40),
      p_component_mod_id, substr(p_component_name, 1, 255), p_qty_per_base,
      substr(upper(p_unit_code), 1, 20), nvl(p_loss_percent, 0),
      p_min_tolerance_pct, p_max_tolerance_pct,
      case when nvl(p_is_required, 1) = 1 then 1 else 0 end,
      substr(p_substitution_group, 1, 100), p_replacement_ratio,
      substr(p_comment_text, 1, 1000), sysdate, substr(p_created_by, 1, 50)
    );

    write_audit(p_bom_id, 'BOM_LINE_ADDED', 'DRAFT', 'DRAFT', 'BOM line added', null, p_created_by);
    return v_id;
  end add_line;

  procedure update_line(
    p_bom_line_id        number,
    p_line_no            number default null,
    p_component_type     varchar2 default null,
    p_component_articul  varchar2 default null,
    p_component_mod_id   number default null,
    p_component_name     varchar2 default null,
    p_qty_per_base       number default null,
    p_unit_code          varchar2 default null,
    p_loss_percent       number default null,
    p_min_tolerance_pct  number default null,
    p_max_tolerance_pct  number default null,
    p_is_required        number default null,
    p_substitution_group varchar2 default null,
    p_replacement_ratio  number default null,
    p_comment_text       varchar2 default null,
    p_updated_by         varchar2 default null
  ) is
    v_bom_id number;
    v_type varchar2(30);
    v_articul varchar2(15);
    v_name varchar2(255);
    v_qty number;
  begin
    select BOM_ID into v_bom_id
      from RRL_BOM_LINE
     where BOM_LINE_ID = p_bom_line_id;
    assert_draft(v_bom_id);

    update RRL_BOM_LINE
       set LINE_NO = nvl(p_line_no, LINE_NO),
           COMPONENT_TYPE = nvl(substr(upper(p_component_type), 1, 30), COMPONENT_TYPE),
           COMPONENT_ARTICUL = nvl(substr(upper(trim(p_component_articul)), 1, 40), COMPONENT_ARTICUL),
           COMPONENT_MOD_ID = nvl(p_component_mod_id, COMPONENT_MOD_ID),
           COMPONENT_NAME = nvl(substr(p_component_name, 1, 255), COMPONENT_NAME),
           QTY_PER_BASE = nvl(p_qty_per_base, QTY_PER_BASE),
           UNIT_CODE = nvl(substr(upper(p_unit_code), 1, 20), UNIT_CODE),
           LOSS_PERCENT = nvl(p_loss_percent, LOSS_PERCENT),
           MIN_TOLERANCE_PCT = nvl(p_min_tolerance_pct, MIN_TOLERANCE_PCT),
           MAX_TOLERANCE_PCT = nvl(p_max_tolerance_pct, MAX_TOLERANCE_PCT),
           IS_REQUIRED = nvl(case when p_is_required is null then null when p_is_required = 1 then 1 else 0 end, IS_REQUIRED),
           SUBSTITUTION_GROUP = nvl(substr(p_substitution_group, 1, 100), SUBSTITUTION_GROUP),
           REPLACEMENT_RATIO = nvl(p_replacement_ratio, REPLACEMENT_RATIO),
           COMMENT_TEXT = nvl(substr(p_comment_text, 1, 1000), COMMENT_TEXT),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where BOM_LINE_ID = p_bom_line_id;

    select COMPONENT_TYPE, COMPONENT_ARTICUL, COMPONENT_NAME, QTY_PER_BASE
      into v_type, v_articul, v_name, v_qty
      from RRL_BOM_LINE
     where BOM_LINE_ID = p_bom_line_id;
    validate_line(v_type, v_articul, v_name, v_qty);

    write_audit(v_bom_id, 'BOM_LINE_UPDATED', 'DRAFT', 'DRAFT', 'BOM line updated', null, p_updated_by);
  exception
    when no_data_found then
      raise_application_error(-20101, 'BOM line not found.');
  end update_line;

  procedure delete_line(
    p_bom_line_id number,
    p_deleted_by  varchar2 default null
  ) is
    v_bom_id number;
  begin
    select BOM_ID into v_bom_id
      from RRL_BOM_LINE
     where BOM_LINE_ID = p_bom_line_id;
    assert_draft(v_bom_id);

    delete from RRL_BOM_LINE
     where BOM_LINE_ID = p_bom_line_id;

    write_audit(v_bom_id, 'BOM_LINE_DELETED', 'DRAFT', 'DRAFT', 'BOM line deleted', null, p_deleted_by);
  exception
    when no_data_found then
      raise_application_error(-20101, 'BOM line not found.');
  end delete_line;

  procedure approve_bom(
    p_bom_id      number,
    p_approved_by varchar2 default null
  ) is
    v_line_count number;
    v_is_primary number;
  begin
    assert_draft(p_bom_id);

    select count(*) into v_line_count
      from RRL_BOM_LINE
     where BOM_ID = p_bom_id;
    if v_line_count = 0 then
      raise_application_error(-20102, 'BOM cannot be approved without lines.');
    end if;

    select IS_PRIMARY into v_is_primary
      from RRL_BOM
     where BOM_ID = p_bom_id;
    if v_is_primary = 1 then
      assert_primary_available(p_bom_id);
    end if;

    update RRL_BOM
       set STATUS = 'APPROVED',
           APPROVED_AT = sysdate,
           APPROVED_BY = substr(p_approved_by, 1, 50),
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_approved_by, 1, 50)
     where BOM_ID = p_bom_id;

    write_audit(p_bom_id, 'BOM_APPROVED', 'DRAFT', 'APPROVED', 'BOM approved', null, p_approved_by);
  end approve_bom;

  procedure block_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  ) is
    v_old_status varchar2(30);
  begin
    select STATUS into v_old_status
      from RRL_BOM
     where BOM_ID = p_bom_id;

    update RRL_BOM
       set STATUS = 'BLOCKED',
           IS_PRIMARY = 0,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where BOM_ID = p_bom_id;

    write_audit(p_bom_id, 'BOM_BLOCKED', v_old_status, 'BLOCKED', p_reason, null, p_updated_by);
  exception
    when no_data_found then
      raise_application_error(-20091, 'BOM not found.');
  end block_bom;

  procedure archive_bom(
    p_bom_id     number,
    p_reason     varchar2 default null,
    p_updated_by varchar2 default null
  ) is
    v_old_status varchar2(30);
  begin
    select STATUS into v_old_status
      from RRL_BOM
     where BOM_ID = p_bom_id;

    update RRL_BOM
       set STATUS = 'ARCHIVED',
           IS_PRIMARY = 0,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where BOM_ID = p_bom_id;

    write_audit(p_bom_id, 'BOM_ARCHIVED', v_old_status, 'ARCHIVED', p_reason, null, p_updated_by);
  exception
    when no_data_found then
      raise_application_error(-20091, 'BOM not found.');
  end archive_bom;

  procedure make_primary(
    p_bom_id     number,
    p_updated_by varchar2 default null
  ) is
    v_status varchar2(30);
  begin
    select STATUS into v_status
      from RRL_BOM
     where BOM_ID = p_bom_id;

    if v_status not in ('APPROVED', 'ACTIVE') then
      raise_application_error(-20103, 'Only APPROVED or ACTIVE BOM can be made primary.');
    end if;

    assert_primary_available(p_bom_id);

    update RRL_BOM
       set IS_PRIMARY = 1,
           UPDATED_AT = sysdate,
           UPDATED_BY = substr(p_updated_by, 1, 50)
     where BOM_ID = p_bom_id;

    write_audit(p_bom_id, 'BOM_MADE_PRIMARY', v_status, v_status, 'BOM marked as primary', null, p_updated_by);
  exception
    when no_data_found then
      raise_application_error(-20091, 'BOM not found.');
  end make_primary;

  function clone_bom(
    p_source_bom_id number,
    p_bom_code      varchar2,
    p_valid_from    date,
    p_valid_to      date default null,
    p_created_by    varchar2 default null
  ) return number is
    v_source RRL_BOM%rowtype;
    v_id number;
    v_code varchar2(100) := upper(trim(p_bom_code));
  begin
    if v_code is null then
      raise_application_error(-20098, 'BOM code is required.');
    end if;
    validate_period(p_valid_from, p_valid_to);

    select * into v_source
      from RRL_BOM
     where BOM_ID = p_source_bom_id;

    select RRL_BOM_SQ.nextval into v_id from dual;

    insert into RRL_BOM (
      BOM_ID, BOM_CODE, BOM_NAME, TARGET_ARTICUL, TARGET_MOD_ID, TARGET_GTIN,
      BOM_KIND, BASE_QTY, BASE_UNIT_CODE, IS_PRIMARY, STATUS, VALID_FROM,
      VALID_TO, WARE_ID, PRODUCTION_LINE, VERSION_NO, PARENT_BOM_ID,
      COMMENT_TEXT, CREATED_AT, CREATED_BY
    ) values (
      v_id, substr(v_code, 1, 100), v_source.BOM_NAME, v_source.TARGET_ARTICUL,
      v_source.TARGET_MOD_ID, v_source.TARGET_GTIN, v_source.BOM_KIND,
      v_source.BASE_QTY, v_source.BASE_UNIT_CODE, 0, 'DRAFT',
      p_valid_from, p_valid_to, v_source.WARE_ID, v_source.PRODUCTION_LINE,
      v_source.VERSION_NO + 1, v_source.BOM_ID, v_source.COMMENT_TEXT,
      sysdate, substr(p_created_by, 1, 50)
    );

    insert into RRL_BOM_LINE (
      BOM_LINE_ID, BOM_ID, LINE_NO, COMPONENT_TYPE, COMPONENT_ARTICUL,
      COMPONENT_MOD_ID, COMPONENT_NAME, QTY_PER_BASE, UNIT_CODE, LOSS_PERCENT,
      MIN_TOLERANCE_PCT, MAX_TOLERANCE_PCT, IS_REQUIRED, SUBSTITUTION_GROUP,
      REPLACEMENT_RATIO, COMMENT_TEXT, CREATED_AT, CREATED_BY
    )
    select RRL_BOM_LINE_SQ.nextval, v_id, LINE_NO, COMPONENT_TYPE, COMPONENT_ARTICUL,
           COMPONENT_MOD_ID, COMPONENT_NAME, QTY_PER_BASE, UNIT_CODE, LOSS_PERCENT,
           MIN_TOLERANCE_PCT, MAX_TOLERANCE_PCT, IS_REQUIRED, SUBSTITUTION_GROUP,
           REPLACEMENT_RATIO, COMMENT_TEXT, sysdate, substr(p_created_by, 1, 50)
      from RRL_BOM_LINE
     where BOM_ID = p_source_bom_id;

    write_audit(v_id, 'BOM_CLONED', null, 'DRAFT', 'BOM cloned from ' || p_source_bom_id, null, p_created_by);
    return v_id;
  exception
    when no_data_found then
      raise_application_error(-20091, 'Source BOM not found.');
  end clone_bom;

  function find_primary_bom(
    p_target_articul  varchar2,
    p_planned_date    date default null,
    p_target_mod_id   number default null,
    p_ware_id         number default null,
    p_production_line varchar2 default null
  ) return number is
    v_id number;
    v_date date := nvl(p_planned_date, trunc(sysdate));
  begin
    select BOM_ID
      into v_id
      from (
        select BOM_ID,
               (case when TARGET_MOD_ID = p_target_mod_id then 1 else 0 end) +
               (case when WARE_ID = p_ware_id then 1 else 0 end) +
               (case when upper(PRODUCTION_LINE) = upper(p_production_line) then 1 else 0 end) SPECIFICITY
          from RRL_BOM
         where TARGET_ARTICUL = upper(trim(p_target_articul))
           and IS_PRIMARY = 1
           and STATUS in ('APPROVED', 'ACTIVE')
           and VALID_FROM <= v_date
           and nvl(VALID_TO, date '2999-12-31') >= v_date
           and (p_target_mod_id is null or TARGET_MOD_ID is null or TARGET_MOD_ID = p_target_mod_id)
           and (p_ware_id is null or WARE_ID is null or WARE_ID = p_ware_id)
           and (p_production_line is null or PRODUCTION_LINE is null or upper(PRODUCTION_LINE) = upper(p_production_line))
         order by SPECIFICITY desc, VALID_FROM desc, BOM_ID desc
      )
     where rownum = 1;

    return v_id;
  exception
    when no_data_found then
      return null;
  end find_primary_bom;
end RRL_BOM_API;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'BOM_VIEW' RIGHT1, 'View BOM catalog and recipe calculations' DESCR from dual
    union all
    select 'BOM_EDIT', 'Create and edit BOM drafts' from dual
    union all
    select 'BOM_APPROVE', 'Approve BOM versions' from dual
    union all
    select 'BOM_BLOCK', 'Block or archive BOM versions' from dual
    union all
    select 'BOM_MAKE_PRIMARY', 'Assign primary BOM versions' from dual
    union all
    select 'BOM_USE_ALTERNATIVE', 'Use an alternative BOM for production order creation' from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-009-bom-production-block' migration_id,
         'BOM tables, lifecycle package, calculation API base, and admin rights' description,
         '009_apply.sql' script_name,
         '009_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when not matched then
  insert (MIGRATION_ID, DESCRIPTION, APPLIED_AT, APPLIED_BY, SCRIPT_NAME, ROLLBACK_SCRIPT, STATUS)
  values (s.MIGRATION_ID, s.DESCRIPTION, sysdate, user, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, 'APPLIED');

commit;

prompt [migration 2026-05-17-009] Apply finished. Run 009_verify.sql.
