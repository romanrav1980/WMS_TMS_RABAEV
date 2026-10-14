from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
start=v.index("def invoice_transport_costs(");end=v.index("\ndef normative_cost_sources(",start)
old=v[start:end];anchor='        cursor.execute("set transaction read only")\n'
assert old.count(anchor)==1
body=old.split(anchor,1)[1]
body="\n".join(line[4:]if line.startswith("    ")else line for line in body.splitlines())
new='''def invoice_snapshot(cursor: Any,invoice: int,actor: str)->dict[str,Any]:
    from decimal import Decimal,localcontext
'''+body+'''

def invoice_transport_costs(gateway: Any,invoice: int,actor: str)->dict[str,Any]:
    with gateway.transaction("Read invoice transport costs in current visible warehouse scope")as cursor:
        cursor.execute("set transaction read only")
        return invoice_snapshot(cursor,invoice,actor)

'''
p.write_text(v[:start]+new+v[end:],encoding="utf-8")
print("614 same invoice snapshot query reusable in bounded rollback-only fixture; runtime read-only wrapper preserved.")
