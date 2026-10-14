declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_MEDIA_ASSET';
 if n=0 then execute immediate q'[create table RRL_STORE_MEDIA_ASSET(
  SHA256 varchar2(64) primary key,MIME_TYPE varchar2(20) not null check(MIME_TYPE in('image/jpeg','image/png')),
  BYTE_COUNT number not null check(BYTE_COUNT>0 and BYTE_COUNT<=4194304),
  WIDTH_PX number not null check(WIDTH_PX>0),HEIGHT_PX number not null check(HEIGHT_PX>0),
  CONTENT_BYTES blob not null,CREATED_AT timestamp with time zone default systimestamp not null,
  constraint RRL_STORE_MEDIA_PIXELS_CK check(WIDTH_PX*HEIGHT_PX<=12000000))]';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIPT_PHOTO';
 if n=0 then execute immediate q'[create table RRL_STORE_RECEIPT_PHOTO(
  PHOTO_ID varchar2(64) primary key,LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
  STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
  VIEW_CODE varchar2(10) not null check(VIEW_CODE in('FRONT','LEFT','RIGHT','BACK','TOP')),
  ASSET_SHA256 varchar2(64) not null references RRL_STORE_MEDIA_ASSET(SHA256),
  RECORDED_BY varchar2(50) not null,RECORDED_AT timestamp with time zone default systimestamp not null,
  constraint RRL_STORE_PHOTO_SOURCE_UK unique(LOAD_OPERATION_ID,STORE_ADDR,VIEW_CODE,ASSET_SHA256))]';
  execute immediate 'create index RRL_STORE_PHOTO_LOAD_I1 on RRL_STORE_RECEIPT_PHOTO(LOAD_OPERATION_ID,STORE_ADDR,RECORDED_AT)';end if;
end;
/
