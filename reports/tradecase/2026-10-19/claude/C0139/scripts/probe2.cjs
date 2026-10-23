// C0139: живые GET (admin) — коды CASE по штрихкоду и выкупы склада 215590763.
const fs=require("fs");const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H={Authorization:"Basic "+Buffer.from("admin:"+pass).toString("base64")};const W="/api/tradecase/warehouses/215590763";
const get=async(p,n=700)=>{const t0=Date.now();const r=await fetch("http://127.0.0.1:8088"+p,{headers:H,signal:AbortSignal.timeout(20000)});const t=await r.text();console.log(r.status,Date.now()-t0+"ms",p,"\n ",t.slice(0,n));};
(async()=>{for(const id of ["CP595000000001155","CASE:1155","690000000312355716"])await get(W+"/stock?pallet_identifier="+encodeURIComponent(id)+"&limit=2");
await get(W+"/documents/TRIP?limit=10",400);})();
