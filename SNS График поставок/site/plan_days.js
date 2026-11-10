/* Недельная эвристика: баланс региона и источника, консолидация неполных партий по району. */
(function(root){
 function suggestDays(candidates,existing,capacity){
  const global=Array(7).fill(0),cities=new Map(),districts=new Map(),smallDistricts=new Map(),sources=new Map();
  const arr=(map,key)=>{if(!map.has(key))map.set(key,Array(7).fill(0));return map.get(key)};
  const districtKey=r=>JSON.stringify([r.city,r.districtKnown?r.district:r.key]);
  const sourceKeys=r=>r.source?[r.source]:r.sources?.length?r.sources:['Источник не указан'];
  function add(r,day,amount){global[day]+=amount;arr(cities,r.city)[day]+=amount;arr(districts,districtKey(r))[day]+=amount;if(amount<capacity*.95)arr(smallDistricts,districtKey(r))[day]+=amount;const names=sourceKeys(r);for(const src of names)arr(sources,src)[day]+=amount/names.length}
  for(const r of existing)if(r.days?.length&&r.weekly!=null)for(const d of r.days)add(r,d,r.weekly/r.days.length);
  const full=r=>r.weekly/r.frequency>=capacity*.95;
  const sorted=[...candidates].sort((a,b)=>Number(full(b))-Number(full(a))||a.city.localeCompare(b.city,'ru')||a.district.localeCompare(b.district,'ru')||b.weekly/b.frequency-a.weekly/a.frequency||a.key.localeCompare(b.key));
  const result={};for(const r of sorted){const days=[],amount=r.weekly/r.frequency,region=arr(cities,r.city),district=arr(districts,districtKey(r)),small=arr(smallDistricts,districtKey(r)),names=sourceKeys(r);for(let i=0;i<r.frequency;i++){let choices=Array.from({length:7},(_,d)=>d).filter(d=>!days.includes(d));function score(d){const origin=names.reduce((n,name)=>n+arr(sources,name)[d],0)/names.length;let value=(region[d]+global[d]*.25+origin*.5)/capacity;if(full(r))value+=district[d]/capacity;else if(small[d]>0&&small[d]+amount<=capacity+1e-9)value-=1.5;return value}choices.sort((a,b)=>score(a)-score(b)||a-b);const day=choices[0];days.push(day);add(r,day,amount)}result[r.key]=days.sort((a,b)=>a-b)}return result;
 }
 if(typeof module!=='undefined'&&module.exports)module.exports=suggestDays;else root.suggestDeliveryDays=suggestDays;
})(typeof window!=='undefined'?window:globalThis);
