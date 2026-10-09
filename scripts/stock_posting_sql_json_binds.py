"""Replace PL/SQL JSON getters in static SQL with typed local binds (Oracle 19c).

Only maintained runtime components are changed. Raw checkpoints stay untouched.
The local DECLARE block keeps values private to the SQL statement or cursor loop.
"""
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"db/migrations/2026-10-08_stock_posting_core"
EXPR=re.compile(r"\b[a-zA-Z][a-zA-Z0-9_$#]*(?:\.(?:get_object|get_array)\([^()]*\))*\.(get_number|get_string|get_clob|to_clob)\((?:[^()]|\([^()]*\))*\)",re.I)

def mask_sql(source):
    # Equal-length mask: ignore quotes, quoted names and both comment styles.
    return re.sub(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|--[^\n]*|/\*[\s\S]*?\*/",
                  lambda m:"".join("\n" if ch=="\n" else " " for ch in m.group()),source)

def transform(source):
    masked=mask_sql(source)
    changes=[];covered=0;ordinal=0
    for token in re.finditer(r"\b(select|insert|update|delete|merge)\b",masked,re.I):
        start=token.start()
        if start<covered: continue
        # DML SQL keywords can be column/trigger names; only statement starts and cursor SELECT.
        cursor=re.search(r"\bfor\s+\w+\s+in\s*\(\s*$",masked[max(0,start-150):start],re.I)
        prefix=masked[:start].rstrip()
        direct=not prefix or prefix.endswith((";","begin","then","else","loop")) or masked[masked.rfind("\n",0,start)+1:start].strip()==""
        if not direct and not cursor: continue
        if cursor:
            blockstart=max(0,start-150)+cursor.start()
            opening=masked.rfind("(",blockstart,start)
            depth=1;sqlend=opening+1
            while depth and sqlend<len(masked):
                ch=masked[sqlend];depth+=int(ch=="(")-int(ch==")");sqlend+=1
            if depth: raise ValueError("Unclosed SQL cursor")
            lo=re.match(r"\s*loop\b",masked[sqlend:],re.I)
            if not lo: continue
            loopdepth=1;blockend=None
            for lt in re.finditer(r"\bend\s+loop\b|\bloop\b",masked[sqlend+lo.end():],re.I):
                if lt.group().lower().startswith("end"): loopdepth-=1
                else: loopdepth+=1
                if loopdepth==0:
                    end=sqlend+lo.end()+lt.end()
                    terminator=masked.find(";",end)
                    blockend=terminator+1;break
            if blockend is None: raise ValueError("Unclosed PL/SQL loop")
        else:
            sqlend=masked.find(";",start)
            if sqlend<0: continue
            sqlend+=1;blockstart=start;blockend=sqlend
        sql=source[start:sqlend];matches=[]
        for match in EXPR.finditer(sql):
            if masked[start+match.start():start+match.start()+1].strip():
                matches.append(match)
        if not matches: continue
        ordinal+=1
        declarations=[];replacements=[]
        for n,match in enumerate(matches,1):
            name=f"v_json_sql_{ordinal}_{n}"
            typ="number" if match.group(1).lower()=="get_number" else "clob" if match.group(1).lower() in("get_clob","to_clob") else "varchar2(32767)"
            declarations.append(f" {name} {typ}:={match.group()};")
            replacements.append((start+match.start(),start+match.end(),name))
        # Each cursor wrapper contains its complete loop. Transform nested SQL recursively.
        block=source[blockstart:blockend]
        for a,b,value in reversed(replacements):
            block=block[:a-blockstart]+value+block[b-blockstart:]
        if cursor:
            bm=mask_sql(block);cursor_loop=re.search(r"\)\s*loop\b",bm,re.I)
            if cursor_loop:
                head=block[:cursor_loop.end()]
                tail=block[cursor_loop.end():]
                tail,nested=transform(tail)
                block=head+tail
        replacement="declare\n"+"\n".join(declarations)+"\nbegin\n"+block+"\nend;"
        changes.append((blockstart,blockend,replacement));covered=blockend
    for start,end,replacement in reversed(changes):
        source=source[:start]+replacement+source[end:]
    return source,len(changes)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    manifest=json.loads((D/"current_runtime_manifest.json").read_text(encoding="utf-8"))
    files=list(dict.fromkeys(manifest["components"]+["100_native_mes_production.sql","102_inventory_count.sql","105_wave_metadata.sql","106_wave_launch.sql","107_native_wave_api.sql"]))
    report={};output={}
    for name in files:
        path=D/name;s=path.read_text(encoding="utf-8");updated,count=transform(s)
        if count:
            report[name]=count
            output[name]=updated
            if args.apply:
                # Relative workspace paths are required by the Windows filesystem broker.
                Path("db/migrations/2026-10-08_stock_posting_core",name).write_text(updated,encoding="utf-8")
    print(json.dumps(output if args.emit else report,ensure_ascii=True,indent=2))

if __name__=="__main__":main()
