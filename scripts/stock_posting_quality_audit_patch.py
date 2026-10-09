import json
from pathlib import Path
D=Path("db/migrations/2026-10-08_stock_posting_core");p=D/"183_pallet_quality_command.sql";s=p.read_text(encoding="utf-8")
# The old terminal audit changes are part of this command, never pre-DML.
needle=" procedure compile_command(p_request clob,p_operation"
at=s.index(needle,s.index("create or replace package body"))
helper=""" procedure terminal_audit(p_request clob,p_uid varchar2) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');t json_object_t;x json_object_t;a json_array_t;
  v_article varchar2(160);v_qty number;v_time varchar2(30);v_zone varchar2(60);n number;
 begin
  if not m.has('terminal_audit') then return;end if;
  t:=m.get_object('terminal_audit');a:=t.get_array('errors');
  if a.get_size>200 or t.get_array('vp_lines').get_size>200 then raise_application_error(-20881,'QUALITY_AUDIT_BOUND');end if;
  if a.get_size>0 and m.get_number('error_count')=0 then raise_application_error(-20871,'QUALITY_ERRORS_WITH_ZERO_COUNT');end if;
  delete from LOT_AUDIT where SSCC=p_uid;delete from LOT_AUDIT_ERROR_LINES where SSCC=p_uid;
  v_zone:=unistr('\\0417\\041E\\041D\\0410_\\042D\\041A\\0421\\041F\\0415\\0414\\0418\\0426\\0418\\0418');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);v_article:=x.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   if x.get_string('condition')=unistr('\\041D\\0415\\0414\\041E\\0421\\0422\\0410\\0427\\0410') then v_zone:=unistr('\\0417\\041E\\041D\\0410_\\041E\\0428\\0418\\0411\\041E\\041A');end if;
   update RRL_SBORKA_PALLET_ROWS set SOBRANO=v_qty where PALLET_UID=p_uid and ARTICUL=v_article;
   if sql%rowcount!=1 then raise_application_error(-20887,'QUALITY_AUDIT_ARTICLE_NOT_UNIQUE');end if;
  end loop;
  a:=t.get_array('vp_lines');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);v_article:=x.get_string('article');v_time:=x.get_string('checked_at');
   update RRL_SBORKA_PALLET_ROWS set TIME_OF_CHECKING=to_date(v_time,'FXYYYY-MM-DD HH24:MI:SS') where PALLET_UID=p_uid and ARTICUL=v_article;
   if sql%rowcount!=1 then raise_application_error(-20887,'QUALITY_AUDIT_ARTICLE_NOT_UNIQUE');end if;
  end loop;
  insert into LOT_AUDIT(SSCC,CONDITION) values(p_uid,v_zone);
 end;
"""
s=s[:at]+helper+s[at:]
needle="  v.put('quality',q);p_domain"
s=s.replace(needle,"  if d.get_object('metadata').has('terminal_audit') then\n   RRL_STOCK_PLAN_HELPER.row_key(r,'LOT_AUDIT',v_uid);RRL_STOCK_PLAN_HELPER.row_key(r,'LOT_AUDIT_ERROR_LINES',v_uid);\n  end if;\n"+needle,1)
needle="  if shipped=1 then\n   sh:=json_object_t.parse(p_request);sh.put('command_type','SHIP_PALLET');\n   RRL_STOCK_SHIPPING_CORE.execute_shipment"
s=s.replace(needle,"  terminal_audit(p_request,v_uid);\n"+needle,1)
print(json.dumps({str(p):s},ensure_ascii=True))
