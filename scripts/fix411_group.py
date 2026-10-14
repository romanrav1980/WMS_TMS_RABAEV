from pathlib import Path
import json
out={}
p=Path('db/migrations/2026-10-12_ni061_group_receive/003_core.sql');t=p.read_text(encoding='utf-8').replace("v_cell:=m.get_string('scan_cell');RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,plan.TARGET_WARE_ID);","v_cell:=m.get_string('scan_cell');")
t=t.replace("if x.get_string('article')!=v_article or x.get_string('base_uom')!=v_uom or RRL_STOCK_MATH.quantity(x.get_string('quantity'))!=v_qty","if x.get_string('article')is null or x.get_string('article')!=v_article or x.get_string('base_uom')is null or x.get_string('base_uom')!=v_uom or x.get_string('quantity')is null or RRL_STOCK_MATH.quantity(x.get_string('quantity'))!=v_qty")
t=t.replace('n number;unit_count number;requested','n number;unit_count number;total_units number:=0;requested')
t=t.replace("manifest:=item.get_object('issued_manifest');","manifest:=item.get_object('issued_manifest');total_units:=total_units+manifest.get_number('physical_unit_count');\n if total_units>10000 then raise_application_error(-20881,'INTERWARE_GROUP_UNIT_BOUND_10000');end if;",1)
out[p.as_posix()]=t
p=Path('db/migrations/2026-10-12_ni061_group_receive/004_owner.sql');t=p.read_text(encoding='utf-8')
t=t.replace('v_event number;unit_count number:=0;','v_event number;v_st number;v_payload clob;unit_count number:=0;')
t=t.replace("v_uid:=item.get_string('uid');v_article:=","v_st:=item.get_number('st_id');v_uid:=item.get_string('uid');v_article:=",1)
t=t.replace("values(op,v_uid,item.get_number('st_id'),v_article,v_qty,v_uom,v_event)","values(op,v_uid,v_st,v_article,v_qty,v_uom,v_event)")
t=t.replace(" insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('INTERWAREGROUP:'"," v_payload:=j.to_clob;\n insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('INTERWAREGROUP:'",1)
t=t.replace("'INTERWAREHOUSE_RECEIVED',j.to_clob);","'INTERWAREHOUSE_RECEIVED',v_payload);",1)
out[p.as_posix()]=t
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''class GroupReceiveItem(BaseModel):
    model_config=ConfigDict(extra="forbid")
    uid: str=Field(strict=True,min_length=1,max_length=200)
    article: str=Field(strict=True,min_length=1,max_length=160)
    scan_article: str=Field(strict=True,min_length=1,max_length=128)
    quantity: str=Field(strict=True,pattern=r"^[0-9]+(\\.[0-9]+)?$",max_length=40)
    base_uom: str=Field(strict=True,min_length=1,max_length=20)

class GroupReceive(PhysicalAction):
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    items: list[GroupReceiveItem]=Field(min_length=2,max_length=200)
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)

    @model_validator(mode="after")
    def distinct_items(self)->"GroupReceive":
        if len({item.uid for item in self.items})!=len(self.items):
            raise ValueError("Each stock leaf must occur once")
        return self

@router.post("/group-receive")
def group_receive(body: GroupReceive,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    return physical("INTERWARE_RECEIVE",body,user,service)

'''
if 'class GroupReceiveItem('not in t:t=t.replace('class PlacementPlan(BaseModel):',addition+'class PlacementPlan(BaseModel):',1)
out[p.as_posix()]=t
print(json.dumps(out))
