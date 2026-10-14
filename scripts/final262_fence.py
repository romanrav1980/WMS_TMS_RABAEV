from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8").replace('    state.order=null;state.line=null;state.policy=null;el(\'receiptConfirm\').disabled=true;','    state.order=null;state.line=null;state.policy=null;el(\'receiptConfirm\').disabled=true;\n    window.dispatchEvent(new CustomEvent("wms-receipt-selection-reset"));')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving-layout.js");s=p.read_text(encoding="utf-8").replace("  async function preview() {","  window.addEventListener('wms-receipt-selection-reset',()=>{order=null;line=null;epoch++;el('receiptLayoutRows').replaceChildren();el('receiptLayoutPreview').disabled=false;message('Выберите заказ и строку.');});\n  async function preview() {")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
