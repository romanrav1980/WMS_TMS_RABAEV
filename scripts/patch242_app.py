from pathlib import Path
root=Path("api/wms_api_server/app/modules/inventory")
for file in ["contracts_interwarehouse.py","infrastructure/interwarehouse.py"]:
 p=root/file;s=p.read_text(encoding="utf-8").replace("def plan_placement(self, operation_id: str, receipt_id: str, actor: str)","def plan_placement(self, operation_id: str, receipt_id: str, actor: str, superseded_task_id: int | None=None, replan_reason: str | None=None)",1)
 if file.startswith("infrastructure"):
  s=s.replace('        try:\n            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_PUTAWAY_PLAN",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata={}))','''        metadata = {} if superseded_task_id is None else {"superseded_task_id":superseded_task_id,"replan_reason":replan_reason}
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,command_type="INTERWARE_PUTAWAY_PLAN",actor=actor,source={"receipt_operation_id":receipt_id},lines=(),metadata=metadata))''',1)
 p.write_text(s,encoding="utf-8")
p=root/"api/interwarehouse_routes.py";s=p.read_text(encoding="utf-8");s=s.replace('@router.post("/placement")','''class PlacementReplan(PlacementPlan):
    superseded_task_id: int | None = Field(default=None,strict=True,gt=0)
    replan_reason: str | None = Field(default=None,strict=True,min_length=1,max_length=500)

    @model_validator(mode="after")
    def replan_contract(self) -> "PlacementReplan":
        if (self.superseded_task_id is None)!=(self.replan_reason is None) or self.replan_reason is not None and not self.replan_reason.strip():
            raise ValueError("Original unstarted task and replan reason required together")
        return self

@router.post("/placement")''',1)
s=s.replace("def placement(body: PlacementPlan,","def placement(body: PlacementReplan,",1).replace("service.plan_placement(body.operation_id,body.receipt_operation_id,user.username)","service.plan_placement(body.operation_id,body.receipt_operation_id,user.username,body.superseded_task_id,body.replan_reason)",1);p.write_text(s,encoding="utf-8")
p=root/"infrastructure/interwarehouse_queue.sql";s=p.read_text(encoding="utf-8").replace("f.TASK_ID PLACED_TASK_ID,","f.TASK_ID PLACED_TASK_ID,active_plan.TASK_ID PLACEMENT_PLAN_TASK_ID,active_plan.TASK_STATUS PLACEMENT_PLAN_TASK_STATUS,",1)
s=s.replace("left join RRL_INTERWARE_PLACEMENT f","left join(select ip.RECEIPT_OPERATION_ID,ip.TASK_ID,wt.STATUS TASK_STATUS from RRL_INTERWARE_PUT_PLAN ip join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=ip.TASK_ID where wt.STATUS not in('DONE','CANCELLED')) active_plan on active_plan.RECEIPT_OPERATION_ID=r.OPERATION_ID\nleft join RRL_INTERWARE_PLACEMENT f",1);p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8").replace('<button id="iwPlacement">Создать задание к воротам рейса</button>','<button id="iwPlacement">Создать задание к воротам рейса</button><label>Основание перепланирования<input id="iwReplanReason" maxlength="500"></label><button id="iwPlacementReplan">Перепланировать не начатое задание</button><p>Старое задание отменяется и новое создаётся одной операцией. Назначенное или начатое задание требует отдельного процесса.</p>',1);p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('r.base_uom+" → "+r.outbound_dock,r.receipt_operation_id','r.base_uom+" → "+r.outbound_dock+(r.placement_plan_task_id?" · задание "+r.placement_plan_task_id:""),r.receipt_operation_id',1)
s=s.replace('el("iwRelease").addEventListener','''el("iwPlacementReplan").addEventListener("click",async()=>{if(busy||pending)return;try{
 const selected=decisionPlans.find(r=>r.receipt_operation_id===el("iwPlacementReceipt").value);
 if(!selected?.placement_plan_task_id||selected.placement_plan_task_status!=="PLANNED")throw Error("Обновите планы и выберите приёмку с ещё не назначенным заданием.");
 const body={operation_id:"INTERWARE.REPLAN:"+crypto.randomUUID(),receipt_operation_id:selected.receipt_operation_id,superseded_task_id:selected.placement_plan_task_id,replan_reason:el("iwReplanReason").value.trim()};if(!body.replan_reason)throw Error("Укажите основание перепланирования.");
 const intent={path:"/placement",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());decisionPlans=[];el("iwPlacementReceipt").replaceChildren();
 }catch(e){say(e.message);}});
 el("iwRelease").addEventListener''',1);p.write_text(s,encoding="utf-8")
