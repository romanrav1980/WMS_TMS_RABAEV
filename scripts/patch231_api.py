from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/api/store_return_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('    complete_good_box: bool=', '    unit_keys: list[str]=Field(default_factory=list,max_length=10000)\n    complete_good_box: bool=')
s=s.replace('body.model_dump(exclude={"operation_id","line_no"})','{**body.model_dump(exclude={"operation_id","line_no","unit_keys"}),**({"unit_keys":body.unit_keys} if body.unit_keys else {})}')
s=s.replace('service.original(receipt_id)','service.original(receipt_id,user.username)');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/contracts_returns.py");s=p.read_text(encoding="utf-8").replace('def original(self,receipt_id: str)','def original(self,receipt_id: str,actor: str|None=None)');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_returns.py");s=p.read_text(encoding="utf-8").replace('from ..contracts import StoreReceiptError','from ..contracts import StoreReceiptError\nfrom ...platform.public import read_oracle_json')
start=s.index('    def original(');body=s[start:]
body=body.replace('def original(self,receipt_id: str)','def original(self,receipt_id: str,actor: str|None=None)')
body=body.replace('self.gateway.fetch_all(', 'rows(')
body=body.replace('        return {"source":headers[0],', '''        units=[]
        for line in lines:
            q.execute("select RRL_STORE_RETURN_UNIT_CORE.accepted_units(:receipt,:uid,:uom) from dual",receipt=receipt_id,uid=line["lot_uid"],uom=line["base_uom"])
            available=read_oracle_json(q.fetchone()[0])
            if len(available)>10000 or len(units)+len(available)>10000:
                raise StoreReceiptError("STORE_RETURN_UNIT_BOUND","Разбейте возврат на отдельные приёмки")
            units.extend(dict(unit,line_no=line["line_no"],lot_uid=line["lot_uid"]) for unit in available)
        return {"units":units,"source":headers[0],''')
header=body.split('\n',1)[0];rest=body.split('\n',1)[1]
prefix='''        with self.gateway.transaction("Consistent current supply-chain return dossier") as q:
            q.execute("set transaction read only")
            if actor is not None:
                q.execute("select count(*)from RUSERS where ID=:actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1",actor=actor)
                if q.fetchone()[0]!=1:
                    raise StoreReceiptError("STORE_RETURN_CURRENT_READER_REQUIRED","Нет действующего права согласования возврата",403)
            def rows(sql: str,binds: dict) -> list[dict[str,Any]]:
                q.execute(sql,binds)
                names=[item[0].lower() for item in q.description]
                return [dict(zip(names,row)) for row in q.fetchall()]
'''
body=header+'\n'+prefix+'\n'.join('    '+line for line in rest.split('\n'))
out[str(p)]=s[:start]+body
print(json.dumps(out,ensure_ascii=True))
