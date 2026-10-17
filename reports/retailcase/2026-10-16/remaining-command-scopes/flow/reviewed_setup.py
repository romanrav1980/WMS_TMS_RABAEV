"""Fresh isolated3EA physical HU execution with WARE/GROUP grants and no flat right."""
from pathlib import Path
import sys,json,secrets,httpx,oracledb
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).parent));import assembly_scope_fixture as f
from app.db import oracle_connection
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.api.warehouse_hu_routes import Move,execute
base=Path('C:\\projects\\TMS\\reports\\retailcase\\2026-10-16\\remaining-command-scopes\\flow');out=base/'acceptance.json';assert not out.exists()
tag=secrets.token_hex(5);prefix='HT16.'+tag;ware=40000000+int(tag[:5],16);other=ware+10000000
x=dict(state='BEFORE_METADATA',tag=tag,prefix=prefix,warehouse=ware,foreign_warehouse=other,actor='HT16O'+tag,role='HT16R'+tag,group='HT16G'+tag,assignment='HT16A'+tag,group_assignment='HT16B'+tag,source='HT16S'+tag,target='HT16T'+tag,rollback_target='HT16U'+tag,foreign='HT16F'+tag,parent='HT16.P:'+tag,child='HT16.C:'+tag,lot='HT16.LOT:'+tag,article='AS16ACE9C011B16',http=[],commands={},started_at=datetime.now(timezone.utc).isoformat(),hardware_verified=False)
g=f.OracleGateway()
def save():out.write_text(json.dumps(x,indent=2,default=str),encoding='utf-8')
with out.open('x',encoding='utf-8')as stream:json.dump(x,stream)
def acl(kind,payload,suffix):
 cmd=f.normalize(f.Command(operation_id=prefix+'.'+suffix,command_type=kind,payload=payload),'ACCESS');x['commands'][suffix]=dict(wire=cmd,state='IN_FLIGHT');save();result=f.AccessMetadataService(g).command('admin',cmd);x['commands'][suffix].update(state='COMMITTED',result=result);save();return result
def native(command,suffix):
 x['commands'][suffix]=dict(wire=command.canonical_json(),state='IN_FLIGHT');save();result=f.StockPosting().post(command);x['commands'][suffix].update(state='COMMITTED',result=result);save();return result
with f.stock_configuration_transaction(g,f.NOTE,'admin','warehouse_settings_edit')as c:
 for w in(ware,other):
  c.execute('insert into RRL_WARES(ID,NAME,PREFIX)values(:w,:n,:p)',w=w,n=prefix+'.W'+str(w),p='H'+tag[:2])
 for cell,w in[(x['source'],ware),(x['target'],ware),(x['rollback_target'],ware),(x['foreign'],other)]:
  c.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,1,0,0,0,0,0)',c=cell,w=w)
  c.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 c.execute('insert into USER_GROUP(ID,NAME)values(:id,:n)',id=x['actor'],n=f.NOTE)
 c.execute('insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:pw,:n,:id,1,0,0)',id=x['actor'],pw=secrets.token_urlsafe(32),n=f.NOTE)
ReceiptConfiguration(g).sku_rule(ware,x['article'],dict(pick_cell=x['source'],temp_min=None,temp_max=None,min_shelf_days=0),'admin')
with g.transaction('Fresh isolated HT16 inventory revision')as c:x['revision']=int(c.callfunc('REVIZION.create_revizion',oracledb.DB_TYPE_NUMBER,[ware,'admin']))
save();native(f.StockCommand(prefix+'.BIRTH','INVENTORY_REGISTER_LOT','admin',(),{'revision_id':x['revision']},metadata=dict(uid=x['lot'],cell=x['source'],article=x['article'],quantity='3',expiry_date='2030-01-01',price='0',reason=f.NOTE)),'BIRTH')
for w in(ware,other):acl('OBJECT_SAVE',dict(kind='WAREHOUSE',object_id=str(w),title=prefix+'.W'+str(w),active=True,expected_version=0),'OBJECT.'+str(w))
acl('ROLE_SAVE',dict(role_id=x['role'],title=f.NOTE,permissions=['warehouse_task_execute','warehouse_task_view','warehouse_task_assign'],active=True,expected_version=0),'ROLE')
now=datetime.now(timezone.utc)
assignment=dict(username=x['actor'],role_id=x['role'],membership='CURRENT',snapshot_version=None,valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=2)).isoformat(),reason=f.NOTE,expected_version=0)
acl('ASSIGN',dict(assignment,assignment_id=x['assignment'],scope_kind='WAREHOUSE',scope_id=str(ware)),'ASSIGN.WARE')
assert g.fetch_all("select RRL_HAS_WRIGHT(:a,'warehouse_task_execute')X,RRL_HAS_WRIGHT(:a,'wms_admin_login')Y from dual",{'a':x['actor']})==[dict(x=0,y=0)]
