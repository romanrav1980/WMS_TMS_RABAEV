using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Data.SqlClient;
using System.Data.OracleClient;
using System.Data.OleDb;


namespace WindowsApplication2
{
    public partial class Безопасность : Form
    {

        public Form1 _parent ;
        public Безопасность()
        {
            InitializeComponent();
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            
        }

        private void textBox1_KeyPress(object sender, KeyPressEventArgs e)
        {




            bool sl = true;
            bool fault= false;
            string fault_text = "";
            if (e.KeyChar == '\r')
            {

                button1.Visible = false;
                button1.Enabled = false;

            ID_.Text = "";
            CONDITION.Text = "";
            TRANSPORT.Text = "";
            FIO.Text = "";
            DOVERENNOST_OT.Text = "";
            TEL.Text = "";
            PASSPORT.Text = "";
            ADDR.Text = "";


                string k = textBox1.Text.Trim();
                k = k.Trim();//();
                k = k.Replace("ЕЯЩТУ_ЫДЩ_", "TZONE_SLO_");
                k = k.Replace("ЕЯЩТУ_ЬД_", "TZONE_ML_");

                // TZONE_SLO_37597
                if (k.IndexOf("TZONE_SLO_") == -1 && k.IndexOf("TZONE_ML_") == -1)
               {

                   fault=false;
                
                   fault_text = "Неудачная проверка маршрута : " + k+" Это не штрих-код сопроводительного листа.";

                   // TRANSPORT_TASK_HISTORY       
                   MessageBox.Show("Это не штрих-код сопроводительного листа.(" + k + ")");
                   textBox1.Text = "";
                   fault = true;
               }else{
                   if (k.IndexOf("TZONE_ML_") == -1)
                   { sl = true;
                        ВидДокумента.Text = "Сопроводительный лист";
                   }
                   else { 
                       sl = false;
                       ВидДокумента.Text = "Маршрутный лист";
                   }

                    string k2=k.Replace( "TZONE_SLO_" , "" );
                    k2 = k2.Replace("TZONE_ML_", "");
                    if( _parent.obj2int(k2)<=0  )
                    {
                        ID_.Text = "0";
                        fault=true;
                        fault_text = "Неверный номер маршрута" + k;
                        MessageBox.Show("Неверный номер маршрута" + k+" "+k2);
                        return;
                    }else
                    {


                     string strSQL9 = " select TT.CONDITION , TT.TRANSPORT , F, I , O , DOVERENNOST_OT ,TEL ,"+
                            " PASSPORT , ADDR  "+
                            " from  RABAEV.RRL_TRANSPORT_TASK TT , " +
                            " RABAEV.RRL_TR_VODITEL VOD where TT.ID=" + k2+
                            " and VOD.ID=TT.VODITEL_ID ";

                        OracleCommand ora_com8 = new OracleCommand();
                        ora_com8.CommandText =  strSQL9;
                        ora_com8.Connection = _parent.get_wms_connection();
                        OracleDataReader ora_read = ora_com8.ExecuteReader();
                        if (ora_read.Read())
                        {

                            CONDITION.Text = _parent.obj2str(ora_read.GetValue(0));
                            TRANSPORT.Text=_parent.obj2str(ora_read.GetValue(1));
                            FIO.Text=_parent.obj2str(ora_read.GetValue(2)) + " "+_parent.obj2str(ora_read.GetValue(3))+" " +_parent.obj2str(ora_read.GetValue(4))  ;
                            DOVERENNOST_OT.Text=_parent.obj2str(ora_read.GetValue(5));
                            TEL.Text = _parent.obj2str(ora_read.GetValue(6));
                            PASSPORT.Text =_parent.obj2str(ora_read.GetValue(7)) ;
                            ADDR.Text = _parent.obj2str(ora_read.GetValue(8));
                            ID_.Text = k2;

                            string sost = _parent.obj2str(ora_read.GetValue(0));
                            if (sost == "ВЫПУЩЕН")
                            {
                                fault_text = "Рейс уже был отгружен. Машину не выпускайте.";
                                MessageBox.Show("Рейс уже был отгружен. Машину не выпускайте.");
                                fault = true;
                            }
                            else
                            {
                                button1.Visible = true;
                                button1.Enabled = true;
                                ID_.Text = k2;

                                //MessageBox.Show("Выпускайте Машину.");
                                fault = false;

                                OracleCommand ora_com = new OracleCommand();
                                ora_com.Connection = _parent.get_wms_connection();
                                ora_com.CommandType = CommandType.StoredProcedure;
                                ora_com.CommandText = "RABAEV.RRL_TRANPORT_TASK_HISTORY_ADD";
                                ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = _parent.obj2int(k2);
                                ora_com.Parameters.Add("TRANSTYPE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("TRANSPORT1", OracleType.VarChar).Value = TRANSPORT.Text;
                                ora_com.Parameters.Add("ROUTETYPE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("WAVE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("SHIPMENT_DATE1", OracleType.DateTime).Value = DateTime.Now;
                                ora_com.Parameters.Add("VODITEL_ID1", OracleType.Int32).Value = 0;
                                ora_com.Parameters.Add("PRIMECHANIE1", OracleType.VarChar).Value = "Разрешен выезд авто. Водитель=" + FIO.Text + " ТК=" + DOVERENNOST_OT.Text;
                                ora_com.Parameters.Add("DOCK1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = _parent.wms_user.user_id;
                                ora_com.Parameters.Add("OPERATION1", OracleType.VarChar).Value = "VERIFY_SECURITY";
                                ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
                                ora_com.ExecuteNonQuery();

                            }
                        }
                        else {
                            fault = true;
                            fault_text = "Водитель не указан, либо номера маршрута не существует. id=" + k2;
                            MessageBox.Show(fault_text);
                        }

                    }


                }

                #region ORACLE 
                if (fault)
               {
                   OracleCommand ora_com = new OracleCommand();
                   ora_com.Connection = _parent.get_wms_connection();
                   ora_com.CommandType = CommandType.StoredProcedure;
                   ora_com.CommandText = "RABAEV.RRL_TRANPORT_TASK_HISTORY_ADD";
                   ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value =  _parent.obj2int( ID_.Text);
                   ora_com.Parameters.Add("TRANSTYPE1", OracleType.VarChar).Value = "";
                   ora_com.Parameters.Add("TRANSPORT1", OracleType.VarChar).Value = "";
                   ora_com.Parameters.Add("ROUTETYPE1", OracleType.VarChar).Value = "";
                   ora_com.Parameters.Add("WAVE1", OracleType.VarChar).Value = "";
                   ora_com.Parameters.Add("SHIPMENT_DATE1", OracleType.DateTime).Value = DateTime.Now;
                   ora_com.Parameters.Add("VODITEL_ID1", OracleType.Int32).Value = 0;
                   ora_com.Parameters.Add("PRIMECHANIE1", OracleType.VarChar).Value = fault_text;
                   ora_com.Parameters.Add("DOCK1", OracleType.VarChar).Value = "";
                   ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = _parent.wms_user.user_id;
                   ora_com.Parameters.Add("OPERATION1", OracleType.VarChar).Value = "VERIFY_SECURITY";
                   ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
                   ora_com.ExecuteNonQuery();

               }
                #endregion


               textBox1.Text = "";

           }
        }

        private void button1_Click(object sender, EventArgs e)
        {

            try
            {

                Dictionary<string, Dictionary<string, string>> database= 
                    new Dictionary<string,Dictionary<string,string>>();
                Dictionary<string, string> constants = new Dictionary<string, string>();
                DateTime min =  DateTime.Now.AddMinutes(20);
                string text = "<BODY><PAGE axes='0' landscape='0' >"+
                    "<LABEL  x='3' y='3'   >Выезд разрешен до " + min + " рейс=" + ID_.Text + " машина=" + TRANSPORT.Text + " водитель=" + FIO.Text + " Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "</LABEL>" +
                    "<LABEL  x='3' y='1190'   >Выезд разрешен до " + min + " рейс=" + ID_.Text + " машина=" + TRANSPORT.Text + " водитель=" + FIO.Text + " Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "</LABEL>" +
                    "<LABEL  x='340' y='800'   >Выезд разрешен до: </LABEL>"+
                    "<LABEL  x='340' y='812'   >"+ min + "</LABEL>" +
                    "<LABEL  x='340' y='860'   >     ДЛЯ ПЕЧАТИ  </LABEL>" +
                    " <RECT   x1='340' x2='470' y1='800' y2='930' thin='1'  ></RECT> " +
                    "</PAGE></BODY>";

                if (ВидДокумента.Text != "Сопроводительный лист")
                {
                    text = "<BODY><PAGE axes='0' landscape='1' >" +
                        "<LABEL  x='0' y='0'   >Выезд разрешен до " + min + " рейс=" + ID_.Text + " машина=" + TRANSPORT.Text + " водитель=" + FIO.Text + " Выезд разрешен до " + min + " рейс=" + ID_.Text + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "</LABEL>" +
                        "<LABEL  x='0' y='780'   >Выезд разрешен до " + min + " рейс=" + ID_.Text + " машина=" + TRANSPORT.Text + " водитель=" + FIO.Text + " Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "Выезд разрешен до " + min + " рейс=" + ID_.Text + "</LABEL>" +
                        "<LABEL  x='940' y='740'   >Выезд разрешен до: </LABEL>" +
                        "<LABEL  x='940' y='752'   >" + min + "</LABEL>" +
                        "<LABEL  x='940' y='764'   >     ДЛЯ ПЕЧАТИ  </LABEL>" +
                        " <RECT   x1='940' x2='1070' y1='740' y2='780' thin='1'  ></RECT> " +
                        "</PAGE></BODY>";
                
                }

                _parent.PrintFromXML(text, database, constants);






                OracleCommand ora_com = new OracleCommand();
                                ora_com.Connection = _parent.get_wms_connection();
                                ora_com.CommandType = CommandType.StoredProcedure;
                                ora_com.CommandText = "RABAEV.RRL_TRANPORT_TASK_HISTORY_ADD";
                                ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = _parent.obj2int(ID_.Text);
                                ora_com.Parameters.Add("TRANSTYPE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("TRANSPORT1", OracleType.VarChar).Value = TRANSPORT.Text;
                                ora_com.Parameters.Add("ROUTETYPE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("WAVE1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("SHIPMENT_DATE1", OracleType.DateTime).Value = DateTime.Now;
                                ora_com.Parameters.Add("VODITEL_ID1", OracleType.Int32).Value = 0;
                                ora_com.Parameters.Add("PRIMECHANIE1", OracleType.VarChar).Value = "Напечатан пропуск. Водитель=" + FIO.Text + " ТК=" + DOVERENNOST_OT.Text;
                                ora_com.Parameters.Add("DOCK1", OracleType.VarChar).Value = "";
                                ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = _parent.wms_user.user_id;
                                ora_com.Parameters.Add("OPERATION1", OracleType.VarChar).Value = "VERIFY_SECURITY";
                                ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
                                ora_com.ExecuteNonQuery();

                                //  _parent.ExecuteOracleNonQuery(" update RRL_TRANSPORT_TASK set CONDITION = 'ВЫПУЩЕН' where id='" + ID_.Text + "' ");
                                // function set_tt_closed( tt_id int )  return int    TRANSPORT_PLN
                                Dictionary<string, object> values = new Dictionary<string, object>();
                                values["tt_id"] = _parent.obj2int(ID_.Text);
                                object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_tt_closed", values, OracleType.Int32, 0);


                                _parent.ОтправитьПисьмаВМагазиныПоУехавшейМашине(_parent.obj2int(ID_.Text));

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

        }

        private void ОбновитьСписокПриходов_Click(object sender, EventArgs e)
        {

            string w = "";
            if ( ВызванныеПриходыУбирать.Checked ) 
            {
                w = " and PRIHOD.is_prihod_fresh(id)<>'вызов' ";
            }


            string strSQL2 = "  select rownum ПП , id УИД , ПОСТАВЩИК , ДОК , МАШИНА ,OHRANA_KPP ,  " + 
               " ТЕЛ_ВОДИТЕЛЯ  , СКЛАД ,  ПРИОРИТЕТ,  invite_time ВРЕМЯ_ВЫЗОВА_НА_ДОК , PRIHOD.is_prihod_fresh(id) ВЫЗВ " + 
               " from ( select OHRANA_KPP ,  nkl.id ,  nkl.postavshik_name ПОСТАВЩИК , nkl.dock ДОК ,  " + 
                           "  nkl.vechile_number МАШИНА , nkl.voditel_phone_numb ТЕЛ_ВОДИТЕЛЯ ,  " + 
                           "  nkl.planning_accept_time ПРИНЯТЬ_ДО  , nkl.CHECKING_TIME ВРЕМЯ_ЦК , " + 
                           "  rrl_skladname_by_id( nkl.ware_id ) СКЛАД , nkl.priority1 ПРИОРИТЕТ , invite_time " + 
                           "  from rrl_prihod_naklad nkl  " + 
                           "  where nkl.prooved=1 and ( nkl.condition in (0,1)  ) and not ( nkl.dock is null ) and nkl.priority1<20  " + 
                           "  and ( not nkl.invite_time is null  ) " + w + 
                           "  order by nkl.priority1 , nkl.invite_time DESC  ) ";

            _parent.fill_view_MINI_WMS(dataGridView1, strSQL2 , 11 );


            /*
              string ware_id = wms_user.ware_id.ToString();
            if (m_выбранный_склад.Text != "")
            { ware_id = m_выбранный_склад.Text;}

           
            ЗАПРОСЫ ftr = new ЗАПРОСЫ();
            ftr._parent = this;
            ftr.sSQL = strSQL;
            ftr.Header_Text = "Очередь машин на приемку. Склады: " + ware_id;
            ftr.repeat_time_in_seconds = 120;
            ftr.Show();
             
             */
        }

        private void НазначитьКПП1_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow != null)
            { 
                long id = _parent.obj2int( dataGridView1.CurrentRow.Cells[1].Value );
                if (id > 0)
                {
                    Dictionary<string, object> values = new Dictionary<string, object>();
                    values["prihod_id"] = id;
                    values["kpp_n"] = "КПП1" ;
                    object ret = _parent.wms_get_spfunction_value2("PRIHOD.set_prihod_kpp", values, OracleType.Int32, 0);
                    dataGridView1.CurrentRow.Cells[5].Value = "КПП1";
                    dataGridView1.CurrentRow.Cells[10].Value = "вызов";

                    
                }
            }


        }

        private void НазначитьКПП2_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow != null)
            {
                long id = _parent.obj2int(dataGridView1.CurrentRow.Cells[1].Value);
                if (id > 0)
                {
                    Dictionary<string, object> values = new Dictionary<string, object>();
                    values["prihod_id"] = id;
                    values["kpp_n"] = "КПП2";
                    object ret = _parent.wms_get_spfunction_value2("PRIHOD.set_prihod_kpp", values, OracleType.Int32, 0);
                    dataGridView1.CurrentRow.Cells[5].Value = "КПП2";
                    dataGridView1.CurrentRow.Cells[10].Value = "вызов";
                }
            }


        }



    }
}