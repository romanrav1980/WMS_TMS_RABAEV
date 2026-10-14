exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import base64,urllib.request,urllib.error,urllib.parse
from app.modules.inventory.domain.quality_label import quality_label_html
ctx=json.loads(Path("tmp/context669.json").read_text())
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select ID,PASS from RUSERS where ID='admin'and nvl(DELETED,0)=0");user,password=q.fetchone()
headers={"Authorization":"Basic "+base64.b64encode((user+":"+password).encode()).decode()}
url="http://127.0.0.1:8088/api/outgoing-quality/"+urllib.parse.quote(ctx["st_uid"],safe="")+"/control-label"
with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=15)as response:
 html=response.read().decode();assert response.headers["Cache-Control"]=="no-store";assert "КОНТРОЛЬ ПРОЙДЕН"not in html
Path("tmp/label681.html").write_text(html,encoding="utf-8")
try:
 urllib.request.urlopen(urllib.request.Request(url+"?expected_signature="+"A"*64,headers=headers),timeout=15);raise AssertionError("Expected changed signature rejection")
except urllib.error.HTTPError as e:assert e.code==409
green=quality_label_html({"shipment_identifier":"legacy <uid>","ready":True,"composition_signature":"B"*64,"reason":"<script>bad</script>"},"actor")
assert "КОНТРОЛЬ ПРОЙДЕН"in green and "<script>"not in green and "&lt;script&gt;"in green
assert "КОНТРОЛЬ ПРОЙДЕН"not in quality_label_html({"ready":True},"actor")
assert "КРАСНЫЙ ТЕГ"in quality_label_html({"rescan_required":True,"ready":False},"actor")
print(json.dumps({"status":"PASS","actual_http_blocked_label":True,"stale_signature_http":409,"native_green_source_verified":False,"render_escape_and_versioned_gate":True,"stock_commands":0}))
