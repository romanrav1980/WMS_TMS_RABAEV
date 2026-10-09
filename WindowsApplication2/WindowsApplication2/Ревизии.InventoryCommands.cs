using System;
using System.Collections.Generic;
using System.Data;
using System.Data.OracleClient;
using System.Globalization;
using System.Diagnostics;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class Ревизии
    {
        private string StockReleaseState()
        {
            return _parent.obj2str(_parent.CachedQuerySingle(
                "select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")).Trim();
        }

        private decimal InventoryDecimal(object value)
        {
            if (value == null || value == DBNull.Value) throw new InvalidOperationException("Введите количество.");
            if (!(value is string)) return Convert.ToDecimal(value, CultureInfo.InvariantCulture);
            decimal result;
            if (Decimal.TryParse((string)value, NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint,
                    CultureInfo.CurrentCulture, out result)) return result;
            if (Decimal.TryParse((string)value, NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint,
                    CultureInfo.InvariantCulture, out result)) return result;
            throw new InvalidOperationException("Некорректное десятичное количество.");
        }

        private string PostInventoryFunction(string function, Dictionary<string, object> values, string identity)
        {
            using (OracleCommand command = new OracleCommand())
            {
                command.Connection = _parent.get_wms_connection();
                command.CommandText = function;
                command.CommandType = CommandType.StoredProcedure;
                foreach (KeyValuePair<string, object> value in values)
                {
                    OracleType type = value.Value is DateTime ? OracleType.DateTime :
                        value.Value is string ? OracleType.VarChar : OracleType.Number;
                    command.Parameters.Add(value.Key, type).Value = value.Value ?? DBNull.Value;
                }
                OracleParameter output = command.Parameters.Add("ret", OracleType.VarChar, 1025);
                output.Direction = ParameterDirection.ReturnValue;
                StockCommandIntent intent = StockCommandIntent.Prepare(command, _parent.wms_user.user_id, identity);
                command.ExecuteNonQuery();
                string result = _parent.obj2str(output.Value);
                if (result == "ok" || result.StartsWith("P_", StringComparison.Ordinal)) intent.Confirm();
                return result;
            }
        }

        private void OpenLotInventory(int revision, string cell)
        {
            string configured = Environment.GetEnvironmentVariable("WMS_INVENTORY_URL");
            Uri address;
            if (!Uri.TryCreate(String.IsNullOrEmpty(configured) ?
                    "http://127.0.0.1:3000/inventory-count.html" : configured, UriKind.Absolute, out address)
                || (address.Scheme != Uri.UriSchemeHttp && address.Scheme != Uri.UriSchemeHttps))
                throw new InvalidOperationException("Неверный WMS_INVENTORY_URL.");
            UriBuilder target = new UriBuilder(address);
            target.Query = (String.IsNullOrEmpty(address.Query) ? "" : address.Query.Substring(1) + "&")
                + "revision_id=" + revision.ToString(CultureInfo.InvariantCulture)
                + "&cell=" + Uri.EscapeDataString(cell ?? "");
            Process.Start(new ProcessStartInfo(target.Uri.AbsoluteUri) { UseShellExecute = true });
        }

        private bool TryPostExplicitCount(DataGridViewCellEventArgs e)
        {
            if (e.ColumnIndex != 2 && e.ColumnIndex != 3 && e.ColumnIndex != 9) return false;
            if (dataGridView1.CurrentRow == null || dataGridView2.CurrentRow == null) return true;
            try
            {
                string state = StockReleaseState();
                if (state == "PREPARED") return false;
                if (state != "ACTIVE") throw new InvalidOperationException("Проводки временно остановлены: " + state);
                int revision = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
                int row = _parent.obj2int32(dataGridView2.CurrentRow.Cells[0].Value);
                string cell = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
                string article = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);
                if (e.ColumnIndex == 9) { OpenLotInventory(revision, cell); return true; }
                Dictionary<string, object> values = new Dictionary<string, object>();
                string function;
                if (e.ColumnIndex == 2)
                {
                    function = "REVIZION.RRL_REVIZION_CELL_SHT";
                    values["articul1"] = article;
                    values["CELL1"] = cell;
                    values["count_sht"] = InventoryDecimal(dataGridView2.CurrentRow.Cells[2].Value);
                    values["revision_row_id1"] = row;
                    values["user_id1"] = _parent.wms_user.user_id;
                }
                else
                {
                    function = "REVIZION.revision_cell_kor";
                    values["cell1"] = cell;
                    values["revision_id1"] = revision;
                    values["count2"] = InventoryDecimal(dataGridView2.CurrentRow.Cells[3].Value);
                    values["user_id3"] = _parent.wms_user.user_id;
                }
                PostInventoryFunction(function, values, "REVISION_ROW:" + row);
                dataGridView1_CellEnter(null, null);
            }
            catch (Exception error)
            {
                if (error.Message.IndexOf("LOT_SELECTION_REQUIRED", StringComparison.Ordinal) >= 0
                    || error.Message.IndexOf("REVISION_ROW_SELECTION_REQUIRED", StringComparison.Ordinal) >= 0)
                    OpenLotInventory(_parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value),
                        _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value));
                MessageBox.Show(error.Message);
                dataGridView1_CellEnter(null, null);
            }
            return true;
        }
    }
}
