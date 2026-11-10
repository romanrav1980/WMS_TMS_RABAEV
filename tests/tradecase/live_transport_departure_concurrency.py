"""Concurrent exact replay of an already departed isolated T07 shipment.

The runner never creates a load or a departure.  It sends the persisted departure
operation twice in parallel, then proves that Oracle still contains one applied
operation and one departed load fact.
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.mcp.tms_mcp_server import oracle_connection

FIXTURE = ROOT / "runtime/test-evidence/tradecase/2026-10-19/T07/fixture-1155.json"
REPORT = ROOT / "reports/tradecase/2026-10-29/codex/t07-departure-concurrency.json"
BASE = "http://127.0.0.1:8088"


def password() -> str:
    match = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    if not match:
        raise RuntimeError("admin password is not available in local AGENTS.md")
    return match.group(1)


def send(task_id: int, body: dict[str, str], secret: str) -> tuple[int, dict]:
    auth = base64.b64encode(("admin:" + secret).encode()).decode()
    request = Request(
        f"{BASE}/api/transport/loading/{task_id}/depart",
        data=json.dumps(body).encode(),
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=35) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def main() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    task_id = int(fixture["transport_task_id"])
    body = fixture["depart_body"]
    operation_id = body["operation_id"]
    secret = password()

    with oracle_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("select nvl(max(LOG_ID),0) from RRL_SQL_SLOW_LOG")
        slow_marker = int(cursor.fetchone()[0])

    with ThreadPoolExecutor(max_workers=2) as pool:
        replies = list(pool.map(lambda _: send(task_id, body, secret), range(2)))

    assert [status for status, _ in replies] == [200, 200], replies
    assert replies[0][1] == replies[1][1], replies

    with oracle_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "select count(*) from RRL_STOCK_OPERATION where OPERATION_ID=:op and COMMAND_TYPE='TRIP_DEPART' and STATE='APPLIED'",
            op=operation_id,
        )
        operation_count = int(cursor.fetchone()[0])
        cursor.execute(
            "select STATUS,DEPARTURE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",
            op=fixture["load_body"]["operation_id"],
        )
        load_status, departure_operation_id = cursor.fetchone()
        cursor.execute(
            "select count(*) from RRL_SQL_SLOW_LOG where LOG_ID>:marker and API_PATH like '/api/transport/loading/%/depart'",
            marker=slow_marker,
        )
        slow_rows = int(cursor.fetchone()[0])

    assert operation_count == 1, operation_count
    assert (load_status, departure_operation_id) == ("DEPARTED", operation_id)
    report = {
        "case": "T07 concurrent exact departure replay",
        "status": "PASS",
        "fixture": FIXTURE.relative_to(ROOT).as_posix(),
        "operation_id": operation_id,
        "http_statuses": [status for status, _ in replies],
        "responses_identical": True,
        "applied_departure_operations": operation_count,
        "load_fact": {"status": load_status, "departure_operation_id": departure_operation_id},
        "slow_sql_rows_for_path": slow_rows,
        "scope": "Existing departed synthetic fixture; no new load, departure, warehouse stock or external connector.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
