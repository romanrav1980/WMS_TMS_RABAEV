(() => {
 const el=id=>document.getElementById(id);
 el("sapTripChoose").addEventListener("click",()=>{
  try{
   const prepared=orderState.preparations.get(orderState.selectedId)?.result;
   if(!prepared?.st_number)throw Error("Сначала покажите сохранённую подготовку СТ.");
   el("sapTripPickerSource").value=prepared.st_number;
   window.dispatchEvent(new CustomEvent("wms-st-trip-picker-open",{detail:{
    st_number:prepared.st_number,purpose:"ASSIGN",source_input_id:"sapTripPickerSource"}}));
  }catch(e){el("sapTripReviewMessage").textContent=e.message;}
 });
 window.addEventListener("wms-st-trip-selected",e=>{
  const prepared=orderState.preparations.get(orderState.selectedId)?.result;
  if(!prepared||prepared.st_number!==e.detail.st_number||el("sapTripPickerSource").value!==e.detail.st_number)return;
  el("sapTripId").value=String(e.detail.trip.trip_id);el("sapTripId").dispatchEvent(new Event("input"));
  el("sapTripReviewMessage").textContent="Выбран рейс "+e.detail.trip.trip_id+". Покажите его текущие ограничения, затем подтвердите назначение СТ.";
 });
 window.addEventListener("wms-admin-auth-ready",()=>{el("sapTripPickerSource").value="";});
})();
