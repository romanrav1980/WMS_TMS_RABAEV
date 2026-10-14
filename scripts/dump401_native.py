exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
names=['RRL_STOCK_INTERWARE_REC','RRL_STOCK_LOCK_API','RRL_INTERWARE_PLAN_GUARD','RRL_HU_CONTAINER_GUARD','RRL_HU_LINK_WRITE_GUARD','RRL_SAP_PALLET_WRITE_GUARD','RRL_HU_TARE_WARE_GUARD','RRL_HU_DEPARTURE_GUARD']
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in names:
  q.execute("select TYPE,TEXT from USER_SOURCE where NAME=:name order by TYPE,LINE",name=name)
  types={}
  for kind,line in q:types.setdefault(kind,[]).append(line.rstrip('\r\n'))
  for kind,lines in types.items():
   key='tmp/native401_'+name.lower()+'_'+kind.lower().replace(' ','_')+'.sql'
   files[key]='create or replace '+ '\n'.join(lines)+'\n/\n'
 q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME in('RRL_FULL_PALLET_SHIPMENT_BIND','RRL_SBORKA_PALLET_ROWS','RRL_INTERWARE_PLAN') order by TABLE_NAME,COLUMN_ID")
 print(json.dumps(files))
