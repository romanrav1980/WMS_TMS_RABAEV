(()=>{
 const table=document.querySelector("#huComposition .table-wrap");if(!table)return;
 const host=document.createElement("section");host.className="hu-tree-workspace";table.before(host);
 const tableDetails=document.createElement("details"),tableSummary=document.createElement("summary");tableSummary.textContent="Таблица полного состава";tableSummary.title="Открыть исходные строки состава для сверки";table.before(tableDetails);tableDetails.append(tableSummary,table);
 const node=(tag,text,cls)=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
 const types={CONTAINER:"Контейнер",CASE:"Собранное место",STOCK:"Товарная партия",PALLET:"Паллета",BOX:"Коробка",ROLL_CAGE:"Ролл-кейдж",BAG:"Мешок"};
 function link(text,page,identifier){
  const a=node("a",text);a.href=page+"?identifier="+encodeURIComponent(identifier);a.title="Открыть существующий экран; движение не проводится";return a;
 }
 window.wmsHuTree={
  clear(){host.replaceChildren();},
  render(data){
   host.replaceChildren();if(!Array.isArray(data.nodes)||!data.nodes.length)return;
   const byId=new Map(data.nodes.map(n=>[n.uid,n])),children=new Map();
   for(const edge of data.links||[]){if(!children.has(edge.parent))children.set(edge.parent,[]);children.get(edge.parent).push(edge.child);}
   const head=node("div","","hu-tree-heading");head.append(node("h3","Вложенность грузового места"),node("p",data.historical_composition?"Исторический состав на момент отгрузки. Операции изменения недоступны.":"Контейнеры объединяют вложения. Товарное количество учитывается на листьях дерева."));
   host.append(head);
   if(data.ancestors?.length){
    const path=node("nav","","hu-tree-ancestors");path.setAttribute("aria-label","Внешние грузовые места");
    path.append(node("span",data.historical_composition?"Внешние места при отгрузке: ":"Входит в: "));
    for(const parent of [...data.ancestors].reverse())path.append(link(parent.uid,"warehouse-hus.html",parent.uid),node("span"," → "));
    path.append(node("strong",data.root));host.append(path);
   }
   const layout=node("div","","hu-tree-layout"),tree=node("div","","hu-tree-branches"),detail=node("aside","","hu-tree-detail");
   layout.append(tree,detail);host.append(layout);let selected=null;
   function select(item){
    selected=item.uid;detail.replaceChildren(node("span",types[item.type]||types[item.kind]||item.kind,"hu-tree-kind"),node("h3",item.sscc||item.uid));
    detail.append(node("p","Внутренний идентификатор: "+item.uid),node("p","Ячейка: "+(item.cell||"не указана")+" · версия "+item.version));
    if(item.article)detail.append(node("p","Артикул: "+item.article),node("p","Количество: "+item.quantity+" "+item.base_uom),node("p","Жёсткий резерв: "+(item.hard_quantity??"—")+" "+item.base_uom));
    if(item.status)detail.append(node("p","Статус: "+item.status));
    if(item.open_task_count)detail.append(node("p","Незавершённых заданий: "+item.open_task_count));
    if(!data.historical_composition&&item.uid!==data.root&&["CONTAINER","CASE"].includes(item.kind))detail.append(link("Открыть состав этого вложения","warehouse-hus.html",item.kind==="CASE"?(item.sscc||item.uid):item.uid));
    if(item.kind==="STOCK")detail.append(link("Текущие единицы, коды и происхождение","pallet-composition.html",item.uid));
    if(data.historical_composition)detail.append(node("p","Положение и количество здесь относятся к отгрузке; текущую прослеживаемость открывайте отдельно."));
    for(const b of tree.querySelectorAll("button[data-uid]"))b.setAttribute("aria-pressed",String(b.dataset.uid===selected));
   }
   const seen=new Set();
   function branch(uid,depth){
    const item=byId.get(uid);if(!item||seen.has(uid)||depth>16)return node("p","Иерархия требует сверки.");
    seen.add(uid);const descendants=children.get(uid)||[],wrap=node("div","","hu-tree-node");
    const b=node("button","","hu-tree-select");b.type="button";b.dataset.uid=uid;b.title="Показать данные этого узла; сканирование и движение не выполняются";
    b.append(node("span",types[item.type]||types[item.kind]||item.kind,"hu-tree-kind"),node("strong",item.sscc||uid));
    if(item.kind==="STOCK")b.append(node("small",item.article+" · "+item.quantity+" "+item.base_uom));
    else b.append(node("small","Вложений: "+descendants.length));
    b.onclick=()=>select(item);wrap.append(b);
    if(descendants.length){const d=node("details",""),s=node("summary","Состав · "+descendants.length);s.title="Развернуть или свернуть вложения";d.open=depth<2;d.append(s);for(const child of descendants)d.append(branch(child,depth+1));wrap.append(d);}
    return wrap;
   }
   tree.append(branch(data.root,0));select(byId.get(data.root)||data.nodes[0]);
   if(seen.size!==data.nodes.length)tree.append(node("p","Часть узлов не связана с показанным корнем. Используйте таблицу для сверки."));
   const totals=node("details","","hu-tree-totals"),summary=node("summary","Итоги по артикулам");summary.title="Показать серверные итоги без смешения единиц измерения";totals.append(summary);
   for(const row of data.quantities||[])totals.append(node("p",row.article+" · "+row.quantity+" "+row.base_uom));
   host.append(totals);
  }
 };
})();
