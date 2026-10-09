"""Preserve original REVIZION, patch only physical methods and their signatures."""
import json,re,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 cur=c.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant install only")
 sources={}
 for kind in ("PACKAGE","PACKAGE BODY"):
  cur.execute("select TEXT from USER_SOURCE where NAME='REVIZION' and TYPE=:k order by LINE",k=kind)
  sources[kind]="".join(row[0] for row in cur)
if "RRL_STOCK_REVISION_ENTRY" in sources["PACKAGE BODY"]:raise RuntimeError("Already adapted")
checkpoint=ROOT/"runtime/stock_posting_20261008/152_revision-native-checkpoint"
checkpoint.mkdir(parents=True,exist_ok=False)
for kind,source in sources.items():
 (checkpoint/(kind.replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
def ascii_source(source):
 source=re.sub(r"--[^\r\n]*","",source)
 def string(match):
  literal=match.group(0)
  if all(ord(ch)<128 for ch in literal):return literal
  value=literal[1:-1].replace("''","'")
  value="".join(ch if ord(ch)<128 and ch!="\\" else "\\"+format(ord(ch),"04x") for ch in value)
  return "unistr('"+value.replace("'","''")+"')"
 return re.sub(r"'(?:[^']|'')*'",string,source)
spec=ascii_source(sources["PACKAGE"]);body=ascii_source(sources["PACKAGE BODY"])
old_spec=re.sub(r"\bREVIZION\b","REVIZION_SP_OLD",spec,flags=re.I)
old_spec=re.sub(r"(package\s+REVIZION_SP_OLD\s+)(is\b)",r"\1accessible by(package REVIZION) \2",old_spec,count=1,flags=re.I)
old_body=re.sub(r"\bREVIZION\b","REVIZION_SP_OLD",body,flags=re.I)
# Each top-level function is delimited by the next top-level declaration.
pattern=r"(?im)^\s*function\s+(\w+)\s*\("
matches=list(re.finditer(pattern,body))
original_methods={m.group(1).upper():body[m.start():matches[i+1].start() if i+1<len(matches) else body.lower().rfind("end revizion;")] for i,m in enumerate(matches)}
adapt={
 "RRL_REVIZION_CELL_SHT":("p_operation_id varchar2 default null", "return RRL_STOCK_REVISION_ENTRY.count_row(articul1,CELL1,count_sht,'EA',revision_row_id1,user_id1,p_operation_id);"),
 "REVISION_CELL_KOR":("p_operation_id varchar2 default null", """select min(ID),max(ID) into row_id,other_row from RRL_REVISION_ROW where CELL=cell1 and REVISION_ID=revision_id1;
 if row_id is null or row_id!=other_row then raise_application_error(-20887,'REVISION_ROW_SELECTION_REQUIRED');end if;
 select ARTICUL1 into article from RRL_REVISION_ROW where ID=row_id;
 return RRL_STOCK_REVISION_ENTRY.count_row(article,cell1,count2,'BOX',row_id,user_id3,p_operation_id);"""),
 "REVISION_CELL_SHT_DELETED":("p_operation_id varchar2 default null", """select min(ID),max(ID) into row_id,other_row from RRL_REVISION_ROW where CELL=cell1 and REVISION_ID=revision_id1;
 if row_id is null or row_id!=other_row then raise_application_error(-20887,'REVISION_ROW_SELECTION_REQUIRED');end if;
 select ARTICUL1 into article from RRL_REVISION_ROW where ID=row_id;
 return RRL_STOCK_REVISION_ENTRY.count_row(article,cell1,count2,'EA',row_id,user_id3,p_operation_id);"""),
}
guards={
 "CLEAR_CELL":"INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html",
 "CLEAR_CELL2":"INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html",
 "RRL_REVIZION_CELL_PALL":"PALLET_COUNT_IS_NOT_MEASURED_QUANTITY: inventory-count.html",
 "RRL_REVIZION_CLEAR_MINUS":"NEGATIVE_STOCK_REQUIRES_EXPLICIT_CORRECTION: inventory-count.html",
 "RRL_INV_CREATE_LINE5":"INVENTORY_LOT_COMMAND_REQUIRED: inventory-count.html",
}
for name,method in original_methods.items():
 if name not in adapt and name not in guards:continue
 head=re.match(r"\s*function\s+(\w+)\s*\((.*?)\)\s*return\s+(\w+)\s*(is|as)\b",method,re.I|re.S)
 if not head:raise RuntimeError("Unsupported declaration: "+name)
 args=head.group(2).strip();ret=head.group(3);calls=",".join(part.strip().split()[0] for part in args.split(","))
 extra=adapt[name][0] if name in adapt else ""
 newargs=args+(","+extra if extra else "")
 declaration="function "+head.group(1)+"("+newargs+") return "+ret
 if extra:
  spec_pattern=r"(function\s+"+re.escape(name)+r"\s*\()(.*?)(\)\s*return\s+\w+\s*;)"
  spec,n=re.subn(spec_pattern,lambda m:m.group(1)+m.group(2)+","+extra+m.group(3),spec,count=1,flags=re.I|re.S)
  if n!=1:raise RuntimeError("Specification anchor missing: "+name)
 action=adapt[name][1] if name in adapt else "raise_application_error(-20886,'"+guards[name]+"');"
 replacement=declaration+""" is
 state varchar2(20);row_id number;other_row number;article varchar2(160);
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD."""+head.group(1)+"("+calls+""");end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 """+action+"\nend;\n"
 body=body.replace(method,replacement,1)
files={
 "152_revision_legacy.sql":"create or replace "+old_spec+"\n/\ncreate or replace "+old_body+"\n/\n",
 "152_revision_adapter.sql":"create or replace "+spec+"\n/\ncreate or replace "+body+"\n/\n",
 "152_revision_original_rollback.sql":"create or replace "+ascii_source(sources["PACKAGE"])+"\n/\ncreate or replace "+ascii_source(sources["PACKAGE BODY"])+"\n/\n",
}
print(json.dumps(files,ensure_ascii=True))
