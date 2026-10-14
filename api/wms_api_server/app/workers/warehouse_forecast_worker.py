"""Bounded derived-history worker; no stock posting or external calls."""
import argparse
import json
import time
from ..forecast_composition import forecast_service

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--warehouse",type=int,required=True)
    parser.add_argument("--actor",required=True)
    parser.add_argument("--limit",type=int,default=50)
    parser.add_argument("--interval",type=float,default=15)
    parser.add_argument("--loop",action="store_true")
    args=parser.parse_args()
    if args.warehouse<1 or not 1<=args.limit<=100 or args.interval<1:
        parser.error("warehouse positive, limit1..100, interval >=1 second")
    service=forecast_service()
    while True:
        result=service.project(args.warehouse,args.limit,args.actor)
        print(json.dumps(result,ensure_ascii=False),flush=True)
        if not args.loop:
            return
        time.sleep(args.interval)

if __name__=="__main__":
    main()
