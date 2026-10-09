create or replace package RRL_MES_PRODUCTION_API as

  function create_order(

    p_order_no           varchar2,

    p_bom_id             number default null,

    p_target_articul     varchar2,

    p_planned_qty        number,

    p_unit_code          varchar2 default 'KG',

    p_ware_id            number default null,

    p_production_line    varchar2 default null,

    p_shift_id           varchar2 default null,

    p_planned_start_at   date default null,

    p_planned_finish_at  date default null,

    p_source_system      varchar2 default null,

    p_source_message_id  varchar2 default null,

    p_idempotency_key    varchar2 default null,

    p_comment_text       varchar2 default null,

    p_created_by         varchar2 default null

  ) return number;



  function issue_raw_to_production(

    p_production_order_id number,

    p_uid_pallet          varchar2 default null,

    p_raw_batch_id        number default null,

    p_raw_articul         varchar2 default null,

    p_quantity            number,

    p_unit_code           varchar2 default 'KG',

    p_source_location     varchar2 default null,

    p_production_location varchar2 default 'MES_PRODUCTION',

    p_created_by          varchar2 default null

  ) return number;



  function complete_order(

    p_production_order_id number,

    p_prod_batch_no       varchar2 default null,

    p_fact_qty            number,

    p_unit_code           varchar2 default 'KG',

    p_pallets_json        clob default null,

    p_idempotency_key     varchar2 default null,

    p_created_by          varchar2 default null

  ) return number;



  procedure apply_mes_movements_to_wms(

    p_production_order_id number,

    p_applied_by          varchar2 default null

  );



  procedure retry_mes_movement(

    p_movement_id number,

    p_updated_by  varchar2 default null

  );

end RRL_MES_PRODUCTION_API;
/

create or replace package RRL_STOCK_MES_MOVEMENT_PLAN authid definer
 accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_MES_MOVEMENT_CORE) as
 function signature(p_m RRL_MES_MOVEMENT%rowtype) return varchar2;
 procedure compile_movements(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
end;
/
