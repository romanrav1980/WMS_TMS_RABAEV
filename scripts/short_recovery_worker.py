"""Local worker: durable Oracle intent, bounded reconnect delay and graceful exit."""
import argparse,json,signal,sys
from pathlib import Path
from threading import Event
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.oracle_gateway import OracleGateway
from app.resource_composition import assign_warehouse
from app.modules.inventory.infrastructure.recovery_worker import ShortRecoveryWorker

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--actor",required=True)
    parser.add_argument("--loop",action="store_true")
    parser.add_argument("--interval",type=float,default=2)
    args=parser.parse_args()
    if not 1<=args.interval<=60:parser.error("interval must be 1..60 seconds")
    stop_file=Path(__file__).resolve().parents[1]/"runtime"/"short_recovery"/"worker.stop"
    stopped=Event()
    def stop(signum: int,frame: object) -> None:
        stopped.set()
    for name in ("SIGINT","SIGTERM","SIGBREAK"):
        if hasattr(signal,name):signal.signal(getattr(signal,name),stop)
    worker=ShortRecoveryWorker(OracleGateway(),args.actor,"short-worker:"+__import__("uuid").uuid4().hex,assign_warehouse)
    failures=0
    while not stopped.is_set():
        if stop_file.exists():break
        try:
            result=worker.process_one()
            failures=0
            if result is not None:print(json.dumps(result,ensure_ascii=True,default=str),flush=True)
        except PermissionError:
            print(json.dumps({"status":"STOPPED","reason":"WORKER_PERMISSION_REQUIRED"}),flush=True)
            return 2
        except (oracledb.DatabaseError,OSError,TimeoutError) as exc:
            failures+=1
            detail=exc.args[0] if exc.args else None
            print(json.dumps({"status":"DATABASE_RETRY","error_type":type(exc).__name__,
                "oracle_code":getattr(detail,"code",None),"attempt":failures,
                "retry_same_saved_operation":True}),flush=True)
            if not args.loop:return 1
        if not args.loop:break
        delay=min(30,args.interval*(2**min(failures,4))) if failures else args.interval
        stopped.wait(delay)
    return 0

if __name__=="__main__":raise SystemExit(main())
