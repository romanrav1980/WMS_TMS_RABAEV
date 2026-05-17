from __future__ import annotations

import hashlib
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..oracle_gateway import OracleGateway
from ..schemas import (
    MesApplyWmsRequest,
    MesCompleteOrderRequest,
    MesCompletionPallet,
    MesProductionOrderCreateRequest,
    MesRawIssueRequest,
)
from .mes_service import MesService


@dataclass(frozen=True)
class ExchangeResult:
    file_name: str
    message_id: str | None
    status: str
    production_order_id: int | None = None
    prod_batch_id: int | None = None
    error: str | None = None


class ProductionExchangeService:
    def __init__(
        self,
        root_dir: str | Path | None = None,
        gateway: OracleGateway | None = None,
        mes_service: MesService | None = None,
    ) -> None:
        settings = get_settings()
        self.root_dir = Path(root_dir or settings.production_exchange_root_dir).resolve()
        self.gateway = gateway or OracleGateway()
        self.mes = mes_service or MesService(self.gateway)

    def ensure_dirs(self) -> None:
        for name in ("in", "processing", "archive", "error", "out"):
            (self.root_dir / name).mkdir(parents=True, exist_ok=True)

    def process_once(self, limit: int = 10) -> list[ExchangeResult]:
        self.ensure_dirs()
        results: list[ExchangeResult] = []
        for source in sorted((self.root_dir / "in").glob("*.json"))[: max(1, limit)]:
            processing = self._move_to_processing(source)
            results.append(self.process_file(processing))
        return results

    def process_file(self, path: Path) -> ExchangeResult:
        message_id: str | None = None
        file_hash = ""
        try:
            raw = path.read_bytes()
            file_hash = hashlib.sha256(raw).hexdigest()
            payload = json.loads(raw.decode("utf-8-sig"))
            message_id = required_text(payload, "messageId")
            source_system = str(payload.get("sourceSystem") or "FILE_EXCHANGE")
            existing = self.get_log(message_id)
            if existing:
                existing_hash = existing.get("file_hash")
                if existing_hash and existing_hash != file_hash:
                    error = f"messageId already exists with different hash: {message_id}"
                    if existing.get("status") != "PROCESSED":
                        self.mark_error(message_id, "HASH_CONFLICT", error)
                    self._write_out(message_id, {"status": "ERROR", "messageId": message_id, "error": error}, suffix=".error")
                    self._move(path, self.root_dir / "error" / path.name)
                    return ExchangeResult(path.name, message_id, "ERROR", error=error)
                if existing.get("status") == "PROCESSED":
                    self._write_out(message_id, {"status": "DUPLICATE", "messageId": message_id, "fileLogId": existing.get("file_log_id")})
                    self._move(path, self.root_dir / "archive" / path.name)
                    return ExchangeResult(path.name, message_id, "DUPLICATE")

            self.register_message(payload, path, file_hash, source_system)
            order_id = self._create_or_get_order(payload, message_id)
            for raw_issue in payload.get("rawIssues") or []:
                self.mes.issue_raw(order_id, MesRawIssueRequest(
                    uid_pallet=raw_issue.get("uidPallet"),
                    raw_batch_id=raw_issue.get("rawBatchId"),
                    raw_articul=raw_issue.get("rawArticul"),
                    quantity=float(raw_issue["quantity"]),
                    unit_code=raw_issue.get("unitCode") or payload.get("unitCode") or "KG",
                    source_location=raw_issue.get("sourceLocation"),
                    production_location=raw_issue.get("productionLocation") or "MES_PROD",
                    created_by=source_system,
                ))

            self.mes.complete_order(order_id, MesCompleteOrderRequest(
                prod_batch_no=payload.get("prodBatchNo"),
                fact_qty=float(payload["factQty"]),
                unit_code=payload.get("unitCode") or "KG",
                pallets=[
                    MesCompletionPallet(
                        uid_pallet=required_text(pallet, "uidPallet"),
                        pallet_no=pallet.get("palletNo"),
                        quantity=pallet.get("quantity"),
                        pack_count=pallet.get("packCount"),
                        sscc=pallet.get("sscc"),
                    )
                    for pallet in payload.get("pallets") or []
                ],
                idempotency_key=f"{message_id}:complete",
                created_by=source_system,
            ))

            if bool(payload.get("applyWms", True)):
                self.mes.apply_wms(order_id, MesApplyWmsRequest(applied_by=source_system))

            order = self.mes.get_order(order_id)
            prod_batch_id = order.get("prod_batch_id")
            self.mark_processed(message_id, prod_batch_id)
            self._write_out(message_id, {
                "status": "PROCESSED",
                "messageId": message_id,
                "productionOrderId": order_id,
                "prodBatchId": prod_batch_id,
            })
            self._move(path, self.root_dir / "archive" / path.name)
            return ExchangeResult(path.name, message_id, "PROCESSED", production_order_id=order_id, prod_batch_id=prod_batch_id)
        except Exception as exc:
            error_text = str(exc)
            if message_id:
                self.mark_error(message_id, "PROCESSING_ERROR", error_text)
                self._write_out(message_id, {"status": "ERROR", "messageId": message_id, "error": error_text}, suffix=".error")
            self._move(path, self.root_dir / "error" / path.name)
            return ExchangeResult(path.name, message_id, "ERROR", error=error_text)

    def _create_or_get_order(self, payload: dict[str, Any], message_id: str) -> int:
        order_no = required_text(payload, "orderNo")
        existing = self.gateway.fetch_all(
            "select PRODUCTION_ORDER_ID from RRL_PRODUCTION_ORDER where ORDER_NO = :order_no",
            {"order_no": order_no},
        )
        if existing:
            return int(existing[0]["production_order_id"])
        return self.mes.create_order(MesProductionOrderCreateRequest(
            order_no=order_no,
            bom_id=payload.get("bomId"),
            target_articul=required_text(payload, "targetArticul"),
            planned_qty=float(payload.get("plannedQty") or payload["factQty"]),
            unit_code=payload.get("unitCode") or "KG",
            ware_id=payload.get("wareId"),
            production_line=payload.get("productionLine"),
            shift_id=payload.get("shiftId"),
            source_system=payload.get("sourceSystem") or "FILE_EXCHANGE",
            source_message_id=message_id,
            idempotency_key=f"{message_id}:order",
            comment_text=payload.get("comment"),
            created_by=payload.get("sourceSystem") or "FILE_EXCHANGE",
        ))

    def get_log(self, message_id: str) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(
            """
            select FILE_LOG_ID, MESSAGE_ID, FILE_HASH, STATUS, CREATED_PROD_BATCH_ID
              from RRL_FILE_EXCHANGE_LOG
             where MESSAGE_ID = :message_id
            """,
            {"message_id": message_id},
        )
        return rows[0] if rows else None

    def register_message(self, payload: dict[str, Any], path: Path, file_hash: str, source_system: str) -> int:
        return self.gateway.call_number_plsql(
            """
            begin
              :result := RRL_PRODUCTION_API.register_file_message(
                p_exchange_type => 'PRODUCTION_RELEASE',
                p_source_system => :source_system,
                p_message_id => :message_id,
                p_external_operation_id => :external_operation_id,
                p_file_name => :file_name,
                p_file_path => :file_path,
                p_file_hash => :file_hash
              );
            end;
            """,
            {
                "source_system": source_system,
                "message_id": required_text(payload, "messageId"),
                "external_operation_id": payload.get("externalOperationId"),
                "file_name": path.name,
                "file_path": str(path),
                "file_hash": file_hash,
            },
        )

    def mark_processed(self, message_id: str, prod_batch_id: int | None) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PRODUCTION_API.mark_file_processed(
                p_message_id => :message_id,
                p_prod_batch_id => :prod_batch_id,
                p_processed_by => 'production-exchange-worker'
              );
            end;
            """,
            {"message_id": message_id, "prod_batch_id": prod_batch_id},
        )

    def mark_error(self, message_id: str, code: str, error: str) -> None:
        self.gateway.execute_plsql(
            """
            begin
              RRL_PRODUCTION_API.mark_file_error(
                p_message_id => :message_id,
                p_error_code => :error_code,
                p_error_text => :error_text,
                p_processed_by => 'production-exchange-worker'
              );
            end;
            """,
            {"message_id": message_id, "error_code": code, "error_text": error[:3900]},
        )

    def _move_to_processing(self, path: Path) -> Path:
        target = self.root_dir / "processing" / path.name
        return self._move(path, target)

    def _move(self, source: Path, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target = target.with_name(f"{target.stem}.{int(time.time())}{target.suffix}")
        shutil.move(str(source), str(target))
        return target

    def _write_out(self, message_id: str, payload: dict[str, Any], suffix: str = "") -> None:
        out_path = self.root_dir / "out" / f"{message_id}{suffix}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if value is None or str(value).strip() == "":
        raise ValueError(f"Missing required field: {key}")
    return str(value).strip()
