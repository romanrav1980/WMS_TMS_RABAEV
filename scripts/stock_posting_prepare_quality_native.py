"""Preserve real QC/row functions; route physical QC before metadata writes."""
import json,re,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1];load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();names=("RRL_SET_SCAN_PROOVE","RRL_SET_SCAN_PROOVE2","RRL_TRIAL_BY_WEIGHT","RRL_TRIAL_BY_WEIGHT2","RRL_UPDATE_PALLET_ROW2","RRL_UPDATE_PALLET_ROW3");sources={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant preparation only")
 for name in names:
  cur.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='FUNCTION' order by LINE",n=name)
  sources[name]="".join(row[0] for row in cur)
cp=ROOT/"runtime/stock_posting_20261008/186_quality-native-checkpoint";cp.mkdir(parents=True,exist_ok=False)
for name,source in sources.items():(cp/(name+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
def ascii_source(source):
 source=re.sub(r"--[^\r\n]*","",source)
 def string(m):
  lit=m.group()
  if lit.isascii():return lit
  value=lit[1:-1].replace("''","'");value="".join(c if ord(c)<128 and c!="\\" else "\\"+format(ord(c),"04x") for c in value)
  return "unistr('"+value.replace("'","''")+"')"
 return re.sub(r"'(?:[^']|'')*'",string,source)
oldsql=[];publicsql=[];calcsql=[];rollback=[]
for name,original in sources.items():
 original=ascii_source(original)
 head=re.match(r"\s*function\s+\w+\s*\((.*?)\)\s*return\s+(\w+)\s*(is|as)\b",original,re.I|re.S)
 if not head:raise RuntimeError("Unsupported native signature "+name)
 args=head.group(1).strip();ret=head.group(2);calls=",".join(part.strip().split()[0] for part in args.split(","))
 old=re.sub(r"\b"+name+r"\b",name+"_SP_OLD",original,flags=re.I)
 old=re.sub(r"(return\s+"+ret+r"\s*)(is|as)\b",r"\1accessible by(function "+name+r") \2",old,count=1,flags=re.I)
 oldsql.append("create or replace "+old+"\n/\n");rollback.append("create or replace "+original+"\n/\n")
 if name.startswith("RRL_UPDATE"):
  calc=original
  match=re.search(r"\bbegin\s+select\s+count\s*\(\s*ID\s*\)\s+into\s+count_nesobrano\b",calc,re.I)
  if not match:raise RuntimeError("Expected automatic proof block "+name)
  finish=re.search(r"exception\s+WHEN\s+NO_DATA_FOUND\s+THEN\s+null;\s*end;",calc[match.start():],re.I)
  if not finish:raise RuntimeError("Expected complete proof block "+name)
  calc=calc[:match.start()]+calc[match.start()+finish.end():]
  calc=re.sub(r"\b"+name+r"\b",name+"_SP_CALC",calc,flags=re.I)
  calc=re.sub(r"(return\s+"+ret+r"\s*)(is|as)\b",r"\1accessible by(function "+name+r") \2",calc,count=1,flags=re.I)
  calcsql.append("create or replace "+calc+"\n/\n")
  action="""if dbms_transaction.local_transaction_id(false) is not null then raise_application_error(-20862,'PALLET_EDIT_REQUIRES_CLEAN_TRANSACTION');end if;
 RRL_STOCK_METADATA_TX.begin_change(user_id1,'outgoing_pallet_edit');
 savepoint RRL_PALLET_EDIT;
 result:="""+name+"_SP_CALC("+calls+""");
 if result!='ok' or result is null then rollback to RRL_PALLET_EDIT;
 else
  update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=0,PROOVED=0,KLADOVSHIK=user_id1 where PALLET_UID=pallet_uid1;
 end if;
 RRL_STOCK_METADATA_TX.end_change;return result;"""
  extra="";decl="result varchar2(1024);"
  handler="exception when others then RRL_STOCK_METADATA_TX.end_change;raise;"
 else:
  extra=",p_operation_id varchar2 default null"+(",p_actor varchar2 default null" if name.startswith("RRL_SET") else "")
  decl=""
  if name=="RRL_SET_SCAN_PROOVE":
   action="return RRL_STOCK_QUALITY_ENTRY.scan(PALLET_UID1,count_of_errors1,prim1,null,p_actor,p_operation_id);"
  elif name=="RRL_SET_SCAN_PROOVE2":
   action="return RRL_STOCK_QUALITY_ENTRY.scan(PALLET_UID1,count_of_errors1,prim1,SBORSHIK1,nvl(p_actor,nvl(KLADOVSHIK1,SBORSHIK1)),p_operation_id);"
  else:
   kind="WEIGHT2" if name.endswith("2") else "WEIGHT"
   action="return RRL_STOCK_QUALITY_ENTRY.weight('"+kind+"',PALLET_UID1,TRIAL_WEIGHT1,WOOD_WEIGHT1,user_id1,p_operation_id);"
  handler=""
 publicsql.append("create or replace function "+name+"("+args+extra+") return "+ret+" authid definer is\n state varchar2(20);"+decl+"""
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return """+name+"_SP_OLD("+calls+""");end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 """+action+"\n"+handler+"\nend;\n/\n")
base="db/migrations/2026-10-08_stock_posting_core/"
files={base+"186_quality_native_legacy.sql":"\n".join(oldsql),base+"186_quality_native_calculations.sql":"\n".join(calcsql),base+"186_quality_native_entrypoints.sql":"\n".join(publicsql),
 base+"186_quality_native_apply.sql":"@@186_quality_native_legacy.sql\n@@186_quality_native_calculations.sql\n@@186_quality_native_entrypoints.sql\n@@014b_recompile.sql\n",
 base+"186_quality_native_rollback.sql":"declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;\n/\n"+"\n".join(rollback)+"\n@@014b_recompile.sql\n"}
print(json.dumps(files,ensure_ascii=True))
