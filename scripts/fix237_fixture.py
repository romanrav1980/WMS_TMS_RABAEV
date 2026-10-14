from pathlib import Path
import json
p=Path("scripts/ni062_marked_supplier_dispatch_case.py");s=p.read_text(encoding="utf-8").replace('dock="QSD237"+tag','dock="QD237"+tag')
old='  q.execute("select RRL_TR_VODITEL_SQ.nextval from dual");driver=q.fetchone()[0];cfg("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:p,\'Own237\',\'Supplier\',\'Driver\',0)",p=driver)\n  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",10,1,0,None]));c.commit()'
new="""  q.execute("select ID from RRL_TR_VODITEL where F='Own237'and I='Supplier'and O='Driver'and nvl(DELETED,0)=0 order by ID");existing=q.fetchone()
  if existing:driver=existing[0]
  else:
   q.execute("select RRL_TR_VODITEL_SQ.nextval from dual");driver=q.fetchone()[0];cfg("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:p,'Own237','Supplier','Driver',0)",p=driver)
  q.execute("select ID from RRL_TR_VEHICLE where NUM=:p and nvl(DELETED,0)=0",p=plate);existing=q.fetchone()
  if existing:vehicle=existing[0]
  else:vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,"15",10,1,0,None]));c.commit()"""
assert old in s;s=s.replace(old,new)
print(json.dumps({str(p):s},ensure_ascii=True))
