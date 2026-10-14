"""Reuse original SKU-face assignment and extended attributes in one CONFIG UOW."""
from typing import Any
import oracledb
from fastapi import HTTPException
from ....schemas import PickFaceArticulUpsertRequest
from ....transaction_gateway import TransactionGateway
from ...platform.public import stock_configuration_transaction

def _base_assign(bound: TransactionGateway,request: PickFaceArticulUpsertRequest) -> int:
    base_params = {
        "pick_face_articul_id": request.pick_face_articul_id,
        "pick_face_id": request.pick_face_id,
        "articul": request.articul,
        "priority": request.priority,
        "min_qty": request.min_qty,
        "max_qty": request.max_qty,
        "case_pick_enabled": request.case_pick_enabled,
        "active": request.active,
        "valid_from": request.valid_from,
        "valid_to": request.valid_to,
        "updated_by": request.updated_by,
    }
    pick_face_articul_id = bound.call_number_plsql(
        """
        begin
          :result := RRL_PICK_TOPOLOGY_API.assign_articul(
            p_pick_face_articul_id => :pick_face_articul_id,
            p_pick_face_id => :pick_face_id,
            p_articul => :articul,
            p_priority => :priority,
            p_min_qty => :min_qty,
            p_max_qty => :max_qty,
            p_case_pick_enabled => :case_pick_enabled,
            p_active => :active,
            p_valid_from => :valid_from,
            p_valid_to => :valid_to,
            p_updated_by => :updated_by
          );
        end;
        """,
        base_params,
    )
    return pick_face_articul_id

def _extended_attributes(bound: TransactionGateway,pick_face_articul_id: int,request: PickFaceArticulUpsertRequest) -> None:
    bound.execute(
        """
        update RRL_PICK_FACE_ARTICUL
           set USE_ARTICUL_REPLENISH_RULE = case when nvl(:use_articul_replenish_rule, 1) = 0 then 0 else 1 end,
               REPLENISHMENT_METHOD = upper(nvl(:replenishment_method, 'IMMEDIATE')),
               REPLENISHMENT_RELEASE_POLICY = upper(nvl(:replenishment_release_policy, 'LAYER_TRIGGER')),
               REPLENISHMENT_QTY_MODE = upper(nvl(:replenishment_qty_mode, 'FILL_TO_VOLUME')),
               MIN_TRIGGER_BOX_QTY = :min_trigger_box_qty,
               MIN_TRIGGER_LAYER_QTY = :min_trigger_layer_qty,
               SAFETY_LAYER_QTY = :safety_layer_qty,
               BOXES_PER_LAYER = :boxes_per_layer,
               BOXES_PER_PALLET = :boxes_per_pallet,
               BOX_VOLUME_M3 = :box_volume_m3,
               ALLOW_PARTIAL_PALLET = case when nvl(:allow_partial_pallet, 1) = 0 then 0 else 1 end,
               PREDICTIVE_BUFFER_MIN = :predictive_buffer_min,
               PICK_RATE_SOURCE = upper(nvl(:pick_rate_source, 'MIXED')),
               RECHECK_ON_PICK_EVENT = case when nvl(:recheck_on_pick_event, 1) = 0 then 0 else 1 end,
               UPDATED_AT = sysdate,
               UPDATED_BY = substr(:updated_by, 1, 50)
         where PICK_FACE_ARTICUL_ID = :pick_face_articul_id
        """,
        {
            "pick_face_articul_id": pick_face_articul_id,
            "use_articul_replenish_rule": request.use_articul_replenish_rule,
            "replenishment_method": request.replenishment_method,
            "replenishment_release_policy": request.replenishment_release_policy,
            "replenishment_qty_mode": request.replenishment_qty_mode,
            "min_trigger_box_qty": request.min_trigger_box_qty,
            "min_trigger_layer_qty": request.min_trigger_layer_qty,
            "safety_layer_qty": request.safety_layer_qty,
            "boxes_per_layer": request.boxes_per_layer,
            "boxes_per_pallet": request.boxes_per_pallet,
            "box_volume_m3": request.box_volume_m3,
            "allow_partial_pallet": request.allow_partial_pallet,
            "predictive_buffer_min": request.predictive_buffer_min,
            "pick_rate_source": request.pick_rate_source,
            "recheck_on_pick_event": request.recheck_on_pick_event,
            "updated_by": request.updated_by,
        },
    )
