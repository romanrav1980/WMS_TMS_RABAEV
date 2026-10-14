from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/logistics-expenses.html");v=p.read_text(encoding="utf-8")
a='<label>Текущий подтверждённый итог'
assert v.count(a)==1
v=v.replace(a,'<label>Исходное нормативное начисление<select id="exNormativeCorrection"><option value="">Не корректировать норматив</option></select></label><p>Выберите один исходник: дополнительный расход или нормативное начисление. Исходная сумма сохраняется, согласуется только поправка.</p>'+a)
p.write_text(v,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/logistics-expenses.js");v=p.read_text(encoding="utf-8")
v=v.replace("articles=null,expenses=[];","articles=null,expenses=[],normativeCosts=[];")
v=v.replace("[rows,catalog]=await Promise.all([request(\"/warehouses/\"+ware),request(\"/articles\")])",
'[rows,catalog,norms]=await Promise.all([request("/warehouses/"+ware),request("/articles"),request("/warehouses/"+ware+"/normative-costs")])')
v=v.replace("articles=catalog;expenses=rows;","articles=catalog;expenses=rows;normativeCosts=norms;el(\"exNormativeCorrection\").replaceChildren(new Option(\"Не корректировать норматив\",\"\"),...norms.map(r=>new Option(r.operation_id+\" · рейс \"+r.trip_id+\" · исходно \"+r.original_total+\" · итог \"+r.confirmed_total+\" \"+r.currency,r.operation_id)));")
a=" function expenseBody()";start=v.index(a);end=v.index("\n",start)
v=v[:start]+''' function expenseBody(){if(!articles)throw Error("Сначала обновите реестр.");const source=expenses.find(r=>r.operation_id===el("exCorrection").value),norm=normativeCosts.find(r=>r.operation_id===el("exNormativeCorrection").value);if(source&&norm)throw Error("Выберите один исходник коррекции.");const body={warehouse_id:positive("exWare"),article_code:source?source.article_code:el("exArticleSelect").value,object_kind:source?source.object_kind:norm?"TRIP":el("exKind").value,object_id:source?source.object_id:norm?norm.trip_id:positive("exObject"),amount:el("exAmount").value.trim(),currency:source?source.currency:norm?norm.currency:el("exCurrency").value.trim().toUpperCase(),expense_date:el("exDay").value,document_reference:el("exReference").value.trim(),reason:el("exReason").value.trim()};if(source){body.correction_of_operation_id=source.operation_id;body.expected_confirmed_total=source.confirmed_total;}if(norm){body.cost_correction_of_operation_id=norm.operation_id;body.expected_confirmed_total=norm.confirmed_total;}return body;}'''+v[end:]
v=v.replace('"exRows","exCorrection"]','"exRows","exCorrection","exNormativeCorrection"]')
v=v.replace("pending=null;articles=null;expenses=[];","pending=null;articles=null;expenses=[];normativeCosts=[];")
v=v.replace('el("exCorrection").addEventListener("change",()=>{const source=', 'el("exCorrection").addEventListener("change",()=>{el("exNormativeCorrection").value="";const source=')
a=' el("exWare").addEventListener("input",'
assert a in v
v=v.replace(a,' el("exNormativeCorrection").addEventListener("change",()=>{el("exCorrection").value="";const source=normativeCosts.find(r=>r.operation_id===el("exNormativeCorrection").value);el("exConfirmed").value=source?source.confirmed_total+" "+source.currency:"";});\n'+a)
v=v.replace("articles=null;expenses=[];el(\"exCorrection\")","articles=null;expenses=[];normativeCosts=[];el(\"exNormativeCorrection\").replaceChildren();el(\"exCorrection\")")
p.write_text(v,encoding="utf-8")
print("606 existing expense report page selects normative origin/current total, signed delta, existing approvals/allocation and exact pending intent reused.")
