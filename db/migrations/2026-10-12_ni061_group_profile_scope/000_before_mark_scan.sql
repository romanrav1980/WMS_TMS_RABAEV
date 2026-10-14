create or replace package body RRL_INTERWARE_MARK_SCAN as  

 function marked(p_article varchar2) return number is n number;  

 begin  

  select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=p_article),0),  

   nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=p_article),0),  

   case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=p_article) then 1 else 0 end) into n from dual;return n;  

 end;  

 function required_for_article(p_article varchar2) return number is begin return marked(p_article);end;  

 function required_for_plan(p_domain clob) return number is  

  d json_object_t:=json_object_t.parse(p_domain);a json_array_t:=d.get_array('legs');l json_object_t;  

 begin  

  for i in 0..a.get_size-1 loop l:=treat(a.get(i) as json_object_t);if marked(l.get_string('article'))=1 then return 1;end if;end loop;return 0;  

 end;  

 procedure validate_scan(p_domain clob,p_metadata clob,p_unit_count out number) is  

  d json_object_t:=json_object_t.parse(p_domain);m json_object_t:=json_object_t.parse(p_metadata);  

  a json_array_t:=d.get_array('legs');scans json_array_t:=json_array_t();l json_object_t;x json_object_t;  

  v_uid varchar2(150);v_cell varchar2(60);v_article varchar2(160);v_base varchar2(20);v_qty number;v_sum number;v_count number;v_profiles number;  

  v_expected number:=0;v_resolved number:=0;scans_clob clob;selected_clob clob;v_key varchar2(4000);  

  type seen_map is table of number index by varchar2(4000);expected seen_map;seen_uids seen_map;  

  type index_map is table of number index by pls_integer;resolved index_map;  

  function profile_key(p_unit varchar2,p_system varchar2,p_profile varchar2) return varchar2 is  

  begin return rawtohex(RRL_STOCK_LOCK_API.resource_key('QCMARK',p_unit,rawtohex(RRL_STOCK_LOCK_API.resource_key('PROFILE',p_system,p_profile))));end;  

 begin  

  p_unit_count:=0;  

  RRL_IW_AGG_SCAN.expand(p_metadata,scans_clob);scans:=json_array_t.parse(scans_clob);  

  if scans.get_size>20000 then raise_application_error(-20881,'QUALITY_MARK_SCAN_BOUND');end if;  

  for i in 0..a.get_size-1 loop  

   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');if marked(v_article)!=1 then continue;end if;  

   selected_clob:=null;if l.has('selected_unit_keys')then selected_clob:=l.get_array('selected_unit_keys').to_clob;end if;  

   v_uid:=l.get_string('uid');v_cell:=l.get_string('cell');v_base:=l.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));  

   if seen_uids.exists(v_uid) then raise_application_error(-20887,'QUALITY_MARK_SPLIT_ALLOCATION_NOT_SUPPORTED');end if;seen_uids(v_uid):=1;  

   select count(*) into v_profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;  

   select count(*)into v_count from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=v_article and(

    p.SCAN_MODE is null or(p.SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION')and not exists(

     select 1 from json_table(p_metadata,'$.aggregation_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',L varchar2(10)path '$.level'))agg

     where agg.S=p.SYSTEM_CODE and agg.P=p.PROFILE_CODE and agg.L=p.SCAN_MODE))

    or(p.SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION')and exists(

     select 1 from json_table(p_metadata,'$.unit_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code'))direct_scan

     where direct_scan.S=p.SYSTEM_CODE and direct_scan.P=p.PROFILE_CODE)));  

   if v_count>0 then raise_application_error(-20887,'INTERWARE_UNIT_CAPTURE_FORBIDDEN_BY_PROFILE');end if;  

   if v_profiles<1 or v_profiles>50 then raise_application_error(-20887,'QUALITY_MARK_PROFILES_REQUIRED');end if;  

   select count(*),sum(BASE_QTY) into v_count,v_sum from RRL_WMS_RECEIPT_UNIT  

    where CURRENT_UID=v_uid and CURRENT_CELL=v_cell and STOCK_STATUS='ISSUED' and BASE_UOM=v_base and(selected_clob is null or exists(select 1 from json_table(selected_clob,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=PHYSICAL_UNIT_KEY));  

   if v_count<1 or v_count>10000 or v_sum!=v_qty then raise_application_error(-20887,'QUALITY_MARK_WHOLE_COMPOSITION_REQUIRED');end if;  

   p_unit_count:=p_unit_count+v_count;if p_unit_count>10000 then raise_application_error(-20881,'QUALITY_PHYSICAL_UNIT_BOUND');end if;  

   -- One bounded matrix query per allocation, never a profile SELECT per physical unit.  

   for z in(select u.PHYSICAL_UNIT_KEY,p.SYSTEM_CODE,p.PROFILE_CODE from RRL_WMS_RECEIPT_UNIT u cross join RRL_SKU_RECEIPT_PROFILE p  

    where u.CURRENT_UID=v_uid and u.CURRENT_CELL=v_cell and u.STOCK_STATUS='ISSUED' and u.BASE_UOM=v_base and(selected_clob is null or exists(select 1 from json_table(selected_clob,'$[*]'columns(K varchar2(64)path '$'))chosen where chosen.K=u.PHYSICAL_UNIT_KEY)) and p.ARTICUL=v_article  

    order by u.PHYSICAL_UNIT_KEY,p.SYSTEM_CODE,p.PROFILE_CODE fetch first 20001 rows only) loop  

    v_expected:=v_expected+1;if v_expected>20000 then raise_application_error(-20881,'QUALITY_MARK_PROFILE_MATRIX_BOUND');end if;  

    expected(profile_key(z.PHYSICAL_UNIT_KEY,z.SYSTEM_CODE,z.PROFILE_CODE)):=0;  

   end loop;  

  end loop;  

  for i in 0..scans.get_size-1 loop  

   x:=treat(scans.get(i) as json_object_t);  

   if x.get_string('system_code') is null or x.get_string('profile_code') is null or x.get_string('code_hash') is null  

    or not regexp_like(x.get_string('code_hash'),'^[a-f0-9]{64}$') then raise_application_error(-20871,'QUALITY_MARK_SCAN_INVALID');end if;  

  end loop;  

  scans_clob:=scans.to_clob;  

  -- One indexed code-registry join. In-memory framed keys enforce exact unit/profile set coverage.  

  for z in(select j.I,j.S,j.P,u.PHYSICAL_UNIT_KEY from  

   json_table(scans_clob,'$[*]' columns(I for ordinality,S varchar2(40) path '$.system_code',P varchar2(80) path '$.profile_code',H varchar2(64) path '$.code_hash'))j  

   join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.S and c.CODE_HASH=j.H  

   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID  

   where u.STOCK_STATUS='ISSUED' and exists(select 1 from json_table(c.PROFILES_JSON,'$[*]' columns(P varchar2(80) path '$.profile'))pr where pr.P=j.P)) loop  

   v_key:=profile_key(z.PHYSICAL_UNIT_KEY,z.S,z.P);  

   if not expected.exists(v_key) then raise_application_error(-20886,'QUALITY_FOREIGN_UNIT_OR_PROFILE');end if;  

   if resolved.exists(z.I) or expected(v_key)=1 then raise_application_error(-20871,'QUALITY_DUPLICATE_MARK_SCAN');end if;  

   resolved(z.I):=1;expected(v_key):=1;v_resolved:=v_resolved+1;  

  end loop;  

  if v_resolved!=scans.get_size then raise_application_error(-20886,'QUALITY_FOREIGN_UNIT_OR_PROFILE');end if;  

  if v_resolved!=v_expected then raise_application_error(-20886,'QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED');end if;  

 end;  

end;


/
