using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class Список_прайсов : Form
    {

        public Form1 _pparent;

        public Список_прайсов()
        {
            InitializeComponent();
        }

        private void Список_прайсов_Load(object sender, EventArgs e)
        {

        }

        private void ВывестиВсе_Click(object sender, EventArgs e)
        {

            string sql1 = " where  ";
            string sql2 = "";
            string sql3 = "";
            string sql4 = "";

            if(Фильтр_регион.Text.Trim()!="")
            {
                sql2=" and PRICE_NAME like '%"+Фильтр_регион.Text.Trim()+"%'";
            }

            if (ФильтрТиповТС.Text.Trim() != "")
            {
                sql3 = " and PRICE_NAME like '[" + ФильтрТиповТС.Text.Trim() + "]%' ";
            }

            if (comboBox1.Text.Trim() != "")
            {
                sql4 = " and COMPANY = '" + comboBox1.Text.Trim() + "' ";
            }


            sql1 = sql1 + (sql2 + sql3 + sql4).Trim().TrimStart('a').TrimStart('n').TrimStart('d');

            if (sql1.Trim() == "where")
            {
                sql1 = "";
            }

            string strSQL = " select  " + 
            " ID , PRICE_NAME , PRICE , COMPANY , RANGE1 , PRICE_FOR_HOURS , TYPE_TR PRICE_FOLDER , "+
            " PRICE_FOR_ADDR , NORM_HOURS  "+
            " from RABAEV.RRL_TRANSPORT_PRICE " + sql1 ;


 

            _pparent.fill_view_MINI_WMS(dataGridView1, strSQL, 9);


        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

           DataGridViewRow dr1 =  dataGridView1.CurrentRow; 
           long ID = _pparent.obj2int( dr1.Cells[0].Value );
           long расстояние = _pparent.obj2int( dr1.Cells[4].Value );
           long ставка_за_рейс = _pparent.obj2int( dr1.Cells[2].Value );
           long стоимость_часа  = _pparent.obj2int( dr1.Cells[5].Value );
           long Стоимость_за_точку  = _pparent.obj2int( dr1.Cells[7].Value );
           long Нормо_часы  = _pparent.obj2int( dr1.Cells[8].Value );

            string strSQL = " update    RABAEV.RRL_TRANSPORT_PRICE set "+
                " PRICE="+ставка_за_рейс.ToString()+" ,RANGE1="+расстояние.ToString()+
                " , PRICE_FOR_HOURS="+стоимость_часа.ToString()+"  , PRICE_FOR_ADDR = "+
                Стоимость_за_точку.ToString()+" ,  NORM_HOURS="+Нормо_часы.ToString()+" " + 
                " where ID = "+ID.ToString()+" " ;



            _pparent.ExecuteOracleNonQuery( strSQL );


        }

        private void dataGridView1_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            DataGridViewRow dr1 = dataGridView1.CurrentRow;
            if (dr1 == null) return;
            регион_подсказка.Text = _pparent.obj2str( dr1.Cells[1].Value ) ;

        }


    }
}