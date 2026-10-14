/* Editable, text-only view of the current pallet's unposted scans. */
window.wmsReceiptScanList={
  render(container,units,aggregations,remove){
    const rows=[];
    const entry=(label,selection)=>{
      const row=document.createElement('li'),text=document.createElement('span'),button=document.createElement('button');
      text.textContent=label;button.type='button';button.textContent='Убрать этот скан';
      button.title='Убрать только этот ошибочный код из формы; остальные коды сохранятся. Принятый товар не изменяется.';
      button.setAttribute('aria-label','Убрать скан: '+label);
      button.addEventListener('click',()=>remove(selection));row.append(text,document.createTextNode(' '),button);rows.push(row);
    };
    for(const [unit_id,codes]of units)for(const scan of codes)
      entry('Единица '+unit_id+': '+scan.system_code+' / '+scan.profile_code+' — '+scan.code,{unit_id,scan});
    for(const scan of aggregations)
      entry((scan.level==='BOX'?'Коробка':'Паллета')+': '+scan.system_code+' / '+scan.profile_code+' — '+scan.code,{scan});
    container.replaceChildren(...rows);
  }
};