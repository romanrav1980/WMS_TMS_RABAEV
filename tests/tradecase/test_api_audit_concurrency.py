import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI

from api.wms_api_server.app.middleware import api_audit
from api.wms_api_server.app.request_context import get_request_context
from api.wms_api_server.app.services.api_audit_service import ApiAuditService


@pytest.mark.parametrize("blocked_stage", ["start", "finish"])
@pytest.mark.parametrize("route_error", [False, True])
def test_slow_audit_does_not_block_other_requests_and_keeps_context(monkeypatch, blocked_stage, route_error):
    entered, release, timed_out = threading.Event(), threading.Event(), threading.Event()
    records = []

    class Audit:
        def __init__(self, **kwargs):
            pass

        def pause(self, stage):
            if stage == blocked_stage:
                entered.set()
                if not release.wait(2):
                    timed_out.set()

        def append_local(self, record):
            records.append((record["phase"], get_request_context(), record))
            return "memory.jsonl"

        def start_call(self, record):
            self.pause("start")
            records.append(("START", get_request_context(), record))
            return 73

        def finish_call(self, id, record):
            self.pause("finish")
            assert id == 73
            records.append(("FINISH", get_request_context(), record))

    settings = SimpleNamespace(audit_enabled=True, audit_max_body_chars=10000, audit_capture_response_body=True)
    monkeypatch.setattr(api_audit, "get_settings", lambda: settings)
    monkeypatch.setattr(api_audit, "ApiAuditService", Audit)
    app = FastAPI()
    app.add_middleware(api_audit.ApiAuditMiddleware)

    async def identity():
        ctx = get_request_context()
        return {"request_id": ctx.request_id, "api_call_id": ctx.api_call_id}

    async def audited():
        if route_error:
            raise RuntimeError("fixture failure")
        return await identity()

    app.get("/audited")(audited)
    app.get("/api/admin/transport/vehicles")(identity)

    async def scenario():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app, raise_app_exceptions=False), base_url="http://test") as client:
            pending = asyncio.create_task(client.get("/audited", headers={"Authorization": "sensitive-token"}))
            try:
                assert await asyncio.to_thread(entered.wait, 1)
                assert not timed_out.is_set(), "Audit blocked the HTTP event loop until its safety timeout"
                assert not pending.done()
                other = await client.get("/api/admin/transport/vehicles")
                assert other.status_code == 200
                assert other.json()["api_call_id"] is None
                assert other.json()["request_id"] == other.headers["X-WMS-Request-Id"]
            finally:
                release.set()
            response = await pending
            request_id = records[0][1].request_id
            if route_error:
                assert response.status_code == 500
                assert records[-1][2]["status"] == "ERROR"
                assert records[-1][2]["error_text"]
            else:
                assert response.status_code == 200
                assert response.headers["X-WMS-Request-Id"] == request_id
                assert response.json() == {"request_id": request_id, "api_call_id": 73}
            assert all(context.request_id == request_id for _, context, _ in records)
            assert [phase for phase, _, _ in records] == ["STARTED", "START", "FINISH", "FINISHED"]
            assert records[-1][1].api_call_id == 73
            assert "sensitive-token" not in records[1][2]["request_headers_json"]
        assert get_request_context() is None

    asyncio.run(scenario())


def test_concurrent_local_audit_records_remain_complete_json(tmp_path):
    service = ApiAuditService(gateway=object(), settings=SimpleNamespace(audit_local_dir=str(tmp_path)))
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda index: service.append_local({"id": index, "body": "приёмка" * 12000}), range(32)))
    rows = [json.loads(line) for path in tmp_path.glob("*.jsonl") for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 32
    assert {row["id"] for row in rows} == set(range(32))
    assert all(row["body"] == "приёмка" * 12000 for row in rows)
