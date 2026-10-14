import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/labels.py");s=p.read_text(encoding="utf-8").replace("from ..domain.pallet_identifiers import normalize_incoming_sscc","from ..domain.pallet_identifiers import normalize_incoming_sscc\nfrom ...platform.public import read_oracle_json")
anchor="    def issue(self, order_id: str, payload: dict, actor: str) -> dict:"
helper="""    @staticmethod
    def _scope(cur, warehouse: int, actor: str) -> None:
        try:
            cur.callproc("RRL_SSCC_ALLOCATOR.assert_scope",[warehouse,actor,"warehouse_receipt_confirm"])
        except oracledb.DatabaseError as exc:
            if getattr(exc.args[0],"code",0)==20882:
                raise PermissionError("Receipt label warehouse access required") from exc
            raise

"""+anchor
assert anchor in s;s=s.replace(anchor,helper).replace('cur.callproc("RRL_SSCC_ALLOCATOR.assert_scope",[order[0],actor,"warehouse_receipt_confirm"])','self._scope(cur,order[0],actor)')
start=s.index("    def document(");end=s.index("    def confirm(",start)
s=s[:start]+"""    def document(self, label_id: str, format: str, actor: str, dpi: int = 203) -> str:
        with self.gateway.transaction("Current warehouse receiving label document READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select o.WARE_ID,l.PAYLOAD_JSON from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID where l.LABEL_ID=:label_id",label_id=label_id)
            row=cur.fetchone()
            if row is None:
                raise LookupError("Label not found")
            self._scope(cur,row[0],actor)
            data=read_oracle_json(row[1])
            return label_zpl(data,dpi) if format=="zpl" else label_html(data)

"""+s[end:]
s=s.replace("with self.gateway.transaction('NI01 operator confirms attached label') as cur:\n            cur.execute","""with self.gateway.transaction('NI01 operator confirms attached label') as cur:
            cur.execute("select o.WARE_ID from RRL_RECEIPT_LABEL l join RRL_SAP_SUPPLY_ORDER o on o.ORDER_ID=l.ORDER_ID where l.LABEL_ID=:label_id",label_id=label_id)
            source=cur.fetchone()
            if source is None:
                raise LookupError("Label not found")
            self._scope(cur,source[0],actor)
            cur.execute""")
s=s.replace("row = cur.fetchone()\n            if not row:\n                raise LookupError('Label not found')","row = cur.fetchone()\n            self._scope(cur,source[0],actor)\n            if not row:\n                raise LookupError('Label not found')")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/application/ports.py");s=p.read_text(encoding="utf-8").replace('def document(self, label_id: str, format: str, dpi: int = 203)','def document(self, label_id: str, format: str, actor: str, dpi: int = 203)');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/receiving_routes.py");s=p.read_text(encoding="utf-8").replace('service.document(label_id, format, dpi)','service.document(label_id, format, user.username, dpi)')
# Only label endpoints receive this permission mapping.
start=s.index('@router.post("/supply-orders/{order_id}/labels"');end=s.index('@router.get("/warehouses/',start)
part=s[start:end]
part=part.replace('    except (LookupError, ValueError) as exc:', '    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except (LookupError, ValueError) as exc:')
part=part.replace('    except LookupError as exc:', '    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except LookupError as exc:')
s=s[:start]+part+s[end:];out[str(p)]=s
print(json.dumps(out))
