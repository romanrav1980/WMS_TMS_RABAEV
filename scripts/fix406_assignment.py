from pathlib import Path
import json
p=Path('scripts/prepare406_group.py');t=p.read_text(encoding='utf-8')
t=t.replace('from app.modules.transport.public import assign_sts','from app.modules.transport.public import assign_sts\nfrom app.modules.transport.infrastructure.st_assignment import unassign_st')
old="if 'assigned'not in saved:assign_sts(gw,first['source_trip'],[second['st']],'admin');saved['assigned']=True;save()"
new="""if 'assigned'not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute('select ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:st_id',st_id=second['st']);number,old_trip=q.fetchone()
 if old_trip and old_trip!=first['source_trip']:unassign_st(gw,old_trip,number)
 assign_sts(gw,first['source_trip'],[number],'admin');saved['assigned']=True;save()"""
assert old in t;t=t.replace(old,new);print(json.dumps({p.as_posix():t}))
