"""Preserve live REMAINS and adapt its indirect native move without swallowing outcomes."""
import json,re,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1];load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();sources={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as conn:
 cur=conn.cursor();cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 if cur.fetchone()!=("RABAEV","orcl"):raise RuntimeError("Unexpected target")
 cur.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
 if cur.fetchone()!=("PREPARED",):raise RuntimeError("Dormant preparation only")
 for kind in ("PACKAGE","PACKAGE BODY"):
  cur.execute("select TEXT from USER_SOURCE where NAME='REMAINS' and TYPE=:t order by LINE",t=kind)
  sources[kind]="".join(row[0] for row in cur)
cp=ROOT/"runtime/stock_posting_20261008/180_remains-original-checkpoint";cp.mkdir(parents=True,exist_ok=False)
for kind,source in sources.items():
 (cp/(kind.replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
def ascii_source(source):
 source=re.sub(r"--[^\r\n]*","",source)
 def string(m):
  lit=m.group()
  if lit.isascii():return lit
  value=lit[1:-1].replace("''","'")
  value="".join(c if ord(c)<128 and c!="\\" else "\\"+format(ord(c),"04x") for c in value)
  return "unistr('"+value.replace("'","''")+"')"
 return re.sub(r"'(?:[^']|'')*'",string,source)
spec=ascii_source(sources["PACKAGE"]);body=ascii_source(sources["PACKAGE BODY"])
for name in ("move_pall_2_picking_cell","close_othod_pallet"):
 pattern=r"(function\s+"+name+r"\s*\()(.*?)(\)\s*return\s+varchar2)"
 spec,n=re.subn(pattern,lambda m:m.group(1)+m.group(2)+",p_operation_id varchar2 default null"+m.group(3),spec,count=1,flags=re.I|re.S);assert n==1
 if name=="close_othod_pallet":
  body,n=re.subn(pattern,lambda m:m.group(1)+m.group(2)+",p_operation_id varchar2 default null"+m.group(3),body,count=1,flags=re.I|re.S);assert n==1
  body=body.replace("return RRL_CLOSE_OTHOD_PALLET(PALLET_ID1, iser_id21);","return RRL_CLOSE_OTHOD_PALLET(PALLET_ID1, iser_id21,p_operation_id);",1)
matches=list(re.finditer(r"(?im)^\s*function\s+(\w+)\s*\(",body))
method=next(body[m.start():matches[i+1].start()] for i,m in enumerate(matches) if m.group(1).lower()=="move_pall_2_picking_cell")
head=re.match(r"\s*function\s+\w+\s*\((.*?)\)\s*return\s+varchar2\s*is",method,re.I|re.S);assert head
# The original method is retained as a local PREPARED-only function.
legacy=re.sub(r"(function\s+)move_pall_2_picking_cell",r"\1legacy_move",method,count=1,flags=re.I)
replacement="function move_pall_2_picking_cell("+head.group(1)+",p_operation_id varchar2 default null) return varchar2 is\n"+"""
 v_state varchar2(20);wire clob;result clob;d json_object_t:=json_object_t();m json_object_t:=json_object_t();s json_object_t:=json_object_t();
 article varchar2(160);target_cell varchar2(60);old_actor varchar2(100);
"""+legacy+"""
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state='PREPARED' then return legacy_move(pall_uid1,user_id2);end if;
 if p_operation_id is null or user_id2 is null or pall_uid1 is null then raise_application_error(-20871,'OPERATION_ID_AND_ACTOR_REQUIRED');end if;
 begin
  select CANONICAL_REQUEST,ACTOR into wire,old_actor from RRL_STOCK_OPERATION where OPERATION_ID=p_operation_id;
  d:=json_object_t.parse(wire);
  if old_actor!=user_id2 or d.get_string('command_type')!='INTERNAL_MOVE'
   or d.get_object('metadata').get_string('uid')!=pall_uid1
   or d.get_object('source').get_string('type')!='ARTICLE_PICK_CELL' then raise_application_error(-20872,'OPERATION_CONTENT_CONFLICT');end if;
 exception when no_data_found then
  select ARTICUL into article from RRL_PALLETS where UID_PALLET=pall_uid1;
  select CELL into target_cell from RRL_ARTICULS where ACTICUL=article;
  if target_cell is null then raise_application_error(-20886,'ARTICLE_PICK_CELL_REQUIRED');end if;
  d.put('contract_version',2);d.put('operation_id',p_operation_id);d.put('command_type','INTERNAL_MOVE');d.put('actor',user_id2);
  s.put('type','ARTICLE_PICK_CELL');d.put('source',s);d.put('lines',json_array_t());d.put('units',json_array_t());
  m.put('uid',pall_uid1);m.put('target_cell',target_cell);m.put('quantity','0');d.put('metadata',m);
 end;
 RRL_STOCK_NATIVE_API.post(d.to_clob,user_id2,result);
 return 'ok_'||d.get_object('metadata').get_string('target_cell');
end;
"""
body=body.replace(method,replacement,1)
p="db/migrations/2026-10-08_stock_posting_core/180_remains_adapter.sql"
print(json.dumps({p:"create or replace "+spec+"\n/\ncreate or replace "+body+"\n/\n"},ensure_ascii=True))
