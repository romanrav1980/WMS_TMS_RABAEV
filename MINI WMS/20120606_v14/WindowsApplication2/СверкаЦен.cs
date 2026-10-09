using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Data.OracleClient;
using System.Data.OleDb;




namespace WindowsApplication2
{
    public partial class СверкаЦен : Form
    {
        public bool m_СверкаНеПройдена = false;
        public string SUPPLIER="";
        public string VEH_NUMBER = "";
        public string ZAKAZ_NUMBER = "";
        public long id=0;
        public Form1 _parent;

        public СверкаЦен()
        {
            InitializeComponent();
        }

        private void СверкаНеПройдена_Click(object sender, EventArgs e)
        {
            m_СверкаНеПройдена = true;
            this.Close();
        }

        private void СверкаПройдена_Click(object sender, EventArgs e)
        {
            // Проверяем что телефон водителя заполнен, машина заполнена, ИНН поставщика и поставщик есть
            if( t_DRIVER_PHONE_NUMBER.Text.Trim() =="" ){
                MessageBox.Show("введите телефон водителя");
                return;
            }

                
                   
            if ( t_SUPPLIER.Text.Trim() == "")
            {
                MessageBox.Show("введите имя поставщика");
                return;
            }

            if (t_VEH_NUMBER.Text.Trim() == "")
            {
                MessageBox.Show("введите номер авто");
                return;
            }


            if (t_ZAKAZ_NUMBER.Text.Trim() == "")
            {
                MessageBox.Show("введите номер заказа");
                return;
            }

            if (t_FIO.Text.Trim() == "")
            {
                MessageBox.Show("введите ФИО водителя");
                return;
            }


            m_СверкаНеПройдена = false;

            string strSQL2 = " update rrl_prihod_naklad set POSTAVSHIK_NAME='" +  t_SUPPLIER.Text.Trim()   + "' , " +
                      " SUPP_INN='" + t_INN.Text.Trim() + "' , SUPP_KPP='" +  t_KPP.Text.Trim()  + "' , "+
                      " ZAKAZ_NUMBER='"+ t_ZAKAZ_NUMBER.Text.Trim() +"' , VECHILE_NUMBER='"+t_VEH_NUMBER.Text.Trim()+"' , "+
                      " VODITEL_PHONE_NUMB='" + t_DRIVER_PHONE_NUMBER.Text.Trim() + "' , VODITEL_NAME='" + t_FIO.Text.Trim()+ "' where id=" + id.ToString() + " ";
            
            _parent.ExecuteOracleNonQuery(strSQL2);
            this.Close();

        }


        private void ОбновитьДанныеПоЗаказуF( string zakaz_numb )
        {
            // Проверим что заказ с таким номером существует
            // По номеру заказа выбираем ИНН контрагента и его имя, если оно не пустое, фиксируем
            if (zakaz_numb.Trim() == "")
            {
                return;
            }

            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = _parent.SM_CONNECTION_STRING();
            ora_conn.Open();
            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = ora_conn;

            ora_com.CommandText = "  select  " + 
            " cli.Name , " + 
            " cli.INN ,  " + 
            " cli.KPP " + 
            " from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli  " + 
            " where d.doctype in ( 'WI' , 'OR' )    " + 
            " and d.docstate in ( 1 , 2 , 3 )  " +
            " and d.id =  '" + zakaz_numb.Trim() + "'    " + 
            " and d.id = s.docid and d.doctype = s.doctype  " + 
            " and s.article = c.article  and cli.ID = d.CLIENTINDEX   ";


            OracleDataReader ora_read= ora_com.ExecuteReader();
            if (ora_read.Read())
            {//  если заказ существует
                string Name = ora_read.GetString(0).Trim();
                string INN = ora_read.GetString(1);
                string KPP = ora_read.GetString(2);
                if (Name != "" || INN != "")
                { // Обновляем данные прихода
                    string strSQL2 = " update rrl_prihod_naklad set POSTAVSHIK_NAME='" + Name + "' , " +
                        " SUPP_INN='" + INN + "' , SUPP_KPP='" + KPP + "'  where id=" + id.ToString() + " ";
                    _parent.ExecuteOracleNonQuery( strSQL2 );
                    
                }

                t_SUPPLIER.Text = Name;
                t_INN.Text = INN;
                t_KPP.Text = KPP;
            }
            else { // если заказ не существует, либо он закрыт
                MessageBox.Show("Заказа '" + zakaz_numb + "' не существует, или он в черновике ");
            }




        }


        private void СверкаЦен_Load(object sender, EventArgs e)
        {
            t_ID.Text = id.ToString();
            string strSQL = "select ZAKAZ_NUMBER from rrl_prihod_naklad where id=" + id.ToString() + " ";
            t_ZAKAZ_NUMBER.Text = _parent.obj2str(  _parent.get_wms_sql_result_single(strSQL) );
            ОбновитьДанныеПоЗаказуF(t_ZAKAZ_NUMBER.Text.Trim());


            string strSQL2 = " select POSTAVSHIK_NAME  , SUPP_INN , SUPP_KPP , "+
                " ZAKAZ_NUMBER , VECHILE_NUMBER , VODITEL_PHONE_NUMB , VODITEL_NAME " +
                " from rrl_prihod_naklad   where id=" + id.ToString() + " ";
            
            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection= _parent.get_wms_connection();
            ora_com.CommandText= strSQL2;
            OracleDataReader ora_read= ora_com.ExecuteReader();
            if( ora_read.Read() )
            {
                t_SUPPLIER.Text = _parent.obj2str( ora_read.GetValue(0) );
                t_INN.Text = _parent.obj2str(ora_read.GetValue(1));
                t_KPP.Text = _parent.obj2str(ora_read.GetValue(2));
                t_ZAKAZ_NUMBER.Text = _parent.obj2str(ora_read.GetValue(3));
                t_VEH_NUMBER.Text = _parent.obj2str(ora_read.GetValue(4));
                t_DRIVER_PHONE_NUMBER.Text = _parent.obj2str(ora_read.GetValue(5));

                t_FIO.Text = _parent.obj2str(ora_read.GetValue(6));
            }

            #region ЗАПОЛНЯЕМ СПРАВОЧНИК СКЛАДОВ
            strSQL=" select ID, name from rrl_wares ";
            Dictionary< object ,object > arr1 =  _parent.get_wms_sql_result_dictionary( strSQL );
            foreach (object key1 in arr1.Keys)
            {
                comboBox1.Items.Add(key1.ToString()+" - "+arr1[key1].ToString());
            }

            #endregion

        }



        private void ОбновитьДанныеПоЗаказу_Click(object sender, EventArgs e)
        {

            ОбновитьДанныеПоЗаказуF(t_ZAKAZ_NUMBER.Text.Trim());
        }

        #region Выбрали склад
        private void comboBox1_SelectedValueChanged(object sender, EventArgs e)
        {



            long current_ware_id = 0;
            try
            {
                current_ware_id = Convert.ToInt32(comboBox1.Text[0].ToString());
                long current_ware_id2 = 0;
                try
                {
                    current_ware_id2 = Convert.ToInt32(comboBox1.Text[0].ToString() + comboBox1.Text[1].ToString());
                }
                catch { }

                if (current_ware_id < current_ware_id2)
                { current_ware_id = current_ware_id2; }

            }
            catch (Exception ex)
            {
                MessageBox.Show("Склад не выбран. Выберите склад");
                return;
            }
            
            if (current_ware_id <= 0)
            {
                MessageBox.Show("Не выбран cклад.");
                return;
            }


            #region ВЫЗОВ ХП.

            if (! _parent.has_right("CHANGE_WARE_ID"))
                        {
                            MessageBox.Show("У вас нет прав на изменение склада");
                            return;
                        } 

            Dictionary<string, object> values = new Dictionary<string, object>();
            values["prih_id"] = id;
            values["new_ware_id"] = current_ware_id;
            object ret = _parent.wms_get_spfunction_value2("PRIHOD.set_ware_id", values, OracleType.Int32, 0);
             
            #endregion

        }
        #endregion




    }
}
