from pathlib import Path
import json
f={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/preparation_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace('r.UNIT_COUNT,to_char(a.NORMA_UKLADKI,{_NUM})','r.UNIT_COUNT,to_char(a.NORMA_UKLADKI,{_NUM}),\n            to_char(cfg.TEMP_MIN,{_NUM}),to_char(cfg.TEMP_MAX,{_NUM})')
s=s.replace('left join RRL_CELLS x on x.CELL=a.CELL','left join RRL_CELLS x on x.CELL=a.CELL\n            left join RRL_RECEIPT_SKU_RULE cfg on cfg.WARE_ID=:warehouse_id and cfg.ARTICUL=r.ARTICUL',1)
s=s.replace('fetch first 1001 rows only""",order_id=order)','fetch first 1001 rows only""",order_id=order,warehouse_id=warehouse)')
s=s.replace("rounded,count,unit_count,norm=row","rounded,count,unit_count,norm,temp_min,temp_max=row")
s=s.replace('"legacy_rounded_quantity":rounded,"blockers":errors}', '"legacy_rounded_quantity":rounded,"temp_min_c":temp_min,"temp_max_c":temp_max,"blockers":errors}')
f[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py");s=p.read_text(encoding="utf-8")
helper="""
def temperature(line: dict) -> tuple[Decimal | None, Decimal | None]:
    try:
        lo=Decimal(str(line["temp_min_c"])) if line.get("temp_min_c") is not None else None
        hi=Decimal(str(line["temp_max_c"])) if line.get("temp_max_c") is not None else None
    except InvalidOperation as exc:
        raise ValueError("AUTO_LAYOUT_INVALID_TEMPERATURE_RANGE") from exc
    if any(x is not None and not x.is_finite() for x in (lo,hi)) or (lo is not None and hi is not None and lo>hi):
        raise ValueError("AUTO_LAYOUT_INVALID_TEMPERATURE_RANGE")
    return lo,hi

def merged_temperature(current: dict, lo: Decimal | None, hi: Decimal | None) -> tuple[Decimal | None, Decimal | None] | None:
    known=lo is not None or hi is not None
    if bool(current["temp_min_c"] is not None or current["temp_max_c"] is not None)!=known:
        return None
    lower=[x for x in (lo,current["temp_min_c"]) if x is not None]
    upper=[x for x in (hi,current["temp_max_c"]) if x is not None]
    result=(max(lower) if lower else None,min(upper) if upper else None)
    if result[0] is not None and result[1] is not None and result[0]>result[1]:
        return None
    return result

"""
s=s.replace("def automatic_layout(",helper+"def automatic_layout(",1)
s=s.replace('        remaining = boxes.numerator','        lo,hi=temperature(line)\n        remaining = boxes.numerator',1)
s=s.replace('            if current is None or current["group"] != group:','            if current is not None and (current["group"]!=group or merged_temperature(current,lo,hi) is None):\n                current=None\n            if current is None:',1)
s=s.replace('"norm": Fraction(0), "lines": []}','"norm": Fraction(0), "lines": [],"temp_min_c":lo,"temp_max_c":hi}',1)
s=s.replace('            current["mass"] += count*box_mass','            current["temp_min_c"],current["temp_max_c"]=merged_temperature(current,lo,hi)\n            current["mass"] += count*box_mass',1)
s=s.replace('"goods_weight_kg": format(exact_decimal(x["mass"]), "f"),','"goods_weight_kg": format(exact_decimal(x["mass"]), "f"),\n         "temp_min_c":str(x["temp_min_c"]) if x["temp_min_c"] is not None else None,\n         "temp_max_c":str(x["temp_max_c"]) if x["temp_max_c"] is not None else None,')
f[str(p)]=s
p=Path("scripts/check1116_auto_layout.py");s=p.read_text(encoding="utf-8")
s+='''

cold={**line("A",q="6"),"temp_min_c":"2","temp_max_c":"4"}
warm={**line("B",q="6"),"temp_min_c":"15","temp_max_c":"20"}
assert len(automatic_layout([cold,warm],{},limits)["pallets"])==2
unknown=line("C",q="6")
assert len(automatic_layout([cold,unknown],{},limits)["pallets"])==2
compatible={**line("B",q="6"),"temp_min_c":"3","temp_max_c":"6"}
result=automatic_layout([cold,compatible],{},limits)
assert len(result["pallets"])==1
assert result["pallet_statistics"][0]["temp_min_c"]=="3" and result["pallet_statistics"][0]["temp_max_c"]=="4"
try:automatic_layout([{**cold,"temp_min_c":"6","temp_max_c":"2"}],{},limits)
except ValueError:pass
else:raise AssertionError("Invalid temperature range accepted")
print("PASS1147 incompatible/known-unknown separated; compatible exact3..4 mixed; invalid range rejected")
'''
f[str(p)]=s
p=Path("wiki/components/nicora_ni021_auto_preparation_20261013.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n1147: prepared warehouseSKU temperature ranges added to same readiness/source_signature. Auto places preserve common known range, reject invalidrange, separate incompatible knownSKU and known-vs-unknown, while existingunknowns mayformnormativeplanwithoutphysicalthermalclaim. Temperature sourcedexistingRRL_RECEIPT_SKU_RULE; numericvehicle/tempfacts stillseparate. Runtimepending/newpurecases1147 pending.\n"
p=Path("wiki/index.md");f[str(p)]="- [Auto layout temperature compatibility1147](components/nicora_ni021_auto_preparation_20261013.md): prepared currentSKU ranges/source signature, incompatible/unknown separation; no vehicle temperature guess.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");f[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1147: same originalpreparationreadiness now currentWARESKU temperatures, source signature covers them; auto layout preserves knownintersection/separatesincompatible+knownvsunknown/rejectinvalid, existingnormativeunknownmixednotphysicallyadmitted. NoDDL/nativewriter change; focusedcasespending.\n"
print(json.dumps(f,ensure_ascii=True))
