using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class СоздатьАртикул : Form
    {

        public Form1 _parent;
        public bool choosed=false;
        public string Tovar_Name="";
        public string Tovar_Group = "";
        public string Tovar_Articul = "";
        public long Tovar_NU = 0;
        public string Tovar_BARCODE_SHT = "";

        public СоздатьАртикул()
        {
            InitializeComponent();
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void button2_Click(object sender, EventArgs e)
        {
            ГруппаТоваров гр = new ГруппаТоваров();
            гр._parent = this._parent;
            гр.ShowDialog();
            if (гр.choosed)
            {
                Код_группы_товаров.Text = гр.choose_gr_id;
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void Создать_товар_Click(object sender, EventArgs e)
        {
            // Проверяем что группа товара выбрана, артикул заполнен и ууникален
            if( Код_группы_товаров.Text.Trim()=="" )
            {
                MessageBox.Show( "Выберите группу товаров" );
                return;
            }
            string art1= Артикул_товара.Text.Trim();
            if (art1 == "")
            {
                MessageBox.Show("Артикул пуст. ");
                return;
            }

            if ( _parent.obj2int32( НормаУкладки.Text )<=0 )
            {
                MessageBox.Show(" Количество штук в поддоне пусто. ");
                return;
            }

            if (Наименование_товара.Text == "")
            {
                MessageBox.Show("Имя товара пусто. ");
                return;
            }

            string art2 = _parent.obj2str(_parent.get_wms_sql_result_single("select count(ACTICUL) as aaa from RABAEV.RRL_ARTICULS where ACTICUL='" + art1 + "'"));
            if (art1 == art2)
            {
                MessageBox.Show("Артикул '" + art1 + "' уже есть. Выберите другой. ");
                return;
            }
            Tovar_Articul = art1;
            Tovar_Name = Наименование_товара.Text.Trim(); 
            Tovar_Group = Код_группы_товаров.Text.Trim();
            choosed = true;
            Tovar_NU = _parent.obj2int32(НормаУкладки.Text);
            Tovar_BARCODE_SHT = Штрих_код.Text.Trim();

            // Создаем товар и сообщаем что создание завершено успешно.
            string strSQL = " insert into RABAEV.RRL_ARTICULS "+
                " ( ACTICUL , NAME ,  RRL_ARTICUL_GROUP , NORMA_UKLADKI , BARCODE_SHT ) " +
                " values "+
                "( '" + Tovar_Articul + "' , '" + Tovar_Name + "' , '" + Tovar_Group + "' , " + Tovar_NU.ToString() + " , '" + Tovar_BARCODE_SHT + "' ) ";
            _parent.ExecuteOracleNonQuery( strSQL );

            this.Close();

        }

        private void СоздатьАртикул_Load(object sender, EventArgs e)
        {
            Код_группы_товаров.Text = this.Tovar_Group  ;
            Ячейка_отбора.Text = "A---";
        }
    }
}
