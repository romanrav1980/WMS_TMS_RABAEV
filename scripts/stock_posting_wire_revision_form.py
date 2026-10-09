"""Emit bounded edits to existing inventory UI and canonical installer."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Expected one anchor "+path+" "+old[:40])
 files[path]=text.replace(old,new,1)
path="WindowsApplication2/WindowsApplication2/WindowsApplication2.csproj"
edit(path,'    <Compile Include="StockCommandIntent.cs" />',
 '    <Compile Include="StockCommandIntent.cs" />\n    <Compile Include="Ревизии.InventoryCommands.cs" />')
path="WindowsApplication2/WindowsApplication2/Ревизии.cs"
edit(path,"""        private void dataGridView2_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
""","""        private void dataGridView2_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (TryPostExplicitCount(e)) return;
""")
for name,field in (("count1","t_count1"),("brak_perc1","t_brak_perc1"),("pall_weight1","t_pall_weight1"),("tn_weight1","t_tn_weight1")):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 import re
 pattern=r"double "+name+r" = _parent\.obj2double\s*\("+field+r"\.Text\);"
 text,n=re.subn(pattern,"decimal "+name+" = InventoryDecimal("+field+".Text);",text,count=1)
 if n!=1:raise RuntimeError("Decimal input anchor "+name)
 files[path]=text
edit(path,"""            string pall_number3 = _parent.obj2str(_parent.wms_get_spfunction_value2("REVIZION.RRL_INV_CREATE_LINE5", 
                values2, OracleType.VarChar, 255));""",
 """            string pall_number3;
            try
            {
                pall_number3 = PostInventoryFunction("REVIZION.RRL_INV_CREATE_LINE5", values2,
                    "INVENTORY_PALLET:" + NAKLAD_ID + ":" + articul2 + ":" + cell1 + ":" + pall_n);
            }
            catch (Exception error) { MessageBox.Show(error.Message); return; }""")
edit(path,"""        private void очиститьОтрицаткельныеОстаткиПоДаннойРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {
""","""        private void очиститьОтрицаткельныеОстаткиПоДаннойРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {
            try
            {
                if (StockReleaseState() != "PREPARED")
                {
                    if (dataGridView1.CurrentRow != null)
                        OpenLotInventory(_parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value),
                            dataGridView2.CurrentRow == null ? "" : _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value));
                    return;
                }
            }
            catch (Exception error) { MessageBox.Show(error.Message); return; }
""")
path="wiki-raw/wms_admin_ui_reference/inventory-count.js"
edit(path,'  window.addEventListener("wms-admin-auth-ready", pending);',
 """  const source = new URLSearchParams(location.search);
  if (/^[1-9][0-9]*$/.test(source.get("revision_id") || "")) el("countRevision").value = source.get("revision_id");
  if (source.get("cell")) el("countCell").value = source.get("cell");
  function onAuthenticated() { pending(); if(el("countRevision").value && el("countCell").value)load(); }
  window.addEventListener("wms-admin-auth-ready", onAuthenticated);
  if(window.wmsAdminAuth.state.user)onAuthenticated();""")
path="db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"
manifest=json.loads((ROOT/path).read_text(encoding="utf-8"))
at=manifest["components"].index("024_posting.sql")
manifest["components"].insert(at,"151_revision_entry.sql")
manifest["packages"].append("RRL_STOCK_REVISION_ENTRY")
manifest["additional_scripts"].extend(["152_revision_legacy.sql","152_revision_adapter.sql"])
files[path]=json.dumps(manifest,indent=2)+"\n"
base="db/migrations/2026-10-08_stock_posting_core/"
files[base+manifest["contracts"]]="\n".join((ROOT/base/f).read_text(encoding="utf-8").split("\n/\n",1)[0]+"\n/\n" for f in manifest["components"] if f!="151_revision_entry.sql")+ "\n"+(ROOT/base/"151_revision_entry.sql").read_text(encoding="utf-8").split("\n/\n",1)[0]+"\n/\n"
files[base+manifest["bundle"]]="@@"+manifest["contracts"]+"\n"+"\n".join("@@"+f for f in manifest["components"]+manifest["additional_scripts"])+"\n@@014b_recompile.sql\n"
path="scripts/stock_posting_install.py"
edit(path,'"RRL_STORNO_ORDER3", "RRL_STORNO_ORDER3_SP_OLD",','"REVIZION", "REVIZION_SP_OLD", "RRL_STORNO_ORDER3", "RRL_STORNO_ORDER3_SP_OLD",')
print(json.dumps(files,ensure_ascii=True))
