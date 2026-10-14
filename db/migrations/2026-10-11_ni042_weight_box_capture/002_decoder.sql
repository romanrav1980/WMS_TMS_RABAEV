create or replace package RRL_WEIGHT_BOX_READ authid definer as
 function decode_json(p_scan varchar2)return clob;
 procedure assert_sku(p_article varchar2,p_gtin varchar2 default null);
end;
/
create or replace package body RRL_WEIGHT_BOX_READ as
 procedure assert_sku(p_article varchar2,p_gtin varchar2 default null)is n number;begin
  select count(*)into n from RRL_ARTICULS a where a.ACTICUL=p_article and a.TYPE_W in(2,3,5,6,7)
   and exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=a.ACTICUL and u.BASE_UOM='KG'and u.INPUT_UOM='KG'and u.NUMERATOR=1 and u.DENOMINATOR=1)
   and(p_gtin is null
    or (regexp_like(a.BARCODE_SHT,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_SHT,14,'0'))
    or (regexp_like(a.BARCODE_KOR,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_KOR,14,'0'))
    or (regexp_like(a.BARCODE_BL,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_BL,14,'0')));
  if n!=1 then raise_application_error(-20886,'WEIGHT_BOX_CURRENT_KG_SKU_AND_GTIN_REQUIRED');end if;
 end;
 function decode_json(p_scan varchar2)return clob is
  v varchar2(512);pos number:=1;stop number;data_start number;ai varchar2(512);data_value varchar2(512);fixed_size number;
  gtin varchar2(14);serial varchar2(20);mass number;digits number;sum_check number:=0;human boolean;seen json_object_t:=json_object_t();j json_object_t:=json_object_t();
 begin
  if p_scan is null or lengthb(p_scan)>512 or instr(p_scan,chr(0))>0 then raise_application_error(-20886,'WEIGHT_BOX_SCAN_BOUND_512');end if;
  v:=p_scan;
  if substr(v,1,3)in(']C1',']d2')then v:=substr(v,4);end if;human:=substr(v,1,1)='(';
  while pos<=length(v)loop
   if seen.get_size>=3 then raise_application_error(-20886,'WEIGHT_BOX_ONLY_AI01_310N_21_SUPPORTED');end if;
   if human then
    if substr(v,pos,1)!='('then raise_application_error(-20886,'WEIGHT_BOX_HRI_AI_REQUIRED');end if;
    stop:=instr(v,')',pos);if stop=0 then raise_application_error(-20886,'WEIGHT_BOX_HRI_AI_REQUIRED');end if;
    ai:=substr(v,pos+1,stop-pos-1);data_start:=stop+1;stop:=instr(v,'(',data_start);
    if stop=0 then stop:=length(v)+1;end if;data_value:=substr(v,data_start,stop-data_start);pos:=stop;
   else
    ai:=case when substr(v,pos,3)='310'then substr(v,pos,4)else substr(v,pos,2)end;pos:=pos+length(ai);
    fixed_size:=case when ai='01'then 14 when regexp_like(ai,'^310[0-5]$','c')then 6 end;
    if fixed_size is not null then data_value:=substr(v,pos,fixed_size);pos:=pos+fixed_size;
    elsif ai='21'then
     stop:=instr(v,chr(29),pos);if stop=0 then stop:=length(v)+1;end if;
     data_value:=substr(v,pos,stop-pos);pos:=stop;
    else raise_application_error(-20886,'WEIGHT_BOX_UNSUPPORTED_AI');end if;
    if substr(v,pos,1)=chr(29)then pos:=pos+1;end if;
   end if;
   if seen.has(ai)then raise_application_error(-20886,'WEIGHT_BOX_DUPLICATE_AI');end if;seen.put(ai,true);
   if ai='01'then
    if gtin is not null or not regexp_like(data_value,'^[0-9]{14}$','c')then raise_application_error(-20886,'WEIGHT_BOX_GTIN14_REQUIRED');end if;gtin:=data_value;
   elsif regexp_like(ai,'^310[0-5]$','c')then
    if mass is not null or not regexp_like(data_value,'^[0-9]{6}$','c')then raise_application_error(-20886,'WEIGHT_BOX_ONE_NET_KG_REQUIRED');end if;
    digits:=to_number(substr(ai,4,1));mass:=to_number(data_value)/power(10,digits);
    if mass<=0 then raise_application_error(-20886,'WEIGHT_BOX_POSITIVE_NET_KG_REQUIRED');end if;
   elsif ai='21'then
    if serial is not null or data_value is null or lengthb(data_value)>20 then raise_application_error(-20886,'WEIGHT_BOX_UNIQUE_SERIAL_REQUIRED');end if;
    for i in 1..length(data_value)loop if ascii(substr(data_value,i,1))<33 or ascii(substr(data_value,i,1))>126 then raise_application_error(-20886,'WEIGHT_BOX_SERIAL_ASCII_REQUIRED');end if;end loop;
    serial:=data_value;
   else raise_application_error(-20886,'WEIGHT_BOX_ONLY_AI01_310N_21_SUPPORTED');end if;
  end loop;
  if gtin is null or serial is null or mass is null then raise_application_error(-20886,'WEIGHT_BOX_GTIN_WEIGHT_SERIAL_REQUIRED');end if;
  for i in 1..13 loop sum_check:=sum_check+to_number(substr(gtin,i,1))*case when mod(i,2)=1 then 3 else 1 end;end loop;
  if to_number(substr(gtin,14,1))!=mod(10-mod(sum_check,10),10)then raise_application_error(-20886,'WEIGHT_BOX_GTIN_CHECK_DIGIT_INVALID');end if;
  j.put('raw_scan',p_scan);j.put('gtin',gtin);j.put('serial',serial);j.put('identity','01'||gtin||'21'||serial);j.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(mass));j.put('physical_box_count',1);j.put('weight_source','GS1_LABEL_NET_KG');j.put('government_confirmation',false);return j.to_clob;
 end;
end;
/
