from pathlib import Path
source=Path("scripts/case264_calendar.py").read_text(encoding="utf-8")
source=source.replace('p=Path("tmp/context264.json");assert not p.exists(),"Resume own context264; no new demand births"', 'p=Path("tmp/context264.json");data=json.loads(p.read_text(encoding="utf-8"));tag=data["tag"];ware=data["ware"];store=data["store"];map_id=data["map_id"];customer=data["customer"];article=data["article"];uom=data["uom"];sender=data["sender"];actor=data["actor"]')
a=source.index(' q.execute("""select m.STORE_CODE')if ' q.execute("""select m.STORE_CODE'in source else source.index(' q.execute("select CUSTOMER_ID,CUSTOMER_CODE')
b=source.index(' initial=svc.calendar_context(',a)
replacement=''' q=c.cursor();q.execute("select PASS,USER_GROUP from RUSERS where ID=:actor",actor=actor);secret,group=q.fetchone()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
'''
source=source[:a]+replacement+source[b:]
exec(compile(source,"resume264.py","exec"))
