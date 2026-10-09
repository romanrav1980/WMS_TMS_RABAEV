"""Run existing OracleApply with credentials in child environment, never command line."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"api/wms_api_server"))


def main():
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.config import get_settings
    parser=argparse.ArgumentParser()
    parser.add_argument("script",type=Path)
    args=parser.parse_args()
    path=args.script.resolve()
    if not path.is_relative_to(ROOT/"db/migrations"): raise ValueError("Versioned migrations only")
    settings=get_settings()
    quote=lambda value:'"'+str(value).replace('"','""')+'"'
    env=dict(os.environ)
    env["STOCK_POSTING_ORACLE_CONNECTION"]=";".join(["User Id="+quote(settings.oracle_user),
        "Password="+quote(settings.oracle_password),"Data Source="+quote(settings.oracle_dsn)])
    binary=ROOT/"runtime/oracle_apply_build/bin/OracleApply.dll"
    if not binary.is_file():
        raise RuntimeError("Build fixed OracleApply into runtime/oracle_apply_build before migration")
    result=subprocess.run(["dotnet",str(binary),"STOCK_POSTING_ORACLE_CONNECTION",str(path),
                           "--stop-on-error"],cwd=ROOT,env=env,check=False)
    raise SystemExit(result.returncode)


if __name__=="__main__": main()