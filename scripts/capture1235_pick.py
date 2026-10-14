exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name in ["RRL_PICKING_API","RRL_PICK_PLAN_ADMISSION"]:
  q.execute("select TYPE,TEXT from USER_SOURCE where NAME=:n order by case TYPE when 'PACKAGE' then 1 else 2 end,LINE",n=name)
  sections={}
  for typ,txt in q:sections[typ]=sections.get(typ,"")+txt
  text="\n".join("create or replace "+v+"\n/\n" for v in sections.values())
  out["db/migrations/2026-10-14_ni033_pick_create_idempotency/000_before_"+name.lower()+".sql"]=text
print(json.dumps(out,ensure_ascii=True))
