import json
from pathlib import Path
p=Path("api/wms_api_server/app/services/tserver_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("def call_spf(self, request: CallSpfRequest)","def call_spf(self, request: CallSpfRequest, actor: str | None = None)",1)
s=s.replace('''        params = {key: value for key, value in request.params.items() if key != "SPF_NAME"}''','''        params = {key: value for key, value in request.params.items() if key != "SPF_NAME"}
        if actor is not None:
            for key in params:
                if key.lower() in {"user_id", "user_id1", "user_id2", "user_id3", "user_id21", "iser_id1", "iser_id21", "kladovshik1", "p_actor", "p_created_by"}:
                    params[key] = actor''',1)
s=s.replace('result = self.call_spf(CallSpfRequest(spf_name=head.get("SPF_NAME"), params=params))','result = self.call_spf(CallSpfRequest(spf_name=head.get("SPF_NAME"), params=params), actor)',1)
out={str(p):s}
p=Path("api/wms_api_server/app/routers/tserver.py");s=p.read_text(encoding="utf-8")
s=s.replace('def call_spf(request: CallSpfRequest)','def call_spf(request: CallSpfRequest, user: AdminUser = Depends(get_current_admin))',1)
s=s.replace('result = TserverService().call_spf(request)','result = TserverService().call_spf(request, user.username)',1)
out[str(p)]=s
p=Path("terminal/wms_terminal_web/src/App.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('onScan={login}','onScan={value => setUserId(value.trim())}',1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
