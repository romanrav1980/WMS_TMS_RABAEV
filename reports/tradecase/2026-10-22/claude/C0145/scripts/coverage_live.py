"""C-0145: live READ ONLY coverage snapshot via the new read model (no writes). Credentials from serv.bat loader, never printed."""
import json, sys, time, pathlib
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.integrations.infrastructure.trade_route import trip_coverage
out = {}
for ware, trip in [(215590763, 'R1.1155'), (215590763, 'R1.1156'), (220793322, 'R1.1168'), (220639789, 'R1.1221')]:
    t = time.perf_counter()
    try:
        r = trip_coverage(OracleGateway(), ware, trip, 'admin'); status = 'OK'
    except Exception as e:
        r = {'error': type(e).__name__, 'code': getattr(e, 'code', str(e))}; status = 'ERR'
    out[f'{ware}/{trip}'] = dict(status=status, ms=round((time.perf_counter() - t) * 1000), result=r)
    print(ware, trip, status, out[f'{ware}/{trip}']['ms'], 'ms', json.dumps(r, default=str)[:700])
pathlib.Path(__file__).parent.parent.joinpath('coverage-live.json').write_text(json.dumps(out, default=str, indent=1), encoding='utf-8')
