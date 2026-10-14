from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .store_source_scope import source_transaction, assert_store_scope","from .store_source_scope import source_transaction, assert_store_scope\nfrom ..domain.preparation_quantities import pallet_share")
old="""            quantity=Decimal(item['quantity']);fraction=quantity/total
            packs=Decimal(row[7])*fraction
            if packs!=packs.to_integral_value():
                raise ValueError('Current legacy row writer requires whole packaging units in each pallet layout')
            weight=Decimal(row[8])*fraction"""
new="""            quantity=Decimal(item['quantity'])
            packs,weight=pallet_share(quantity,total,Decimal(row[7]),Decimal(row[8]))"""
assert old in s;s=s.replace(old,new)
print(json.dumps({str(p):s},ensure_ascii=True))
