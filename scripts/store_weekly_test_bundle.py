from pathlib import Path
import json
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows')
base={'members':[{'address':'TEST','delivery_window_from':None,'delivery_window_to':None}], 'store_window_profiles':[{'address':'TEST','profile_version':1,'mode':'WEEKLY','time_zone':'Europe/Moscow','windows':[{'weekday':3,'from_minute':540,'to_minute':720},{'weekday':3,'from_minute':780,'to_minute':1080}]}]}
cases=[]
def add(name,arrival,duration,expect,service=None,mut=None):
 b=json.loads(json.dumps(base))
 if mut:mut(b)
 cases.append((name,b,arrival,duration,expect,service))
add('wait_until_open','2026-10-14 08:30',30,None,'2026-10-14 09:00')
add('lunch_gap_not_envelope','2026-10-14 11:45',30,None,'2026-10-14 13:00')
add('exact_end_allowed','2026-10-14 11:30',30,None,'2026-10-14 11:30')
add('closed_day','2026-10-15 09:00',30,'STORE_CLOSED')
add('no_interval_fits','2026-10-14 17:50',30,'STORE_NO_FEASIBLE_INTERVAL')
add('missing_profile','2026-10-14 09:00',30,'DELIVERY_WINDOW_UNCONFIGURED',mut=lambda b:b.update(store_window_profiles=[]))
add('partial_st','2026-10-14 09:00',30,'DELIVERY_WINDOW_PARTIAL',mut=lambda b:b['members'][0].update(delivery_window_from='2026-10-14 09:00:00'))
add('materialized_wins_closed_day','2026-10-15 09:00',30,None,'2026-10-15 10:00',mut=lambda b:b['members'][0].update(delivery_window_from='2026-10-15 10:00:00',delivery_window_to='2026-10-15 12:00:00'))
add('reversed_st','2026-10-14 09:00',30,'DELIVERY_WINDOW_REVERSED_OR_EMPTY',mut=lambda b:b['members'][0].update(delivery_window_from='2026-10-14 12:00:00',delivery_window_to='2026-10-14 09:00:00'))
add('mixed_member_intersection','2026-10-14 11:45',30,None,'2026-10-14 14:00',mut=lambda b:b['members'].append({'address':'TEST','delivery_window_from':'2026-10-14 14:00:00','delivery_window_to':'2026-10-14 16:00:00'}))
lines=['-- Pure native calculator checks. No table mutation or commit. Run after installation.']
for name,b,arrival,duration,expected,service in cases:
 j=json.dumps(b,separators=(',',':'))
 check=f"if nvl(err,'OK')!='{expected or 'OK'}' then raise_application_error(-20999,'{name}: '||nvl(err,'OK'));end if;"
 if service:check+=f"\n if svc!=to_date('{service}','YYYY-MM-DD HH24:MI')or svc is null then raise_application_error(-20999,'{name}: wrong service');end if;"
 lines.append(f"declare a date;z date;svc date;kind varchar2(40);err varchar2(150);begin\n RRL_STORE_WINDOW_RULES.resolve('{j}','TEST',to_date('{arrival}','YYYY-MM-DD HH24:MI'),'Europe/Moscow',{duration},a,z,svc,kind,err);\n {check}\nend;\n/\n")
(p/'selftest.sql').write_text('\n'.join(lines),encoding='utf-8')
(p/'verify.sql').write_text("""-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows
declare n number;begin
 select count(*)into n from USER_OBJECTS where OBJECT_NAME in('RRL_STORE_WINDOW_RULES','RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'STORE_WEEKLY_PACKAGES_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME in('RRL_STORE_WINDOW_RULES','RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')and ATTRIBUTE='ERROR';
 if n>0 then raise_application_error(-20808,'STORE_WEEKLY_COMPILATION_ERRORS');end if;
end;
/
""",encoding='utf-8')
(p/'apply.sql').write_text("""-- MIGRATION_ID: 2026-10-14-ni081-store-weekly-windows
-- Root applies only after store-profile and vehicle-outer-dimensions dependencies.
@@001_window_rules.sql
@@002_route_schedule.sql
@@003_time_snapshot.sql
@@verify.sql
@@selftest.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-ni081-store-weekly-windows' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Native weekly store windows and current store/fleet snapshot V7; no stock changes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
""",encoding='utf-8')
