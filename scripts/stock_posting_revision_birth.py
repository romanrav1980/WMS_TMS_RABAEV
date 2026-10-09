"""Wire existing inventory pallet creation to one Oracle inventory command."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if old=="end;\n/\n" and text.count(old)==2:
  at=text.rfind(old);files[path]=text[:at]+new+text[at+len(old):];return
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path+" "+old[:40])
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/151_revision_entry.sql"
edit(path,"end;\n/\ncreate or replace package body",
 " function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2;\nend;\n/\ncreate or replace package body")
edit(path,"end;\n/\n", """ function birth_legacy(p_facts clob,p_actor varchar2,p_operation varchar2) return varchar2 is
  requested json_object_t:=json_object_t.parse(p_facts);d json_object_t;m json_object_t;s json_object_t:=json_object_t();
  saved clob;result clob;old_wire clob;wire clob;doc number;other_doc number;naklad number;uid varchar2(200);
 begin
  if p_actor is null or p_operation is null then raise_application_error(-20871,'INVENTORY_OPERATION_ACTOR_REQUIRED');end if;
  begin select CANONICAL_REQUEST into saved from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
  exception when no_data_found then saved:=null;end;
  if saved is not null then
   d:=json_object_t.parse(saved);d.on_error(1);
   if d.get_string('actor')!=p_actor or d.get_string('command_type')!='INVENTORY_REGISTER_LOT'
    or not d.get_object('metadata').has('legacy_facts') then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   wire:=requested.to_clob;old_wire:=d.get_object('metadata').get_object('legacy_facts').to_clob;
   if dbms_lob.compare(wire,old_wire)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT');end if;
   RRL_STOCK_NATIVE_API.post(saved,p_actor,result);return d.get_object('metadata').get_string('uid');
  end if;
  naklad:=requested.get_number('receipt_document_id');
  select min(ID),max(ID) into doc,other_doc from RRL_REVIZION where REV_NAKLAD_ID=naklad;
  if doc is null or doc!=other_doc then raise_application_error(-20887,'INVENTORY_REVISION_DOCUMENT_AMBIGUOUS');end if;
  if requested.get_number('pallet_number') is null or requested.get_number('pallet_number')<1
   or requested.get_number('pallet_number')!=trunc(requested.get_number('pallet_number')) then raise_application_error(-20871,'INVENTORY_PALLET_NUMBER_REQUIRED');end if;
  uid:='P_'||requested.get_string('article')||'_G3_'||requested.get_string('cell')||'_'||RRL_STOCK_PLAN_HELPER.decimal_text(requested.get_number('pallet_number'));
  d:=json_object_t();d.put('contract_version',2);d.put('operation_id',p_operation);d.put('actor',p_actor);d.put('command_type','INVENTORY_REGISTER_LOT');
  d.put('lines',json_array_t());d.put('units',json_array_t());s.put('revision_id',doc);d.put('source',s);
  m:=json_object_t();m.put('reason','Measured inventory pallet');m.put('uid',uid);m.put('article',requested.get_string('article'));
  m.put('cell',requested.get_string('cell'));m.put('quantity',requested.get_string('quantity'));m.put('expiry_date',requested.get_string('expiry_date'));
  m.put('price',1);m.put('legacy_facts',requested);d.put('metadata',m);
  RRL_STOCK_NATIVE_API.post(d.to_clob,p_actor,result);return uid;
 end;
end;
/
""")
# edit above must replace BODY end only: specification marker was extended already.
path="db/migrations/2026-10-08_stock_posting_core/152_revision_adapter.sql"
text=(ROOT/path).read_text(encoding="utf-8")
pat=r"(function\s+RRL_INV_CREATE_LINE5\s*\()([^;]*?)(\)\s*return\s+varchar2)"
text,n=re.subn(pat,lambda m:m.group(1)+m.group(2)+",p_operation_id varchar2 default null"+m.group(3),text,count=2,flags=re.I|re.S)
if n!=2:raise RuntimeError("Birth declaration anchors")
text=text.replace("state varchar2(20);row_id number;other_row number;article varchar2(160);\nbegin",
 "state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();\nbegin")
old="raise_application_error(-20886,'INVENTORY_LOT_COMMAND_REQUIRED: inventory-count.html');"
new="""facts.put('article',articul2);facts.put('cell',cell1);facts.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(count1));
 facts.put('expiry_date',to_char(expiury_date,'YYYY-MM-DD'));facts.put('mod_id',fasovka_id1);
 facts.put('defect_percent',brak_perc1);facts.put('gross_weight',pall_weight1);facts.put('net_weight',tn_weight1);
 facts.put('box_count',count_kor1);facts.put('pallet_number',pall_n);facts.put('receipt_document_id',NAKLAD_ID);
 return RRL_STOCK_REVISION_ENTRY.birth_legacy(facts.to_clob,user_id2,p_operation_id);"""
if text.count(old)!=1:raise RuntimeError("Birth action anchor")
files[path]=text.replace(old,new)
path="db/migrations/2026-10-08_stock_posting_core/125_inventory_birth.sql"
edit(path,"price number;\n begin","price number;legacy json_object_t;legacy_doc number;legacy_owner number;mod_id number;gross number;net number;boxes number;defect number;\n begin")
edit(path,"  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');","""  if m.has('legacy_facts') then
   legacy:=m.get_object('legacy_facts');legacy.on_error(1);legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_doc is null or legacy_owner is null or legacy_doc!=legacy_owner then raise_application_error(-20887,'INVENTORY_SOURCE_DOCUMENT_CONFLICT');end if;
   mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if gross is null or gross<0 or net is null or net<0 or (gross>0 and net>gross) or boxes is null or boxes<0
    or defect is null or defect<0 or defect>100 or mod_id<0 then raise_application_error(-20871,'INVENTORY_PALLET_FACTS_INVALID');end if;
   if mod_id>0 then select ID into mod_id from RRL_ARTICUL_MODS where ID=mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');""")
edit(path,"  v.put('document',doc);","""  if legacy_doc is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(legacy_doc));end if;
  v.put('document',doc);""")
edit(path,"marked number;current_version number;v_count_cell varchar2(60);",
 "marked number;current_version number;v_count_cell varchar2(60);legacy json_object_t;legacy_doc number;legacy_owner number;mod_id number;gross number;net number;boxes number;defect number;")
edit(path,"  RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);","""  if d.get_object('metadata').has('legacy_facts') then
   legacy:=d.get_object('metadata').get_object('legacy_facts');legacy_doc:=legacy.get_number('receipt_document_id');
   select REV_NAKLAD_ID into legacy_owner from RRL_REVIZION where ID=doc;
   if legacy_owner is null or legacy_owner!=legacy_doc then raise_application_error(-20890,'CLOSURE_CHANGED: inventory source document');end if;
   mod_id:=nvl(legacy.get_number('mod_id'),0);gross:=legacy.get_number('gross_weight');net:=legacy.get_number('net_weight');
   boxes:=legacy.get_number('box_count');defect:=legacy.get_number('defect_percent');
   if mod_id>0 then select ID into mod_id from RRL_ARTICUL_MODS where ID=mod_id and ARTICUL=article;end if;
  end if;
  RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);""")
edit(path,"  RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,qty,0,base,version,0);","""  if legacy is not null then
   update RRL_PALLETS set MOD_ID=mod_id,WEIGHT_BRUTTO=gross,WEIGHT_TN=net,COUNT_KOR=boxes,DEFECT_PERC=defect where UID_PALLET=uid;
  end if;
  RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,qty,0,base,version,0);""")
print(json.dumps(files,ensure_ascii=True))
