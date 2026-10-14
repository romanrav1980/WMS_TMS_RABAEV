(() => {
  const common=window.wmsWaveCommandIntent;
  function valid(value) {
    if(!common.baseValid(value))return false;
    const body=value.body;
    if(Object.keys(body).some(k=>!['operation_id','disposition','reason'].includes(k)))return false;
    if(body.disposition===undefined)return body.reason===undefined;
    return['RETURNED_TO_PLANNING','PARTIAL_SHIPPED_RETURNED'].includes(body.disposition)&&
      typeof body.reason==='string'&&Boolean(body.reason.trim())&&body.reason.length<=1000;
  }
  window.wmsWaveExecutionIntent=common.create('wms-wave-execution-intent:',valid);
})();
