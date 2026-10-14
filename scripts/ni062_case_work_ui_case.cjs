const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const elements=new Map(),storage=new Map(),posted=[];let fail=true;
function element(id){if(!elements.has(id))elements.set(id,{value:"",textContent:"",children:[],listeners:{},addEventListener(kind,fn){this.listeners[kind]=fn;},replaceChildren(...children){this.children=children;},append(child){this.children.push(child);}});return elements.get(id);}
const dossier={case_id:"STORE:OWN",case_version:1,status:"OPEN",reason_text:"Own",obligations:[],findings:[],losses:[]};
const context={document:{getElementById:element,querySelectorAll:()=>[],createElement:()=>({textContent:"",addEventListener(){}})},
 window:{wmsAdminAuth:{state:{apiBase:"http://own",user:{username:"own",permissions:["*"]}},headers:()=>({}),hasPermission:()=>true},addEventListener(){}},
 localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
 crypto:require("node:crypto"),fetch:async(url,options)=>{
  if(options.method==="POST"){posted.push({url,body:JSON.parse(options.body)});if(fail){fail=false;throw Error("network timeout");}return{ok:true,status:200,json:async()=>({operation_id:posted.at(-1).body.operation_id,action:"ASSIGN",case_version:2})};}
  return{ok:true,status:200,json:async()=>dossier};
 }};
vm.runInNewContext(fs.readFileSync("wiki-raw/wms_admin_ui_reference/store-investigations.js","utf8"),context);
async function click(id){await element(id).listeners.click();}
(async()=>{
 element("caseId").value="STORE:OWN";await click("caseLoad");
 element("caseExp").value="EXP";element("caseSec").value="SEC";element("caseDeadline").value="2026-10-12T10:00";
 await click("caseAssign");assert.equal(storage.size,1);assert.equal(posted.length,1);
 const original=JSON.stringify(posted[0]);assert.equal(posted[0].body.expected_version,1);
 assert.match(posted[0].body.search_deadline,/\.\d{6}\+00:00$/);
 element("caseExp").value="OTHER";await click("caseRetry");
 assert.equal(JSON.stringify(posted[1]),original);assert.equal(storage.size,0);
 console.log("PASS091 actual case UI handlers freeze version/UTC deadline/actor intent before send; unknown timeout retries exact original body/ID and clears confirmed result");
})().catch(error=>{console.error(error);process.exitCode=1;});
