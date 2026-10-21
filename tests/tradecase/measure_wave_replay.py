"""Compare complete native continuation replay paths; real Oracle in both arms."""
from contextlib import contextmanager
import json
from pathlib import Path
import statistics
import sys
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/"api/wms_api_server")]
from app.oracle_gateway import OracleGateway
from app.schemas import PickWaveActionRequest
from app.services.picking_service import PickingService
from app.modules.fulfillment.infrastructure.wave_continuation import WaveContinuation
from tools.mcp.tms_mcp_server import oracle_connection


class CountingGateway(OracleGateway):
    def __init__(self):
        super().__init__();self.transactions=0

    @contextmanager
    def transaction(self, name):
        self.transactions+=1
        with super().transaction(name) as cursor:yield cursor


def physical(ware):
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w",w=ware)
        return list(q.fetchone())


if __name__=="__main__":
    out=ROOT/"runtime/test-evidence/tradecase/2026-10-21/T06"
    fixture=json.loads((out/"factory-case.json").read_text());wave=fixture["wave"]
    request=PickWaveActionRequest(operation_id="FC21."+str(fixture["warehouse_id"])+".launch",updated_by="admin")
    before=physical(fixture["warehouse_id"]);responses=[];arms={}
    # Baseline forces the original seven-step path; DB effects/results are never mocked.
    for arm in ["original_completed_path","completed_read"]:
        times=[];counts=[]
        for _ in range(6):
            gateway=CountingGateway();started=time.perf_counter()
            if arm=="original_completed_path":
                with patch.object(WaveContinuation,"completed",return_value=False):
                    result=PickingService(gateway).launch_wave(wave,request)
            else:result=PickingService(gateway).launch_wave(wave,request)
            times.append(round((time.perf_counter()-started)*1000,3));counts.append(gateway.transactions);responses.append(result)
        arms[arm]=dict(times_ms=times,median_warm_ms=statistics.median(times[1:]),continuation_gateway_transactions=counts)
    assert all(r==responses[0]for r in responses)
    after=physical(fixture["warehouse_id"]);assert before==after==[10,0]
    assert set(arms["original_completed_path"]["continuation_gateway_transactions"])=={8}
    assert set(arms["completed_read"]["continuation_gateway_transactions"])=={2}
    report=dict(status="PASS",arms=arms,stock_before=before,stock_after=after,response=responses[0],
        environment="same process and Oracle shared pool; original arm first, no flush; admin; six each, first excluded from warm median",
        limits="Transaction counts cover continuation gateway; stock posting has its own unchanged UOW. This is cached replay, not initial launch throughput or HTTP p95.")
    (out/"wave-replay-comparison.json").write_text(json.dumps(report,indent=2),encoding="utf-8");print(json.dumps(report))
