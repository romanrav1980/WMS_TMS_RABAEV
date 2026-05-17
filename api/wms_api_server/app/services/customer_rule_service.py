from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import (
    CustomerProductRuleCreateRequest,
    CustomerShelfLifeRuleCreateRequest,
    CustomerStackRuleCreateRequest,
    CustomerVehicleRuleCreateRequest,
    VehicleTypeCreateRequest,
)


def _trim_text(value: Any, max_len: int, upper: bool = False) -> str | None:
    if value is None:
        return None
    text = str(value)[:max_len]
    return text.upper() if upper else text


class CustomerRuleService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_product_rules(self, customer_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select CUSTOMER_PRODUCT_RULE_ID,
                   CUSTOMER_ID,
                   CUSTOMER_STORE_MAP_ID,
                   ARTICUL,
                   PRODUCT_GROUP,
                   MIN_SHELF_LIFE_DAYS,
                   MIN_SHELF_LIFE_PERCENT,
                   PALLET_CASE_QTY,
                   PALLET_LAYER_QTY,
                   PALLET_LAYER_COUNT,
                   MAX_PALLET_WEIGHT,
                   MAX_PALLET_VOLUME,
                   MAX_PALLET_HEIGHT,
                   PALLET_TYPE,
                   ALLOW_TOP_STACKING,
                   MUST_BE_SEPARATE_PALLET,
                   STACK_COMPATIBILITY_GROUP,
                   RULE_PRIORITY,
                   ACTIVE,
                   VALID_FROM,
                   VALID_TO,
                   CREATED_AT
              from RRL_CUSTOMER_PRODUCT_RULE
             where CUSTOMER_ID = :customer_id
             order by RULE_PRIORITY, CUSTOMER_PRODUCT_RULE_ID
            """,
            {"customer_id": customer_id},
        )

    def create_product_rule(self, customer_id: int, request: CustomerProductRuleCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CUSTOMER_PRODUCT_RULE_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER_PRODUCT_RULE (
                CUSTOMER_PRODUCT_RULE_ID, CUSTOMER_ID, CUSTOMER_STORE_MAP_ID,
                ARTICUL, PRODUCT_GROUP, MIN_SHELF_LIFE_DAYS,
                MIN_SHELF_LIFE_PERCENT, PALLET_CASE_QTY, PALLET_LAYER_QTY,
                PALLET_LAYER_COUNT, MAX_PALLET_WEIGHT, MAX_PALLET_VOLUME,
                MAX_PALLET_HEIGHT, PALLET_TYPE, ALLOW_TOP_STACKING,
                MUST_BE_SEPARATE_PALLET, STACK_COMPATIBILITY_GROUP,
                RULE_PRIORITY, ACTIVE, VALID_FROM, VALID_TO, CREATED_AT, CREATED_BY
              ) values (
                v_id, :customer_id, :customer_store_map_id,
                cast(:articul as varchar2(40)), cast(:product_group as varchar2(100)),
                :min_shelf_life_days, :min_shelf_life_percent,
                :pallet_case_qty, :pallet_layer_qty, :pallet_layer_count,
                :max_pallet_weight, :max_pallet_volume, :max_pallet_height,
                cast(:pallet_type as varchar2(50)), :allow_top_stacking,
                :must_be_separate_pallet, cast(:stack_compatibility_group as varchar2(100)),
                :rule_priority, :active, nvl(:valid_from, trunc(sysdate)),
                :valid_to, sysdate, cast(:created_by as varchar2(50))
              );
              :result := v_id;
            end;
            """,
            {
                "customer_id": customer_id,
                **request.model_dump(),
                "articul": _trim_text(request.articul, 40, upper=True),
                "product_group": _trim_text(request.product_group, 100),
                "pallet_type": _trim_text(request.pallet_type, 50),
                "stack_compatibility_group": _trim_text(request.stack_compatibility_group, 100),
                "created_by": _trim_text(request.created_by, 50),
            },
        )

    def list_shelf_life_rules(self, customer_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select SHELF_LIFE_RULE_ID,
                   CUSTOMER_ID,
                   CUSTOMER_STORE_MAP_ID,
                   ARTICUL,
                   PRODUCT_GROUP,
                   MIN_SHELF_LIFE_DAYS,
                   MIN_SHELF_LIFE_PERCENT,
                   RULE_PRIORITY,
                   ACTIVE,
                   VALID_FROM,
                   VALID_TO,
                   CREATED_AT
              from RRL_CUSTOMER_SHELF_LIFE_RULE
             where CUSTOMER_ID = :customer_id
             order by RULE_PRIORITY, SHELF_LIFE_RULE_ID
            """,
            {"customer_id": customer_id},
        )

    def create_shelf_life_rule(self, customer_id: int, request: CustomerShelfLifeRuleCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CSL_RULE_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER_SHELF_LIFE_RULE (
                SHELF_LIFE_RULE_ID, CUSTOMER_ID, CUSTOMER_STORE_MAP_ID,
                ARTICUL, PRODUCT_GROUP, MIN_SHELF_LIFE_DAYS,
                MIN_SHELF_LIFE_PERCENT, RULE_PRIORITY, ACTIVE,
                VALID_FROM, VALID_TO, CREATED_AT, CREATED_BY
              ) values (
                v_id, :customer_id, :customer_store_map_id,
                cast(:articul as varchar2(40)), cast(:product_group as varchar2(100)),
                :min_shelf_life_days, :min_shelf_life_percent,
                :rule_priority, :active, nvl(:valid_from, trunc(sysdate)),
                :valid_to, sysdate, cast(:created_by as varchar2(50))
              );
              :result := v_id;
            end;
            """,
            {
                "customer_id": customer_id,
                **request.model_dump(),
                "articul": _trim_text(request.articul, 40, upper=True),
                "product_group": _trim_text(request.product_group, 100),
                "created_by": _trim_text(request.created_by, 50),
            },
        )

    def list_stack_rules(self, customer_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select STACK_RULE_ID,
                   CUSTOMER_ID,
                   CUSTOMER_STORE_MAP_ID,
                   ARTICUL,
                   PRODUCT_GROUP,
                   PALLET_CASE_QTY,
                   PALLET_LAYER_QTY,
                   PALLET_LAYER_COUNT,
                   MAX_PALLET_WEIGHT,
                   MAX_PALLET_VOLUME,
                   MAX_PALLET_HEIGHT,
                   PALLET_TYPE,
                   ALLOW_TOP_STACKING,
                   MUST_BE_SEPARATE_PALLET,
                   STACK_COMPATIBILITY_GROUP,
                   RULE_PRIORITY,
                   ACTIVE,
                   VALID_FROM,
                   VALID_TO,
                   CREATED_AT
              from RRL_CUSTOMER_PRODUCT_STACK_RULE
             where CUSTOMER_ID = :customer_id
             order by RULE_PRIORITY, STACK_RULE_ID
            """,
            {"customer_id": customer_id},
        )

    def create_stack_rule(self, customer_id: int, request: CustomerStackRuleCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CPS_RULE_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER_PRODUCT_STACK_RULE (
                STACK_RULE_ID, CUSTOMER_ID, CUSTOMER_STORE_MAP_ID,
                ARTICUL, PRODUCT_GROUP, PALLET_CASE_QTY, PALLET_LAYER_QTY,
                PALLET_LAYER_COUNT, MAX_PALLET_WEIGHT, MAX_PALLET_VOLUME,
                MAX_PALLET_HEIGHT, PALLET_TYPE, ALLOW_TOP_STACKING,
                MUST_BE_SEPARATE_PALLET, STACK_COMPATIBILITY_GROUP,
                RULE_PRIORITY, ACTIVE, VALID_FROM, VALID_TO, CREATED_AT, CREATED_BY
              ) values (
                v_id, :customer_id, :customer_store_map_id,
                cast(:articul as varchar2(40)), cast(:product_group as varchar2(100)),
                :pallet_case_qty, :pallet_layer_qty, :pallet_layer_count,
                :max_pallet_weight, :max_pallet_volume, :max_pallet_height,
                cast(:pallet_type as varchar2(50)), :allow_top_stacking,
                :must_be_separate_pallet, cast(:stack_compatibility_group as varchar2(100)),
                :rule_priority, :active, nvl(:valid_from, trunc(sysdate)),
                :valid_to, sysdate, cast(:created_by as varchar2(50))
              );
              :result := v_id;
            end;
            """,
            {
                "customer_id": customer_id,
                **request.model_dump(),
                "articul": _trim_text(request.articul, 40, upper=True),
                "product_group": _trim_text(request.product_group, 100),
                "pallet_type": _trim_text(request.pallet_type, 50),
                "stack_compatibility_group": _trim_text(request.stack_compatibility_group, 100),
                "created_by": _trim_text(request.created_by, 50),
            },
        )

    def list_vehicle_rules(self, customer_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select r.CUSTOMER_VEHICLE_RULE_ID,
                   r.CUSTOMER_ID,
                   r.CUSTOMER_STORE_MAP_ID,
                   r.VEHICLE_TYPE_ID,
                   vt.VEHICLE_TYPE_CODE,
                   vt.VEHICLE_TYPE_NAME,
                   r.MAX_PALLET_COUNT,
                   r.MAX_WEIGHT,
                   r.MAX_VOLUME,
                   r.SPLIT_ORDER_BY_CAPACITY,
                   r.RULE_PRIORITY,
                   r.ACTIVE,
                   r.VALID_FROM,
                   r.VALID_TO,
                   r.CREATED_AT
              from RRL_CUSTOMER_VEHICLE_RULE r
              join RRL_VEHICLE_TYPE vt
                on vt.VEHICLE_TYPE_ID = r.VEHICLE_TYPE_ID
             where r.CUSTOMER_ID = :customer_id
             order by r.RULE_PRIORITY, r.CUSTOMER_VEHICLE_RULE_ID
            """,
            {"customer_id": customer_id},
        )

    def create_vehicle_rule(self, customer_id: int, request: CustomerVehicleRuleCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CVR_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER_VEHICLE_RULE (
                CUSTOMER_VEHICLE_RULE_ID, CUSTOMER_ID, CUSTOMER_STORE_MAP_ID,
                VEHICLE_TYPE_ID, MAX_PALLET_COUNT, MAX_WEIGHT, MAX_VOLUME,
                SPLIT_ORDER_BY_CAPACITY, RULE_PRIORITY, ACTIVE,
                VALID_FROM, VALID_TO, CREATED_AT, CREATED_BY
              ) values (
                v_id, :customer_id, :customer_store_map_id,
                :vehicle_type_id, :max_pallet_count, :max_weight, :max_volume,
                :split_order_by_capacity, :rule_priority, :active,
                nvl(:valid_from, trunc(sysdate)), :valid_to,
                sysdate, substr(:created_by, 1, 50)
              );
              :result := v_id;
            end;
            """,
            {"customer_id": customer_id, **request.model_dump()},
        )

    def list_vehicle_types(self, active_only: int | None = None) -> list[dict[str, Any]]:
        where_sql = " where ACTIVE = 1" if active_only is not None and int(active_only) == 1 else ""
        return self.gateway.fetch_all(
            f"""
            select VEHICLE_TYPE_ID,
                   VEHICLE_TYPE_CODE,
                   VEHICLE_TYPE_NAME,
                   MAX_PALLET_COUNT,
                   MAX_WEIGHT,
                   MAX_VOLUME,
                   ACTIVE,
                   CREATED_AT,
                   UPDATED_AT
              from RRL_VEHICLE_TYPE
              {where_sql}
             order by VEHICLE_TYPE_CODE
            """
        )

    def create_vehicle_type(self, request: VehicleTypeCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              begin
                select VEHICLE_TYPE_ID
                  into v_id
                  from RRL_VEHICLE_TYPE
                 where upper(VEHICLE_TYPE_CODE) = upper(:vehicle_type_code);

                update RRL_VEHICLE_TYPE
                   set VEHICLE_TYPE_NAME = substr(:vehicle_type_name, 1, 255),
                       MAX_PALLET_COUNT = :max_pallet_count,
                       MAX_WEIGHT = :max_weight,
                       MAX_VOLUME = :max_volume,
                       ACTIVE = :active,
                       UPDATED_AT = sysdate,
                       UPDATED_BY = substr(:created_by, 1, 50)
                 where VEHICLE_TYPE_ID = v_id;
              exception
                when no_data_found then
                  select RRL_VEHICLE_TYPE_SQ.nextval into v_id from dual;
                  insert into RRL_VEHICLE_TYPE (
                    VEHICLE_TYPE_ID, VEHICLE_TYPE_CODE, VEHICLE_TYPE_NAME,
                    MAX_PALLET_COUNT, MAX_WEIGHT, MAX_VOLUME,
                    ACTIVE, CREATED_AT, CREATED_BY
                  ) values (
                    v_id, upper(substr(:vehicle_type_code, 1, 50)),
                    substr(:vehicle_type_name, 1, 255),
                    :max_pallet_count, :max_weight, :max_volume,
                    :active, sysdate, substr(:created_by, 1, 50)
                  );
              end;
              :result := v_id;
            end;
            """,
            request.model_dump(),
        )
