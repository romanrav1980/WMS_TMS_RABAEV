/* Preserve the original loading command until its own server result is confirmed. */
(() => {
 const valid = value => {
  if(!value || !Number.isSafeInteger(value.trip_id) || value.trip_id<1 ||
   !/^[A-Za-z0-9_.:-]{1,100}$/.test(value.body?.operation_id||''))return false;
  if(value.path==='/api/inventory/pallet-floor-types')return true;
  if(value.path==='/api/transport/loading/'+value.trip_id+'/depart')return true;
  return ['/api/transport/loading/confirm','/api/transport/loading/confirm-single',
   '/api/transport/loading/confirm-reconciliation'].includes(value.path)&&value.body.transport_task_id===value.trip_id;
 };
 window.wmsLoadingIntent={create:storageKey=>window.wmsCommandIntent.create('',valid,{storageKey}),
  confirms:(saved,result)=>result?.operation_id===saved.body.operation_id};
})();
