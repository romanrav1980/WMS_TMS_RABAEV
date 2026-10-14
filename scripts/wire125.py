from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .trace_aggregation_source import", "from .receipt_regulatory_parent import create_receipt_parent\nfrom .trace_aggregation_source import",1)
start=s.index("        crpt_parent = None")
end=s.index("        for (system, digest), identity in identities.items():",start)
s=s[:start]+"""        crpt_parent,regulatory_sscc = None,None
        if any(system == 'CRPT' for system, _ in identities):
            crpt_parent,regulatory_sscc=create_receipt_parent(cur,pallet,marks["scanned"])
"""+s[end:]
s=s.replace('identity["serial"], identity["code"], pallet]', 'identity["serial"], identity["code"], regulatory_sscc]')
s=s.replace("                cur.callproc('RRL_PRODUCTION_API.ADD_AGGREGATION_ITEM', [crpt_parent, 'CIS', identity['identity'], None, identity['gtin'], None])","                if crpt_parent is not None:\n                    cur.callproc('RRL_PRODUCTION_API.ADD_AGGREGATION_ITEM', [crpt_parent, 'CIS', identity['identity'], None, identity['gtin'], None])")
s=s.replace("'p_uid_pallet': pallet, 'p_sscc': pallet","'p_uid_pallet': pallet, 'p_sscc': regulatory_sscc if system=='CRPT' else None")
print(json.dumps({p.as_posix():s},ensure_ascii=True))
