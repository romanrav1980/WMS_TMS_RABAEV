(() => {
  const e=id=>document.getElementById(id);
  let busy=false;
  async function plan() {
    const auth=window.wmsAdminAuth;
    if(busy)return;
    if(!auth?.hasPermission("resource_shift_edit"))throw Error("Нет права управления сменами.");
    const id=e("reachBaseShift").value.trim();
    const main=Number(e("reachMainDrivers").value), duty=Number(e("reachDutyDrivers").value);
    if(!/^[1-9][0-9]*$/.test(id)||!Number.isInteger(main)||main<1||main>200||!Number.isInteger(duty)||duty<1||duty>2)throw Error("Укажите смену, число основных водителей и одного или двух дежурных.");
    busy=true;e("reachShiftPlan").disabled=true;
    try {
      const response=await fetch((auth.state.apiBase||"http://127.0.0.1:8088").replace(/\/$/,"")+"/api/resources/reach-shifts/"+id,
        {method:"POST",headers:auth.headers({"Content-Type":"application/json"}),body:JSON.stringify({main_drivers:main,duty_drivers:duty})});
      const data=await response.json();
      if(!response.ok)throw Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));
      e("reachShiftResult").textContent=data.shifts.map(s=>(s.reach_shift_role==="MAIN"?"Основная группа":"Дежурные")+" · смена "+s.shift_id+
        " · "+s.start_at+" — "+s.finish_at+" · водителей "+s.expected_drivers).join("\n")+
        "\nПеред выходом завершите текущий физический шаг и передайте оставшиеся задания.";
    }finally{busy=false;e("reachShiftPlan").disabled=false;}
  }
  e("reachShiftPlan").addEventListener("click",()=>plan().catch(error=>{e("reachShiftResult").textContent=error.message;}));
})();
