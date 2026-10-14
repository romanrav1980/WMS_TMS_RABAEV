from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/fulfillment/domain/store_order.py");s=p.read_text(encoding="utf-8").replace('same_day: bool, received: datetime) -> dict:', 'same_day: bool, received: datetime, delivery_exception: bool | None = None) -> dict:')
s=s.replace("    if str(delivery.isoweekday()) not in weekdays.split(','):\n        raise ValueError('Delivery date is outside store calendar')","    calendar_allowed = delivery_exception if delivery_exception is not None else str(delivery.isoweekday()) in weekdays.split(',')")
s=s.replace("'late': late, 'offset_minutes': offset_minutes}","'late': late, 'offset_minutes': offset_minutes, 'calendar_allowed': calendar_allowed,\n            'calendar_basis': 'DATE_EXCEPTION' if delivery_exception is not None else 'WEEKLY_SOURCE_BOOK'}");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/store_orders.py");s=p.read_text(encoding="utf-8")
s=s.replace("'status':'DRAFT' if times['late'] else 'IMPORTED'","'status':'DRAFT' if times['late'] or not times['calendar_allowed'] else 'IMPORTED'")
s=s.replace("'admission_status':'PENDING_LATE' if times['late'] else 'ACCEPTED'","'admission_status':'PENDING_CALENDAR' if not times['calendar_allowed'] else 'PENDING_LATE' if times['late'] else 'ACCEPTED'")
s=s.replace("'delivery_date':data['DeliveryDate'],'utc_offset_minutes':times['offset_minutes'],'idempotent':False","'delivery_date':data['DeliveryDate'],'utc_offset_minutes':times['offset_minutes'],'idempotent':False,\n                          'calendar_basis':times['calendar_basis'],'calendar_exception':times.get('calendar_exception'),\n                          'late':times['late'],'calendar_allowed':times['calendar_allowed']")
old="cur.execute('select UTC_OFFSET_MINUTES,DELIVERY_WEEKDAYS,ALLOW_SAME_DAY from RRL_SAP_STORE_CALENDAR where WARE_ID=:w and CUSTOMER_STORE_MAP_ID=:s', {'w':int(data['WarehouseId']),'s':store[0]})"
new='''cur.execute("""select cal.UTC_OFFSET_MINUTES,cal.DELIVERY_WEEKDAYS,cal.ALLOW_SAME_DAY,ex.DAY_STATE,ex.VERSION_NO,ex.OPERATION_ID,ex.SOURCE_REFERENCE
          from RRL_SAP_STORE_CALENDAR cal left join RRL_SAP_STORE_CAL_EXCEPTION ex
          on ex.WARE_ID=cal.WARE_ID and ex.CUSTOMER_STORE_MAP_ID=cal.CUSTOMER_STORE_MAP_ID
            and ex.DELIVERY_DATE=to_date(:delivery_date,'YYYY-MM-DD')
            and ex.VERSION_NO=(select max(latest.VERSION_NO)from RRL_SAP_STORE_CAL_EXCEPTION latest
              where latest.WARE_ID=cal.WARE_ID and latest.CUSTOMER_STORE_MAP_ID=cal.CUSTOMER_STORE_MAP_ID and latest.DELIVERY_DATE=to_date(:delivery_date,'YYYY-MM-DD'))
          where cal.WARE_ID=:w and cal.CUSTOMER_STORE_MAP_ID=:s""",
          {'w':int(data['WarehouseId']),'s':store[0],'delivery_date':data['DeliveryDate']})'''
assert old in s;s=s.replace(old,new).replace("times = calendar(data,settings[0],settings[1],bool(settings[2]),received)","times = calendar(data,settings[0],settings[1],bool(settings[2]),received, None if settings[3] is None else settings[3]=='OPEN')\n        times['calendar_exception']=None if settings[3] is None else {'day_state':settings[3],'version':settings[4],'operation_id':settings[5],'source_reference':settings[6]}")
start=s.index('    def configure(');end=s.index('    def list(',start)
s=s[:start]+'''    def configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict:
        from .store_calendar import configure_calendar
        return configure_calendar(self.gateway, warehouse, store_code, body, actor)

    def calendar_context(self, warehouse: int, store_code: str, day: str, actor: str) -> dict:
        from .store_calendar import calendar_context
        return calendar_context(self.gateway, warehouse, store_code, day, actor)

    def set_calendar_exception(self, operation: str, body: dict, actor: str) -> dict:
        from .store_calendar import set_exception
        return set_exception(self.gateway, operation, body, actor)

'''+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/application/ports.py");s=p.read_text(encoding="utf-8").replace('    def configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict: ...','''    def configure(self, warehouse: int, store_code: str, body: dict, actor: str) -> dict: ...
    def calendar_context(self, warehouse: int, store_code: str, day: str, actor: str) -> dict: ...
    def set_calendar_exception(self, operation: str, body: dict, actor: str) -> dict: ...''');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/fulfillment/api/store_order_routes.py");s=p.read_text(encoding="utf-8")
s='from datetime import date\nfrom typing import Literal\nfrom pydantic import ConfigDict\n'+s
s=s.replace("    except ValueError as exc:\n        raise HTTPException(422,str(exc)) from exc\n\n\n@router.get('/{order_id}')", "    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except ValueError as exc:\n        raise HTTPException(422,str(exc)) from exc\n\n\n@router.get('/{order_id}')")
s+='''
class CalendarException(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int = Field(strict=True, gt=0)
    store_code: str = Field(min_length=1, max_length=100)
    delivery_date: date
    expected_version: int = Field(strict=True, ge=0)
    day_state: Literal["OPEN", "CLOSED"]
    source_reference: str = Field(min_length=8, max_length=500)
    reason: str = Field(min_length=8, max_length=500)


@router.get('/warehouses/{warehouse}/stores/{store_code}/calendar-context')
def calendar_context(warehouse: int, store_code: str, delivery_date: date,
                     user: AdminUser=Depends(require_permission('customer_rule_edit')),
                     service: StoreOrdersPort=Depends(store_order_service)) -> dict:
    try:
        return service.calendar_context(warehouse,store_code,delivery_date.isoformat(),user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc


@router.post('/calendar-exceptions')
def calendar_exception(body: CalendarException, user: AdminUser=Depends(require_permission('customer_rule_edit')),
                       service: StoreOrdersPort=Depends(store_order_service)) -> dict:
    try:
        return service.set_calendar_exception(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
