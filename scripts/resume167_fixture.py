from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/ni033_case_http_close_flow.py"
s=p.read_text(encoding="utf-8")
s=s.replace('tag=uuid4().hex[:10]','tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:10]',1)
a=s.index(' meta("declare x RRL_ARTICULS');b=s.index(' meta("insert into RRL_WARES',a)
fragment=s[a:b]
s=s[:a]+''' q.execute("select count(*)from RRL_ARTICULS where ACTICUL=:id",id=article)
 if q.fetchone()[0]==0:
'''+''.join(' '+line for line in fragment.splitlines(keepends=True))+s[b:]
s=s.replace('prefix="Q167"+tag[:2]','prefix="Q"+tag[:2]')
p.write_text(s,encoding="utf-8")
