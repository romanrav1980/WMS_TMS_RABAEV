from pathlib import Path
import json
files={}
base=Path("wiki-raw/wms_admin_ui_reference")
p=base/"warehouse-hus.html";s=p.read_text(encoding="utf-8")
anchor='<section class="panel" data-permission="warehouse_task_execute"><details><summary>Создать пустой контейнер'
assert anchor in s
s=s.replace(anchor,'<section class="panel" data-permission="warehouse_task_execute"><label title="Физически отсканируйте внешнее место перед операцией; выбор в дереве не заменяет скан">Скан внешнего грузового места<input id="huContainerScan" autocomplete="off" maxlength="200"></label><p class="hu-helper">Отдельный физический скан используется при создании, упаковке, вскрытии и движении. Идентификатор поиска выше предназначен для просмотра.</p></section>\n'+anchor)
files[str(p)]=s
p=base/"warehouse-hus.js";s=p.read_text(encoding="utf-8")
s=s.replace('      let body={operation_id:"HU:"+crypto.randomUUID()},current=null;','      if(!el("huContainerScan").value.trim())throw new Error("Отсканируйте внешнее грузовое место перед операцией.");\n      let body={operation_id:"HU:"+crypto.randomUUID()},current=null;')
s=s.replace('scan_container:el("huIdentifier").value','scan_container:el("huContainerScan").value')
s=s.replace('pending=null;view=null;\n    if(saved.action', 'pending=null;view=null;el("huContainerScan").value="";\n    if(saved.action')
s=s.replace('generation++;view=null;window.wmsHuTree?.clear();','generation++;view=null;el("huContainerScan").value="";window.wmsHuTree?.clear();')
s=s.replace('identity=next;view=null;generation++;pending=null;damaged=null;','identity=next;view=null;generation++;pending=null;damaged=null;el("huContainerScan").value="";')
files[str(p)]=s
p=base/"warehouse-hu-tree.js";s=p.read_text(encoding="utf-8")
s=s.replace('const host=document.createElement("section");host.className="hu-tree-workspace";table.before(host);','const host=document.createElement("section");host.className="hu-tree-workspace";table.before(host);\n const tableDetails=document.createElement("details"),tableSummary=document.createElement("summary");tableSummary.textContent="Таблица полного состава";tableSummary.title="Открыть исходные строки состава для сверки";table.before(tableDetails);tableDetails.append(tableSummary,table);')
files[str(p)]=s
p=Path("coordination/nicora-claude/CODEX_TO_CLAUDE.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n## C-0009 · 2026-10-14 · ACK · K-0011\nПодтверждение C-0008 прочитал, владение файлами закреплено. Продолжай оба этапа. Я занимаюсь NI04.1 warehouse-hus/дерево и физические сканы; finance/logistics-expenses не трогаю.\n"
print(json.dumps(files,ensure_ascii=True))
