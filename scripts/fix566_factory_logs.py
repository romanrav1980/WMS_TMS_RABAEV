import json
from pathlib import Path
p=Path("scripts/case565_depart_profile.py");v=p.read_text(encoding="utf-8")
lines=[]
for line in v.splitlines():
 if line.lstrip().startswith("print(")and "PASS"in line and "PASS565"not in line:
  line=line[:len(line)-len(line.lstrip())]+'print("Pipeline565 original positive creation step; legacy negative checks outside this run",flush=True)'
 lines.append(line)
v="\n".join(lines)+"\n"
v=v.replace('wire=json.loads(wire.read()if hasattr(wire,"read")else wire)','wire=wire if isinstance(wire,dict)else json.loads(wire.read()if hasattr(wire,"read")else wire)')
out={str(p):v}
p=Path("scripts/build565_depart_profile_case.py");v=p.read_text(encoding="utf-8")
v=v.replace("class Trim(ast.NodeTransformer):","class Trim(ast.NodeTransformer):\n def visit_Expr(self,node):\n  if isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='print'and node.value.args and isinstance(node.value.args[0],ast.Constant)and isinstance(node.value.args[0].value,str)and node.value.args[0].value.startswith('PASS'):return None\n  return self.generic_visit(node)")
v=v.replace('wire=json.loads(wire.read()if hasattr(wire,"read")else wire)','wire=wire if isinstance(wire,dict)else json.loads(wire.read()if hasattr(wire,"read")else wire)')
out[str(p)]=v
print(json.dumps(out))
