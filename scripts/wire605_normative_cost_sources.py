from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
v=v.replace('return {"trip_id":trip,"warehouse_id":ware,"recognized":read_oracle_json(rows[0][0])if rows else None,',
'''if rows:
            from .normative_correction import confirmed_total
            recognized=read_oracle_json(rows[0][0]);current_total=confirmed_total(cursor,recognized["operation_id"])
        else:recognized=None;current_total=None
        return {"trip_id":trip,"warehouse_id":ware,"recognized":recognized,"confirmed_total":current_total,''')
v+='''

def normative_cost_sources(gateway: Any,ware: int,actor: str)->list[dict[str,Any]]:
    with gateway.transaction("Read original normative correction sources")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        cursor.execute("""select r.OPERATION_ID,r.TT_ID,r.CURRENCY,json_value(r.RESULT_JSON,'$.total'),
         to_char(RRL_NORM_COST_CORRECTION.confirmed_total(r.OPERATION_ID),'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')
         from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_COST_CLAIM c on c.OPERATION_ID=r.OPERATION_ID
         where r.WARE_ID=:ware order by r.CREATED_AT desc,r.OPERATION_ID desc fetch first 101 rows only""",ware=ware)
        rows=cursor.fetchall()
        if len(rows)>100:raise LogisticsCostError("NORMATIVE_CORRECTION_SOURCE_BOUND","Не более 100 исходных начислений; нужна ограниченная выборка")
        return [{"operation_id":op,"trip_id":trip,"currency":currency,"original_total":original,"confirmed_total":current}for op,trip,currency,original,current in rows]
''';p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_expenses.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def articles(",'''    def normative_cost_sources(self,ware: int,actor: str)->list[dict[str,Any]]:
        from .transport_cost_read import normative_cost_sources
        return normative_cost_sources(self.gateway,ware,actor)

    def articles(''',1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/contracts_expenses.py");v=p.read_text(encoding="utf-8")
v=v.replace("    def articles(","    def normative_cost_sources(self,ware: int,actor: str)->list[dict[str,Any]]: ...\n    def articles(",1);p.write_text(v,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/api/logistics_expense_routes.py");v=p.read_text(encoding="utf-8")
v+='''

@router.get("/warehouses/{ware_id}/normative-costs")
def normative_cost_sources(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsExpensePort=Depends(logistics_expense_service))->list[dict[str,Any]]:
    if ware_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.normative_cost_sources(ware_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
''';p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/TransportCostPreview.tsx");v=p.read_text(encoding="utf-8")
v=v.replace("cost_posted:boolean;","cost_posted:boolean;confirmed_total?:string;")
v=v.replace("apiFetch<{recognized:Preview|null}>","apiFetch<{recognized:Preview|null;confirmed_total:string}>")
v=v.replace("const result=saved.recognized??await","const result=(saved.recognized?{...saved.recognized,confirmed_total:saved.confirmed_total}:null)??await")
v=v.replace('Затраты проведены и сохранены.','Затраты проведены и сохранены.')
v=v.replace('   <p>Итого:', '   {current.cost_posted&&<p>Подтверждённый итог с корректировками: {current.confirmed_total} {current.currency}.</p>}\n   <p>Исходное начисление:')
p.write_text(v,encoding="utf-8")
print("605 current adjusted total and original normative sources visible, original archived recognition untouched.")
