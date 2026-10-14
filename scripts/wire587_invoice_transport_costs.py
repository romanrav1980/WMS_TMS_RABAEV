from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
v+='''

def invoice_transport_costs(gateway: Any,invoice: int,actor: str)->dict[str,Any]:
    from decimal import Decimal,localcontext
    with gateway.transaction("Read invoice transport costs in current visible warehouse scope")as cursor:
        cursor.execute("set transaction read only")
        cursor.execute("""select r.RESULT_JSON from RRL_LOGISTICS_COST_RUN r
         join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID
         join RRL_TRANSPORT_TASK t on t.ID=r.TT_ID
         join RUSERS u on u.ID=:actor and nvl(u.DELETED,0)=0
          and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
          and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
         where t.PAY_ORDER_ID=:invoice order by r.TT_ID,r.OPERATION_ID fetch first 201 rows only""",
                       actor=actor,invoice=invoice)
        rows=cursor.fetchall()
        if len(rows)>200:raise LogisticsCostError("TRANSPORT_INVOICE_BOUND","Не более 200 транспортных начислений; используйте детализацию рейса")
        items=[read_oracle_json(row[0])for row in rows]
        totals={}
        with localcontext()as context:
            context.prec=80
            for item in items:
                code=item["currency"];value=Decimal(item["total"])
                if not value.is_finite()or value<0:
                    raise LogisticsCostError("TRANSPORT_RECOGNIZED_AMOUNT_INVALID","Некорректный сохранённый финансовый итог")
                totals[code]=totals.get(code,Decimal(0))+value
        return {"invoice_id":invoice,"items":items,"currency_totals":[{"currency":code,"amount":format(value,"f")}for code,value in sorted(totals.items())],
                "scope":"VISIBLE_WAREHOUSES","carrier_invoice_changed":False,"stock_changed":False}
''';p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def transport_costs(",'''    def invoice_transport_costs(self,invoice: int,actor: str)->dict[str,Any]:
        from .transport_cost_read import invoice_transport_costs
        return invoice_transport_costs(self.gateway,invoice,actor)

    def transport_costs(''',1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def transport_costs(","    def invoice_transport_costs(self,invoice: int,actor: str)->dict[str,Any]: ...\n    def transport_costs(",1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''

@router.get("/billing-orders/{invoice_id}/transport-costs")
def invoice_transport_costs(invoice_id: int,
                            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                            service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if invoice_id<1:raise HTTPException(422,"Positive invoice ID required")
    try:return service.invoice_transport_costs(invoice_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
''';p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx");v=p.read_text(encoding="utf-8")
v='import {BillingTransportCosts} from "./BillingTransportCosts";\n'+v
v=v.replace('<BillingExtraExpenses invoiceId={invoiceId}/>','<BillingTransportCosts invoiceId={invoiceId}/><BillingExtraExpenses invoiceId={invoiceId}/>');p.write_text(v,encoding="utf-8")
print("587 existing invoice shows separate recognised Q26 costs/current warehouse scope.")
