-- The owner reset physical stock. Preserve explicit legacy unit types, never infer missing units.
declare v_state varchar2(20);n number;
begin
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v_state!='PREPARED' then raise_application_error(-20808,'LEGACY_UOM_BOOTSTRAP_REQUIRES_PREPARED');end if;
 select count(*) into n from RRL_REMAINS;
 if n!=0 then raise_application_error(-20808,'LEGACY_UOM_BOOTSTRAP_REQUIRES_ZERO_STOCK');end if;
 RRL_STOCK_CONFIG_API.begin_change('admin','warehouse_settings_edit');
 insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)
 with cards as(
  select ACTICUL ARTICUL,max(UNIT_TYPE) LEGACY_UOM,max(COUNT_SHT_IN_KOR) PACK,
   case when upper(max(UNIT_TYPE)) in('EA','PCS','ST','ШТ') then 'EA' else 'KG' end BASE_UOM
  from RRL_ARTICULS where ACTICUL is not null group by ACTICUL
  having count(*)=1 and upper(max(UNIT_TYPE)) in('EA','PCS','ST','ШТ','KG','КГ')
 ), eligible as(select c.* from cards c where not exists(select 1 from RRL_STOCK_UOM_CONVERSION u where u.ARTICUL=c.ARTICUL)),
 aliases as(
  select ARTICUL,BASE_UOM INPUT_UOM,BASE_UOM,1 NUM,1 DEN from eligible
  union select ARTICUL,LEGACY_UOM,BASE_UOM,1,1 from eligible
  union select ARTICUL,'PCS',BASE_UOM,1,1 from eligible where BASE_UOM='EA'
  union select ARTICUL,'ST',BASE_UOM,1,1 from eligible where BASE_UOM='EA'
  union select ARTICUL,'ШТ',BASE_UOM,1,1 from eligible where BASE_UOM='EA'
  union select ARTICUL,'BOX',BASE_UOM,PACK,1 from eligible where BASE_UOM='EA' and PACK between 1 and 1000000000 and PACK=trunc(PACK)
  union select ARTICUL,'CAR',BASE_UOM,PACK,1 from eligible where BASE_UOM='EA' and PACK between 1 and 1000000000 and PACK=trunc(PACK)
  union select ARTICUL,'CS',BASE_UOM,PACK,1 from eligible where BASE_UOM='EA' and PACK between 1 and 1000000000 and PACK=trunc(PACK)
  union select ARTICUL,'KAR',BASE_UOM,PACK,1 from eligible where BASE_UOM='EA' and PACK between 1 and 1000000000 and PACK=trunc(PACK)
 )
 select ARTICUL,INPUT_UOM,BASE_UOM,1,NUM,DEN,case when BASE_UOM='EA' then 0 else 3 end,'LEGACY_EXPLICIT_UNIT_ZERO_STOCK_20261008' from aliases;
 insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)
 select a.ARTICUL,1,greatest(nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU f where f.ARTICUL=a.ARTICUL),0),
  case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=a.ARTICUL) then 1 else 0 end),'STOCK_BOOTSTRAP'
 from(select distinct ARTICUL from RRL_STOCK_UOM_CONVERSION)a
 where not exists(select 1 from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=a.ARTICUL);
 RRL_STOCK_CONFIG_API.end_change;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-031-explicit-legacy-uom' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Zero-stock bootstrap from explicit legacy unit types; NULL/ambiguous cards excluded; exact piece/box and kg factors',sysdate,user,'075_legacy_uom_bootstrap.sql','075_legacy_uom_bootstrap_rollback.sql','APPLIED');
commit;
