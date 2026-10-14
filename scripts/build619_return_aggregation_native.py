from pathlib import Path
import json,hashlib
f=Path("db/migrations/2026-10-12_ni062_return_aggregation")
spec=(f/"000_before_rrl_iw_agg_scan_package.sql").read_text(encoding="utf-8")
assert "accessible by(package RRL_INTERWARE_MARK_SCAN)"in spec
spec=spec.replace("accessible by(package RRL_INTERWARE_MARK_SCAN)","accessible by(package RRL_INTERWARE_MARK_SCAN,package RRL_STORE_RETURN_UNIT_CORE)")
(f/"001_shared_resolver_access.sql").write_text(spec,encoding="utf-8")
v=(f/"000_before_rrl_store_return_unit_core_package_body.sql").read_text(encoding="utf-8")
v=v.replace("SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')","SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION','BOX','PALLET')",1)
a="wire clob:=approved_proof(p_approval);proof json_object_t;qty number;lot_value varchar2(200);lines json_array_t:=json_array_t();x json_object_t:=json_object_t();resolved json_array_t;"
b=a+"normalized json_object_t;expanded_wire clob;input_wire clob;direct_wire clob;profile_wire clob;bad_direct number;aggregation_count number:=0;"
assert a in v;v=v.replace(a,b)
a="if p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0 then"
b="if(p_metadata.has('unit_scans')and p_metadata.get_array('unit_scans').get_size>0)or(p_metadata.has('aggregation_scans')and p_metadata.get_array('aggregation_scans').get_size>0)then"
assert a in v;v=v.replace(a,b,1)
a="  RRL_STORE_MARK_CORE.resolve_disposition(proof,p_metadata,lines,resolved);proof.put('units',resolved);return proof.to_clob;"
b="""  normalized:=p_metadata.clone();profile_wire:=proof.get_array('profiles').to_clob;
  direct_wire:=to_clob('[]');if normalized.has('unit_scans')then direct_wire:=normalized.get_array('unit_scans').to_clob;end if;
  select count(*)into bad_direct from json_table(direct_wire,'$[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code'))scan_value
   join json_table(profile_wire,'$[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',M varchar2(40)path '$.scan_mode'))profile_value
    on profile_value.S=scan_value.S and profile_value.P=scan_value.P where profile_value.M in('BOX','PALLET');
  if bad_direct!=0 then raise_application_error(-20887,'RETURN_AGGREGATION_ONLY_NO_UNIT_FALLBACK');end if;
  if normalized.has('aggregation_scans')then aggregation_count:=normalized.get_array('aggregation_scans').get_size;end if;
  if aggregation_count>0 then
   input_wire:=normalized.to_clob;RRL_IW_AGG_SCAN.expand(input_wire,expanded_wire);
   normalized.put('unit_scans',json_array_t.parse(expanded_wire));
  end if;
  RRL_STORE_MARK_CORE.resolve_disposition(proof,normalized,lines,resolved);proof.put('units',resolved);return proof.to_clob;"""
assert a in v;v=v.replace(a,b)
(f/"002_return_unit_core.sql").write_text(v,encoding="utf-8")
(f/"checkpoint.json").write_text(json.dumps({"migration_id":"2026-10-12-619-return-aggregation-custody","status":"PREPARED_NOT_APPLIED","source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in f.glob("*.sql")},
"scope":"Existing return custody/receive unit owner delegates registered aggregation expansion to shared resolver; no new units, stock writer or warehouse tree.",
"limits":"Original registered aggregate must retain current unit origin and allowed current profile/level/version/lifecycle. Moving to new return UID does not silently re-authorize old aggregation; future lifecycle/repacking separate.",
"recovery":"Fresh shared resolver spec and return core body captured; compatibility rollback restores prior code only before new aggregate custody facts."},indent=2)+"\n",encoding="utf-8")
print("619 registered-only return custody scan prepared; exact approved unit/profile matrix preserved, aggregate-only no direct-unit fallback.")
