"""Remove the final direct WinForms stock edit and close reviewed writer gates."""
import json,re,hashlib
from pathlib import Path
out={}
p=Path("WindowsApplication2/WindowsApplication2/Form1.cs");s=p.read_text(encoding="utf-8")
start=s.index("        private void dataGrid_ПАЛЛЕТЫ_ОТКУДА_CellEndEdit(")
end=s.index("\n        private void ",start+1)
s=s[:start]+'''        private void dataGrid_ПАЛЛЕТЫ_ОТКУДА_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow == null) return;
            string pallet = dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow.Cells[0].Value.ToString();
            string cell = ЯЧЕЙКА_ОТКУДА.Text;
            try
            {
                using (OracleCommand command = new OracleCommand())
                {
                    command.Connection = get_wms_connection();
                    command.CommandType = CommandType.Text;
                    command.CommandText = "select REMAIN from RRL_REMAINS where UID_POLETA=:p and CELL=:c";
                    command.Parameters.Add("p", OracleType.VarChar).Value = pallet;
                    command.Parameters.Add("c", OracleType.VarChar).Value = cell;
                    dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow.Cells[1].Value = command.ExecuteScalar();
                }
                string configured = Environment.GetEnvironmentVariable("WMS_INVENTORY_URL");
                Uri address;
                if (!Uri.TryCreate(String.IsNullOrEmpty(configured) ?
                        "http://127.0.0.1:3000/inventory-count.html" : configured, UriKind.Absolute, out address)
                    || (address.Scheme != Uri.UriSchemeHttp && address.Scheme != Uri.UriSchemeHttps))
                    throw new InvalidOperationException("Неверный WMS_INVENTORY_URL.");
                UriBuilder target = new UriBuilder(address);
                target.Query = (String.IsNullOrEmpty(address.Query) ? "" : address.Query.Substring(1) + "&")
                    + "cell=" + Uri.EscapeDataString(cell) + "&uid=" + Uri.EscapeDataString(pallet);
                MessageBox.Show("Коррекция остатка выполняется по документу инвентаризации. Выберите или создайте документ и подтвердите измеренное количество.");
                System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(target.Uri.AbsoluteUri) { UseShellExecute = true });
            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }
'''+s[end:]
out[str(p)]=s
pick=Path("api/wms_api_server/app/services/picking_service.py")
text=pick.read_text(encoding="utf-8")
for marker in ("CASE_PICK_CONFIRM_REQUIRED","complete_existing_task(self.gateway","reserve_existing_wave_sources",
               "release_existing_document_reservations","_post_wave_command"):
 if marker not in text:raise RuntimeError("Reviewed picking source drift")
if re.search(r"(insert\s+into|update|delete\s+from)\s+(?:RABAEV\.)?(?:RRL_REMAINS|RRL_EVENTS|RRL_STOCK_RESERVATION)",s,re.I):
 raise RuntimeError("Direct desktop stock writer remains")
sql="""declare s varchar2(20);begin select STATE into s from RRL_STOCK_RELEASE where RELEASE_ID=1;
if s!='PREPARED' then raise_application_error(-20808,'REGISTRY_REQUIRES_PREPARED');end if;end;
/
"""
for path,content,adapter in ((p,s,"StockCommandIntent;inventory-count.html;native Oracle adapters"),
                           (pick,text,"task_completion.py;wave_commands.py;case_pick_commands.py")):
 digest=hashlib.sha256(content.encode("utf-8")).hexdigest()
 sql+="update RRL_STOCK_WRITER_REGISTRY set STATE='ADAPTED',SOURCE_HASH='"+digest+"',ADAPTER_REFERENCE='"+adapter+"',UPDATED_AT=systimestamp where WRITER_KEY='LOCAL:"+str(path).replace("\\","/")+"';\n"
out["db/migrations/2026-10-08_stock_posting_core/211_final_writer_registry.sql"]=sql+"commit;\n"
print(json.dumps(out,ensure_ascii=True))
