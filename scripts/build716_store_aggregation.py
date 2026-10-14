exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import hashlib
out={};d="db/migrations/2026-10-12_ni053_store_aggregation"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_IW_AGG_SCAN'and TYPE='PACKAGE'order by LINE");spec="create or replace "+"".join(x[0]for x in q)+"/\n"
before=Path("tmp/714_store_mark.sql").read_text(encoding="utf-8")
out[d+"/000_before_mark.sql"]=before;out[d+"/000_before_resolver.sql"]=spec
out[d+"/001_resolver_access.sql"]=spec.replace("package RRL_STORE_RETURN_UNIT_CORE","package RRL_STORE_RETURN_UNIT_CORE,package RRL_STORE_AGG_SCAN")
out[d+"/002_scan.sql"]="""create or replace package RRL_STORE_AGG_SCAN authid definer accessible by(package RRL_STORE_MARK_CORE) as
 procedure normalize(p_proof clob,p_metadata clob,p_scans out clob);
end;
/
create or replace package body RRL_STORE_AGG_SCAN as
 procedure normalize(p_proof clob,p_metadata clob,p_scans out clob)is
  proof json_object_t:=json_object_t.parse(p_proof);m json_object_t:=json_object_t.parse(p_metadata);
  scans json_array_t:=json_array_t();aggregates json_array_t:=json_array_t();result json_array_t:=json_array_t();
  entry json_object_t;input json_object_t;entries json_array_t;expanded json_array_t;value json_object_t;
  wire clob;direct_wire clob;units_wire clob;expanded_wire clob;disposition varchar2(20);bad number;
 begin
  if m.has('unit_scans')then scans:=m.get_array('unit_scans');end if;
  if m.has('aggregation_scans')then aggregates:=m.get_array('aggregation_scans');end if;
  if scans is null or aggregates is null or scans.get_size>20000 or aggregates.get_size>1000 then raise_application_error(-20881,'STORE_AGG_SCAN_BOUND');end if;
  direct_wire:=scans.to_clob;units_wire:=proof.get_array('units').to_clob;
  select count(*)into bad from json_table(direct_wire,'$[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash'))scan_value
   join RRL_WMS_RECEIPT_CODE code on code.SYSTEM_CODE=scan_value.S and code.CODE_HASH=scan_value.H
   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=code.UID_PALLET and u.UNIT_ID=code.UNIT_ID
   join json_table(units_wire,'$.dummy'columns(K varchar2(64)path '$.key'))unused on 1=0;
  -- Check the mode on the exact physical key, so equal profile names across SKUs do not prohibit UNIT evidence.
  select count(*)into bad from json_table(direct_wire,'$[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',H varchar2(64)path '$.code_hash'))scan_value
   join RRL_WMS_RECEIPT_CODE code on code.SYSTEM_CODE=scan_value.S and code.CODE_HASH=scan_value.H
   join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=code.UID_PALLET and u.UNIT_ID=code.UNIT_ID
   join json_table(units_wire,'$[*]'columns(K varchar2(64)path '$.key',nested path '$.profiles[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',M varchar2(40)path '$.scan_mode')))expected
    on expected.K=u.PHYSICAL_UNIT_KEY and expected.S=scan_value.S and expected.P=scan_value.P where expected.M in('BOX','PALLET');
  if bad!=0 then raise_application_error(-20887,'STORE_AGGREGATION_ONLY_NO_UNIT_FALLBACK');end if;
  for i in 0..scans.get_size-1 loop result.append(scans.get(i));end loop;
  for i in 0..aggregates.get_size-1 loop
   entry:=treat(aggregates.get(i)as json_object_t).clone();disposition:=entry.get_string('disposition');
   if disposition is null or disposition not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20871,'STORE_AGG_DISPOSITION_REQUIRED');end if;
   entry.remove('disposition');input:=json_object_t();entries:=json_array_t();entries.append(entry);input.put('aggregation_scans',entries);wire:=input.to_clob;
   RRL_IW_AGG_SCAN.expand(wire,expanded_wire);expanded:=json_array_t.parse(expanded_wire);
   for j in 0..expanded.get_size-1 loop value:=treat(expanded.get(j)as json_object_t);value.put('disposition',disposition);result.append(value);end loop;
   if result.get_size>20000 then raise_application_error(-20881,'STORE_AGG_EXPANDED_BOUND');end if;
  end loop;
  p_scans:=result.to_clob;
 end;
end;
/
"""
# Remove the unused preliminary query; one authoritative exact-key mode check.
a=out[d+"/002_scan.sql"];start=a.index("  select count(*)into bad");end=a.index("  -- Check",start);out[d+"/002_scan.sql"]=a[:start]+a[end:]
after=before.replace("SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')","SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION','BOX','PALLET')")
anchor="  if p_metadata.has('unit_scans')then scans:=p_metadata.get_array('unit_scans');end if;"
assert after.count(anchor)==1
after=after.replace(anchor,"  declare v_wire clob;begin RRL_STORE_AGG_SCAN.normalize(p_proof.to_clob,p_metadata.to_clob,v_wire);scans:=json_array_t.parse(v_wire);end;")
out[d+"/003_mark.sql"]=after
out[d+"/apply.sql"]="@@001_resolver_access.sql\n@@002_scan.sql\n@@003_mark.sql\n@@004_ledger.sql\n"
out[d+"/rollback.sql"]="@@000_before_mark.sql\n@@000_before_resolver.sql\ndrop package RRL_STORE_AGG_SCAN;\n"
out[d+"/004_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-716-store-aggregation'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Store disposition uses existing registered aggregate resolver and exact issued unit/profile matrix',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[d+"/verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STORE_MARK_CORE','RRL_STORE_AGG_SCAN','RRL_IW_AGG_SCAN');\n"
out[d+"/checkpoint.json"]=json.dumps({"schema":"RABAEV","source_hashes":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in [("mark",before),("resolver",spec)]},"recovery":"restore captured bodies/spec; receipts remain immutable; no quantity birth","quantity_owner":"RRL_STOCK_POSTING_API"},indent=2)
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s0=p.read_text(encoding="utf-8");s0=s0.replace("class UnloadingDetails(BaseModel):","class StoreAggregationScan(StoreUnitScan):\n    level: Literal[\"BOX\",\"PALLET\"]\n\n\nclass UnloadingDetails(BaseModel):");s0=s0.replace("class StoreReceiptRequest(BaseModel):","class StoreReceiptRequest(BaseModel):\n    aggregation_scans: list[StoreAggregationScan]=Field(default_factory=list,max_length=1000)");out[str(p)]=s0
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");s0=p.read_text(encoding="utf-8");anchor='        return self.post("STORE_RECEIPT",operation_id,'
code="""        aggregates=metadata.get("aggregation_scans",[])
        if aggregates:
            from ...inventory.public import normalize_interwarehouse_scans
            normalized=[]
            try:
                for entry in aggregates:
                    disposition=entry.get("disposition","ACCEPTED")
                    if disposition not in("ACCEPTED","REFUSED","DAMAGED"):raise ValueError("Invalid aggregate disposition")
                    value=normalize_interwarehouse_scans({"aggregation_scans":[{k:v for k,v in entry.items()if k!="disposition"}]})["aggregation_scans"][0]
                    normalized.append(dict(value,disposition=disposition))
            except ValueError as exc:
                raise StoreReceiptError("STORE_AGG_SCAN_INVALID",str(exc),422,operation_id)from exc
            metadata["aggregation_scans"]=normalized
        else:metadata.pop("aggregation_scans",None)
"""
assert s0.count(anchor)==1;out[str(p)]=s0.replace(anchor,code+anchor)
print(json.dumps(out,ensure_ascii=True))
