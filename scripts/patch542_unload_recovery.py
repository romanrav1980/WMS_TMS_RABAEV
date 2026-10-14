import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/store_unloading.py");v=p.read_text(encoding="utf-8")
a=v.index('    with gateway.transaction("Read original store unloading fact")')
block=v[a:];v=v[:a]+"    try:\n"+"\n".join("    "+line for line in block.splitlines())+'''\n    except oracledb.DatabaseError as exc:
        code=getattr(exc.args[0],"code",0)
        if code==20882 or code==1403 or 20800<=code<=20999:
            raise StoreReceiptError("STORE_UNLOAD_SOURCE_UNAVAILABLE",str(exc.args[0]).split("\\n",1)[0],
                                    403 if code==20882 else 409)from exc
        raise
'''
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/delivery/useStoreReceipt.ts");v=p.read_text(encoding="utf-8")
v=v.replace(' const current=useRef(key);',' const inFlight=useRef(false);\n const current=useRef(key);')
v=v.replace('  if(busy)return;setBusy(true);','  if(busy||inFlight.current)return;inFlight.current=true;setBusy(true);')
v=v.replace('  }finally {setBusy(false);}\n }\n async function confirm','  }finally {inFlight.current=false;setBusy(false);}\n }\n async function confirm')
v=v.replace('  if(busy||pending||!preview)return;','  if(busy||inFlight.current||pending||!preview)return;')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreUnloadingPanel.tsx");v=p.read_text(encoding="utf-8")
v=v.replace(' const current=useRef(scope);',' const inFlight=useRef(false);\n const current=useRef(scope);')
v=v.replace('  if(busy||disabled)return;const key=scope;','  if(busy||inFlight.current||disabled)return;inFlight.current=true;const key=scope;')
v=v.replace('  }finally{if(current.current===key)setBusy(false);}','  }finally{inFlight.current=false;if(current.current===key)setBusy(false);}')
v=v.replace('  if(pending||preview.already_received','  if(pending||inFlight.current||preview.already_received')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/finance/TransportTariffSources.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('<button type="button" onClick={read}','<button type="button" title="Прочитать исходные тарифы и опубликованные версии без начисления расходов" onClick={read}')
out[str(p)]=v
print(json.dumps(out))
