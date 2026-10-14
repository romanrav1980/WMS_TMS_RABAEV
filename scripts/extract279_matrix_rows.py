from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/services/distance_matrix_service.py");s=p.read_text(encoding="utf-8")
a=s.index('        merge_sql = """');b=s.index('        if statements:',a)
block=s[a:b]
block="\n".join(line[4:]if line.startswith("    ")else line for line in block.splitlines())
out["api/wms_api_server/app/modules/transport/infrastructure/distance_matrix_rows.py"]='"""Bounded rows for the existing distance-matrix MERGE; no execution or provider calls."""\nfrom typing import Any\n\ndef matrix_merge_statements(addrs: list[dict],matrix: list[list[float]],durations: list[list[float]] | None,fresh_pair_keys: set,source: str) -> tuple[list,int,int]:\n'+block.replace("provider.name","source")+"\n    return statements,computed_pairs,skipped_pairs\n"
s=s[:a]+"""        from ..modules.transport.public import matrix_merge_statements
        statements,computed_pairs,skipped_pairs=matrix_merge_statements(addrs,matrix,durations,fresh_pair_keys,provider.name)

"""+s[b:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/public.py");out[str(p)]=p.read_text(encoding="utf-8")+"\nfrom .infrastructure.distance_matrix_rows import matrix_merge_statements\n"
print(json.dumps(out,ensure_ascii=True))
