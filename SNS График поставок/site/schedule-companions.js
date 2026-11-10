(function(root){
 function rankCompanions(rows, history, from, to, identity){
  const byKey=new Map(rows.map(r=>[r.key,r])),trips=new Map(),counts=new Map();
  for(const item of history){if(!item.trip||!item.start||item.start<from||item.start>to||(!item.recipient_id&&!item.address))continue;const key=identity(item);if(!byKey.has(key))continue;if(!trips.has(item.trip))trips.set(item.trip,new Set());trips.get(item.trip).add(key)}
  for(const members of trips.values()){const list=[...members];for(let i=0;i<list.length;i++)for(let j=i+1;j<list.length;j++){const a=byKey.get(list[i]),b=byKey.get(list[j]);if(a.city!==b.city||a.district!==b.district||/не определён/i.test(a.districtMethod||'')||/не определён/i.test(b.districtMethod||''))continue;for(const [x,y] of [[a.key,b.key],[b.key,a.key]]){if(!counts.has(x))counts.set(x,new Map());const m=counts.get(x);m.set(y,(m.get(y)||0)+1)}}}
  const ranked=new Map();for(const [key,m] of counts)ranked.set(key,[...m].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'ru')).map(([key,count])=>({key,count})));return ranked;
 }
 if(typeof module!=='undefined'&&module.exports)module.exports=rankCompanions;else root.rankScheduleCompanions=rankCompanions;
})(typeof window!=='undefined'?window:globalThis);
