/* QC storage contracts use the same durable command owner as waves and HU. */
(() => {
 const object=v=>!!v&&typeof v==='object'&&!Array.isArray(v);
 const exact=(v,keys)=>object(v)&&Object.keys(v).every(k=>keys.includes(k));
 const text=(v,max)=>typeof v==='string'&&v.length>0&&v.length<=max;
 const identifier=v=>text(v,150)&&!v.includes('\u0000');
 const operation=v=>text(v,100)&&/^[A-Za-z0-9_.:-]+$/.test(v);
 const signature=v=>typeof v==='string'&&/^[A-F0-9]{64}$/.test(v);
 const decimal=v=>typeof v==='string'&&/^(0|[1-9][0-9]*)(\.[0-9]{1,9})?$/.test(v);
 function item(v){return exact(v,['scan_id','barcode','quantity'])&&text(v.scan_id,100)&&text(v.barcode,128)&&v.quantity==='1';}
 function mark(v){return exact(v,['system_code','profile_code','code'])&&text(v.system_code,40)&&text(v.profile_code,80)&&
   new TextEncoder().encode(v.profile_code).length<=80&&text(v.code,4000);}
 const list=(v,valid,max)=>Array.isArray(v)&&v.length<=max&&v.every(valid);
 function valid(v){
  if(!exact(v,['identifier','kind','body'])||!identifier(v.identifier)||!object(v.body))return false;
  const b=v.body,base=['operation_id','expected_composition_signature','note'];
  if(!operation(b.operation_id)||!signature(b.expected_composition_signature)||
    !(b.note===undefined||b.note===null||(typeof b.note==='string'&&b.note.length<=1000)))return false;
  if(v.kind==='plan')return exact(b,base);
  if(v.kind==='scan')return exact(b,[...base,'error_count','scans','item_scans'])&&Number.isSafeInteger(b.error_count)&&b.error_count>=0&&
    list(b.scans,mark,20000)&&list(b.item_scans,item,20000);
  if(v.kind==='final-weight')return exact(b,[...base,'capture_key'])&&signature(b.capture_key);
  if(v.kind==='weight')return exact(b,[...base,'gross_weight','wood_weight','quality_kind','measurement_origin'])&&
    (b.measurement_origin===undefined||b.measurement_origin==='MANUAL_CONFIRMED')&&
    decimal(b.gross_weight)&&Number(b.gross_weight)>0&&decimal(b.wood_weight)&&['WEIGHT','WEIGHT2'].includes(b.quality_kind);
  return false;
 }
 function validDraft(v){return exact(v,['identifier','signature','entries'])&&identifier(v.identifier)&&signature(v.signature)&&
   list(v.entries,x=>exact(x,['kind','value'])&&((x.kind==='item'&&item(x.value))||(x.kind==='mark'&&mark(x.value))),40000);}
 function readDraft(storageKey){
  const raw=localStorage.getItem(storageKey);if(raw===null)return{storageKey,raw,value:null};
  try{const value=JSON.parse(raw);if(!validDraft(value))throw Error('INVALID');return{storageKey,raw,value};}
  catch{return{storageKey,raw,value:null,damaged:true};}
 }
 const store=window.wmsCommandIntent.create('wms-outgoing-quality:',valid,{invalid:'Некорректная сохранённая команда контроля.'});
 window.wmsQualityIntent={...store,validDraft,readDraft};
})();
