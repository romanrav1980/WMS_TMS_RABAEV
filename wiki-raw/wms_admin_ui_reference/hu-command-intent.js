/* HU recovery uses the same durable storage owner as wave commands. */
(() => {
  const commands={"create":"HU_CREATE","attach":"HU_ATTACH","attach-case":"HU_ATTACH","detach":"HU_DETACH","detach-case":"HU_DETACH","move":"HU_MOVE","unpack":"HU_UNPACK","unpack-case":"HU_UNPACK","relocate-slot":"HU_RELOCATE_SLOT","repack-slot":"HU_REPACK_SLOT","repack-case-slot":"HU_REPACK_SLOT"};
  const text=(v,max)=>typeof v==="string"&&v.length>0&&v.length<=max;
  function valid(v){
    const b=v?.body;
    return !!(v&&typeof v==="object"&&!Array.isArray(v)&&(commands[v.action]||["plan-move","ship"].includes(v.action))
      &&b&&typeof b==="object"&&!Array.isArray(b)&&text(b.identifier,200)
      &&text(b.operation_id,100)&&/^[A-Za-z0-9_.:-]+$/.test(b.operation_id)
      &&typeof b.scan_container==="string"&&b.scan_container.length<=200
      &&(v.action==="create"||(Number.isSafeInteger(b.expected_version)&&b.expected_version>=0)));
  }
  function confirms(saved,data){
    if(!valid(saved)||!data||data.operation_id!==saved.body.operation_id)return false;
    const id=saved.body.identifier;
    if(saved.action==="plan-move")return data.status==="PLANNED"&&data.pallet_identifier===id&&data.unit_code==="HU"
      &&Number.isSafeInteger(data.task_id)&&data.task_id>0;
    if(saved.action==="ship")return data.status==="SHIPPED"&&data.uid===id&&Array.isArray(data.shipments);
    return data.command===commands[saved.action]&&(data.root===id||data.pallet_identifier===id||data.parent?.root===id);
  }
  const store=window.wmsCommandIntent.create("wms-hu-intent:",valid,{invalid:"Некорректная сохранённая операция с грузовым местом."});
  window.wmsHuIntent={...store,confirms};
})();
