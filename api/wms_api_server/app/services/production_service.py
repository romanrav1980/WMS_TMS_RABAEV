from typing import Any

from ..oracle_gateway import OracleGateway
from ..schemas import (
    AggregationCreateRequest,
    CrptCodeRequest,
    MercuryBatchRequest,
    PalletAttachRequest,
    ProductionBatchCreate,
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

    def get_batch_status(self, prod_batch_id: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(
            """
            select PROD_BATCH_ID,
                   PROD_BATCH_NO,
                   QUALITY_STATUS,
                   MERCURY_STATUS,
                   CRPT_STATUS,
                   TOTAL_QUANTITY,
                   TOTAL_PACK_COUNT,
                   UPDATED_AT
              from RRL_PROD_BATCH
             where PROD_BATCH_ID = :prod_batch_id
            """,
            {"prod_batch_id": prod_batch_id},
        )
        return rows[0] if rows else {}


def _model_dict(model) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
