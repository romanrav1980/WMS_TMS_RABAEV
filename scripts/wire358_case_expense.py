from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/expense_manifest.py");s=p.read_text(encoding="utf-8");out["tmp/358_before_expense_manifest.py"]=s
s=s.replace("from .expense_box_weight import missing_leaf_weight","from .expense_box_weight import missing_leaf_weight\nfrom ..domain.physical_boxes import physical_box_count",1)
start=s.index('    cursor.execute("select b.LOAD_OPERATION_ID,b.BOX_UID')
end=s.index("    rows=[];keys=set();units=set()",start)
s=s[:start]+"""    cursor.execute(\"\"\"select b.LOAD_OPERATION_ID,b.BOX_UID,b.GROSS_WEIGHT_KG,b.BOX_CONTENT_VERSION,
       b.CASE_BOX_TASK_ID,b.MEASUREMENT_ORIGIN,b.FINAL_SCALE_CAPTURE,b.WAREHOUSE_QC_OPERATION,
       b.TARE_WEIGHT_KG,b.NET_WEIGHT_KG,b.SIGNATURE_VERSION,b.MEASURED_CONTENT_VERSION,b.COVERAGE_COMPLETE
       from RRL_TT_LOAD_BOX_WEIGHT b join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=b.LOAD_OPERATION_ID
       where l.TT_ID=:id order by b.LOAD_OPERATION_ID,b.BOX_UID fetch first 10001 rows only\"\"\",id=trip)
    columns=[x[0].lower()for x in cursor.description]
    measurements=[dict(zip(columns,row))for row in cursor.fetchall()]
    if len(measurements)>10000:raise LogisticsCostError("EXPENSE_BOX_PROOF_BOUND","Не более 10000 измерений коробок")
    proofs: dict[str,dict[str,Decimal]]={}
    full_proofs: dict[str,list[dict[str,Any]]]={}
    for proof in measurements:
        load=proof["load_operation_id"];proofs.setdefault(load,{})[proof["box_uid"]]=Decimal(str(proof["gross_weight_kg"]))
        full_proofs.setdefault(load,[]).append(proof)
""" +s[end:]
s=s.replace('if not leaves or any(n.get("kind")=="CASE" for n in nodes):','if not leaves:',1)
needle='        for node in leaves:'
replacement="""        if len(nodes)>200 or len({n["uid"]for n in nodes})!=len(nodes):
            raise LogisticsCostError("EXPENSE_FROZEN_TREE_BOUND","Нужен точный ограниченный архив физических мест")
        if basis=="WEIGHT"and any(n.get("kind")=="CASE"and n.get("scale_qc")for n in nodes):
            try:physical_box_count(tree,full_proofs.get(load,[]))
            except ValueError as exc:raise LogisticsCostError("EXPENSE_CASE_BOX_PROOF_REQUIRED",str(exc))from exc
        for node in leaves:"""
assert needle in s;s=s.replace(needle,replacement,1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/expense_box_weight.py");s=p.read_text(encoding="utf-8");out["tmp/358_before_expense_box_weight.py"]=s
s=s.replace('if nodes[current].get("type")=="BOX" and current in proofs:','if (nodes[current].get("type")=="BOX"or(nodes[current].get("kind")=="CASE"and nodes[current].get("scale_qc")))and current in proofs:',1)
idx=s.index('    tare=sum(')
s=s[:idx]+"""    case_proof=nodes[box].get("scale_qc")if nodes[box].get("kind")=="CASE"else None
    if case_proof:
        net=Decimal(case_proof["net_weight_kg"])
        if not net.is_finite()or net<=0:raise LogisticsCostError("EXPENSE_CASE_BOX_POSITIVE_NET_REQUIRED","Нужна положительная измеренная масса товара малой тары")
        return net,box
"""+s[idx:];out[p.as_posix()]=s
print(json.dumps(out))
