from pathlib import Path
import httpx,hashlib
for name in ("receiving.js","receiving.html","receiving-intent.js"):
 local=Path("wiki-raw/wms_admin_ui_reference/"+name).read_bytes()
 response=httpx.get("http://127.0.0.1:8088/wms-admin/"+name+"?v=20261013-945",timeout=15)
 print(name,response.status_code,len(local),len(response.content),"same",local==response.content,"etag",response.headers.get("etag"))
 if local!=response.content:Path("tmp/945_server_"+name).write_bytes(response.content)
