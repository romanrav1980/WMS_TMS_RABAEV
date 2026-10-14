from pathlib import Path
p=Path('api/wms_api_server/app/modules/finance/infrastructure/reconciliation_stock_documents.py');s=p.read_text(encoding='utf-8').replace('varchar2(160)','varchar2(200)');p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py');s=p.read_text(encoding='utf-8');s=s.replace('    def report(self,','    def stock_conflicts(self,ware: int,metric: str,after: str | None,limit: int,actor: str) -> dict[str,Any]:\n        from .stock_conflict_page import stock_conflict_page\n        return stock_conflict_page(self.gateway,ware,metric,after,limit,actor)\n\n    def report(self,',1);p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/modules/finance/contracts_reconciliation.py');s=p.read_text(encoding='utf-8').replace('    def report(self,','    def stock_conflicts(self,ware: int,metric: str,after: str | None,limit: int,actor: str) -> dict[str,Any]: ...\n    def report(self,',1);p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/modules/finance/api/day_reconciliation_routes.py');s=p.read_text(encoding='utf-8').replace('from typing import Any','from typing import Any,Literal').replace('HTTPException,Query','HTTPException,Query,Path');s+='''

@router.get("/warehouses/{ware_id}/stock-conflicts")
def stock_conflicts(ware_id: int=Path(gt=0),metric: Literal["stock_quantity_invariants","physical_unit_composition"]=Query(...),
                    after: str | None=Query(None,max_length=2048),limit: int=Query(50,ge=1,le=100),
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: DayReconciliationPort=Depends(day_reconciliation_service)) -> dict[str,Any]:
    try:return service.stock_conflicts(ware_id,metric,after,limit,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
''';p.write_text(s,encoding='utf-8')
