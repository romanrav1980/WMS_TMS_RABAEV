// C0139: живые GET под admin (только чтение) — исполнение рейса, груз в пути, CASE, основания склада 215590763.
const fs=require("fs");const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H={Authorization:"Basic "+Buffer.from("admin:"+pass).toString("base64")};const W="/api/tradecase/warehouses/215590763";
const get=async(p,n=1500)=>{const t0=Date.now();try{const r=await fetch("http://127.0.0.1:8088"+p,{headers:H,signal:AbortSignal.timeout(20000)});const t=await r.text();console.log(r.status,Date.now()-t0+"ms",p,"\n ",t.slice(0,n));try{return JSON.parse(t);}catch{return null;}}catch(e){console.log("ERR",p,String(e));}};
(async()=>{await get(W+"/documents/TRIP?limit=5");const ex=await get(W+"/trips/R1.1155/execution");await get(W+"/trips/NOPE/execution",300);
const ld=ex?.loads?.[0]?.load_operation_id;if(ld)await get(W+"/stock/transit?load_operation_id="+encodeURIComponent(ld)+"&limit=2");
await get("/api/admin/transport/tasks/33660",900);await get("/api/transport/loading/33660/status",600);
const o=await get(W+"/documents/ORDER?limit=10",2500);await get(W+"/stock/pallets?limit=5",900);await get(W+"/buyouts?after=0&limit=3",900);})();
