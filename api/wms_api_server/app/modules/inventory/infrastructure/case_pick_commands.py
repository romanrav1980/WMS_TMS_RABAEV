"""Bridge existing CASE confirmation to the Oracle posting command."""
import json
from hashlib import sha256
from .stock_posting_uow import StockPosting
from ..contracts_stock import StockCommand, StockPostingError
from ..domain.stock_quantity import quantity_text
from ..domain.mark_identity import canonical_mark


def resolve_case_codes(gateway, task_id: int, line_id: int, scans) -> tuple[str, ...]:
    if not scans:
        return ()
    batch = []
    identities = set()
    for index, scan in enumerate(scans):
        digest = sha256(canonical_mark(scan.system_code, scan.profile_code, scan.code)["identity"].encode()).hexdigest()
        identity = (scan.system_code, scan.profile_code, digest)
        if identity in identities:
            raise ValueError("Duplicate scanned marking code")
        identities.add(identity)
        batch.append({"index": index, "system": scan.system_code, "profile": scan.profile_code, "hash": digest})
    result = {}
    import oracledb
    with gateway.transaction("Resolve CASE unit scans without stock writes") as cursor:
        for start in range(0, len(batch), 500):
            selected = batch[start:start + 500]
            wire = cursor.var(oracledb.DB_TYPE_CLOB)
            wire.setvalue(0, json.dumps(selected, separators=(",", ":")))
            cursor.execute("""
                select j.SCAN_INDEX,u.PHYSICAL_UNIT_KEY
                  from json_table(:scans,'$[*]' columns(SCAN_INDEX number path '$.index',
                    SYSTEM_CODE varchar2(40) path '$.system',PROFILE_CODE varchar2(60) path '$.profile',
                    CODE_HASH varchar2(64) path '$.hash')) j
                  join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.SYSTEM_CODE and c.CODE_HASH=j.CODE_HASH
                  join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
                  join RRL_PALLETS p on p.UID_PALLET=u.CURRENT_UID
                  join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=:task and l.CASE_PICK_LINE_ID=:line
                    and l.ARTICUL=p.ARTICUL and l.CELL_CODE=u.CURRENT_CELL
                  join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID
                    and r.UID_PALLET=u.CURRENT_UID and r.CELL=u.CURRENT_CELL
                    and r.SOURCE_DOC_TYPE='PICK_WAVE' and r.SOURCE_DOC_ID=l.PICK_WAVE_ID and r.SOURCE_LINE_ID=l.PICK_TASK_ID
                 where u.STOCK_STATUS!='ISSUED' and r.RESERVATION_KIND='HARD' and r.STATUS in('ACTIVE','ALLOCATED','PICKING')
                   and exists(select 1 from RRL_SKU_RECEIPT_PROFILE f where f.ARTICUL=l.ARTICUL
                     and f.SYSTEM_CODE=j.SYSTEM_CODE and f.PROFILE_CODE=j.PROFILE_CODE)
            """, {"scans": wire, "task": task_id, "line": line_id})
            for index, key in cursor:
                index = int(index)
                if index in result or not key:
                    raise ValueError("Ambiguous physical unit for scanned CASE code")
                result[index] = key
            if any(item["index"] not in result for item in selected):
                raise ValueError("Scanned unit is not reserved for this CASE line in the pick cell")
    return tuple(sorted(set(result.values())))


def post_case_pick(gateway, task_id: int, line_id: int, request):
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if state and state[0]["state"] == "PREPARED":
        return None
    operation = request.operation_id
    if not operation and request.offline_event_id:
        operation = "CASE.PICK:" + sha256(request.offline_event_id.encode()).hexdigest()
    if not operation or not request.actor or request.fact_qty is None:
        raise ValueError("Operation ID, authenticated actor and measured cumulative quantity required")
    if request.unit_keys and request.unit_scans:
        raise ValueError("Choose unit identities or scanned marking codes")
    submitted = request.model_dump(mode="json")
    submitted["fact_qty"] = quantity_text(request.fact_qty)
    if len(json.dumps(submitted, ensure_ascii=True).encode()) > 2 * 1024 * 1024:
        raise ValueError("CASE scan payload exceeds 2 MiB")
    source = {"case_task_id": task_id, "case_line_id": line_id}
    saved = gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:o", {"o": operation})
    if saved:
        wire = saved[0]["canonical_request"]
        old = json.loads(wire.read() if hasattr(wire, "read") else wire)
        if (old["actor"] != request.actor or old["command_type"] != "CASE_PICK_CONFIRM"
                or old["source"] != source or old["metadata"].get("requested_confirmation") != submitted):
            raise StockPostingError("OPERATION_CONTENT_CONFLICT", operation)
        metadata, units = old["metadata"], tuple(old["units"])
    else:
        units = tuple(request.unit_keys) if request.unit_keys else resolve_case_codes(gateway, task_id, line_id, request.unit_scans)
        metadata = {"fact_qty": quantity_text(request.fact_qty), "scan_cell": request.scan_cell,
            "scan_product": request.scan_product or request.scan_box, "scan_container": request.scan_container,
            "offline_event_id": request.offline_event_id, "requested_confirmation": submitted}
    return StockPosting().post(StockCommand(operation_id=operation, command_type="CASE_PICK_CONFIRM",
        actor=request.actor, source=source, lines=(), units=units, metadata=metadata))
