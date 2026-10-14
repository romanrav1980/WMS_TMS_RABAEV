exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
files={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ['RRL_STOCK_INTERWARE_CUSTODY','RRL_STOCK_INTERWARE_NEXT','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_HU_SHIP_CMD','RRL_INTERWARE_DEPART_GATE','RRL_STORE_ORDER_SOURCE']:
  q.execute("select TYPE,TEXT from USER_SOURCE where NAME=:name order by TYPE,LINE",name=name);kinds={}
  for kind,line in q:kinds.setdefault(kind,[]).append(line.rstrip('\r\n'))
  for kind,lines in kinds.items():files['tmp/native426_'+name.lower()+'_'+kind.lower().replace(' ','_')+'.sql']='create or replace '+'\n'.join(lines)+'\n/\n'
print(json.dumps(files))
