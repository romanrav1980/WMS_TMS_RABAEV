from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/master_data/public.py");v=p.read_text(encoding="utf-8")
v+="\nfrom .infrastructure.topology_coverage import published_cell_coverage\n";v=v.replace('"build_policy_service"]','"build_policy_service", "published_cell_coverage"]');out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py");v=p.read_text(encoding="utf-8")
v=v.replace('from .cost_access import require_warehouse','from .cost_access import require_warehouse\nfrom ...master_data.public import published_cell_coverage')
v=v.replace("tc.CELL_KIND in('TRANSPORT_STAGING','GATE')","tc.CELL_KIND in('TRANSPORT_STAGING','GATE','FILM_WRAP')")
a='    return {"warehouse_id":ware,"business_date":day.isoformat()'
b='    coverage=published_cell_coverage(cur,ware)\n    verified=coverage["classification_complete"] and bool(codes)\n'+a
assert a in v;v=v.replace(a,b)
v=v.replace('LATEST_PUBLISHED_STAGING_GATE_OR_EXPLICIT_LEGACY_EXPEDITION_GROUP','LATEST_PUBLISHED_STAGING_GATE_WRAP_OR_EXPLICIT_LEGACY_EXPEDITION_GROUP')
v=v.replace('"all_shipping_zone_coverage_verified":False,"shipping_zone_empty_confirmed":False,','"classification_coverage":coverage,\n        "all_shipping_zone_coverage_verified":verified,\n        "shipping_zone_empty_confirmed":verified and not any(row["occupied"]for row in occupancy),')
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py");v=p.read_text(encoding="utf-8")
a='            occupied=sum(row["occupied"]for row in shipping["cells"])'
b='            if not shipping["all_shipping_zone_coverage_verified"]:blockers.append({"code":"shipping_zone_classification_incomplete","count":1})\n'+a
assert a in v;v=v.replace(a,b);out[str(p)]=v
p=Path("wiki-raw/wms_admin_ui_reference/shipping-register.js");v=p.read_text(encoding="utf-8")
a="    ' Полнота списка грузовой зоны не подтверждена; зона не объявлена пустой.';"
b="""    (v.all_shipping_zone_coverage_verified?
     (v.shipping_zone_empty_confirmed?' Все ячейки каталога классифицированы опубликованной схемой; зарегистрированная грузовая зона пуста в этом снимке.':' Все ячейки каталога классифицированы; грузовая зона занята.'):
     ' Классификация ячеек неполная: '+(v.classification_coverage?.unclassified_cell_count??'?')+' без роли, '+(v.classification_coverage?.ambiguous_cell_count??'?')+' неоднозначных. Примеры: '+(v.classification_coverage?.incomplete_cell_sample||[]).join(', ')+'. Опубликуйте полную схему склада.')+
    ' Незарегистрированные физические зоны этим отчётом не проверяются; день автоматически не закрывается.';"""
assert a in v;v=v.replace(a,b);out[str(p)]=v
print(json.dumps(out,ensure_ascii=True))
