from pathlib import Path
p=Path('wiki-raw/wms_admin_ui_reference/case-short-intent.js');s=p.read_text(encoding='utf-8').replace("const typed=cpTsdEl('cpTsdFactQty').value.trim()||'0',posted=String(line.picked_qty??'0');", "const posted=String(line.picked_qty??'0'),typed=cpTsdEl('cpTsdFactQty').value.trim()||posted;");p.write_text(s,encoding='utf-8')
