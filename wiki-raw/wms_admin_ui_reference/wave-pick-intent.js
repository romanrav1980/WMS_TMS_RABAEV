(() => {
  const common=window.wmsWaveCommandIntent;
  window.wmsWavePickIntent=common.create('wms-wave-pick-release-intent:',value=>
    common.baseValid(value)&&Object.keys(value.body).length===1&&Object.hasOwn(value.body,'operation_id'));
})();
