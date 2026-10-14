window.workloadOverview=(()=>{
 const node=(tag,value,className)=>{const n=document.createElement(tag);n.textContent=value;if(className)n.className=className;return n;};
 const hours=value=>value==null?'не определено':String(value).replace(/(\.\d*?)0+$/,'$1').replace(/\.$/,'')+' ч';
 const date=value=>new Date(value).toLocaleString('ru-RU',{timeZone:'UTC',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
 function render(root,result){
  const section=node('section','','rw-overview'),heading=node('h2','Нагрузка по интервалам');
  const rows=result.intervals||[],unknown=rows.filter(r=>r.deficit_person_hours==null).length;
  const deficit=rows.filter(r=>r.deficit_person_hours!=null&&Number(r.deficit_person_hours)>0).length;
  const summary=node('div','','rw-summary');
  for(const [label,value]of [['Интервалов с дефицитом',deficit],['Требуют исходных данных',unknown],['Активных сессий сейчас',result.current_presence_count]]){
   const card=node('div','','rw-metric');card.append(node('strong',String(value)),node('span',label));summary.append(card);
  }
  section.append(heading,summary,node('p','Время показано в UTC. Синие полосы — потребность, зелёные — утверждённый план выхода. Текущая сессия не подтверждает будущую явку.','rw-legend'));
  const filter=node('label','Показать '),select=document.createElement('select');select.title='Отфильтровать интервалы текущего расчёта; планы не изменятся';select.setAttribute('aria-label','Интервалы нагрузки');
  for(const [v,t]of [['all','Все интервалы'],['deficit','С дефицитом'],['unknown','Недостаточно данных']])select.add(new Option(t,v));filter.append(select);section.append(filter);
  const list=node('div','','rw-intervals');section.append(list);
  function draw(){
   list.replaceChildren();
   for(const row of rows){
    const missing=row.deficit_person_hours==null,short=!missing&&Number(row.deficit_person_hours)>0;
    if(select.value==='deficit'&&!short||select.value==='unknown'&&!missing)continue;
    const card=node('article','',`rw-interval ${missing?'rw-unknown':short?'rw-deficit':'rw-covered'}`);
    card.append(node('h3',date(row.from_utc)+' — '+date(row.to_utc)+' UTC'),node('span',missing?'Расчёт неполный':short?'Нужен плановый ресурс':'Расчётный дефицит отсутствует','rw-badge'));
    const maximum=Math.max(Number(row.required_person_hours??row.known_required_person_hours??0),Number(row.planned_person_hours),0.000001);
    for(const [label,value,kind]of [['Потребность',row.required_person_hours,'required'],['План выхода',row.planned_person_hours,'planned']]){
     const band=node('div','','rw-band');band.append(node('span',label+': '+hours(value)));
     const track=node('div','','rw-track'),bar=node('div','','rw-bar '+kind);bar.style.width=value==null?'0%':Math.min(100,Math.max(0,Number(value)/maximum*100))+'%';track.setAttribute('aria-hidden','true');track.append(bar);band.append(track);card.append(band);
    }
    card.append(node('p','Дефицит: '+hours(row.deficit_person_hours)+' · сотрудников в плане: '+row.planned_people));
    if(missing)card.append(node('p','Строк без нормы: '+row.missing_norm_line_ids.length+'; без окна волны: '+row.unscheduled_line_ids.length+'. Известная часть потребности: '+hours(row.known_required_person_hours)+'.'));
    list.append(card);
   }
   if(!list.children.length)list.append(node('p','В выбранном фильтре интервалов нет.'));
  }
  select.addEventListener('change',draw);draw();root.append(section);
 }
 return{render};
})();