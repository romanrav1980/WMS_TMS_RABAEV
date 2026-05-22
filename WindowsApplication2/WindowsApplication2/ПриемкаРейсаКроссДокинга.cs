using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class ПриемкаРейсаКроссДокинга : Form
    {

        public Form1 _parent;


        public ПриемкаРейсаКроссДокинга()
        {
            InitializeComponent();
        }

        private void ПоказатьПаллеты_Click(object sender, EventArgs e)
        {
            string s2 = "";

            if ( ПоказыватьНеПринятые.Checked )
            {
                s2 = " and  TRANSTASK_ID=1  ";
            }

            string strSQL = " select  PALLET_UID  , ADDR ,   KROSS_WEIGHT , TRIAL_WEIGHT , 'false' , REMOTE_TT_ID , TRANSTASK_ID , ware_id   " +
                "  from RABAEV.RRL_SBORKA_PALLETS where  REMOTE_TT_ID = " + НомерРейса.Text + " " + s2;
            _parent.fill_view_MINI_WMS(dataGridView1, strSQL, 7  );
        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (e.ColumnIndex != 3) return;
            if (dataGridView1.CurrentRow == null) return;

            string PALLET_UID = _parent.obj2str(dataGridView1.CurrentRow.Cells[0].Value);
            double TRIAL_WEIGHT = _parent.obj2double( dataGridView1.CurrentRow.Cells[3].Value);

            if (TRIAL_WEIGHT <= 0) {
                MessageBox.Show("Укажите вес");
                return;
            }

            string strSQL = " update  RABAEV.RRL_SBORKA_PALLETS set TRANSTASK_ID=null , TRIAL_WEIGHT=" + TRIAL_WEIGHT.ToString().Replace(',', '.') 
                + " where PALLET_UID='" + PALLET_UID + "'  ";
            _parent.ExecuteOracleNonQuery(strSQL);

        }

        private void ЗафиксироватьПринятие_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView1.Rows)
            {
                if (_parent.obj2bool(dr.Cells[4].Value))
                { //  REMOTE_TT_ID = " + НомерРейса.Text + " 
                    string PALLET_UID = _parent.obj2str( dr.Cells[0].Value );
                    string strSQL = " update  RABAEV.RRL_SBORKA_PALLETS set TRANSTASK_ID=null  where  PALLET_UID='" + PALLET_UID + "'  ";
                    _parent.ExecuteOracleNonQuery(strSQL);
                }
            }

            foreach (DataGridViewRow dr in dataGridView1.Rows)
            {
                if (_parent.obj2bool(dr.Cells[4].Value))
                {
                    dataGridView1.Rows.Remove(dr);
                }
            }
            MessageBox.Show("Рейс принят на склад. Паллеты можно планировать к отгрузке.");
            
        }

        private void dataGridView1_KeyPress(object sender, KeyPressEventArgs e)
        {

        }

        private void dataGridView1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.F5)
            { 
                        foreach (DataGridViewRow dr in dataGridView1.Rows)
                        {
                            if (dr.Cells[0].Selected)
                            {
                                ((DataGridViewCheckBoxCell)dr.Cells[4]).Value = true;
                            }
                        }
            }
        }


    }
}
