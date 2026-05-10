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
    public partial class BillingTransport : Form
    {

        public string WMS_CONNECTION_STRING_INST;
        public Form1 __parent;
 
        public BillingTransport()
        {
            InitializeComponent();
        }



        private void fill_view_MINI_WMS(DataGridView dgv1, string strSQL, int column_fill_count)
        {
            dgv1.Rows.Clear();
            OracleCommand ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;
            long m_count = 0;
            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {
                    object[] values1 = new object[column_fill_count];
                    for (int yy = 0; yy < column_fill_count; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }
                    dgv1.Rows.Add(values1);
                    m_count++;
                }

                ora_reader.Close();
                ora_conn.Close();
            }
            catch (Exception Ex)
            {
                MessageBox.Show(" f343 " + Ex.Message);
            }
            dgv1.Columns[0].ToolTipText = m_count.ToString() + " = количество записей";
            // dgv1.Columns[0].HeaderText = dgv1.Columns[0].HeaderText + "[" + m_count.ToString() +"]";

        }



        #region ОБНОВЛЕНИЕ СТРОКИ

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

            if( dataGridView1.CurrentRow== null ){return;}
            string COMPANY = Convert.ToString(dataGridView1.CurrentRow.Cells[2].Value);
            if (COMPANY.Trim() == "") { return; }

            try
            {
                OracleCommand ora_com = new OracleCommand();
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                
                
                int ID7 = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
                string NUM = Convert.ToString(dataGridView1.CurrentRow.Cells[1].Value);
                string NUM_PLAT = Convert.ToString(dataGridView1.CurrentRow.Cells[9].Value);

                if (NUM == "") 
                {
                    string strSQL7 = " select count( NUM )+1 from RABAEV.RRL_BILL_ORDERS   where COMPANY='" + COMPANY+ "'  ";
                    OracleCommand ora_com7 = new OracleCommand();
                    ora_com7.CommandText = strSQL7;
                    ora_com7.Connection = ora_conn;
                    NUM = (ora_com7.ExecuteScalar().ToString());
                    dataGridView1.CurrentRow.Cells[1].Value = NUM;
                }

                DateTime DATEOFORDER = DateTime.Today;
                if(dataGridView1.CurrentRow.Cells[3].Value!=null)
                {
                    DATEOFORDER = Convert.ToDateTime(dataGridView1.CurrentRow.Cells[3].Value);
                }
                else {
                    dataGridView1.CurrentRow.Cells[3].Value = DATEOFORDER;
                }


                DateTime DATEFROM;
                if( dataGridView1.CurrentRow.Cells[4].Value!=null )
                {
                     DATEFROM = Convert.ToDateTime(dataGridView1.CurrentRow.Cells[4].Value);
                }
                else {
                    try
                    {
                        string strSQL7 = " select MAX( DATETO ) from RABAEV.RRL_BILL_ORDERS   where COMPANY='" + COMPANY + "'  ";
                        OracleCommand ora_com7 = new OracleCommand();
                        ora_com7.CommandText = strSQL7;
                        ora_com7.Connection = ora_conn;
                        DATEFROM = Convert.ToDateTime(ora_com7.ExecuteScalar());
                        DATEFROM.AddDays(1);
                    }
                    catch {
                        DATEFROM = DateTime.Today.AddDays(-7);
                    }
                    dataGridView1.CurrentRow.Cells[4].Value = DATEFROM;
                }

                DateTime DATETO = DateTime.Today;
                try
                {
                    DATETO = Convert.ToDateTime(dataGridView1.CurrentRow.Cells[5].Value);
                }
                catch {
                    DATETO = DATEFROM.AddDays(7);
                    dataGridView1.CurrentRow.Cells[5].Value = DATETO;
                }

                if (DATETO.Year < 2000) {
                    DATETO = DATEFROM.AddDays(7);
                    dataGridView1.CurrentRow.Cells[5].Value = DATETO;
                }

                // OracleCommand ora_com = new OracleCommand();

                ora_com.CommandText = "RABAEV.RRL_BILL_ADD_TTBILL";
                ora_com.CommandType = CommandType.StoredProcedure;
 


                ora_com.Parameters.Add("ID1", OracleType.Int32).Value = ID7.ToString();
                ora_com.Parameters.Add("NUM1", OracleType.VarChar).Value = NUM.ToString();
                ora_com.Parameters.Add("COMPANY1", OracleType.VarChar).Value = COMPANY.ToString();
                ora_com.Parameters.Add("DATEOFORDER1", OracleType.DateTime).Value = DATEOFORDER;
                ora_com.Parameters.Add("DATEFROM1", OracleType.DateTime).Value = DATEFROM;
                ora_com.Parameters.Add("DATETO1", OracleType.DateTime).Value = DATETO;
                ora_com.Parameters.Add("ret", OracleType.Int32).Direction = ParameterDirection.ReturnValue;

                ora_com.Parameters.Add("NUM_PLAT1", OracleType.VarChar).Value = NUM_PLAT.ToString();
                



                try
                {
                    int rowsAffected2 = ora_com.ExecuteNonQuery();
                    dataGridView1.CurrentRow.Cells[0].Value = Convert.ToInt32(ora_com.Parameters["ret"].Value);
                }
                catch(Exception ex)
                {

                    MessageBox.Show( ex.Message );
                }



            }
            catch (Exception ex)
            {
                MessageBox.Show( ex.Message );
            }
        
        }
        #endregion

        private string date2sql_ora(DateTime dt)
        {
            return "'" + dt.Day + "." + dt.Month + "." + dt.Year + "'";
        }


        private void button1_Click(object sender, EventArgs e)
        {

            string company_filter="";
            if (Filter_company.SelectedIndex > 0)
            {
                company_filter = " and COMPANY= '" + Filter_company.Text + "' ";
            }

            string strSQL = " select ID , NUM Номер , COMPANY Компания , DATEOFORDER ДатаСчета ,  "+
            "   DATEFROM от , DATETO до , RRL_BILLINGORDER_sum(ID) , int2bool(closed) , int2bool(PAYED) , NUM_PLAT  " +
                " from  RABAEV.RRL_BILL_ORDERS where DATEOFORDER<=" + date2sql_ora( dateTimePicker2.Value ) +
                " and DATEOFORDER>= " + date2sql_ora( dateTimePicker1.Value ) +" " + company_filter+" order by ID desc ";


   

            fill_view_MINI_WMS( this.dataGridView1 , strSQL  , 10 );

        }



        private void BillingTransport_Load(object sender, EventArgs e)
        {
            try
            {
                //Filter_company.Items.Add("Выберите компанию");
                Filter_company.Items.Clear();
                OracleDataReader ora_read;//= new OracleDataReader();
                OracleCommand ora_com = new OracleCommand();
                OracleConnection ora_conn = new OracleConnection();

                ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                string strSQL = "  select COMPANYNAME from RABAEV.RRL_BILL_COMPANY where DELETED=0 order by pos ";
                ora_com.CommandText = strSQL;
                ora_read = ora_com.ExecuteReader();
                while (ora_read.Read())
                {

                    ((DataGridViewComboBoxColumn)dataGridView1.Columns[2]).Items.Add(ora_read.GetValue(0).ToString());
                   // Filter_company.Items.Add(ora_read.GetValue(0).ToString());
                }


            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }
        }

        private void button2_Click(object sender, EventArgs e)
        {



            if (dataGridView1.CurrentRow == null) return;
            // id Счета.
            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }

           


            if (!__parent.has_right("EDIT_BILL_TT"))
            {
                MessageBox.Show(" Нет прав на редактирование Счетов на  оплату транспортных услуг. ");
                return;
            }
            // Добавление или удаление поездки из счета.
           


           



            #region ДОБАВЛЕНИЕ РЕЙСОВ 
            char[] sp = new char[2];
            sp[0]=' ';
            sp[1]='\n';
            string textBox1_Text = textBox1.Text.Replace("ЕЯЩТУ_ЬД_", " ").Replace("TZONE_ML_", " ");
            string[] ids = textBox1_Text.Split(sp);

            foreach (string h in ids)
            {
                long t_id = 0;
                try
                {
                    t_id = Convert.ToInt32(h);
                }
                catch { }

                if (t_id > 0)
                {
                    OracleCommand ora_com = new OracleCommand();
                    OracleConnection ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                    ora_conn.Open();
                    ora_com.Connection = ora_conn;
                    ora_com.CommandText = "RABAEV.RRL_ADD_TT_2_BILLINGORDER";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("bill_id", OracleType.Int32).Value = id;
                    ora_com.Parameters.Add("tt_id", OracleType.Int32).Value = t_id;
                    ora_com.Parameters.Add("act", OracleType.Int32).Value = 1;
                    ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();
                    string ret = ora_com.Parameters["ret"].Value.ToString();
                    if (ret != "OK")
                    {
                        MessageBox.Show("Ошибка при добавлении рейа №" + t_id.ToString() +" "+ ret);
                       // return;
                    }

                }
            }

            #endregion



        }

        private void пересчитатьВсеРейсыToolStripMenuItem_Click(object sender, EventArgs e)
        {
 


            if (! __parent.has_right("CALC_TT_PRICE"))
            {
                MessageBox.Show(" У вас нет прав на CALC_TT_PRICE ");
                return;
            }

            foreach (DataGridViewRow dr in  dataGridView2.Rows )
            {
                if(dr != null )
                if (  dr.Cells[0].Value!=null)
                {
                    #region По всем  рейсам
                    if (  __parent.obj2double( dr.Cells[2].Value) <= 0 )
                    {
                        string tt_id = dr.Cells[0].Value.ToString();
                        if (__parent.obj2int(tt_id) == 0)
                        {
                            return;
                        }
                        string ret = __parent.wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
                        double price = __parent.obj2double(ret);

                        #region ЕСЛИ ПРАЙС=0, то его просто нет в базе, надо внести

                        #endregion

                        dr.Cells[2].Value = price;
                    }
                    #endregion
                }


            }





        }

        private void пересчитатьДанныйРейсToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void dataGridView1_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            #region Выводим список маршрутов за данный период по данной компании 
            
            if (dataGridView1.CurrentRow == null) return;
            long id= Convert.ToInt32( dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }

            string h_Company = dataGridView1.CurrentRow.Cells[2].Value.ToString();
            DateTime h_Data_ot = Convert.ToDateTime( dataGridView1.CurrentRow.Cells[4].Value.ToString() );
            DateTime h_Data_to = Convert.ToDateTime(  dataGridView1.CurrentRow.Cells[5].Value.ToString());
            string strSQL = " select T.ID , int2bool( RABAEV.ISIF( PAY_ORDER_ID , " + id.ToString() + " ) ) , PRICE , " +
                "   RRL_TT_REGIONS( T.ID) , TRANSTYPE  , TRANSPORT  , T.SHIPMENT_DATE , " +
                "   RRL_TT_VODITEL_INFO(T.VODITEL_ID) , round(TEMP_WEIGHT , 0 ) , PAY_ORDER_ID , T.HOURS " +
                " from  RABAEV.RRL_TRANSPORT_TASK T , RRL_TR_VODITEL VOD  " +
                " where ((PAY_ORDER_ID =" + id.ToString() + " ) or ( SHIPMENT_DATE <= " + date2sql_ora( h_Data_to ) + 
                " and   SHIPMENT_DATE >= " + date2sql_ora( h_Data_ot ) +
                " and (( PAY_ORDER_ID is null) or    ( PAY_ORDER_ID =0) )) " +
                " and VOD.ID = T.VODITEL_ID and VOD.DOVERENNOST_OT='" + h_Company + "' " + 
                "  and T.DELETED<>1 )"+
                "  order by T.ID DESC " ;

            //TEMP_REGION
            fill_view_MINI_WMS(this.dataGridView2, strSQL, 11);



            #endregion

        }

        private void dataGridView2_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            // id Счета.
            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }

            if (dataGridView2.CurrentRow == null) return;
            // id Счета.
            long tt_id = Convert.ToInt32(dataGridView2.CurrentRow.Cells[0].Value);
            long tt_hours = 0;
            try
            {
                tt_hours = Convert.ToInt32(dataGridView2.CurrentRow.Cells[10].Value);
            }
            catch { }

            if (tt_id <= 0) { return; }


            if (! __parent.has_right("EDIT_BILL_TT"))
            {
                MessageBox.Show(" Нет прав на редактирование Счетов на  оплату транспортных услуг. ");
                return;
            }
            // Добавление или удаление поездки из счета.
            long added=0;
            try
            {
                if( Convert.ToBoolean( dataGridView2.CurrentRow.Cells[1].Value ) )
                {
                    added = 1;
                }
            }
            catch { }



            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = "RABAEV.RRL_ADD_TT_2_BILLINGORDER";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("bill_id", OracleType.Int32).Value = id;
            ora_com.Parameters.Add("tt_id", OracleType.Int32).Value = tt_id;
            ora_com.Parameters.Add("act", OracleType.Int32).Value = added;

            ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();



            string strSQL = " update  RABAEV.RRL_TRANSPORT_TASK   set hours=" + tt_hours.ToString() + " where ID=" + tt_id.ToString();
            ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;
            ora_com.Connection = ora_conn;
            ora_com.ExecuteNonQuery();


            if (ret != "OK")
            {
                MessageBox.Show(ret);
                return;
            }




        }



        private void закрытьToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (dataGridView1.CurrentRow == null) return;
            // id Счета.
            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }


            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = "RABAEV.RRL_CLOSE_BILLINGORDER";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("bill_id", OracleType.Int32).Value = id;
            ora_com.Parameters.Add("act", OracleType.Int32).Value = 1;

            ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();
            if (ret != "OK")
            {
                MessageBox.Show(ret);
                return;
            }
            else {
                dataGridView1.CurrentRow.Cells[7].Value = 1;
            }

        }

        private void установитьОплатуToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            // id Счета.
            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }


            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = "RABAEV.RRL_PAY_BILLINGORDER";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("bill_id", OracleType.Int32).Value = id;
            ora_com.Parameters.Add("act", OracleType.Int32).Value = 1;

            ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();
            if (ret != "OK")
            {
                MessageBox.Show(ret);
                return;
            }
        }

        private void открытьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            // id Счета.
            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }


            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = "RABAEV.RRL_CLOSE_BILLINGORDER";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("bill_id", OracleType.Int32).Value = id;
            ora_com.Parameters.Add("act", OracleType.Int32).Value = 0;

            ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();
            if (ret != "OK")
            {
                MessageBox.Show(ret);
                return;
            }
            else {
                dataGridView1.CurrentRow.Cells[7].Value = 0;
            }
        }

        private void рассчитатьСтоимостьРейсаToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (! __parent.has_right("CALC_TT_PRICE"))
            {
                MessageBox.Show(" У вас нет прав на CALC_TT_PRICE ");
                return;
            }

            DataGridViewRow dr = dataGridView2.CurrentRow;
            if (dr == null) return;
            string tt_id = dr.Cells[0].Value.ToString();
            if (__parent.obj2int(tt_id) == 0)
            {
                return;
            }

            string ret = __parent.wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
            double price = __parent.obj2double(ret);

            #region ЕСЛИ ПРАЙС=0, то его просто нет в базе, надо внести
            if (price == 0)
            {
                if (__parent.has_right("CREATE_TT_PRICE"))
                {

                    string reg = __parent.wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID", "tt_id", tt_id);
                    string rai = __parent.wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID2", "tt_id", tt_id);

                    ПРАЙСЫ пр = new ПРАЙСЫ();
                    пр.РАЙОН = rai;
                    пр.РЕГИОН = reg;
                    пр._pparent = this.__parent;
                    пр.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
                    пр.ShowDialog();

                }
                else
                {
                    MessageBox.Show(" У вас нет прав на CREATE_TT_PRICE ");
                    return;
                }

            }
            #endregion

            dataGridView2.CurrentRow.Cells[2].Value = price;



        }

        private void splitContainer1_Panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void распечататьРеестрРейсовПоСчетуToolStripMenuItem_Click(object sender, EventArgs e)
        {

            long id = Convert.ToInt32(dataGridView1.CurrentRow.Cells[0].Value);
            if (id <= 0) { return; }


            Dictionary<string, string> constants = new Dictionary<string, string>();
            constants["invoice_id"] = id.ToString();
            __parent.PrintFromXMLFile("transport_invoice_reestr.xml", null, constants);

        }


     

    }
}