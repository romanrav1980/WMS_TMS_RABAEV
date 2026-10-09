"""Register the exact initial writer inventory as UNCONVERTED, never auto-approve."""
import json
import sys
from pathlib import Path
from stock_posting_environment import load_local_oracle_environment

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"api/wms_api_server"))


def main():
    load_local_oracle_environment()
    from app.db import oracle_connection
    report=json.loads((ROOT/"runtime/stock_posting_20261008/checkpoint/writer-checkpoint.json").read_text(encoding="utf-8"))
    writers=[]
    for row in report["oracle_writers"]:
        writers.append(("ORACLE:"+row["type"]+":"+row["name"],"inventory",row["sha256"]))
    for row in report["local_writers"]:
        writers.append(("LOCAL:"+row["path"],"inventory",row["sha256"]))
    with oracle_connection() as connection:
        cursor=connection.cursor()
        cursor.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if cursor.fetchone()[0]!="PREPARED": raise RuntimeError("Cannot overwrite active writer inventory")
        for key,owner,digest in writers:
            cursor.execute("""merge into RRL_STOCK_WRITER_REGISTRY d using(
                select :k WRITER_KEY,:o OWNER_DOMAIN,:h SOURCE_HASH from dual)s on(d.WRITER_KEY=s.WRITER_KEY)
                when not matched then insert(WRITER_KEY,OWNER_DOMAIN,SOURCE_HASH,STATE)
                values(s.WRITER_KEY,s.OWNER_DOMAIN,s.SOURCE_HASH,'UNCONVERTED')""",
                {"k":key,"o":owner,"h":digest})
        connection.commit()
    print(json.dumps({"registered_candidates":len(writers),"state":"UNCONVERTED","activation":False}))


if __name__=="__main__": main()
