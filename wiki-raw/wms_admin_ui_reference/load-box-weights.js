(() => {
 const el=id=>document.getElementById(id);
 let nodes=[],fields=[];
 function render(tree){
  el("loadBoxRows").replaceChildren();fields=[];nodes=tree?.nodes||[];
  const parent=new Map((tree?.links||[]).map(link=>[link.child,link.parent])),byId=new Map(nodes.map(node=>[node.uid,node])),selected=new Set();
  for(const leaf of nodes.filter(node=>node.kind==="STOCK")){
   let uid=leaf.uid;
   for(let depth=0;depth<17;depth++){
    const node=byId.get(uid);
    if(node?.kind==="CONTAINER"&&node.type==="BOX"){selected.add(uid);break;}
    if(!parent.has(uid))break;uid=parent.get(uid);
   }
  }
  for(const uid of selected){
   const node=byId.get(uid),row=document.createElement("fieldset"),legend=document.createElement("legend");
   legend.textContent="Физическая коробка "+uid+" · версия "+node.version;row.append(legend);
   const field={node};
   for(const [key,text] of [["scan","Скан коробки"],["mass","Брутто коробки, кг"],["reference","Номер отдельного измерения / акта"]]){
    const label=document.createElement("label"),input=document.createElement("input");label.textContent=text;
    input.autocomplete="off";if(key==="mass")input.inputMode="decimal";if(key==="reference")input.maxLength=100;
    label.append(input);row.append(label);field[key]=input;
   }
   fields.push(field);el("loadBoxRows").append(row);
  }
  el("loadBoxWeightsEnabled").disabled=!fields.length;if(!fields.length)el("loadBoxWeightsEnabled").checked=false;
  if(!fields.length){const text=document.createElement("p"),measured=nodes.filter(n=>n.kind==="CASE"&&n.scale_qc);text.textContent=measured.length?"Вес "+measured.length+" коробов передаётся из итогового весового контроля. Повторно вводить его здесь не нужно.":"Нет отдельных коробок с собственным идентификатором. Норматив товара не заменяет измерение.";el("loadBoxRows").append(text);}
 }
 function collect(){
  if(!el("loadBoxWeightsEnabled").checked)return undefined;
  if(!fields.length)throw new Error("Для весовой приёмки нужны реальные идентифицированные коробки и их отдельные измерения.");
  return fields.map(field=>({box_uid:field.node.uid,content_version:field.node.version,scan_box:field.scan.value,
   gross_weight_kg:field.mass.value,measurement_ref:field.reference.value,origin:"MANUAL_CONFIRMED"}));
 }
 window.wmsPhysicalBoxes={render,collect};
})();
