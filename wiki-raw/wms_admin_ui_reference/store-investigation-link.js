(()=>{
 let applied=false;
 function open(){
  if(applied||!window.wmsAdminAuth?.state.user)return;
  const value=new URLSearchParams(location.search).get('case_id');
  if(!value||!/^[A-Za-z0-9_.:-]{1,100}$/.test(value))return;
  const input=document.getElementById('caseId'),button=document.getElementById('caseLoad');
  if(!input||!button||input.disabled||button.disabled)return;
  applied=true;input.value=value;input.dispatchEvent(new Event('input',{bubbles:true}));button.click();
 }
 window.addEventListener('wms-admin-auth-ready',open);open();
})();