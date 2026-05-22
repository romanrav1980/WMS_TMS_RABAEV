using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Data.OracleClient;
using System.Data.OleDb;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class ИнтеграцияИКроссДокинг : Form
    {
        public int tt_id = 0 ;
        public Form1 _parent;

        public ИнтеграцияИКроссДокинг()
        {
            InitializeComponent();
            
        }


        private void СинхронизоватьПаллеты_Click( object sender, EventArgs e )
        {
            
            foreach( DataGridViewRow dr  in  dataGridView1.Rows )
            {
                if (_parent.obj2bool(dr.Cells[8].Value))
                {
                    Dictionary<string, object> values = new Dictionary<string, object>();
                    string sost_reisa = dr.Cells[2].Value.ToString();
                    if (true || sost_reisa == "ВЫПУЩЕН")
                    {
                        values["sb_pall_uid"] = dr.Cells[0].Value.ToString();
                        object ret4 = _parent.wms_get_spfunction_value2("CROSS_DOCKING.SYNC_SBORKA_PALL", values, OracleType.Int32, 0);
                        string txt = "не известно";
                        if (_parent.obj2int32(ret4) == -1)
                            txt = "паллет на собран";
                        if (_parent.obj2int32(ret4) == 2)
                            txt = "ok";
                        if (_parent.obj2int32(ret4) == 1)
                            txt = "был синхронизован";
                        if (_parent.obj2int32(ret4) == -3)
                            txt = "ошибка";

                        dr.Cells[3].Value = txt;
                    }
                    else
                    {
                        dr.Cells[3].Value = "РЕЙС НЕ ВЫПУЩЕН";
                    }
                }
            }

        }

        private void ВывестиСписокПаллет_Click(object sender, EventArgs e)
        {
            string strSQL = " SELECT pts.pallet_uid, pts.addr , tt.CONDITION , '' s , tt.ID , tt.TRANSPORT , pts.condition , RRL_SKLADNAME_BY_ID( pts.ware_id ) " +
            "  FROM rrl_sborka_pallets pts, rabaev.rrl_addr adr , RRL_TRANSPORT_TASK tt " +
            "  WHERE pts.addr = adr.addr " +
            "    AND adr.Region = 'Уфа' " +
            "    AND pts.STDATE >= " + _parent.date2sql_ora(ДатаОт.Value) + " " +
            "    AND pts.STDATE <= " + _parent.date2sql_ora(ДатаДо.Value) + " " +
            "    and pts.TRANSTASK_ID = tt.ID and KROSS_SYNCRONIZED is null ";
            // and ='ВЫПУЩЕН'

            if (tt_id > 0)
            {
                strSQL = " SELECT pts.pallet_uid, pts.addr , tt.CONDITION , '' s , tt.ID , tt.TRANSPORT , pts.condition , "+
                   " RRL_SKLADNAME_BY_ID( pts.ware_id ) " +
                   "  FROM rrl_sborka_pallets pts, rabaev.rrl_addr adr , RRL_TRANSPORT_TASK tt " +
                   "  WHERE pts.addr = adr.addr " +
                   "    AND adr.Region = 'Уфа' " +
                 //  "    AND pts.STDATE >= " + _parent.date2sql_ora(ДатаОт.Value) + " " +
                 //  "    AND pts.STDATE <= " + _parent.date2sql_ora(ДатаДо.Value) + " " +
                   "    and pts.TRANSTASK_ID = tt.ID and pts.TRANSTASK_ID=" + tt_id + " and KROSS_SYNCRONIZED is null ";

            }

            _parent.fill_view_MINI_WMS(dataGridView1, strSQL, 8);
        }

        private void dataGridView1_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if(e.RowIndex<=0) return;

            if (e.ColumnIndex == 1)
            {
                object o = _parent.obj2str(dataGridView1.Rows[e.RowIndex].Cells[6].Value);
                if ( o.ToString() == "2" )
                {
                    e.CellStyle.BackColor = Color.Green;
                }
            }


        }

        private void dataGridView1_KeyDown(object sender, KeyEventArgs e)
        {


            if (e.KeyCode == Keys.F5)
            {

                foreach (DataGridViewRow dr in dataGridView1.Rows)
                {
                    dr.Cells[8].Value = dr.Cells[0].Selected;
                }
            }


        }

        private void ИнтеграцияИКроссДокинг_Load(object sender, EventArgs e)
        {
            if (tt_id > 0)
            {
                ВывестиСписокПаллет_Click(null, null);
            }
        }
    }
}
