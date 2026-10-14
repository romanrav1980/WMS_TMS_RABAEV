"""Bounded periodic reconciliation of explicitly selected warehouses, using the existing root."""
import argparse,json,signal,sys,time
from pathlib import Path
from datetime import datetime,timezone
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.replenishment_composition import build_minimax_service, build_replenishment_continuation
parser=argparse.ArgumentParser()
parser.add_argument("--warehouse",type=int,action="append",required=True)
parser.add_argument("--actor",required=True)
parser.add_argument("--interval",type=int,default=30)
parser.add_argument("--once",action="store_true")
args=parser.parse_args()
if any(w<1 for w in args.warehouse) or len(set(args.warehouse))>10 or args.interval<15:
    parser.error("Select 1..10 distinct positive warehouses, interval >=15 seconds")
stopping=False
def stop(*_):
    global stopping
    stopping=True
signal.signal(signal.SIGINT,stop)
signal.signal(signal.SIGTERM,stop)
service=build_minimax_service()
continuation=build_replenishment_continuation()
marker=Path(__file__).resolve().parents[1]/"runtime/minimax_worker/worker.stop"
while not stopping and not marker.exists():
    for warehouse in sorted(set(args.warehouse)):
        if stopping or marker.exists():break
        try:
            continued=continuation.reconcile(warehouse,args.actor)
            result=service.reconcile(warehouse,args.actor)
            record={"at":datetime.now(timezone.utc).isoformat(),"warehouse":warehouse,"wave_id":result["wave_id"],
                    "continued":continued["processed"],"created":result["created"],"faces":len(result["faces"]),"status":"OK"}
        except Exception as exc:
            record={"at":datetime.now(timezone.utc).isoformat(),"warehouse":warehouse,"status":"ERROR",
                    "error_type":type(exc).__name__,"detail":str(getattr(exc,"detail",exc))[:1000]}
        print(json.dumps(record,ensure_ascii=False,default=str),flush=True)
    if args.once:break
    for _ in range(args.interval):
        if stopping or marker.exists():break
        time.sleep(1)
