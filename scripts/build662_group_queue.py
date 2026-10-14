import json
from pathlib import Path
files={}
def edit(path,old,new):
 p=Path(path);s=files.get(path,p.read_text(encoding="utf-8"))
 if old not in s:raise RuntimeError(path+" anchor missing")
 files[path]=s.replace(old,new)
root="api/wms_api_server/app/modules/inventory/"
edit(root+"contracts_interwarehouse.py","def group_queue(self,ware: int,actor: str)","def group_queue(self,ware: int,actor: str,limit: int=200,after_operation_id: str|None=None)")
edit(root+"infrastructure/interwarehouse.py","def group_queue(self,ware: int,actor: str)","def group_queue(self,ware: int,actor: str,limit: int=200,after_operation_id: str|None=None)")
edit(root+"infrastructure/interwarehouse.py",".queue(ware,actor)",".queue(ware,actor,limit,after_operation_id)")
edit(root+"infrastructure/interwarehouse_group_read.py","def queue(self,ware: int,actor: str)","def queue(self,ware: int,actor: str,limit: int=200,after_operation_id: str|None=None)")
edit(root+"infrastructure/interwarehouse_group_read.py",'q.execute("set transaction read only");_scope(q,ware,actor)\n            q.execute', '''q.execute("set transaction read only");_scope(q,ware,actor)
            if not 1<=limit<=200:
                raise StoreReturnReceiveError("INTERWARE_GROUP_PAGE_BOUND","Page size must be 1..200",422)
            if after_operation_id is not None:
                q.execute("select 1 from RRL_IW_GROUP_PLAN where OPERATION_ID=:after_id and TARGET_WARE_ID=:ware",after_id=after_operation_id,ware=ware)
                if q.fetchone() is None:
                    raise StoreReturnReceiveError("INTERWARE_GROUP_CURSOR_INVALID","Reload the warehouse queue",422)
            q.execute''')
edit(root+"infrastructure/interwarehouse_group_read.py","from RRL_IW_GROUP_PLAN p left join RRL_IW_GROUP_UNLOAD","from RRL_IW_GROUP_PLAN p left join RRL_IW_GROUP_PLAN anchor on anchor.OPERATION_ID=:after_id and anchor.TARGET_WARE_ID=:ware\n                left join RRL_IW_GROUP_UNLOAD")
edit(root+"infrastructure/interwarehouse_group_read.py",'where p.TARGET_WARE_ID=:ware order by p.ARRIVAL_DUE desc,p.OPERATION_ID fetch first 200 rows only""",ware=ware)','''where p.TARGET_WARE_ID=:ware
                and (:after_id is null or p.ARRIVAL_DUE<anchor.ARRIVAL_DUE
                    or (p.ARRIVAL_DUE=anchor.ARRIVAL_DUE and p.OPERATION_ID>anchor.OPERATION_ID))
                order by p.ARRIVAL_DUE desc,p.OPERATION_ID fetch first :page_limit rows only""",
                ware=ware,after_id=after_operation_id,page_limit=limit)''')
edit(root+"api/interwarehouse_routes.py",'def group_queue(ware_id: int,user:', 'def group_queue(ware_id: int,limit: int=Query(default=200,ge=1,le=200),after_operation_id: str|None=Query(default=None,min_length=1,max_length=100),user:')
edit(root+"api/interwarehouse_routes.py",'service.group_queue(ware_id,user.username)','service.group_queue(ware_id,user.username,limit,after_operation_id)')
html="wiki-raw/wms_admin_ui_reference/interwarehouse-groups.html"
edit(html,'<button id="ggRefresh">Обновить</button>','<button id="ggRefresh">Обновить</button><button id="ggNext" hidden>Следующие 100 мест</button>')
js="wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js"
edit(js,'let identity="",epoch=0,busy=false,pending=null,detail=null,proof=null,scans=[];','let identity="",epoch=0,busy=false,pending=null,detail=null,proof=null,scans=[],queueCursor=null;')
old='''el("ggRefresh").addEventListener("click",()=>read(async current=>{
 const ware=positiveInt("ggWare"),rows=await request("/group-warehouses/"+ware);if(!current()||ware!==Number(el("ggWare").value))return;'''
new='''function loadQueue(next=false){return read(async current=>{
 const ware=positiveInt("ggWare"),cursor=next?queueCursor:null;
 if(next&&!cursor)return;
 const rows=await request("/group-warehouses/"+ware+"?limit=100"+(cursor?"&after_operation_id="+encodeURIComponent(cursor):""));if(!current()||ware!==Number(el("ggWare").value))return;
 queueCursor=rows.length===100?rows[rows.length-1].operation_id:null;el("ggNext").hidden=!queueCursor;'''
edit(js,old,new)
anchor='''detail=null;el("ggProfile").replaceChildren();el("ggLots").replaceChildren();el("ggState").textContent="Грузовых мест: "+rows.length;restoreScans();
}));'''
edit(js,anchor,'''detail=null;el("ggProfile").replaceChildren();el("ggLots").replaceChildren();el("ggState").textContent="На странице грузовых мест: "+rows.length;restoreScans();
});}
el("ggRefresh").addEventListener("click",()=>loadQueue());
el("ggNext").addEventListener("click",()=>loadQueue(true));''')
edit(js,'if(id==="ggWare")el("ggPlan").replaceChildren();','if(id==="ggWare"){el("ggPlan").replaceChildren();queueCursor=null;el("ggNext").hidden=true;}')
edit(js,'if(fp===identity)return;identity=fp;epoch++;detail=null;','if(fp===identity)return;identity=fp;epoch++;queueCursor=null;el("ggNext").hidden=true;detail=null;')
print(json.dumps(files))
