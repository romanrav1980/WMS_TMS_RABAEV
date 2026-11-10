begin execute immediate q'[create table RRL_TRADE_TOPUP_PALLETIZATION(
 WARE_ID number not null,
 SKU_ID varchar2(100 char) not null,
 PALLET_TYPE_ID number not null,
 BOXES_PER_PLACE number not null,
 MAX_STACK_LAYERS number default 1 not null,
 ACTIVE number default 1 not null,
 VERSION_NO number default 1 not null,
 CREATED_AT timestamp default systimestamp not null,
 CREATED_BY varchar2(100 char) not null,
 UPDATED_AT timestamp default systimestamp not null,
 UPDATED_BY varchar2(100 char) not null,
 constraint RRL_TRADE_TOPUP_PALLETIZATION_PK primary key(WARE_ID,SKU_ID),
 constraint RRL_TRADE_TOPUP_PALLETIZATION_PT_FK foreign key(PALLET_TYPE_ID) references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 constraint RRL_TRADE_TOPUP_PALLETIZATION_CHK check(BOXES_PER_PLACE>0 and MAX_STACK_LAYERS>=1 and ACTIVE in(0,1) and VERSION_NO>=1)
)]';end;
/
begin execute immediate 'create index RRL_TRADE_TOPUP_PALLETIZATION_IX on RRL_TRADE_TOPUP_PALLETIZATION(PALLET_TYPE_ID,ACTIVE)';end;
/