/* Only editable receiving data, never a receipt command or printer confirmation. */
window.wmsReceiptFormState={
 fields:['receiptSscc','receiptQuantity','receiptBatch','receiptExpiry','receiptProduced','receiptBarcode','receiptWeight','receiptHeight','receiptHeightM','receiptVolume','receiptUnit','receiptUnitQuantity','receiptMarkCode','receiptProfile','receiptScanMode'],
 capture(state){return {fields:Object.fromEntries(this.fields.map(id=>[id,document.getElementById(id).value])),
  units:Array.from(state.units,([unit_id,codes])=>({unit_id,codes,quantity:state.unitQuantities.get(unit_id)||null})),aggregations:state.aggregations};},
 valid(data,policy){
  if(!data||!data.fields||Object.keys(data.fields).length!==this.fields.length||!this.fields.every(id=>typeof data.fields[id]==='string'&&data.fields[id].length<=4000)||
   data.fields.receiptSscc.length>50||!Array.isArray(data.units)||data.units.length>10000||!Array.isArray(data.aggregations)||data.aggregations.length>1000)return false;
  const scan=(value,mode)=>value&&typeof value.code==='string'&&value.code.length>0&&new TextEncoder().encode(value.code).length<=4000&&
   policy.profiles?.some(p=>p.system_code===value.system_code&&p.profile_code===value.profile_code&&(p.scan_mode==='UNIT_OR_AGGREGATION'||p.scan_mode===mode));
  return new Set(data.units.map(u=>u?.unit_id)).size===data.units.length&&data.units.every(u=>u&&typeof u.unit_id==='string'&&u.unit_id.length>0&&u.unit_id.length<=128&&
   (u.quantity===null||typeof u.quantity==='string')&&Array.isArray(u.codes)&&u.codes.length>0&&u.codes.length<=50&&u.codes.every(c=>scan(c,'UNIT')))&&
   data.aggregations.every(a=>['BOX','PALLET'].includes(a?.level)&&scan(a,a.level));
 },
 apply(data,state,updateMode,render){
  state.operation=crypto.randomUUID();state.label=null;
  for(const id of this.fields)if(id!=='receiptScanMode')document.getElementById(id).value=data.fields[id];
  updateMode();document.getElementById('receiptScanMode').value=data.fields.receiptScanMode;
  state.units=new Map(data.units.map(u=>[u.unit_id,u.codes]));state.unitQuantities=new Map(data.units.map(u=>[u.unit_id,u.quantity]));state.aggregations=data.aggregations;
  document.getElementById('receiptPrintedScan').value='';document.getElementById('receiptZpl').disabled=true;document.getElementById('receiptConfirmLabel').disabled=true;
  document.getElementById('receiptLabelMessage').textContent='Восстановлен ввод, а не подтверждение печати. Проверьте физическую этикетку паллеты.';render();
 }
};