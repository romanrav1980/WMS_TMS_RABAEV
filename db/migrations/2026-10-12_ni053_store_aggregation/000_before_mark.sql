create or replace package body RRL_STORE_MARK_CORE as 

 function stock_leaf(p_tree json_object_t)return json_object_t is

 nodes json_array_t:=p_tree.get_array('nodes');node json_object_t;candidate json_object_t;n number:=0;

 begin

 if nodes.get_size<1 or nodes.get_size>200 or p_tree.get_number('leaf_count')!=1 or p_tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;

 for i in 0..nodes.get_size-1 loop

 candidate:=treat(nodes.get(i)as json_object_t);

 if candidate.get_string('kind')='STOCK'then node:=candidate;n:=n+1;

 elsif candidate.get_string('kind')not in('CONTAINER','CASE')then raise_application_error(-20886,'STORE_MARK_NESTED_STOCK_ONLY_REQUIRED');end if;

 end loop;

 if n!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;

 return node;

 end;

 function stock_leaves(p_tree json_object_t)return json_array_t is

 nodes json_array_t:=p_tree.get_array('nodes');result json_array_t:=json_array_t();candidate json_object_t;

 begin

 if nodes.get_size<1 or nodes.get_size>200 or p_tree.get_number('leaf_count')<1 or p_tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_FROZEN_STOCK_SCOPE_REQUIRED');end if;

 for i in 0..nodes.get_size-1 loop candidate:=treat(nodes.get(i)as json_object_t);

 if candidate.get_string('kind')='STOCK'then result.append(candidate);

 elsif candidate.get_string('kind')not in('CONTAINER','CASE')then raise_application_error(-20886,'STORE_MARK_NESTED_STOCK_ONLY_REQUIRED');end if;end loop;

 if result.get_size!=p_tree.get_number('leaf_count')then raise_application_error(-20886,'STORE_MARK_EXACT_STOCK_LEAVES_REQUIRED');end if;return result;

 end;

 function source_proof(p_domain json_object_t)return json_object_t is

 tree json_object_t:=p_domain.get_object('snapshot');leaves json_array_t;node json_object_t;proof json_object_t:=json_object_t();leafproof json_object_t;

 allunits json_array_t:=json_array_t();signatures json_array_t:=json_array_t();units json_array_t;unit_value json_object_t;signature_entry json_object_t;

 profiles clob;first_profiles clob;n number;bad number;matched number;scan_total number:=0;profile_union json_array_t:=json_array_t();ordinary_lots json_array_t:=json_array_t();current_profiles json_array_t;profile_item json_object_t;profile_key varchar2(500);article varchar2(160);wire clob;v_lot_uid varchar2(200);

 type keys_map is table of number index by varchar2(64);seen keys_map;seen_profiles keys_map;k varchar2(64);

 begin

 leaves:=stock_leaves(tree);

 for z in 0..leaves.get_size-1 loop

 node:=treat(leaves.get(z)as json_object_t);article:=node.get_string('article');v_lot_uid:=node.get_string('uid');

 wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_domain.get_string('load_operation_id'),node.get_string('uid'),tree.to_clob);leafproof:=json_object_t.parse(wire);

 select count(*),sum(case when SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')then 0 else 1 end),

 json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)

 into n,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article;

 units:=leafproof.get_array('units');

 if n=0 and units.get_size=0 then ordinary_lots.append(node.get_string('uid'));

 else

 if n=0 or units.get_size=0 then raise_application_error(-20886,'STORE_MARK_UNIT_PROFILE_MATRIX_REQUIRED');end if;

 if n>50 or bad!=0 or leafproof.get_number('physical_unit_count')<1 then raise_application_error(-20886,'STORE_MARK_CURRENT_UNIT_PROFILES_REQUIRED');end if;

 current_profiles:=json_array_t.parse(profiles);

 for pi in 0..current_profiles.get_size-1 loop profile_item:=treat(current_profiles.get(pi)as json_object_t);

 profile_key:=rawtohex(sys.dbms_crypto.hash(profile_item.to_clob,sys.dbms_crypto.hash_sh256));

 if not seen_profiles.exists(profile_key)then seen_profiles(profile_key):=1;profile_union.append(profile_item);end if;end loop;

 if profile_union.get_size>50 then raise_application_error(-20881,'STORE_MARK_PROFILE_UNION_BOUND_50');end if;

 select count(distinct u.PHYSICAL_UNIT_KEY||':'||c.SYSTEM_CODE||':'||pr.PROFILE_CODE)into matched

 from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID

,json_table(c.PROFILES_JSON,'$[*]'columns(PROFILE_CODE varchar2(80)path '$.profile',PROFILE_VERSION varchar2(40)path '$.version'))pr

,RRL_SKU_RECEIPT_PROFILE profile where profile.ARTICUL=article and profile.SYSTEM_CODE=c.SYSTEM_CODE and profile.PROFILE_CODE=pr.PROFILE_CODE and profile.PROFILE_VERSION=pr.PROFILE_VERSION

 and u.CURRENT_UID=v_lot_uid and u.STOCK_STATUS='ISSUED';

 if matched!=n*leafproof.get_number('physical_unit_count')then raise_application_error(-20886,'STORE_MARK_CURRENT_SAVED_CODE_PROFILE_VERSION_REQUIRED');end if;

 units:=leafproof.get_array('units');

 for i in 0..units.get_size-1 loop unit_value:=treat(units.get(i)as json_object_t);k:=unit_value.get_string('key');

 if seen.exists(k)then raise_application_error(-20886,'STORE_MARK_DUPLICATE_PHYSICAL_UNIT');end if;seen(k):=1;

 unit_value.put('lot_uid',node.get_string('uid'));unit_value.put('article',article);unit_value.put('profiles',current_profiles);allunits.append(unit_value);end loop;

 end if;

 signature_entry:=json_object_t();signature_entry.put('uid',node.get_string('uid'));signature_entry.put('signature',leafproof.get_string('unit_signature'));signatures.append(signature_entry);

 scan_total:=scan_total+n*units.get_size;

 if allunits.get_size>10000 or scan_total>20000 then raise_application_error(-20881,'STORE_MARK_SCAN_BOUND');end if;

 end loop;

 if allunits.get_size!=tree.get_number('physical_unit_count')then raise_application_error(-20884,'STORE_MARK_EXACT_TREE_PHYSICAL_UNIT_COUNT');end if;

 proof.put('ordinary_lots',ordinary_lots);proof.put('units',allunits);proof.put('profiles',profile_union);proof.put('supported',true);proof.put('physical_unit_count',allunits.get_size);proof.put('expected_scan_count',scan_total);

 if leaves.get_size=1 then proof.put('unit_signature',leafproof.get_string('unit_signature'));else proof.put('unit_signature',rawtohex(sys.dbms_crypto.hash(signatures.to_clob,sys.dbms_crypto.hash_sh256)));end if;

 return proof;

 end;

 function preview(p_domain json_object_t)return clob is p json_object_t; 

 begin p:=source_proof(p_domain);return p.to_clob; 

 exception when others then 

  if sqlcode between -20999 and -20800 then p:=json_object_t();p.put('supported',false);p.put('reason',substr(sqlerrm,1,250));return p.to_clob;else raise;end if; 

 end; 

 procedure verify_scans(p_domain json_object_t,p_metadata json_object_t,p_proof out json_object_t)is 

 begin p_proof:=source_proof(p_domain);end; 

 function tuple_key(p_unit varchar2,p_system varchar2,p_profile varchar2)return varchar2 is 

 begin return rawtohex(RRL_STOCK_LOCK_API.resource_key('STOREMARK',p_unit,rawtohex(RRL_STOCK_LOCK_API.resource_key('PROFILE',p_system,p_profile))));end; 

 procedure resolve_disposition(p_proof json_object_t,p_metadata json_object_t,p_lines json_array_t,p_units out json_array_t)is 

  units json_array_t:=p_proof.get_array('units');profiles json_array_t:=p_proof.get_array('profiles');scans json_array_t:=json_array_t(); 

  unit_value json_object_t;profile_value json_object_t;scan_value json_object_t;line_value json_object_t;result_value json_object_t; 

  type marks_map is table of number index by varchar2(4000);expected marks_map;resolved marks_map;coverage marks_map; 

  type state_map is table of varchar2(20)index by varchar2(64);states state_map;type count_map is table of number index by varchar2(64);unit_profile_counts count_map; 

  k varchar2(4000);unit_key varchar2(64);disposition varchar2(20);wire clob;resolved_count number:=0; 

  accepted number:=0;missing number:=0;refused number:=0;damaged number:=0;qty number;profile_count number:=profiles.get_size;lot_key varchar2(200);line_lot varchar2(200);

 type qty_map is table of number index by varchar2(200);accepted_lots qty_map;missing_lots qty_map;refused_lots qty_map;damaged_lots qty_map;declared_lots qty_map;ordinary_keys qty_map;ordinary_array json_array_t; 

  function nonnegative(p_text varchar2)return number is 

  begin if regexp_like(p_text,'^0{1,18}([.]0{1,9})?$')then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end; 

 begin

  if p_proof.has('ordinary_lots')then ordinary_array:=p_proof.get_array('ordinary_lots');for i in 0..ordinary_array.get_size-1 loop ordinary_keys(ordinary_array.get_string(i)):=1;end loop;end if;

  if p_metadata.has('unit_scans')then scans:=p_metadata.get_array('unit_scans');end if; 

  if scans.get_size>20000 or p_lines.get_size<1 or p_lines.get_size>200 then raise_application_error(-20881,'STORE_MARK_DISPOSITION_BOUND');end if; 

  for i in 0..units.get_size-1 loop 

   unit_value:=treat(units.get(i)as json_object_t);unit_key:=unit_value.get_string('key');coverage(unit_key):=0;states(unit_key):='MISSING';lot_key:=unit_value.get_string('lot_uid');if lot_key is null then raise_application_error(-20886,'STORE_MARK_UNIT_LOT_REQUIRED');end if;

   if not accepted_lots.exists(lot_key)then accepted_lots(lot_key):=0;missing_lots(lot_key):=0;refused_lots(lot_key):=0;damaged_lots(lot_key):=0;end if; 

   profiles:=unit_value.get_array('profiles');unit_profile_counts(unit_key):=profiles.get_size;

   for j in 0..profiles.get_size-1 loop 

    profile_value:=treat(profiles.get(j)as json_object_t);expected(tuple_key(unit_key,profile_value.get_string('system_code'),profile_value.get_string('profile_code'))):=0; 

   end loop; 

  end loop; 

  for i in 0..scans.get_size-1 loop 

   scan_value:=treat(scans.get(i)as json_object_t); 

   if scan_value.get_string('system_code')is null or scan_value.get_string('profile_code')is null or not regexp_like(scan_value.get_string('code_hash'),'^[a-f0-9]{64}$')then raise_application_error(-20871,'STORE_MARK_SCAN_INVALID');end if; 

   disposition:=nvl(scan_value.get_string('disposition'),'ACCEPTED'); 

   if disposition not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20871,'STORE_MARK_PHYSICAL_SCAN_DISPOSITION_REQUIRED');end if; 

  end loop; 

  wire:=scans.to_clob; 

  for z in(select j.I,j.S,j.P,nvl(j.D,'ACCEPTED')D,u.PHYSICAL_UNIT_KEY from 

   json_table(wire,'$[*]'columns(I for ordinality,S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash',D varchar2(20)path '$.disposition'))j 

   join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.S and c.CODE_HASH=j.H 

   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID 

   where u.STOCK_STATUS='ISSUED'and exists(select 1 from json_table(c.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile'))pr where pr.P=j.P))loop 

   k:=tuple_key(z.PHYSICAL_UNIT_KEY,z.S,z.P); 

   if not expected.exists(k)then raise_application_error(-20886,'STORE_MARK_FOREIGN_UNIT_OR_PROFILE');end if; 

   if resolved.exists(to_char(z.I))or expected(k)=1 then raise_application_error(-20871,'STORE_MARK_DUPLICATE_SCAN');end if; 

   if coverage(z.PHYSICAL_UNIT_KEY)>0 and states(z.PHYSICAL_UNIT_KEY)!=z.D then raise_application_error(-20886,'STORE_MARK_ONE_UNIT_DISPOSITION_REQUIRED');end if; 

   resolved(to_char(z.I)):=1;expected(k):=1;coverage(z.PHYSICAL_UNIT_KEY):=coverage(z.PHYSICAL_UNIT_KEY)+1;states(z.PHYSICAL_UNIT_KEY):=z.D;resolved_count:=resolved_count+1; 

  end loop; 

  if resolved_count!=scans.get_size then raise_application_error(-20886,'STORE_MARK_FOREIGN_CODE');end if; 

  p_units:=json_array_t(); 

  for i in 0..units.get_size-1 loop 

   unit_value:=treat(units.get(i)as json_object_t);unit_key:=unit_value.get_string('key');disposition:=states(unit_key);qty:=RRL_STOCK_MATH.quantity(unit_value.get_string('quantity')); 

   if coverage(unit_key)>0 and coverage(unit_key)!=unit_profile_counts(unit_key) then raise_application_error(-20886,'STORE_MARK_ALL_UNIT_PROFILES_REQUIRED');end if; 

   lot_key:=unit_value.get_string('lot_uid');

   if disposition='ACCEPTED'then accepted_lots(lot_key):=accepted_lots(lot_key)+qty;elsif disposition='MISSING'then missing_lots(lot_key):=missing_lots(lot_key)+qty;elsif disposition='REFUSED'then refused_lots(lot_key):=refused_lots(lot_key)+qty;else damaged_lots(lot_key):=damaged_lots(lot_key)+qty;end if; 

   result_value:=unit_value.clone();result_value.put('disposition',disposition);p_units.append(result_value); 

  end loop; 

  for i in 0..p_lines.get_size-1 loop

   line_value:=treat(p_lines.get(i)as json_object_t);line_lot:=line_value.get_string('lot_uid');

   if line_lot is null or declared_lots.exists(line_lot)or(not accepted_lots.exists(line_lot)and not ordinary_keys.exists(line_lot))then raise_application_error(-20886,'STORE_MARK_EXACT_LOT_LINES_REQUIRED');end if;declared_lots(line_lot):=1;

   if accepted_lots.exists(line_lot)then

   if nonnegative(line_value.get_string('accepted'))!=accepted_lots(line_lot)or nonnegative(line_value.get_string('missing'))!=missing_lots(line_lot)or nonnegative(line_value.get_string('refused'))!=refused_lots(line_lot)or nonnegative(line_value.get_string('damaged'))!=damaged_lots(line_lot)or nonnegative(line_value.get_string('extra'))!=0 then raise_application_error(-20886,'STORE_MARK_EXACT_UNIT_DISPOSITION_QUANTITY_REQUIRED');end if;

   end if;

  end loop;

  if declared_lots.count!=accepted_lots.count+ordinary_keys.count then raise_application_error(-20886,'STORE_MARK_ALL_LOT_LINES_REQUIRED');end if;

 end; 

 procedure persist(p_operation varchar2,p_load varchar2,p_units json_array_t,p_actor varchar2)is 

  x json_object_t;key_value varchar2(64);state_value varchar2(20);qty number;uom varchar2(20);version_value number; 

 begin 

  for i in 0..p_units.get_size-1 loop 

   x:=treat(p_units.get(i)as json_object_t);key_value:=x.get_string('key');state_value:=x.get_string('disposition');qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));uom:=x.get_string('base_uom');version_value:=x.get_number('version'); 

   insert into RRL_STORE_RECEIPT_UNIT(OPERATION_ID,LOAD_OPERATION_ID,PHYSICAL_UNIT_KEY,UNIT_DISPOSITION,BASE_QTY,BASE_UOM,SOURCE_UNIT_VERSION,RECORDED_BY) 

    values(p_operation,p_load,key_value,state_value,qty,uom,version_value,p_actor); 

  end loop; 

 end; 

 procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t)is node json_object_t;leaves json_array_t:=stock_leaves(p_domain.get_object('snapshot'));nodes clob:=p_domain.get_object('snapshot').get_array('nodes').to_clob;

 begin

 for v in(select CASE_ID from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))where NODE_KIND='CASE')loop

 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.CASE_ID));end loop;

 for i in 0..leaves.get_size-1 loop node:=treat(leaves.get(i)as json_object_t);

 RRL_STOCK_PLAN_HELPER.stock_closure(p_policies,p_resources,node.get_string('uid'),node.get_string('article'),p_domain.get_object('snapshot').get_string('cell'),null);

 end loop;

 end;

end;



/
