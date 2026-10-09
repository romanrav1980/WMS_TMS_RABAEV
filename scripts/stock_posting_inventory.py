"""Read-only source/row checkpoint before stock maintenance in authorized dev."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
WRITES=re.compile(r"\b(insert\s+into|update|delete\s+from|merge\s+into)\s+(?:rabaev\s*\.\s*)?(rrl_(?:remains|events|stock_reservation|pick_reservation|pick_wave_reservation))\b",re.I)


def hits(text):
    return [{"table":m.group(2).upper(),"verb":m.group(1).upper(),"line":text.count("\n",0,m.start())+1} for m in WRITES.finditer(text)]


def rows(cursor,sql):
    cursor.execute(sql)
    cols=[x[0].lower() for x in cursor.description]
    return [dict(zip(cols,row)) for row in cursor.fetchall()]


def main():
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.db import oracle_connection
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=ROOT/"runtime/stock_posting_20261008/checkpoint")
    out=parser.parse_args().output.resolve()
    if not out.is_relative_to(ROOT/"runtime"):
        raise ValueError("Checkpoint must remain in repository runtime")
    (out/"oracle").mkdir(parents=True,exist_ok=True)
    report={"purpose":"read-only checkpoint; not a VM snapshot or cutover B0"}
    with oracle_connection() as conn:
        cur=conn.cursor()
        cur.execute("select user,sys_context('USERENV','SERVICE_NAME'),cast(null as number) from dual")
        user,service,scn=cur.fetchone()
        if user!="RABAEV" or service.lower()!="orcl": raise RuntimeError("RABAEV/orcl only")
        report.update(schema=user,service=service,scn=scn)
        report["invalid_before"]=rows(cur,"select object_name,object_type from user_objects where status='INVALID'")
        active={r["trigger_name"] for r in rows(cur,"select trigger_name from user_triggers where table_name='RRL_EVENTS' and status='ENABLED'")}
        cur.execute("select name,type,line,text from user_source order by name,type,line")
        sources={}
        for name,kind,_,text in cur: sources.setdefault((name,kind),[]).append(text)
        report["oracle_writers"]=[]
        for (name,kind),lines in sources.items():
            if name.startswith("BIN$") and name not in active: continue
            text="".join(lines)
            found=hits(text)
            if not found: continue
            filename=re.sub(r"[^A-Za-z0-9_$.-]","_",name+"_"+kind.replace(" ","_")+".sql")
            path=out/"oracle"/filename
            path.write_text("create or replace "+text.rstrip()+"\n/\n",encoding="utf-8")
            report["oracle_writers"].append({"name":name,"type":kind,"source":filename,"hits":found,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"status":"requires_adapter"})
        report["anomaly_rows"]=rows(cur,"""select rowidtochar(rowid) row_id,cell,uid_poleta,remain,othod_nakl_id,time_of_last_update
            from rrl_remains where cell is null or uid_poleta is null or remain is null or remain<0
            or (cell,uid_poleta) in(select cell,uid_poleta from rrl_remains group by cell,uid_poleta having count(*)>1)
            order by uid_poleta,cell,rowid""")
        conn.rollback()
    report["local_writers"]=[]
    for folder in [ROOT/"api/wms_api_server/app",ROOT/"WindowsApplication2/WindowsApplication2"]:
        for path in sorted(folder.rglob("*")):
            if path.suffix not in {".py",".cs"} or {"bin","obj","__pycache__"} & set(path.parts): continue
            found=hits(path.read_text(encoding="utf-8-sig",errors="replace"))
            if found: report["local_writers"].append({"path":path.relative_to(ROOT).as_posix(),"hits":found,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"status":"requires_adapter"})
    (out/"writer-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps({"oracle_writers":len(report["oracle_writers"]),"local_files":len(report["local_writers"]),"preserved_rows":len(report["anomaly_rows"]),"output":str(out)}))


if __name__=="__main__": main()