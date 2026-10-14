from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_weighted_case.py");t=p.read_text(encoding="utf-8")
t=t.replace("class WeightedCasePort(Protocol):",'''class WeighedLineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100)
    warehouse_scale_capture: str = Field(pattern=r"^[A-F0-9]{64}$")
    scan_cell: str = Field(min_length=1, max_length=60)
    scan_container: str = Field(min_length=1, max_length=150)


class WeightedCasePort(Protocol):''')
t=t.replace('    def confirm(self, task:', '    def weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]: ...\n    def confirm(self, task:')
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py");t=p.read_text(encoding="utf-8").replace("import WeightedCaseRequest","import WeightedCaseRequest, WeighedLineRequest")
a="    def confirm(self, task:"
insert='''    def weigh_line(self, task: int, line: int, request: WeighedLineRequest, actor: str) -> dict[str, Any]:
        submitted = request.model_dump(mode="json")
        source = {"case_task_id": task, "case_line_id": line}
        saved = self.gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",
                                      {"p_op": request.operation_id})
        if saved:
            old = read_oracle_json(saved[0]["canonical_request"])
            if (old["actor"] != actor or old["command_type"] != "CASE_PICK_CONFIRM" or old["source"] != source
                    or old["metadata"].get("weighed_confirmation") != submitted):
                raise StockPostingError("OPERATION_CONTENT_CONFLICT", request.operation_id)
            metadata = old["metadata"]
        else:
            try:
                with self.gateway.transaction("Weighed CASE current source READ ONLY") as q:
                    q.execute("set transaction read only")
                    q.callproc("RRL_CASE_TASK_ACCESS.assert_scope", [task, actor, "case_pick_execute"])
                    q.execute("""select c.WEIGHT_KG,c.SCANNED_PRODUCT,nvl(l.PICKED_QTY,0)
                        from RRL_WH_SCALE_CAPTURE c join RRL_CASE_PICK_LINE l
                          on l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID and l.CASE_PICK_LINE_ID=c.CASE_PICK_LINE_ID
                        where c.CAPTURE_KEY=:p_key and c.CASE_PICK_TASK_ID=:p_task and c.CASE_PICK_LINE_ID=:p_line
                          and c.MEASUREMENT_BASIS='NET'""",
                        p_key=request.warehouse_scale_capture,p_task=task,p_line=line)
                    row = q.fetchone()
                    if row is None:
                        raise ValueError("The NET capture belongs to another CASE line or is missing")
                    weight, product, previous = row
                    metadata = {"fact_qty": format(Decimal(str(previous))+Decimal(str(weight)), "f"),
                        "scan_cell": request.scan_cell, "scan_container": request.scan_container,
                        "scan_product": product, "offline_event_id": None,
                        "warehouse_scale_capture": request.warehouse_scale_capture,
                        "weighed_confirmation": submitted}
            except oracledb.DatabaseError as exc:
                code = exc.args[0].code
                if code in {20882, 20886, 1403, 1422}:
                    raise StockPostingError("WEIGHED_CASE_SOURCE_REJECTED", request.operation_id, code) from exc
                raise
        return StockPosting().post(StockCommand(operation_id=request.operation_id, command_type="CASE_PICK_CONFIRM",
            actor=actor, source=source, lines=(), units=(), metadata=metadata))

'''
assert t.count(a)==1;t=t.replace(a,insert+a)
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py");t=p.read_text(encoding="utf-8").replace("import WeightedCaseRequest,","import WeightedCaseRequest, WeighedLineRequest,")
t+='''

@router.post("/tasks/{task}/lines/{line}/weigh-line")
def confirm_weighed_line(task: int, line: int, body: WeighedLineRequest,
                         user: AdminUser = Depends(require_permission("case_pick_execute")),
                         service: WeightedCasePort = Depends(weighted_case_service)) -> dict:
    try:
        return {"case_pick_task_id": task, "case_pick_line_id": line,
                **service.weigh_line(task, line, body, user.username)}
    except ValueError as exc:
        raise HTTPException(409, {"code": "WEIGHED_CASE_SOURCE_REJECTED", "message": str(exc),
                                 "outcome_confirmed": True, "retry_same_operation_id": False}) from exc
'''
out[str(p)]=t
print(json.dumps(out,ensure_ascii=True))
