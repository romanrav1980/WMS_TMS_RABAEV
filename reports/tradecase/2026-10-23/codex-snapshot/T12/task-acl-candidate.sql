select *
              from (
                select TASK_ID, TASK_TYPE, TASK_SOURCE, SOURCE_TASK_ID,
                       SOURCE_MOVEMENT_ID, SOURCE_DOC_TYPE, SOURCE_DOC_ID,
                       PRODUCTION_ORDER_ID, PROD_BATCH_ID, RAW_ARTICUL,
                       TARGET_ARTICUL, UID_PALLET, SSCC, FROM_WARE_ID,
                       FROM_CELL, TO_WARE_ID, TO_CELL, QTY, UNIT_CODE,
                       QTY_MODE, FACT_QTY, PARENT_TASK_ID,
                       to_char(QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY_EXACT,
                       to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,
                       TO_CELL_SLOT_ID, HU_CONTENT_VERSION,
                       (select sl.SLOT_CODE from RRL_TOPOLOGY_CELL_SLOT sl where sl.CELL_SLOT_ID=RRL_WAREHOUSE_TASK.TO_CELL_SLOT_ID) TO_SLOT_CODE,
                       PRIORITY, STATUS, ASSIGNED_TO, RESOURCE_ID,
                       RESOURCE_SESSION_ID, EQUIPMENT_ID,
                       PLANNED_START_AT, PLANNED_FINISH_AT, DISPATCH_PRIORITY,
                       WAIT_PLAN_OPERATION_ID,WAIT_DECISION_OPERATION_ID,WAIT_ST_NUMBER,WAIT_TARGET_TT_ID,
                       CREATED_AT,
                       CREATED_BY, STARTED_AT, FINISHED_AT, CANCELLED_AT,
                       CANCELLED_BY, LAST_ERROR
                  from (select wt.*,wp.PLAN_OPERATION_ID WAIT_PLAN_OPERATION_ID,wr.DECISION_OPERATION_ID WAIT_DECISION_OPERATION_ID,
                         wd.ST_NUMBER WAIT_ST_NUMBER,wd.TARGET_TT_ID WAIT_TARGET_TT_ID
                    from RRL_WAREHOUSE_TASK wt left join RRL_ST_DEFER_WAIT_PLAN wp on wp.TASK_ID=wt.TASK_ID
                    left join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=wp.PLAN_OPERATION_ID
                    left join RRL_ST_DEFER_DECISION wd on wd.OPERATION_ID=wr.DECISION_OPERATION_ID) RRL_WAREHOUSE_TASK
                   where ((FROM_WARE_ID is not null or TO_WARE_ID is not null)
        and (FROM_WARE_ID is null or (select RRL_ACCESS_API.allowed(:view_actor,'warehouse_task_view','WAREHOUSE',to_char(FROM_WARE_ID),ASSIGNED_TO) from dual)=1)
        and (TO_WARE_ID is null or (select RRL_ACCESS_API.allowed(:view_actor,'warehouse_task_view','WAREHOUSE',to_char(TO_WARE_ID),ASSIGNED_TO) from dual)=1))
                 order by case STATUS
                            when 'PLANNED' then 1
                            when 'ASSIGNED' then 2
                            when 'IN_PROGRESS' then 3
                            when 'ERROR' then 4
                            else 9
                          end,
                          PRIORITY,
                          WAIT_PLAN_OPERATION_ID,WAIT_DECISION_OPERATION_ID,WAIT_ST_NUMBER,WAIT_TARGET_TT_ID,
                       CREATED_AT,
                          TASK_ID
              )
             where rownum <= :limit