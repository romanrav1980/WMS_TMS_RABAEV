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
            string strSQL = " select  " + 
            " ID , PRICE_NAME , PRICE , COMPANY , RANGE1 , PRICE_FOR_HOURS , TYPE_TR PRICE_FOLDER , "+
            " PRICE_FOR_ADDR , NORM_HOURS  "+
            " from RABAEV.RRL_TRANSPORT_PRICE where COMPANY='"+comboBox1.Text+"' ";


 

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


    }
}