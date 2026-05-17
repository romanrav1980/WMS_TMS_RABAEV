from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import (
    AggregationItemRequest,
    AggregationCreateRequest,
    CrptCodeRequest,
    CrptCodeStatusRequest,
    MercuryBatchRequest,
    MercuryOperationCreateRequest,
    MercuryOperationUpdateRequest,
    MercurySiteRequest,
    PalletAttachRequest,
    ProductionBatchCreate,
    RawBatchCreate,
    RawUsageRequest,
)


class ProductionService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def create_batch(self, request: ProductionBatchCreate) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.create_prod_batch(
                p_prod_batch_no => :prod_batch_no,
                p_articul => :articul,
                p_mod_id => :mod_id,
                p_gtin => :gtin,
                p_product_name => :product_name,
                p_total_quantity => :total_quantity,
                p_total_pack_count => :total_pack_count,
                p_unit_code => :unit_code,
                p_ware_id => :ware_id,
                p_source_system => :source_system,
                p_source_message_id => :source_message_id,
                p_external_operation_id => :external_operation_id,
                p_external_batch_id => :external_batch_id,
                p_production_order_id => :production_order_id,
                p_produced_date_from => :produced_date_from,
                p_produced_date_to => :produced_date_to,
                p_expiry_date_from => :expiry_date_from,
                p_expiry_date_to => :expiry_date_to,
                p_production_line => :production_line,
                p_shift_id => :shift_id,
                p_mercury_required => :mercury_required,
                p_crpt_required => :crpt_required,
                p_created_by => :created_by
              );
            end;
            """,
            _model_dict(request),
        )

    def attach_pallet(self, prod_batch_id: int, request: PalletAttachRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PRODUCTION_API.attach_pallet(
                p_prod_batch_id => :prod_batch_id,
                p_uid_pallet => :uid_pallet,
                p_pallet_no => :pallet_no,
                p_quantity => :quantity,
                p_pack_count => :pack_count,
                p_net_weight => :net_weight,
                p_gross_weight => :gross_weight,
                p_sscc => :sscc,
                p_quality_status => :quality_status,
                p_created_by => :created_by
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def create_raw_batch(self, request: RawBatchCreate) -> int:
        raw_params = _model_dict(request)
        raw_batch_id = self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.register_raw_batch(
                p_raw_batch_no => :raw_batch_no,
                p_articul => :articul,
                p_supplier_id => :supplier_id,
                p_producer_name => :producer_name,
                p_quantity_initial => :quantity_initial,
                p_quantity_available => :quantity_available,
                p_unit_code => :unit_code,
                p_ware_id => :ware_id,
                p_mercury_stock_entry_uuid => :mercury_stock_entry_uuid,
                p_mercury_vsd_uuid => :mercury_vsd_uuid,
                p_created_by => :created_by
              );
            end;
            """,
            {
                "raw_batch_no": raw_params["raw_batch_no"],
                "articul": raw_params["articul"],
                "supplier_id": raw_params["supplier_id"],
                "producer_name": raw_params["producer_name"],
                "quantity_initial": raw_params["quantity_initial"],
                "quantity_available": raw_params["quantity_available"],
                "unit_code": raw_params["unit_code"],
                "ware_id": raw_params["ware_id"],
                "mercury_stock_entry_uuid": raw_params["mercury_stock_entry_uuid"],
                "mercury_vsd_uuid": raw_params["mercury_vsd_uuid"],
                "created_by": raw_params["created_by"],
            },
        )
        self.gateway.execute(
            """
            update RRL_RAW_BATCH
               set PRODUCED_DATE_FROM = nvl(:produced_date_from, PRODUCED_DATE_FROM),
                   PRODUCED_DATE_TO = nvl(:produced_date_to, PRODUCED_DATE_TO),
                   EXPIRY_DATE_FROM = nvl(:expiry_date_from, EXPIRY_DATE_FROM),
                   EXPIRY_DATE_TO = nvl(:expiry_date_to, EXPIRY_DATE_TO),
                   MERCURY_SITE_ID = nvl(:mercury_site_id, MERCURY_SITE_ID)
             where RAW_BATCH_ID = :raw_batch_id
            """,
            {
                "raw_batch_id": raw_batch_id,
                "produced_date_from": raw_params["produced_date_from"],
                "produced_date_to": raw_params["produced_date_to"],
                "expiry_date_from": raw_params["expiry_date_from"],
                "expiry_date_to": raw_params["expiry_date_to"],
                "mercury_site_id": raw_params["mercury_site_id"],
            },
        )
        return raw_batch_id

    def add_raw_usage(self, prod_batch_id: int, request: RawUsageRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.add_raw_usage(
                p_prod_batch_id => :prod_batch_id,
                p_raw_batch_id => :raw_batch_id,
                p_raw_articul => :raw_articul,
                p_quantity_planned => :quantity_planned,
                p_quantity_fact => :quantity_fact,
                p_unit_code => :unit_code,
                p_used_by => :used_by
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def add_crpt_code(self, prod_batch_id: int, request: CrptCodeRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.add_crpt_code(
                p_prod_batch_id => :prod_batch_id,
                p_uid_pallet => :uid_pallet,
                p_gtin => :gtin,
                p_cis => :cis,
                p_serial_no => :serial_no,
                p_datamatrix_full => :datamatrix_full,
                p_parent_sscc => :parent_sscc
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def create_aggregation(self, prod_batch_id: int, request: AggregationCreateRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.create_aggregation(
                p_sscc => :sscc,
                p_prod_batch_id => :prod_batch_id,
                p_uid_pallet => :uid_pallet,
                p_parent_sscc => :parent_sscc,
                p_aggregation_level => :aggregation_level
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def add_aggregation_item(self, aggregation_id: int, request: AggregationItemRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PRODUCTION_API.add_aggregation_item(
                p_aggregation_id => :aggregation_id,
                p_child_type => :child_type,
                p_child_cis => :child_cis,
                p_child_sscc => :child_sscc,
                p_gtin => :gtin,
                p_prod_batch_id => :prod_batch_id
              );
            end;
            """,
            {"aggregation_id": aggregation_id, **_model_dict(request)},
        )

    def set_mercury_batch(self, prod_batch_id: int, request: MercuryBatchRequest) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PRODUCTION_API.set_mercury_batch(
                p_prod_batch_id => :prod_batch_id,
                p_mercury_operation_id => :mercury_operation_id,
                p_stock_entry_uuid => :stock_entry_uuid,
                p_stock_entry_guid => :stock_entry_guid,
                p_vet_document_uuid => :vet_document_uuid,
                p_vet_document_status => :vet_document_status,
                p_vet_document_type => :vet_document_type,
                p_vet_document_form => :vet_document_form,
                p_product_item_guid => :product_item_guid,
                p_product_item_name => :product_item_name,
                p_last_error => :last_error
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def upsert_mercury_site(self, request: MercurySiteRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_REGULATORY_API.upsert_mercury_site(
                p_site_code => :site_code,
                p_site_name => :site_name,
                p_ware_id => :ware_id,
                p_enterprise_guid => :enterprise_guid,
                p_enterprise_uuid => :enterprise_uuid,
                p_business_guid => :business_guid,
                p_business_uuid => :business_uuid,
                p_address_text => :address_text,
                p_active => :active,
                p_updated_by => :updated_by
              );
            end;
            """,
            _model_dict(request),
        )

    def create_mercury_operation(
        self, prod_batch_id: int | None, request: MercuryOperationCreateRequest
    ) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_REGULATORY_API.create_mercury_operation(
                p_prod_batch_id => :prod_batch_id,
                p_raw_batch_id => :raw_batch_id,
                p_mercury_site_id => :mercury_site_id,
                p_operation_type => :operation_type,
                p_mercury_operation_id => :mercury_operation_id,
                p_external_operation_id => :external_operation_id,
                p_status => :status,
                p_request_json => :request_json,
                p_created_by => :created_by
              );
            end;
            """,
            {"prod_batch_id": prod_batch_id, **_model_dict(request)},
        )

    def update_mercury_operation(
        self, operation_row_id: int, request: MercuryOperationUpdateRequest
    ) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_REGULATORY_API.update_mercury_operation(
                p_operation_row_id => :operation_row_id,
                p_status => :status,
                p_mercury_operation_id => :mercury_operation_id,
                p_external_operation_id => :external_operation_id,
                p_response_json => :response_json,
                p_last_error => :last_error,
                p_updated_by => :updated_by
              );
            end;
            """,
            {"operation_row_id": operation_row_id, **_model_dict(request)},
        )

    def set_crpt_code_status(self, request: CrptCodeStatusRequest) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_REGULATORY_API.set_crpt_code_status(
                p_cis => :cis,
                p_code_status => :code_status,
                p_event_type => :event_type,
                p_document_id => :document_id,
                p_document_no => :document_no,
                p_payload_json => :payload_json,
                p_error_text => :error_text,
                p_updated_by => :updated_by
              );
            end;
            """,
            _model_dict(request),
        )

    def get_batch_status(self, prod_batch_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select PROD_BATCH_ID,
                   PROD_BATCH_NO,
                   QUALITY_STATUS,
                   AGING_REQUIRED_HOURS,
                   AGING_UNTIL,
                   SHIPMENT_ALLOWED_AT,
                   SHIPMENT_RELEASE_STATUS,
                   SHIPMENT_BLOCK_REASON,
                   SHIPMENT_EFFECTIVE_STATUS,
                   IS_SHIPMENT_ALLOWED,
                   MERCURY_STATUS,
                   CRPT_STATUS,
                   TOTAL_QUANTITY,
                   TOTAL_PACK_COUNT,
                   UPDATED_AT
              from RRL_PROD_BATCH_READY_V
             where PROD_BATCH_ID = :prod_batch_id
            """,
            {"prod_batch_id": prod_batch_id},
        )
        return rows[0] if rows else {}

    def get_regulatory_status(self, prod_batch_id: int) -> dict[str, Any]:
        batch_rows = self.gateway.fetch_all(
            """
            select PROD_BATCH_ID,
                   PROD_BATCH_NO,
                   MERCURY_REQUIRED,
                   CRPT_REQUIRED,
                   MERCURY_STATUS,
                   CRPT_STATUS,
                   MERCURY_SITE_ID,
                   EXPIRY_DATE_FROM,
                   EXPIRY_DATE_TO
              from RRL_PROD_BATCH
             where PROD_BATCH_ID = :prod_batch_id
            """,
            {"prod_batch_id": prod_batch_id},
        )
        if not batch_rows:
            return {}

        mercury_rows = self.gateway.fetch_all(
            """
            select mb.PROD_BATCH_ID,
                   mb.MERCURY_OPERATION_ID,
                   mb.STOCK_ENTRY_UUID,
                   mb.STOCK_ENTRY_GUID,
                   mb.VET_DOCUMENT_UUID,
                   mb.VET_DOCUMENT_STATUS,
                   mb.VET_DOCUMENT_TYPE,
                   mb.VET_DOCUMENT_FORM,
                   mb.PRODUCT_ITEM_GUID,
                   mb.PRODUCT_ITEM_NAME,
                   mb.LAST_ERROR,
                   mb.UPDATED_AT,
                   s.SITE_CODE,
                   s.SITE_NAME
              from RRL_MERCURY_BATCH mb
              left join RRL_MERCURY_SITE s
                on s.MERCURY_SITE_ID = mb.MERCURY_SITE_ID
             where mb.PROD_BATCH_ID = :prod_batch_id
            """,
            {"prod_batch_id": prod_batch_id},
        )
        counts = self.gateway.fetch_all(
            """
            select 'CRPT_CODES' metric, count(*) value
              from RRL_CRPT_CODES
             where PROD_BATCH_ID = :prod_batch_id
            union all
            select 'CRPT_INTRODUCED', count(*)
              from RRL_CRPT_CODES
             where PROD_BATCH_ID = :prod_batch_id
               and INTRODUCED_AT is not null
            union all
            select 'CRPT_WITHDRAWN', count(*)
              from RRL_CRPT_CODES
             where PROD_BATCH_ID = :prod_batch_id
               and WITHDRAWN_AT is not null
            union all
            select 'AGGREGATIONS', count(*)
              from RRL_CRPT_AGGREGATION
             where PROD_BATCH_ID = :prod_batch_id
            union all
            select 'MERCURY_OPERATIONS', count(*)
              from RRL_MERCURY_OPERATION
             where PROD_BATCH_ID = :prod_batch_id
            union all
            select 'OUTBOX_PENDING', count(*)
              from RRL_REGULATORY_OUTBOX
             where PROD_BATCH_ID = :prod_batch_id
               and STATUS = 'PENDING'
            """,
            {"prod_batch_id": prod_batch_id},
        )
        return {
            "batch": batch_rows[0],
            "mercury": mercury_rows[0] if mercury_rows else None,
            "metrics": {row["metric"]: row["value"] for row in counts},
        }

    def list_mercury_sites(self, active: int | None = None) -> list[dict[str, Any]]:
        if active is None:
            return self.gateway.fetch_all(
                """
                select MERCURY_SITE_ID, SITE_CODE, SITE_NAME, WARE_ID,
                       ENTERPRISE_GUID, ENTERPRISE_UUID, BUSINESS_GUID, BUSINESS_UUID,
                       ADDRESS_TEXT, ACTIVE, CREATED_AT, UPDATED_AT
                  from RRL_MERCURY_SITE
                 order by SITE_CODE
                """
            )
        return self.gateway.fetch_all(
            """
            select MERCURY_SITE_ID, SITE_CODE, SITE_NAME, WARE_ID,
                   ENTERPRISE_GUID, ENTERPRISE_UUID, BUSINESS_GUID, BUSINESS_UUID,
                   ADDRESS_TEXT, ACTIVE, CREATED_AT, UPDATED_AT
              from RRL_MERCURY_SITE
             where ACTIVE = :active
             order by SITE_CODE
            """,
            {"active": active},
        )

    def get_raw_batch(self, raw_batch_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select RAW_BATCH_ID, RAW_BATCH_NO, EXTERNAL_RAW_BATCH_ID, ARTICUL,
                   SUPPLIER_ID, PRODUCER_NAME, PRODUCED_DATE_FROM, PRODUCED_DATE_TO,
                   EXPIRY_DATE_FROM, EXPIRY_DATE_TO, QUANTITY_INITIAL,
                   QUANTITY_AVAILABLE, UNIT_CODE, WARE_ID, QUALITY_STATUS,
                   MERCURY_SITE_ID, MERCURY_STOCK_ENTRY_UUID, MERCURY_VSD_UUID,
                   CREATED_AT, CREATED_BY
              from RRL_RAW_BATCH
             where RAW_BATCH_ID = :raw_batch_id
            """,
            {"raw_batch_id": raw_batch_id},
        )
        return rows[0] if rows else {}

    def list_journal(
        self,
        prod_batch_id: int | None = None,
        system_code: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": max(1, min(limit, 500))}
        if prod_batch_id is not None:
            conditions.append("PROD_BATCH_ID = :prod_batch_id")
            params["prod_batch_id"] = prod_batch_id
        if system_code:
            conditions.append("SYSTEM_CODE = :system_code")
            params["system_code"] = system_code
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select JOURNAL_ID, SYSTEM_CODE, ENTITY_TYPE, ENTITY_ID, PROD_BATCH_ID,
                       RAW_BATCH_ID, UID_PALLET, SSCC, OPERATION_TYPE, OLD_STATUS,
                       NEW_STATUS, DOCUMENT_ID, EXTERNAL_OPERATION_ID, MESSAGE,
                       CREATED_AT, CREATED_BY
                  from RRL_REG_OPERATION_JOURNAL
                  {where_sql}
                 order by CREATED_AT desc, JOURNAL_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )

    def list_outbox(
        self,
        status: str | None = None,
        system_code: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions = []
        params: dict[str, Any] = {"limit": max(1, min(limit, 500))}
        if status:
            conditions.append("STATUS = :status")
            params["status"] = status
        if system_code:
            conditions.append("SYSTEM_CODE = :system_code")
            params["system_code"] = system_code
        where_sql = " where " + " and ".join(conditions) if conditions else ""
        return self.gateway.fetch_all(
            f"""
            select *
              from (
                select OUTBOX_ID, SYSTEM_CODE, EVENT_TYPE, PROD_BATCH_ID, UID_PALLET,
                       DOCUMENT_NO, STATUS, TRY_COUNT, LAST_ERROR, CREATED_AT,
                       SENT_AT, ACCEPTED_AT, IDEMPOTENCY_KEY
                  from RRL_REGULATORY_OUTBOX
                  {where_sql}
                 order by CREATED_AT desc, OUTBOX_ID desc
              )
             where rownum <= :limit
            """,
            params,
        )


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
