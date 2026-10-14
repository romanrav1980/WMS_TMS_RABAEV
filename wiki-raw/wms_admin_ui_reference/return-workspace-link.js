(()=>{
 // Navigation fills warehouse identity only; existing handlers perform the read.
 let opened=false;
 const screens={"interwarehouse.html":["iwWare","iwLoad"],"supplier-handover.html":["shWare","shLoad"],"logistics-costs.html":["lcWare","lcReadRates"],"store-return-receiving.html":["receiveWare","receiveLoad"],"store-return-putaway.html":["putWare","putLoad"],"supplier-return.html":["srWare","srLoad"],"return-disposal.html":["rdWare","rdLoad"]};
 function open(){
  if(opened||!window.wmsAdminAuth?.state.user)return;
  const ids=screens[location.pathname.split("/").pop()];if(!ids)return;
  const ware=Number(new URLSearchParams(location.search).get("warehouse_id"));
  if(!Number.isSafeInteger(ware)||ware<1)return;
  const input=document.getElementById(ids[0]),button=document.getElementById(ids[1]);
  if(!input||!button||input.disabled||button.disabled)return;
  const permission=button.closest("[data-permission]")?.dataset.permission;
  if(permission&&!window.wmsAdminAuth.hasPermission(permission))return;
  opened=true;input.value=String(ware);input.dispatchEvent(new Event("input",{bubbles:true}));button.click();
 }
 window.addEventListener("wms-admin-auth-ready",open);open();
})();
