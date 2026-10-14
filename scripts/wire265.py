from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py");s=p.read_text(encoding="utf-8").replace('from ...platform.public import read_oracle_json','from ...platform.public import read_oracle_json\nfrom .store_source_scope import source_transaction, assert_store_scope')
s=s.replace("with self.gateway.transaction('NI02 receive immutable SAP customer demand') as cur:","with source_transaction(self.gateway,'NI02 receive immutable SAP customer demand',actor,'sap_store_order_import',int(data['WarehouseId'])) as cur:")
s=s.replace("cur.execute('lock table RRL_SAP_STORE_ORDER in share row exclusive mode')","cur.execute('lock table RRL_SAP_STORE_ORDER in share row exclusive mode')\n            assert_store_scope(cur,actor,'sap_store_order_import',int(data['WarehouseId']))")
a=s.index('    def list(');s=s[:a]+'''    def list(self, warehouse: int | None, limit: int, actor: str) -> list[dict]:
        from .store_order_reads import list_store_orders
        return list_store_orders(self.gateway, warehouse, limit, actor)

    def get(self, order_id: int, actor: str) -> dict:
        from .store_order_reads import store_order_detail
        return store_order_detail(self.gateway, order_id, actor)
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py");s=p.read_text(encoding="utf-8").replace('from ....oracle_gateway import OracleGateway','from ....oracle_gateway import OracleGateway\nfrom ...platform.public import read_oracle_json\nfrom .store_source_scope import source_transaction, assert_store_scope')
s=s.replace("with self.gateway.transaction('SAP demand to existing legacy ST preparation') as cur:", "with source_transaction(self.gateway,'SAP demand to existing legacy ST preparation',actor,'customer_order_import',order=order_id) as cur:")
s=s.replace("            if row[1]:", "            assert_store_scope(cur,actor,'customer_order_import',row[3])\n            if row[1]:",1).replace('json.loads(self._text(row[2]))','read_oracle_json(row[2])');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/application/ports.py");s=p.read_text(encoding="utf-8").replace('def list(self, warehouse: int | None, limit: int)','def list(self, warehouse: int | None, limit: int, actor: str)').replace('def get(self, order_id: int)','def get(self, order_id: int, actor: str)');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('    return service.list(warehouse_id,limit)','''    try:
        return service.list(warehouse_id,limit,user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc''')
s=s.replace('service.get(order_id)','service.get(order_id,user.username)')
# Protected operations have server-derived actor; all handlers expose native forbidden as403.
s=s.replace('    except LookupError as exc:', '    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except LookupError as exc:')
needle='    except (ValueError,ET.ParseError,UnicodeDecodeError) as exc:';s=s.replace(needle,'    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n'+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
