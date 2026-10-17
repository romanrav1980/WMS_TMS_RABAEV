// C0122: живые GET под admin (только чтение) — формы ответов receipt/workspaces.
const fs=require("fs"); const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H={Authorization:"Basic "+Buffer.from("admin:"+pass).toString("base64")};
(async()=>{for(const p of ["/api/access/workspaces?limit=5","/api/case-pick/tasks/1151","/api/case-pick/tasks/1151/transfer-receipt?offline_event_id=MT16.926cdde30a.TRANSFER","/api/case-pick/tasks/1151/transfer-receipt?offline_event_id=ABSENT.X"]){
 const r=await fetch("http://127.0.0.1:8088"+p,{headers:H}); console.log(r.status,p,(await r.text()).slice(0,900));}})();
