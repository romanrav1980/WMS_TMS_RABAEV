create or replace package RRL_STORE_EVIDENCE_API authid definer as
 procedure register_photo(p_load varchar2,p_store varchar2,p_view varchar2,p_actor varchar2,p_mime varchar2,p_width number,p_height number,p_bytes blob,p_result out clob);
 function photos_json(p_load varchar2,p_store varchar2,p_actor varchar2) return clob;
end;
/
create or replace context RRL_STORE_MEDIA_CTX using RABAEV.RRL_STORE_EVIDENCE_API;
/
create or replace package body RRL_STORE_EVIDENCE_API as
 procedure clear_context is
 begin
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','TX_ID',null);
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','ASSET_HASH',null);
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','PHOTO_ID',null);
 end;
 procedure register_photo(p_load varchar2,p_store varchar2,p_view varchar2,p_actor varchar2,p_mime varchar2,p_width number,p_height number,p_bytes blob,p_result out clob) is
  source_json clob;sha varchar2(64);photo_key varchar2(64);size_no number;n number;comparison_no number;j json_object_t:=json_object_t();identity_text clob;old_mime varchar2(20);old_width number;old_height number;
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20886,'PHOTO_UPLOAD_OUTSIDE_STOCK_TRANSACTION_REQUIRED');end if;
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(p_load,p_actor,p_store,source_json);
  size_no:=dbms_lob.getlength(p_bytes);
  if p_mime is null or p_mime not in('image/jpeg','image/png') or p_view is null or p_view not in('FRONT','LEFT','RIGHT','BACK','TOP')
   or size_no is null or size_no<1 or size_no>4194304 or p_width is null or p_height is null or least(p_width,p_height)<1
   or p_width*p_height>12000000 or p_width!=trunc(p_width) or p_height!=trunc(p_height) then raise_application_error(-20886,'PHOTO_ARCHIVE_CONTRACT_INVALID');end if;
  sha:=rawtohex(sys.dbms_crypto.hash(p_bytes,sys.dbms_crypto.hash_sh256));
  declare a json_array_t:=json_array_t();begin a.append(p_load);a.append(p_store);a.append(p_view);a.append(sha);identity_text:=a.to_clob;end;
  photo_key:=rawtohex(sys.dbms_crypto.hash(identity_text,sys.dbms_crypto.hash_sh256));
  select TT_ID into n from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load for update;
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(p_load,p_actor,p_store,source_json);
  select count(*) into n from RRL_STORE_RECEIPT_PHOTO where PHOTO_ID=photo_key;
  if n=0 then
   select count(*) into n from RRL_STORE_RECEIPT_PHOTO where LOAD_OPERATION_ID=p_load and STORE_ADDR=p_store;
   if n>=12 then raise_application_error(-20881,'PHOTO_ARCHIVE_LIMIT_12');end if;
  end if;
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','ASSET_HASH',sha);
  dbms_session.set_context('RRL_STORE_MEDIA_CTX','PHOTO_ID',photo_key);
  begin
   insert into RRL_STORE_MEDIA_ASSET(SHA256,MIME_TYPE,BYTE_COUNT,WIDTH_PX,HEIGHT_PX,CONTENT_BYTES)values(sha,p_mime,size_no,p_width,p_height,p_bytes);
  exception when dup_val_on_index then
   select MIME_TYPE,WIDTH_PX,HEIGHT_PX,dbms_lob.compare(CONTENT_BYTES,p_bytes) into old_mime,old_width,old_height,comparison_no from RRL_STORE_MEDIA_ASSET where SHA256=sha;
   if old_mime!=p_mime or old_width!=p_width or old_height!=p_height or comparison_no is null or comparison_no!=0 then raise_application_error(-20886,'PHOTO_ASSET_HASH_CONTENT_CONFLICT');end if;
  end;
  begin
   insert into RRL_STORE_RECEIPT_PHOTO(PHOTO_ID,LOAD_OPERATION_ID,STORE_ADDR,VIEW_CODE,ASSET_SHA256,RECORDED_BY)values(photo_key,p_load,p_store,p_view,sha,p_actor);
  exception when dup_val_on_index then
   select count(*) into n from RRL_STORE_RECEIPT_PHOTO where PHOTO_ID=photo_key and LOAD_OPERATION_ID=p_load and STORE_ADDR=p_store and VIEW_CODE=p_view and ASSET_SHA256=sha;
   if n!=1 then raise_application_error(-20886,'PHOTO_SOURCE_IDENTITY_CONFLICT');end if;
  end;
  clear_context;
  j.put('photo_id',photo_key);j.put('load_operation_id',p_load);j.put('store_address',p_store);j.put('view',p_view);j.put('sha256',sha);j.put('byte_count',size_no);j.put('mime_type',p_mime);j.put('width_px',p_width);j.put('height_px',p_height);j.put('status','ARCHIVED');p_result:=j.to_clob;
 exception when others then clear_context;raise;
 end;
 function photos_json(p_load varchar2,p_store varchar2,p_actor varchar2) return clob is source_json clob;a json_array_t:=json_array_t();j json_object_t;n number:=0;
 begin
  RRL_STOCK_STORE_RECEIPT_READ.describe_load(p_load,p_actor,p_store,source_json);
  for r in(select p.PHOTO_ID,p.VIEW_CODE,p.ASSET_SHA256,p.RECORDED_BY,p.RECORDED_AT,s.MIME_TYPE,s.BYTE_COUNT,s.WIDTH_PX,s.HEIGHT_PX
    from RRL_STORE_RECEIPT_PHOTO p join RRL_STORE_MEDIA_ASSET s on s.SHA256=p.ASSET_SHA256
    where p.LOAD_OPERATION_ID=p_load and p.STORE_ADDR=p_store order by p.RECORDED_AT,p.PHOTO_ID fetch first 13 rows only)loop
   n:=n+1;if n>12 then raise_application_error(-20881,'PHOTO_ARCHIVE_LIST_BOUND_12');end if;
   j:=json_object_t();j.put('photo_id',r.PHOTO_ID);j.put('view',r.VIEW_CODE);j.put('sha256',r.ASSET_SHA256);j.put('recorded_by',r.RECORDED_BY);j.put('recorded_at',to_char(r.RECORDED_AT,'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM'));j.put('mime_type',r.MIME_TYPE);j.put('byte_count',r.BYTE_COUNT);j.put('width_px',r.WIDTH_PX);j.put('height_px',r.HEIGHT_PX);a.append(j);
  end loop;return a.to_clob;
 end;
end;
/
