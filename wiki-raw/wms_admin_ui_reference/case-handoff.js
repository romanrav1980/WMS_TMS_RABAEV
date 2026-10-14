(() => {
  const prefix=()=> "case.handoff:"+caseApiBase()+":"+(window.wmsAdminAuth?.state.user?.username||"")+":";
  async function send(task) {
    const key=prefix()+task.case_pick_task_id;
    let saved=localStorage.getItem(key),body=saved?JSON.parse(saved):null;
    if(!body) {
      const current=await caseFetch("/api/case-pick/tasks/"+task.case_pick_task_id);
      const resource=Number(prompt("ID ресурса нового комплектовщика"));
      if(!Number.isSafeInteger(resource)||resource<=0)return;
      const session=Number(prompt("ID активной сессии нового комплектовщика"));
      if(!Number.isSafeInteger(session)||session<=0)return;
      const carrier=prompt("Отсканируйте идентификатор передаваемой паллеты");
      if(!carrier)return;
      body={to_resource_id:resource,to_resource_session_id:session,reason:"Подтверждённая передача из ARM комплектации",
        offline_event_id:"HANDOFF:"+crypto.randomUUID(),scan_container:carrier,
        expected_content_version:current.content_version,expected_assigned_to:current.assigned_to,
        expected_from_session_id:current.resource_session_id};
      localStorage.setItem(key,JSON.stringify(body));
    }
    try {
      await caseFetch("/api/case-pick/tasks/"+task.case_pick_task_id+"/transfer",{method:"POST",
        headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
      localStorage.removeItem(key);
    } catch(error) {
      if([400,403,404,409,422].includes(error.status))localStorage.removeItem(key);
      else error.message+=". Запрос сохранён: повторите «Передать» для того же задания.";
      throw error;
    }
  }
  window.caseHandoff={send};
})();
