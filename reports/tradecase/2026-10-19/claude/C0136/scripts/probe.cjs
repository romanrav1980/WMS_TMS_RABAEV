// C0136: живые GET под admin (только чтение) — выкупы, финансовые основания, единицы запаса склада 211559882.
const fs=require("fs");const pass=fs.readFileSync("C:/projects/TMS/AGENTS.md","utf8").match(/PASS=(\S+?)[`,)\s]/)[1];
const H={Authorization:"Basic "+Buffer.from("admin:"+pass).toString("base64")};const W="/api/tradecase/warehouses/211559882";
const get=async p=>{const t0=Date.now();try{const r=await fetch("http://127.0.0.1:8088"+p,{headers:H,signal:AbortSignal.timeout(20000)});const t=await r.text();console.log(r.status,Date.now()-t0+"ms",p,"\n ",t.slice(0,1300));try{return JSON.parse(t);}catch{return null;}}catch(e){console.log("ERR",p,String(e));}};
(async()=>{await get(W+"/site");for(const k of ["BUYOUT","ORDER","RECIPIENT"])await get(W+"/documents/"+k+"?limit=3");
const b=await get(W+"/buyouts?after=0&limit=5&pending_only=false");const id=b?.items?.[0]&&(b.items[0].buyout_id||b.items[0].identity);
if(id){await get(W+"/buyouts/"+encodeURIComponent(id));await get(W+"/buyouts/"+encodeURIComponent(id)+"/units?limit=3");}
const p=await get(W+"/stock/pallets?limit=5");const pal=p?.items?.[0]?.pallet_identifier;if(pal)await get(W+"/stock?pallet_identifier="+encodeURIComponent(pal)+"&limit=3");})();
