import json
import os
import shutil
import sys
import time
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / "api" / "wms_api_server"
sys.path.insert(0, str(API_ROOT))

os.environ.setdefault("WMS_ORACLE_USER", "RABAEV")
os.environ.setdefault("WMS_ORACLE_PASSWORD", "RABAEVWMS")
os.environ.setdefault("WMS_ORACLE_DSN", "127.0.0.1:1521/orcl")

from app.schemas import BomCreateRequest, BomLineRequest  # noqa: E402
from app.services.bom_service import BomService  # noqa: E402
from app.services.production_exchange_service import ProductionExchangeService  # noqa: E402


def main() -> int:
    suffix = time.strftime("%Y%m%d%H%M%S")
    target_articul = f"FG-FILE-PETFOOD-{suffix[-6:]}"
    raw_articul = "RM-MEAT-BEEF-FROZ-01"
    message_id = f"FILE-MES-{suffix}"
    order_no = f"FILE-MES-ORDER-{suffix}"
    lot_no = f"FILE-MES-LOT-{suffix}"
    raw_pallet = f"FILE-MES-RAW-{suffix}"
    fg_pallet = f"FILE-MES-FG-{suffix}"
    exchange_root = ROOT / "tmp" / "mes_file_exchange_smoke"

    if exchange_root.exists():
        shutil.rmtree(exchange_root)
    (exchange_root / "in").mkdir(parents=True)

    bom_service = BomService()
    bom_id = bom_service.create_bom(
        BomCreateRequest(
            bom_code=f"FILE-MES-BOM-{suffix}",
            bom_name="File exchange MES smoke BOM",
            target_articul=target_articul,
            base_qty=100,
            base_unit_code="KG",
            is_primary=1,
            valid_from=date.today(),
            created_by="file-exchange-smoke",
        )
    )
    bom_service.add_line(
        bom_id,
        BomLineRequest(
            line_no=10,
            component_type="RAW",
            component_articul=raw_articul,
            component_name="Beef frozen block",
            qty_per_base=50,
            unit_code="KG",
            created_by="file-exchange-smoke",
        ),
    )
    bom_service.approve_bom(bom_id, "file-exchange-smoke")

    payload = {
        "messageId": message_id,
        "sourceSystem": "FILE-SMOKE",
        "orderNo": order_no,
        "targetArticul": target_articul,
        "plannedQty": 100,
        "factQty": 100,
        "unitCode": "KG",
        "wareId": 9102,
        "productionLine": "LINE-FILE",
        "prodBatchNo": lot_no,
        "rawIssues": [
            {
                "uidPallet": raw_pallet,
                "rawArticul": raw_articul,
                "quantity": 50,
                "unitCode": "KG",
                "sourceLocation": "RM-A01-01",
                "productionLocation": "MES_PROD",
            }
        ],
        "pallets": [
            {
                "uidPallet": fg_pallet,
                "palletNo": 1,
                "quantity": 100,
                "packCount": 10,
                "sscc": ("0000000000" + suffix)[-18:],
            }
        ],
        "applyWms": True,
    }

    input_path = exchange_root / "in" / f"{message_id}.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    service = ProductionExchangeService(root_dir=exchange_root)
    results = service.process_once(limit=1)
    if len(results) != 1 or results[0].status != "PROCESSED":
        raise AssertionError(f"Expected one PROCESSED result, got {results}")

    response = json.loads((exchange_root / "out" / f"{message_id}.json").read_text(encoding="utf-8"))
    if response["status"] != "PROCESSED":
        raise AssertionError(f"Expected PROCESSED response, got {response}")

    duplicate_path = exchange_root / "in" / f"{message_id}.duplicate.json"
    duplicate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    duplicate_results = service.process_once(limit=1)
    if len(duplicate_results) != 1 or duplicate_results[0].status != "DUPLICATE":
        raise AssertionError(f"Expected one DUPLICATE result, got {duplicate_results}")

    order = service.mes.get_order(results[0].production_order_id or 0)
    genealogy = service.mes.get_genealogy(results[0].production_order_id or 0)
    movements = order.get("movements", [])
    applied = [movement for movement in movements if movement.get("status") == "APPLIED_TO_WMS"]
    if len(applied) < 3:
        raise AssertionError(f"Expected at least 3 applied movements, got {len(applied)}")
    if not genealogy.get("raw_usage"):
        raise AssertionError("Expected raw usage in genealogy.")
    if not genealogy.get("pallets"):
        raise AssertionError("Expected finished-goods pallets in genealogy.")

    log_rows = service.gateway.fetch_all(
        """
        select MESSAGE_ID, STATUS, CREATED_PROD_BATCH_ID
          from RRL_FILE_EXCHANGE_LOG
         where MESSAGE_ID = :message_id
        """,
        {"message_id": message_id},
    )
    if len(log_rows) != 1 or log_rows[0].get("status") != "PROCESSED":
        raise AssertionError(f"Expected one PROCESSED file log row, got {log_rows}")

    print(json.dumps({
        "status": "ok",
        "bom_id": bom_id,
        "message_id": message_id,
        "production_order_id": results[0].production_order_id,
        "prod_batch_id": results[0].prod_batch_id,
        "movements": len(movements),
        "applied_movements": len(applied),
        "raw_usage": len(genealogy.get("raw_usage", [])),
        "pallets": len(genealogy.get("pallets", [])),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
