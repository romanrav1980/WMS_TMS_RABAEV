from pathlib import Path
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows')
r=(p/'000_before_rrl_tt_route_schedule_package_body.sql').read_text(encoding='utf-8')
r=r.replace("address varchar2(200);norm number;", "address varchar2(255);window_kind varchar2(40);window_error varchar2(150);window_service date;norm number;")
a=r.index("   select count(*),count(case when wf is null")
z=r.index("   select count(*),min(norm)",a)
r=r[:a]+r[z:]
a=r.index("   if missing>0 or opening is null")
z=r.index("   if n!=1 or cnt!=1",a)
r=r[:a]+r[z:]
needle="   if clock_at is not null and clock_at<opening then segment('WAIT',(opening-clock_at)*1440);end if;"
replacement="""   RRL_STORE_WINDOW_RULES.resolve(p_source,address,clock_at,p_zone,norm,opening,closing,window_service,window_kind,window_error);
   if window_error is not null then issue(window_error);errors.append(window_error);clock_at:=null;end if;
   if clock_at is not null and clock_at<window_service then segment('WAIT',(window_service-clock_at)*1440);end if;"""
assert r.count(needle)==1;r=r.replace(needle,replacement)
r=r.replace("o.put('window_strict',strict);o.put('issues',errors);", "o.put('window_strict',strict);o.put('window_source',window_kind);o.put('issues',errors);")
r=r.replace('varchar2(200)','varchar2(255)')
(p/'002_route_schedule.sql').write_text('-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows\n'+r,encoding='utf-8')
t=(p/'000_before_rrl_tt_time_api_package_body.sql').read_text(encoding='utf-8')
needle="  b.put('destination_rules',a);a:=json_array_t();n:=0;"
patch="""
  declare profile_wire clob;vehicle_count number;vehicle_id number;vehicle_material json_object_t:=json_object_t();begin
   RRL_STORE_WINDOW_RULES.material(b.to_clob,profile_wire);b.put('store_window_profiles',json_array_t.parse(profile_wire));
   select count(*),min(ID)into vehicle_count,vehicle_id from RRL_TR_VEHICLE where upper(trim(NUM))=upper(trim(w.TRANSPORT))and nvl(DELETED,0)=0;
   vehicle_material.put('matching_vehicle_count',vehicle_count);
   if vehicle_count=1 then vehicle_material.put('current',json_object_t.parse(RRL_VEHICLE_PROFILE_API.describe_profile(vehicle_id)));
   else vehicle_material.put('state',case when vehicle_count=0 then 'ABSENT'else 'AMBIGUOUS'end);end if;
   b.put('vehicle_profile_material',vehicle_material);
  end;
"""
assert t.count(needle)==1;t=t.replace(needle,needle+patch)
t=t.replace("put('source_contract_version',6)","put('source_contract_version',7)")
(p/'003_time_snapshot.sql').write_text('-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows\n'+t,encoding='utf-8')
rollback=(p/'000_before_rrl_tt_route_schedule_package_body.sql').read_text(encoding='utf-8')+'\n'+(p/'000_before_rrl_tt_time_api_package_body.sql').read_text(encoding='utf-8')+"\ndrop package RRL_STORE_WINDOW_RULES;\n/\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-ni081-store-weekly-windows';\ncommit;\n/\n"
(p/'rollback.sql').write_text(rollback,encoding='utf-8')
