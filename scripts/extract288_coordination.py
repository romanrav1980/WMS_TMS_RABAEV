from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
start=s.index('            dispatcher(cur,actor)')
end=s.index('    except (TransportLoadingError,StoreReturnReceiveError)')
body=s[start:end];body='\n'.join(line[8:]if line.startswith('        ')else line for line in body.splitlines())+'\n'
s=s[:start]+'            return read_coordination(cur,trip,actor)\n'+s[end:]+'\n\ndef read_coordination(cur: Any,trip: int,actor: str) -> dict[str,Any]:\n'+body
print(json.dumps({p.as_posix():s},ensure_ascii=True))
