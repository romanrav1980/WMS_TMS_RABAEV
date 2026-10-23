"""C-0148: live READ ONLY route points -> recipient links via the new read model (no writes). Credentials never printed."""
import json, sys, time, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.trade_route_plan import route_points
out = {}
for ware, trip in [(215590763, 'R1.1155'), (215590763, 'R1.1156'), (220793322, 'R1.1168'), (220793322, 'R1.1169'), (220639789, 'R1.1221'), (215590763, 'NO.SUCH.TRIP')]:
    timings = []
    for _ in range(3):
        t = time.perf_counter()
        try:
            r = route_points(OracleGateway(), ware, trip, 'admin'); status = 'OK'
        except Exception as e:
            r = {'error': type(e).__name__, 'code': getattr(e, 'code', str(e))}; status = 'ERR'
        timings.append(round((time.perf_counter() - t) * 1000))
    out[f'{ware}/{trip}'] = dict(status=status, ms=timings, result=r)
    print(ware, trip, status, timings, json.dumps(r, default=str)[:600])
pathlib.Path(__file__).parent.parent.joinpath('route-points-live.json').write_text(json.dumps(out, default=str, indent=1), encoding='utf-8')
