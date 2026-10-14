exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for wall,zone in [('2026-10-14 09:00','Europe/Moscow'),('2026-10-25 02:30','Europe/Berlin'),('2026-03-29 02:30','Europe/Berlin'),('2026-10-14 09:00','UTC')]:
  q.execute('''with input as(select to_date(:wall,'YYYY-MM-DD HH24:MI')w,:zone z from dual), offsets as(
   select distinct cast(from_tz(cast(w+(level-49)/24 as timestamp),'UTC')at time zone(z)as date)-(w+(level-49)/24) d
   from input connect by level<=97), candidates as(select w-d candidate,z,w from input cross join offsets)
   select count(distinct candidate),to_char(min(candidate),'YYYY-MM-DD HH24:MI') from candidates
   where cast(from_tz(cast(candidate as timestamp),'UTC')at time zone(z)as date)=w''',wall=wall,zone=zone)
  print(wall,zone,q.fetchone())
