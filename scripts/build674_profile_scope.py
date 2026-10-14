import json,hashlib
from pathlib import Path
root="db/migrations/2026-10-12_ni061_group_profile_scope/"
s=Path("tmp/666_rrl_interware_mark_scan.sql").read_text(encoding="utf-8")
before="create or replace "+s+"\n/\n"
# Original validator checks direct scans by profile globally; restrict them to this physical lot.
old="""select 1 from json_table(p_metadata,'$.unit_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code'))direct_scan"""
new="""select 1 from json_table(p_metadata,'$.unit_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash'))direct_scan,
     RRL_WMS_RECEIPT_UNIT direct_unit,RRL_WMS_RECEIPT_CODE direct_code
     where direct_unit.CURRENT_UID=v_uid and direct_code.UID_PALLET=direct_unit.UID_PALLET
      and direct_code.UNIT_ID=direct_unit.UNIT_ID and direct_code.SYSTEM_CODE=direct_scan.S
      and direct_code.CODE_HASH=direct_scan.H
      and direct_scan.S=p.SYSTEM_CODE and direct_scan.P=p.PROFILE_CODE"""
assert old in before
after=before.replace(old,new).replace("where direct_scan.S=p.SYSTEM_CODE and direct_scan.P=p.PROFILE_CODE)));",")));")
group_path=Path("db/migrations/2026-10-12_ni061_group_aggregation/001_group_rec.sql")
group=group_path.read_text(encoding="utf-8")
start=group.index("  -- An aggregation on one lot")
end=group.index("  if RRL_INTERWARE_MARK_SCAN.required_for_plan",start)
group_new=group[:start]+group[end:]
group_new=group_new.replace("declare scan_domain json_object_t:=json_object_t();scan_domain_wire clob;metadata_scan_wire clob;begin","declare scan_domain json_object_t:=json_object_t();begin").replace("scan_domain.put('legs',legs);scan_domain_wire:=scan_domain.to_clob;metadata_scan_wire:=m.to_clob;","scan_domain.put('legs',legs);")
files={root+"000_before_mark_scan.sql":before,root+"000_before_group_rec.sql":group,root+"001_mark_scan.sql":after,root+"002_group_rec.sql":group_new,
root+"003_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-674-interware-profile-scope'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Authoritative interwarehouse direct-scan mode guard scoped to physical lot; mixed-profile group proof',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",root+"apply.sql":"@001_mark_scan.sql\n@002_group_rec.sql\n@003_ledger.sql\n",
root+"rollback.sql":"@000_before_mark_scan.sql\n@000_before_group_rec.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-12-674-interware-profile-scope';\n/\n",
root+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_INTERWARE_MARK_SCAN','RRL_IW_GROUP_REC');\n",
root+"checkpoint.json":json.dumps({"schema":"RABAEV","service":"127.0.0.1:1521/orcl","before_mark_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_mark_sha256":hashlib.sha256(after.encode()).hexdigest(),"before_group_sha256":hashlib.sha256(group.encode()).hexdigest(),"after_group_sha256":hashlib.sha256(group_new.encode()).hexdigest(),"recovery":"paired source rollback; no new data/stock writer"},indent=2)}
print(json.dumps(files))
