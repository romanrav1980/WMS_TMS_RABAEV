from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import CustomerAddressCreateRequest, CustomerCreateRequest, CustomerUpdateRequest


def _trim_text(value: Any, max_len: int, upper: bool = False) -> str | None:
    if value is None:
        return None
    text = str(value)[:max_len]
    return text.upper() if upper else text


class CustomerOrderService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def list_customers(self, search: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if search:
            conditions.append(
                "("
                "upper(c.CUSTOMER_CODE) like :search "
                "or upper(c.CUSTOMER_NAME) like :search "
                "or upper(nvl(m.LEGACY_ADDR, '')) like :search"
                ")"
            )
            params["search"] = f"%{search.upper()}%"
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select c.CUSTOMER_ID,
                       c.CUSTOMER_CODE,
                       c.CUSTOMER_NAME,
                       c.CUSTOMER_TYPE,
                       c.INN,
                       c.KPP,
                       c.GLN,
                       c.EDI_ID,
                       c.ACTIVE,
                       m.LEGACY_ADDR,
                       m.STORE_CODE,
                       m.STORE_NAME,
                       m.ADDRESS_TEXT,
                       c.CREATED_AT
                  from RRL_CUSTOMER c
                  left join RRL_CUSTOMER_STORE_MAP m
                    on m.CUSTOMER_ID = c.CUSTOMER_ID
                   and m.ACTIVE = 1
                  {where_sql}
                 order by c.CUSTOMER_NAME, c.CUSTOMER_ID
              )
             where rownum <= :limit
            """,
            params,
        )

    def create_customer(self, request: CustomerCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CUSTOMER_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER (
                CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE,
                INN, KPP, GLN, EDI_ID, DEFAULT_VEHICLE_TYPE_ID,
                SPLIT_ORDER_BY_VEHICLE_CAPACITY,
                DEFAULT_MIN_SHELF_LIFE_DAYS, DEFAULT_MIN_SHELF_LIFE_PERCENT,
                ACTIVE, CREATED_AT, CREATED_BY
              ) values (
                v_id, cast(:customer_code as varchar2(100)), cast(:customer_name as varchar2(255)),
                cast(:customer_type as varchar2(30)), cast(:inn as varchar2(20)),
                cast(:kpp as varchar2(20)), cast(:gln as varchar2(32)), cast(:edi_id as varchar2(100)),
                :default_vehicle_type_id, nvl(:split_order_by_vehicle_capacity, 0),
                :default_min_shelf_life_days, :default_min_shelf_life_percent,
                nvl(:active, 1), sysdate, cast(:created_by as varchar2(50))
              );
              :result := v_id;
            end;
            """,
            {
                **request.model_dump(),
                "customer_code": _trim_text(request.customer_code, 100, upper=True),
                "customer_name": _trim_text(request.customer_name, 255),
                "customer_type": _trim_text(request.customer_type, 30, upper=True),
                "inn": _trim_text(request.inn, 20),
                "kpp": _trim_text(request.kpp, 20),
                "gln": _trim_text(request.gln, 32),
                "edi_id": _trim_text(request.edi_id, 100),
                "created_by": _trim_text(request.created_by, 50),
            },
        )

    def update_customer(self, customer_id: int, request: CustomerUpdateRequest) -> None:
        touched = request.model_fields_set
        params: dict[str, Any] = {
            "customer_id": customer_id,
            "updated_by": (request.updated_by or "api")[:50],
        }
        set_clauses: list[str] = []

        string_fields = {
            "customer_code": ("CUSTOMER_CODE", 100, True),
            "customer_name": ("CUSTOMER_NAME", 255, False),
            "customer_type": ("CUSTOMER_TYPE", 30, True),
            "inn": ("INN", 20, False),
            "kpp": ("KPP", 20, False),
            "gln": ("GLN", 32, False),
            "edi_id": ("EDI_ID", 100, False),
        }
        number_fields = {
            "default_vehicle_type_id": "DEFAULT_VEHICLE_TYPE_ID",
            "split_order_by_vehicle_capacity": "SPLIT_ORDER_BY_VEHICLE_CAPACITY",
            "default_min_shelf_life_days": "DEFAULT_MIN_SHELF_LIFE_DAYS",
            "default_min_shelf_life_percent": "DEFAULT_MIN_SHELF_LIFE_PERCENT",
            "active": "ACTIVE",
        }

        for field_name, (column_name, max_len, should_upper) in string_fields.items():
            if field_name not in touched:
                continue
            value = getattr(request, field_name)
            if value is not None:
                value = str(value)[:max_len]
                if should_upper:
                    value = value.upper()
            params[field_name] = value
            set_clauses.append(f"{column_name} = cast(:{field_name} as varchar2({max_len}))")

        for field_name, column_name in number_fields.items():
            if field_name not in touched:
                continue
            params[field_name] = getattr(request, field_name)
            set_clauses.append(f"{column_name} = :{field_name}")

        set_clauses.append("UPDATED_AT = sysdate")
        set_clauses.append("UPDATED_BY = cast(:updated_by as varchar2(50))")
        set_sql = ",\n                     ".join(set_clauses)
        self.gateway.execute_plsql(
            f"""
            begin
              update RRL_CUSTOMER
                 set {set_sql}
               where CUSTOMER_ID = :customer_id;

              if sql%rowcount = 0 then
                raise_application_error(-20801, 'customer not found');
              end if;
            end;
            """,
            params,
        )

    def create_customer_address(self, customer_id: int, request: CustomerAddressCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            declare
              v_id number;
            begin
              select RRL_CUSTOMER_ADDRESS_SQ.nextval into v_id from dual;
              insert into RRL_CUSTOMER_ADDRESS (
                CUSTOMER_ADDRESS_ID, CUSTOMER_ID, ADDRESS_TYPE, ADDRESS_TEXT,
                CITY, REGION, POSTAL_CODE, GLN, ACTIVE, CREATED_AT, CREATED_BY
              ) values (
                v_id, :customer_id, cast(:address_type as varchar2(30)), cast(:address_text as varchar2(1000)),
                cast(:city as varchar2(100)), cast(:region as varchar2(100)), cast(:postal_code as varchar2(20)),
                cast(:gln as varchar2(32)), nvl(:active, 1), sysdate, cast(:created_by as varchar2(50))
              );
              :result := v_id;
            end;
            """,
            {
                "customer_id": customer_id,
                **request.model_dump(),
                "address_type": _trim_text(request.address_type, 30, upper=True),
                "address_text": _trim_text(request.address_text, 1000),
                "city": _trim_text(request.city, 100),
                "region": _trim_text(request.region, 100),
                "postal_code": _trim_text(request.postal_code, 20),
                "gln": _trim_text(request.gln, 32),
                "created_by": _trim_text(request.created_by, 50),
            },
        )

    def get_customer(self, customer_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select c.CUSTOMER_ID,
                   c.CUSTOMER_CODE,
                   c.CUSTOMER_NAME,
                   c.CUSTOMER_TYPE,
                   c.INN,
                   c.KPP,
                   c.GLN,
                   c.EDI_ID,
                   c.DEFAULT_VEHICLE_TYPE_ID,
                   c.SPLIT_ORDER_BY_VEHICLE_CAPACITY,
                   c.DEFAULT_MIN_SHELF_LIFE_DAYS,
                   c.DEFAULT_MIN_SHELF_LIFE_PERCENT,
                   c.ACTIVE,
                   c.CREATED_AT,
                   c.UPDATED_AT
              from RRL_CUSTOMER c
             where c.CUSTOMER_ID = :customer_id
            """,
            {"customer_id": customer_id},
        )
        if not rows:
            return None
        customer = rows[0]
        customer["addresses"] = self.gateway.fetch_all(
            """
            select CUSTOMER_ADDRESS_ID,
                   ADDRESS_TYPE,
                   ADDRESS_TEXT,
                   CITY,
                   REGION,
                   POSTAL_CODE,
                   GLN,
                   ACTIVE
              from RRL_CUSTOMER_ADDRESS
             where CUSTOMER_ID = :customer_id
             order by ADDRESS_TYPE, CUSTOMER_ADDRESS_ID
            """,
            {"customer_id": customer_id},
        )
        customer["legacy_mappings"] = self.gateway.fetch_all(
            """
            select CUSTOMER_STORE_MAP_ID,
                   LEGACY_ADDR,
                   STORE_CODE,
                   STORE_NAME,
                   ADDRESS_TEXT,
                   DEFAULT_ROUTE_ID,
                   DEFAULT_DOCK_ID,
                   ACTIVE
              from RRL_CUSTOMER_STORE_MAP
             where CUSTOMER_ID = :customer_id
             order by CUSTOMER_STORE_MAP_ID
            """,
            {"customer_id": customer_id},
        )
        return customer

    def list_customer_orders(
        self,
        status: str | None = None,
        order_no: str | None = None,
        legacy_order_id: int | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}
        if status:
            conditions.append("upper(co.STATUS) = :status")
            params["status"] = status.upper()
        if order_no:
            conditions.append("upper(co.ORDER_NO) like :order_no")
            params["order_no"] = f"%{order_no.upper()}%"
        if legacy_order_id is not None:
            conditions.append("co.LEGACY_ORDER_ID = :legacy_order_id")
            params["legacy_order_id"] = legacy_order_id
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select co.CUSTOMER_ORDER_ID,
                       co.LEGACY_ORDER_ID,
                       co.ORDER_NO,
                       co.STATUS,
                       co.WARE_ID,
                       co.ORDER_DATE,
                       co.SHIPMENT_DATE,
                       c.CUSTOMER_ID,
                       c.CUSTOMER_NAME,
                       m.LEGACY_ADDR,
                       count(r.CUSTOMER_ORDER_ROW_ID) ROW_COUNT,
                       nvl(sum(r.ORDER_QTY), 0) TOTAL_ORDER_QTY,
                       nvl(sum(r.PACK_COUNT), 0) TOTAL_PACK_COUNT,
                       co.CREATED_AT
                  from RRL_CUSTOMER_ORDER co
                  join RRL_CUSTOMER c
                    on c.CUSTOMER_ID = co.CUSTOMER_ID
                  left join RRL_CUSTOMER_STORE_MAP m
                    on m.CUSTOMER_STORE_MAP_ID = co.CUSTOMER_STORE_MAP_ID
                  left join RRL_CUSTOMER_ORDER_ROW r
                    on r.CUSTOMER_ORDER_ID = co.CUSTOMER_ORDER_ID
                  {where_sql}
                 group by co.CUSTOMER_ORDER_ID,
                          co.LEGACY_ORDER_ID,
                          co.ORDER_NO,
                          co.STATUS,
                          co.WARE_ID,
                          co.ORDER_DATE,
                          co.SHIPMENT_DATE,
                          c.CUSTOMER_ID,
                          c.CUSTOMER_NAME,
                          m.LEGACY_ADDR,
                          co.CREATED_AT
                 order by co.CUSTOMER_ORDER_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def get_customer_order(self, customer_order_id: int) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select co.CUSTOMER_ORDER_ID,
                   co.LEGACY_ORDER_ID,
                   co.ORDER_NO,
                   co.STATUS,
                   co.WARE_ID,
                   co.ORDER_DATE,
                   co.SHIPMENT_DATE,
                   co.ROUTE_ID,
                   co.DOCK_ID,
                   c.CUSTOMER_ID,
                   c.CUSTOMER_NAME,
                   m.CUSTOMER_STORE_MAP_ID,
                   m.LEGACY_ADDR,
                   m.ADDRESS_TEXT,
                   co.CREATED_AT,
                   co.UPDATED_AT
              from RRL_CUSTOMER_ORDER co
              join RRL_CUSTOMER c
                on c.CUSTOMER_ID = co.CUSTOMER_ID
              left join RRL_CUSTOMER_STORE_MAP m
                on m.CUSTOMER_STORE_MAP_ID = co.CUSTOMER_STORE_MAP_ID
             where co.CUSTOMER_ORDER_ID = :customer_order_id
            """,
            {"customer_order_id": customer_order_id},
        )
        if not rows:
            return None
        order = rows[0]
        order["rows"] = self.gateway.fetch_all(
            """
            select CUSTOMER_ORDER_ROW_ID,
                   LEGACY_ORDER_ROW_ID,
                   LINE_NO,
                   ARTICUL,
                   PRODUCT_NAME,
                   UNIT_CODE,
                   ORDER_QTY,
                   ORDER_WEIGHT,
                   PACK_COUNT,
                   WARE_ID,
                   MOD_ID,
                   STATUS
              from RRL_CUSTOMER_ORDER_ROW
             where CUSTOMER_ORDER_ID = :customer_order_id
             order by LINE_NO, CUSTOMER_ORDER_ROW_ID
            """,
            {"customer_order_id": customer_order_id},
        )
        return order

    def import_legacy_order(self, legacy_order_id: int, created_by: str | None = None) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_CUSTOMER_ORDER_API.import_legacy_order(
                p_legacy_order_id => :legacy_order_id,
                p_created_by => :created_by
              );
            end;
            """,
            {"legacy_order_id": legacy_order_id, "created_by": created_by},
        )

    def get_fulfillment(self, customer_order_id: int) -> list[dict[str, Any]]:
        return self.gateway.fetch_all(
            """
            select FULFILLMENT_ID,
                   CUSTOMER_ORDER_ID,
                   LEGACY_SBORKA_PALLET_ID,
                   PALLET_UID,
                   ADDRESS_TEXT,
                   STATUS,
                   FACT_QTY,
                   FACT_WEIGHT,
                   SOURCE_SYSTEM,
                   CREATED_AT
              from RRL_CUSTOMER_ORDER_FULFILLMENT
             where CUSTOMER_ORDER_ID = :customer_order_id
             order by FULFILLMENT_ID
            """,
            {"customer_order_id": customer_order_id},
        )
