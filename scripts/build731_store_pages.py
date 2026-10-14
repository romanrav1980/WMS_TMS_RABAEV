from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py");s=p.read_text(encoding="utf-8")
start=s.index("    def places(");end=s.index("    def confirm(",start);old=s[start:end]
sql=old.split('rows=self.gateway.fetch_all("""',1)[1].split('""",',1)[0]
sql=sql[:sql.index("             order by")]
sql=sql.replace("receipt.RECEIPT_STATE","receipt.RECEIPT_STATE,lf.LOADED_AT SORT_AT",1)
new='''    def places(self,trip_id: int,store_address: str,actor: str,after: str="",limit: int=200)->list[dict[str,Any]]:
        if limit<1 or limit>200 or len(after)>100:raise StoreReceiptError("STORE_PLACE_PAGE_BOUND","Use a page of1..200 places",422)
        params={"trip":trip_id,"addr":store_address,"actor":actor,"after_id":after,"page_size":limit}
        eligible="""'''+sql+'''"""
        if after:
            found=self.gateway.fetch_all("with eligible as("+eligible+")select count(*) N from eligible where LOAD_OPERATION_ID=:after_id",{k:v for k,v in params.items()if k!="page_size"})
            if found[0]["n"]!=1:raise StoreReceiptError("STORE_PLACE_CURSOR_SCOPE","Cursor must belong to the current trip/address/receiver",422)
        return self.gateway.fetch_all("with eligible as("+eligible+""")
            select l.LOAD_OPERATION_ID,l.ROOT_KEY,l.GROSS_WEIGHT_KG,l.DEPARTED_AT,l.RECEIPT_OPERATION_ID,l.RECEIPT_STATE from eligible l
             where :after_id is null or exists(select 1 from eligible anchor where anchor.LOAD_OPERATION_ID=:after_id
                and(l.SORT_AT>anchor.SORT_AT or(l.SORT_AT=anchor.SORT_AT and l.LOAD_OPERATION_ID>anchor.LOAD_OPERATION_ID)))
             order by l.SORT_AT,l.LOAD_OPERATION_ID fetch first :page_size rows only""",params)

'''
s=s[:start]+new+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/contracts.py");s=p.read_text(encoding="utf-8").replace("def places(self, trip_id: int, store_address: str, actor: str)","def places(self, trip_id: int, store_address: str, actor: str,after: str=\"\",limit: int=200)");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s=p.read_text(encoding="utf-8").replace("def places(trip_id: int,store_address: str,","def places(trip_id: int,store_address: str,after: str=Query(\"\",max_length=100),limit: int=Query(200,ge=1,le=200),").replace("service.places(trip_id,store_address,user.username)","service.places(trip_id,store_address,user.username,after,limit)");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");s=p.read_text(encoding="utf-8").replace('const [corrupt,setCorrupt]=useState(false);','const [corrupt,setCorrupt]=useState(false),[more,setMore]=useState(false);').replace('setPlaces([]);setPreview(null);setPending(null);','setPlaces([]);setMore(false);setPreview(null);setPending(null);',1).replace("async function loadPlaces(recover=false)","async function loadPlaces(recover=false,append=false)").replace('const scope=key,damaged=','const after=append?places.at(-1)?.load_operation_id||"":"",scope=key,damaged=').replace('encodeURIComponent(address),credentials);','encodeURIComponent(address)+"&limit=100"+(after?"&after="+encodeURIComponent(after):""),credentials);',1).replace('setPlaces(data);setMessage','setPlaces(rows=>append?[...rows,...data.filter(x=>!rows.some(old=>old.load_operation_id===x.load_operation_id))]:data);setMore(data.length===100);setMessage',1).replace('corrupt,recover:()=>loadPlaces(true),','corrupt,more,next:()=>loadPlaces(false,true),recover:()=>loadPlaces(true),');out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreReceiptPanel.tsx");s=p.read_text(encoding="utf-8").replace('   {preview&&<>','   {flow.more&&<button onClick={()=>void flow.next()} disabled={flow.busy||flow.corrupt}>Следующие грузовые места</button>}\n   {preview&&<>');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
