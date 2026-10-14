exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.oracle_gateway import OracleGateway
from app.services.resource_management_service import ResourceManagementService
from app.schemas import ResourceEquipmentCreateRequest,ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,WarehouseTaskStatusRequest
from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
from app.services.warehouse_task_service import WarehouseTaskService
from datetime import datetime,timedelta
actor="TR22613508027ed";code="IW22713508027ed";ware=51365792
resources=ResourceManagementService()
equipment=resources.create_equipment(ResourceEquipmentCreateRequest(equipment_code=code,equipment_type="REACHTRUCK",ware_id=ware,created_by="admin"))
resource=resources.create_resource(ResourceCreateRequest(resource_code=code,resource_name="Own227 marked placement",resource_type="REACHTRUCK",equipment_id=equipment,user_id=actor,ware_id=ware,created_by="admin"))
QualificationAdmin(OracleGateway()).set_qualification(resource,"PUTAWAY",True,"admin")
now=datetime.now()
shift=resources.create_shift(ResourceShiftCreateRequest(shift_code=code,shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=4),ware_id=ware,status="OPEN",created_by="admin"))
session=resources.login_session(ResourceSessionLoginRequest(shift_id=shift,resource_id=resource,equipment_id=equipment,operator_user_id=actor,created_by="admin"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TASK_ID from RRL_INTERWARE_PUT_PLAN where OPERATION_ID='IW227.PLAN:13508027ed'");task=q.fetchone()[0]
WarehouseTaskService().assign_task(task,WarehouseTaskStatusRequest(updated_by=actor,assigned_to=actor,resource_id=resource,resource_session_id=session,equipment_id=equipment))
print(json.dumps({"resource_id":resource,"resource_session_id":session,"equipment_id":equipment}))
