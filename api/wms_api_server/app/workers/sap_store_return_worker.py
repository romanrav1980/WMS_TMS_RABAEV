"""Reuse the existing exclusive file gateway; service actor must be explicitly configured."""
import argparse
import json
from pathlib import Path
import time
from ..delivery_composition import build_sap_store_returns
from ..modules.integrations.public import receive_gateway_files


class ConfiguredReceiver:
    def __init__(self,actor: str) -> None:
        self.actor=actor
        self.service=build_sap_store_returns()

    def receive(self,raw: bytes,actor: str) -> dict:
        return self.service.receive(raw,self.actor)


def main() -> None:
    parser=argparse.ArgumentParser(description="SAP store return XML file gateway")
    parser.add_argument("--actor",required=True,help="Active RUSERS service actor with sap_return_import")
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[4]/"exchange"/"sap_store_returns")
    parser.add_argument("--watch",action="store_true")
    args=parser.parse_args()
    receiver=ConfiguredReceiver(args.actor)
    while True:
        result=receive_gateway_files(args.root,receiver,limit=20,min_age=2)
        if result or not args.watch:
            print(json.dumps(result,ensure_ascii=True),flush=True)
        if not args.watch:
            break
        time.sleep(2)


if __name__=="__main__":
    main()
