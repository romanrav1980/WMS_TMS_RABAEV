create or replace package RRL_STOCK_QC_ITEM authid definer as
 procedure resolve_barcode(p_code varchar2,p_article out varchar2,p_input_uom out varchar2);
 procedure validate_scan(p_domain clob,p_metadata clob);
end;
/
create or replace package body RRL_STOCK_QC_ITEM as
 procedure resolve_barcode(p_code varchar2,p_article out varchar2,p_input_uom out varchar2) is n number:=0;
 begin
  if p_code is null or lengthb(p_code)>128 then raise_application_error(-20886,'QUALITY_FOREIGN_ITEM_BARCODE');end if;
  for z in(select ACTICUL ARTICLE,'EA' INPUT_UOM from RRL_ARTICULS where BARCODE_SHT=p_code
    union all select ACTICUL,'BOX' from RRL_ARTICULS where BARCODE_KOR=p_code) loop
   n:=n+1;if n>1 then raise_application_error(-20887,'QUALITY_ITEM_BARCODE_AMBIGUOUS');end if;
   p_article:=z.ARTICLE;p_input_uom:=z.INPUT_UOM;
  end loop;
  if n!=1 then raise_application_error(-20886,'QUALITY_FOREIGN_ITEM_BARCODE');end if;
 end;

 procedure validate_scan(p_domain clob,p_metadata clob) is
  d json_object_t:=json_object_t.parse(p_domain);m json_object_t:=json_object_t.parse(p_metadata);a json_array_t:=d.get_array('legs');scans json_array_t:=json_array_t();
  l json_object_t;x json_object_t;v_article varchar2(160);v_base varchar2(20);v_code varchar2(128);v_event varchar2(100);v_input varchar2(20);
  v_qty number;v_value number;v_version number;v_num number;v_den number;v_scale number;v_matches number;k varchar2(160);v_hash varchar2(128);
  type quantity_map is table of number index by varchar2(160);expected quantity_map;actual quantity_map;
  type unit_map is table of varchar2(20) index by varchar2(160);base_units unit_map;
  type event_map is table of varchar2(128) index by varchar2(100);events event_map;
  type article_cache is table of varchar2(160) index by varchar2(128);articles article_cache;
  type amount_cache is table of number index by varchar2(128);amounts amount_cache;
 begin
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');
   if RRL_STOCK_QC_MARK.required_for_article(v_article)=1 then continue;end if;
   v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));v_base:=l.get_string('base_uom');
   if not expected.exists(v_article) then expected(v_article):=0;base_units(v_article):=v_base;end if;
   if base_units(v_article)!=v_base then raise_application_error(-20887,'QUALITY_ITEM_BASE_UOM_CONFLICT');end if;
   expected(v_article):=expected(v_article)+v_qty;
  end loop;
  if m.has('item_scans') then scans:=m.get_array('item_scans');end if;
  if scans.get_size>20000 then raise_application_error(-20881,'QUALITY_ITEM_SCAN_BOUND');end if;
  for i in 0..scans.get_size-1 loop
   x:=treat(scans.get(i) as json_object_t);v_code:=x.get_string('barcode');v_event:=x.get_string('scan_id');v_qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   if v_qty!=1 then raise_application_error(-20871,'QUALITY_UNIT_SCAN_ONE_ITEM_REQUIRED');end if;
   if v_code is null or v_event is null then raise_application_error(-20871,'QUALITY_ITEM_SCAN_FIELDS_REQUIRED');end if;
   v_hash:=rawtohex(RRL_STOCK_LOCK_API.resource_key('QCITEM',v_code,RRL_STOCK_PLAN_HELPER.decimal_text(v_qty)));
   if events.exists(v_event) then
    if events(v_event)!=v_hash then raise_application_error(-20871,'QUALITY_ITEM_SCAN_EVENT_CONTENT_CONFLICT');end if;
    continue;
   end if;events(v_event):=v_hash;v_matches:=0;
   if articles.exists(v_code) then v_article:=articles(v_code);v_value:=amounts(v_code);else
   resolve_barcode(v_code,v_article,v_input);v_matches:=1;
   if v_matches!=1 or not expected.exists(v_article) then raise_application_error(-20886,'QUALITY_FOREIGN_ITEM_BARCODE');end if;
   select max(POLICY_VERSION) into v_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_input and POLICY_VERSION=v_version;
   if v_base!=base_units(v_article) then raise_application_error(-20887,'QUALITY_ITEM_BASE_UOM_CONFLICT');end if;
   v_value:=RRL_STOCK_MATH.convert_exact(x.get_string('quantity'),v_num,v_den,v_scale);
    articles(v_code):=v_article;amounts(v_code):=v_value;
   end if;
   if not actual.exists(v_article) then actual(v_article):=0;end if;
   actual(v_article):=actual(v_article)+v_value;
   if actual(v_article)>expected(v_article) then raise_application_error(-20886,'QUALITY_ITEM_QUANTITY_EXCESS');end if;
  end loop;
  k:=expected.first;while k is not null loop
   if not actual.exists(k) then raise_application_error(-20886,'QUALITY_ITEM_COMPOSITION_COVERAGE_REQUIRED:'||k);end if;
   if actual(k)!=expected(k) then raise_application_error(-20886,'QUALITY_ITEM_COMPOSITION_COVERAGE_REQUIRED:'||k);end if;k:=expected.next(k);
  end loop;
 end;
end;
/
