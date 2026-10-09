"""Emit row projection and stable native revision replay changes."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=(2 if old=="  for i in 0..a.get_size-1 loop" else 1):raise RuntimeError("Missing unique anchor "+path+" "+old[:45])
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/151_revision_entry.sql"
text=(ROOT/path).read_text(encoding="utf-8")
# Preserve JSON keys and uppercase SQL column identifiers.
text="".join(part if i%2 else re.sub(r"\bcell\b","v_cell",part)
 for i,part in enumerate(re.split(r"('(?:[^']|'')*')",text)))
text=text.replace(" function count_row(", " function count_row(",1)
declaration=" function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2;\n"
text=text.replace("end;\n/\ncreate or replace package body",declaration+"end;\n/\ncreate or replace package body",1)
implementation=""" function count_document(p_cell varchar2,p_document number,p_quantity number,p_unit varchar2,p_actor varchar2,p_operation varchar2) return varchar2 is
  saved clob;result clob;d json_object_t;r json_object_t;row_id number;other_row number;article varchar2(160);
 begin
  if p_operation is null or p_actor is null or p_quantity is null or p_quantity<0 then raise_application_error(-20871,'INVENTORY_OPERATION_QUANTITY_REQUIRED');end if;
  begin select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);d.on_error(1);
   if d.get_string('actor')!=p_actor or d.get_string('command_type')!='INVENTORY_COUNT'
    or d.get_object('source').get_number('revision_id')!=p_document
    or not d.get_object('metadata').has('requested_revision_row') then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   r:=d.get_object('metadata').get_object('requested_revision_row');
   if r.get_string('cell')!=p_cell or r.get_string('unit')!=p_unit
    or r.get_string('quantity')!=RRL_STOCK_PLAN_HELPER.decimal_text(p_quantity) then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return 'ok';
  end if;
  select min(ID),max(ID) into row_id,other_row from RRL_REVISION_ROW where CELL=p_cell and REVISION_ID=p_document;
  if row_id is null or row_id!=other_row then raise_application_error(-20887,'REVISION_ROW_SELECTION_REQUIRED: inventory-count.html');end if;
  select ARTICUL1 into article from RRL_REVISION_ROW where ID=row_id;
  return count_row(article,p_cell,p_quantity,p_unit,row_id,p_actor,p_operation);
 end;
"""
text=text.rsplit("end;\n/",1)[0]+implementation+"end;\n/\n";files[path]=text
path="db/migrations/2026-10-08_stock_posting_core/152_revision_adapter.sql"
text=(ROOT/path).read_text(encoding="utf-8")
for name,unit in (("revision_cell_kor","BOX"),("revision_cell_sht_deleted","EA")):
 pat=r"(function "+name+r"\([^;]*?\) return varchar2 is\n)(.*?)(\nend;)"
 match=re.search(pat,text,re.I|re.S)
 if not match:raise RuntimeError(name)
 body=match.group(2)
 start=body.index(" select min(ID),max(ID)")
 body=body[:start]+" return RRL_STOCK_REVISION_ENTRY.count_document(cell1,revision_id1,count2,'"+unit+"',user_id3,p_operation_id);"
 text=text[:match.start(2)]+body+text[match.end(2):]
files[path]=text
path="db/migrations/2026-10-08_stock_posting_core/102_inventory_count.sql"
edit(path,"type keys is table of boolean", "revision_row number;row_doc number;row_cell varchar2(60);row_article varchar2(160);\n  type keys is table of boolean")
edit(path,"  for i in 0..a.get_size-1 loop", """  if d.get_object('metadata').has('revision_row_id') then
   revision_row:=d.get_object('metadata').get_number('revision_row_id');
   if a.get_size!=1 or revision_row is null then raise_application_error(-20871,'INVENTORY_REVISION_ROW_SINGLE_LOT_REQUIRED');end if;
   x:=treat(a.get(0) as json_object_t);
   select REVISION_ID,CELL,ARTICUL1 into row_doc,row_cell,row_article from RRL_REVISION_ROW where ID=revision_row;
   if row_doc is null or row_doc!=doc or row_cell is null or row_cell!=x.get_string('cell')
    or row_article is null or row_article!=x.get_string('article') then raise_application_error(-20887,'INVENTORY_REVISION_ROW_IDENTITY_CONFLICT');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVISION_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(revision_row));
  end if;
  for i in 0..a.get_size-1 loop""")
edit(path,"base varchar2(20);units clob;", "base varchar2(20);units clob;revision_row number;row_doc number;row_cell varchar2(60);row_article varchar2(160);other_lots number;v_uid varchar2(200);")
edit(path,"  a:=v.get_array('counts');original:=d.get_object('metadata').get_array('counts');",
 """  a:=v.get_array('counts');original:=d.get_object('metadata').get_array('counts');
  if d.get_object('metadata').has('revision_row_id') then
   revision_row:=d.get_object('metadata').get_number('revision_row_id');x:=treat(a.get(0) as json_object_t);
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_REVISION_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(revision_row)));
   select REVISION_ID,CELL,ARTICUL1 into row_doc,row_cell,row_article from RRL_REVISION_ROW where ID=revision_row for update;
   if row_doc is null or row_doc!=doc or row_cell is null or row_cell!=x.get_string('cell')
    or row_article is null or row_article!=x.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: revision row');end if;
   v_uid:=x.get_string('uid');
   select count(*) into other_lots from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
    where s.CELL=row_cell and p.ARTICUL=row_article and s.REMAIN>0 and s.UID_POLETA!=v_uid;
   if other_lots>0 then raise_application_error(-20887,'LOT_SELECTION_REQUIRED: inventory-count.html');end if;
  end if;""")
edit(path,"  result.put('operation_id',d.get_string('operation_id'));",
 """  if revision_row is not null then
   sourcex:=treat(original.get(0) as json_object_t);
   update RRL_REVISION_ROW set COUNT1=qty,REV_DATE=sysdate,
    COUNT_KOR=case when sourcex.get_string('unit')='BOX' then to_number(sourcex.get_string('quantity'),'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''') else COUNT_KOR end,
    REMARK1=substr(nvl(REMARK1,'')||' POSTED:'||d.get_string('operation_id'),1,255)
    where ID=revision_row;
  end if;
  result.put('operation_id',d.get_string('operation_id'));""")
# Materialize JSON values outside Oracle static SQL (avoids ORA-40573).
files[path]=files[path].replace("update RRL_REVISION_ROW set COUNT1=qty,REV_DATE=sysdate,", """declare v_row_unit varchar2(20):=sourcex.get_string('unit');v_row_qty varchar2(30):=sourcex.get_string('quantity');v_row_op varchar2(100):=d.get_string('operation_id');begin
   update RRL_REVISION_ROW set COUNT1=qty,REV_DATE=sysdate,""").replace("case when sourcex.get_string('unit')='BOX' then to_number(sourcex.get_string('quantity')","case when v_row_unit='BOX' then to_number(v_row_qty").replace("||d.get_string('operation_id'),1,255)","||v_row_op,1,255)").replace("    where ID=revision_row;\n  end if;","    where ID=revision_row;end;\n  end if;")
print(json.dumps(files,ensure_ascii=True))
