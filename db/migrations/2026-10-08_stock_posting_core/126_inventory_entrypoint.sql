create or replace function RRL_ADD_INV_LINE(
 CELL5 varchar2,articul5 varchar2,COUNT15 number,date_of_expire5 date,PRICE5 number,inventory_id int,iser_id5 varchar2,
 p_operation_id varchar2 default null) return varchar2 authid definer is
 st varchar2(20);uid varchar2(200);operation varchar2(100);j json_object_t:=json_object_t();src json_object_t:=json_object_t();m json_object_t:=json_object_t();result clob;
begin
 select STATE into st from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if st='PREPARED' then return RRL_ADD_INV_LINE_SP_OLD(CELL5,articul5,COUNT15,date_of_expire5,PRICE5,inventory_id,iser_id5);end if;
 uid:='P_'||articul5||'_G'||to_char(inventory_id,'TM9')||'_'||CELL5;
 operation:=nvl(p_operation_id,'INV.REG:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(uid,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 j.put('contract_version',2);j.put('operation_id',operation);j.put('command_type','INVENTORY_REGISTER_LOT');j.put('actor',iser_id5);
 src.put('revision_id',inventory_id);j.put('source',src);j.put('lines',json_array_t());j.put('units',json_array_t());
 m.put('uid',uid);m.put('cell',CELL5);m.put('article',articul5);m.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(COUNT15));
 m.put('expiry_date',to_char(date_of_expire5,'YYYY-MM-DD'));m.put('price',PRICE5);m.put('reason','Initial inventory import');j.put('metadata',m);
 RRL_STOCK_NATIVE_API.post(j.to_clob,iser_id5,result);return '';
end;
/
