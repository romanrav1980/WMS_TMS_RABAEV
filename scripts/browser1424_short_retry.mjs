import {chromium} from '../admin/wms_admin_frontend/node_modules/playwright/index.mjs';import fs from 'node:fs';
const b=await chromium.launch({headless:true});try{
 const p=await b.newPage(),errors=[],bodies=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:8088/wms-admin/case-pick-tsd.html?case_task_id=1134');await p.locator('#adminLoginForm button[type=submit]').click();await p.locator('#cpTsdTaskId').filter({hasText:'1134'}).waitFor();
 let phase=0;await p.route('**/api/case-pick/tasks/1134/lines/1137/short',r=>{bodies.push(r.request().postData());phase++;const body=JSON.parse(r.request().postData());return r.fulfill({status:phase===1?503:200,contentType:'application/json',body:JSON.stringify(phase===1?{detail:'TEST unknown response'}:{case_pick_task_id:1134,case_pick_line_id:1137,case_pick_short_id:1424,offline_event_id:body.offline_event_id,status:'PENDING_APPROVAL'})});});
 await p.locator('#cpTsdShort').click();await p.locator('#cpTsdRetryPosting').waitFor();
 await p.locator('#cpTsdRetryPosting').click();await p.waitForFunction(()=>!localStorage.getItem(JSON.stringify(['nicora.casePickIntent',cpTsdApiBase(),cpTsdUser()])));
 if(bodies.length!==2||bodies[0]!==bodies[1])throw Error('Shortage replay changed');
 const integrity=await p.evaluate(()=>{
  const task=cpTsd.task,line=cpTsdCurrentLine();document.getElementById('cpTsdFactQty').value='999';let unpostedBlocked=false;try{cpCaseShortIntent.create(task,line);}catch{unpostedBlocked=true;}
  document.getElementById('cpTsdFactQty').value='';const intent=cpCaseShortIntent.create(task,line);return {unpostedBlocked,emptyUsesPosted:intent.payload.picked_qty===line.picked_qty,wrongIdentityRejected:!cpCaseShortIntent.confirms(intent,{case_pick_short_id:1,offline_event_id:'OTHER'})};
 });
 if(Object.values(integrity).some(v=>!v)||errors.length)throw Error(JSON.stringify({integrity,errors}));
 fs.writeFileSync('tmp/result1424.json',JSON.stringify({sameBodyReplay:true,interceptedPosts:bodies.length,oracleWrites:0,integrity,errors},null,2));console.log(JSON.stringify({sameBodyReplay:true,integrity,errors}));
}finally{await b.close();}
