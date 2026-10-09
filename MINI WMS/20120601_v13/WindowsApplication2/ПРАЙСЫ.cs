using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

using System.Data.OracleClient;
using System.Data.OleDb;

using System.Drawing.Printing;

namespace WindowsApplication2
{
    public partial class ПРАЙСЫ : Form
    {

        public string РЕГИОН="";
        public string РАЙОН="";
        public string КОНТОРА = "";
        public Form1 _pparent;
        public string WMS_CONNECTION_STRING_INST;

        public ПРАЙСЫ()
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




        private void ПРАЙСЫ_Load(object sender, EventArgs e)
        {

            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_conn.Open();

            radioButton1.Text = РЕГИОН;
            radioButton2.Text = РАЙОН;
            contora1.Text = КОНТОРА;



            if (radioButton1.Text == "")
            {
                radioButton1.Enabled = false;
            }

            if (radioButton2.Text == "")
            {
                radioButton2.Enabled = false;
            }


            #region РАБОТА С ОРАКЛ 




            #region РАЙОН
            OracleCommand ora_com = new OracleCommand();
            string str_sql4 = "";
            if (КОНТОРА == "")
            {
                str_sql4 = " or  ( COMPANY is null )  ";
            }

            string strSQL = " select PRICE , RANGE1 , PRICE_FOR_HOURS ,  PRICE_FOR_ADDR , NORM_HOURS " +
                " from RRL_TRANSPORT_PRICE where PRICE_NAME='" + radioButton1.Text + "' "+
                " and ( COMPANY='" + КОНТОРА + "'  " + str_sql4 + " ) ";
            ora_com.CommandText = strSQL;
            long m_count = 0;
            try
            {
            
                
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();
                if (ora_reader.Read())
                {
                    price1.Text = ora_reader.GetDouble(0).ToString();
                    range1.Text = ora_reader.GetDouble(1).ToString();
                    price_hours1.Text = ora_reader.GetDouble(2).ToString();
                    price_addr1.Text = ora_reader.GetDouble(3).ToString();
                    normative_hours1.Text = ora_reader.GetDouble(4).ToString();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            #endregion

            #region РЕГИОН


             ora_com = new OracleCommand();
             str_sql4 = "";
            if (КОНТОРА == "")
            {
                str_sql4 = " or  ( COMPANY is null )  ";
            }

            strSQL = " select PRICE , RANGE1 , PRICE_FOR_HOURS, PRICE_FOR_ADDR , NORM_HOURS "+
                " from RRL_TRANSPORT_PRICE where PRICE_NAME='" + radioButton2.Text + 
                "'  and ( COMPANY='" + КОНТОРА + "'  " + str_sql4 + " ) ";

            ora_com.CommandText = strSQL;
            m_count = 0;
            try
            {

                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();
                if (ora_reader.Read())
                {
                    price2.Text = ora_reader.GetDouble(0).ToString();
                    range2.Text = ora_reader.GetDouble(1).ToString();
                    price_hours2.Text = ora_reader.GetDouble(2).ToString();
                    price_addr2.Text = ora_reader.GetDouble(3).ToString();
                    normative_hours2.Text = ora_reader.GetDouble(4).ToString();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }


            #endregion

            strSQL = "select Distinct COMPANY from RRL_TRANSPORT_PRICE where PRICE_NAME='" + radioButton1.Text + "'  ";

            #endregion


        }

        private void button1_Click(object sender, EventArgs e)
        {

            string PRICE_NAME1="";
            long PRICE2 = 0;
            long kilometers1 = 0;
            long price_hours11 = 0;
            long price_addr11 = 0;
            long hours_normative = 0;
            long PRICE2_ADDR = 0;

            try
            {
                if (radioButton1.Checked)
                {
                    PRICE_NAME1 = radioButton1.Text;
                    PRICE2 = Convert.ToInt32(price1.Text);
                    kilometers1 = Convert.ToInt32(range1.Text);
                    price_hours11 = Convert.ToInt32(price_hours1.Text);
                    price_addr11 = Convert.ToInt32(price_addr1.Text);
                    hours_normative = Convert.ToInt32( Convert.ToDouble (normative_hours1.Text));
                    PRICE2_ADDR= Convert.ToInt32(price_addr1.Text);
                }

                if (radioButton2.Checked)
                {
                    PRICE_NAME1 = radioButton2.Text;
                    PRICE2 = Convert.ToInt32(price2.Text);
                    kilometers1 = Convert.ToInt32(range2.Text);
                    price_hours11 = Convert.ToInt32(price_hours2.Text);
                    price_addr11 = Convert.ToInt32(price_addr2.Text);
                    hours_normative =  Convert.ToInt32( Convert.ToDouble (normative_hours2.Text));
                    PRICE2_ADDR = Convert.ToInt32(price_addr2.Text);

                }
            }
            catch {
                MessageBox.Show("количество км и сумма не могут быть пустыми");
                return;
            }
            if ((PRICE_NAME1.Trim()) == "") 
            {
                MessageBox.Show("Имя прайса не может быть пустым");
                return;
            }
            if (PRICE_NAME1.IndexOf(']') == -1)
            {
                MessageBox.Show("Имя прайса должно содержать знак ]");
                return;
            }
            string COMPANY2 = contora1.Text;

            
            // ================================================================

            OracleConnection ora_con = new OracleConnection();
            ora_con.ConnectionString = WMS_CONNECTION_STRING_INST;
            ora_con.Open();

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = ora_con;

            ora_com.CommandText = "RABAEV.RRL_SET_TRANSPORT_PRICE";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("PRICE_NAME1", OracleType.VarChar).Value = PRICE_NAME1;

            string PATH_NAME = PRICE_NAME1.Substring(PRICE_NAME1.IndexOf(']') + 1);

            ora_com.Parameters.Add("PATH_NAME1", OracleType.VarChar).Value = PATH_NAME;

            ora_com.Parameters.Add("PRICE2", OracleType.Number).Value = PRICE2;
            ora_com.Parameters.Add("kilometers1", OracleType.Number).Value = kilometers1;

            ora_com.Parameters.Add("price_hours1", OracleType.Number).Value = price_hours11;

            ora_com.Parameters.Add("PRICE2_ADDR", OracleType.Number).Value = PRICE2_ADDR;
            ora_com.Parameters.Add("hours_normative1", OracleType.Number).Value = hours_normative; 
            
             

            ora_com.Parameters.Add("COMPANY2", OracleType.VarChar).Value = COMPANY2;

            ora_com.Parameters.Add("tmpVar", OracleType.VarChar, 25).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com.ExecuteNonQuery();
            string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
            MessageBox.Show("Данные сохранены" + tmpVar);
            // ================================================================


        }

      

        private void range1_TextChanged(object sender, EventArgs e)
        {
            if (КОНТОРА == "МОНЕТКА") return;

            if (range1.Text.Trim() == "")
            {
                return;
            }

            if( 1==1 )
            {
                string PRICE_NAME1 = "";
                long PRICE2 = 0;
                long kilometers1 = 0;

                try
                {
                    radioButton1.Checked = true;
                    
                        PRICE_NAME1 = radioButton1.Text;
                        kilometers1 = Convert.ToInt32(range1.Text);
                    
                    
                }
                catch {
                    return;
                }
                try{
                    string price_type = PRICE_NAME1.Substring(0, PRICE_NAME1.LastIndexOf(']')+1 );

                    string strSQL = " select price from RRL_TT_BILL_PRICE_KM " +
                        " where TT='" + price_type + "' and KM_FROM<" + kilometers1.ToString() + 
                        " and KM_TO>=" + kilometers1.ToString() + " ";


                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = _pparent.get_wms_connection();
                    ora_com.CommandText = strSQL;
                    string price_for_km = ora_com.ExecuteScalar().ToString();
                    price1.Text =  Convert.ToString((kilometers1 * Convert.ToInt32(price_for_km)));

                }catch{
                    price1.Text = "";
                return;
                }

            }

        }

        private void range2_TextChanged(object sender, EventArgs e)
        {

            if (КОНТОРА == "МОНЕТКА") return;

            if (range2.Text.Trim() == "")
            {
                return;
            }

            if (1==1)
            {
                string PRICE_NAME1 = "";
                long PRICE2 = 0;
                long kilometers1 = 0;

                try
                {


                    radioButton2.Checked = true;
                    PRICE_NAME1 = radioButton2.Text;
                    kilometers1 = Convert.ToInt32(range2.Text);

                }
                catch
                {
                    return;
                }
                try
                {
                    string price_type = PRICE_NAME1.Substring(0, PRICE_NAME1.LastIndexOf(']') + 1);

                    string strSQL = " select price from RRL_TT_BILL_PRICE_KM " +
                        " where TT='" + price_type + "' and KM_FROM<" + kilometers1.ToString() +
                        " and KM_TO>=" + kilometers1.ToString() + " ";


                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = _pparent.get_wms_connection();
                    ora_com.CommandText = strSQL;
                    string price_for_km = ora_com.ExecuteScalar().ToString();
                    price2.Text = Convert.ToString((kilometers1 * Convert.ToInt32(price_for_km)));

                }
                catch
                {
                    price2.Text = "";
                    return;
                }

            }

        }

        private void priv__Click(object sender, EventArgs e)
        {
            if (radioButton1.Checked)
            {
                if (range1.Text == "") return;

                string PRICE_NAME1 = radioButton1.Text;
                long kilometers1 = Convert.ToInt32(range1.Text);
                string price_type = PRICE_NAME1.Substring(0, PRICE_NAME1.LastIndexOf(']') + 1);
                long ставка_за_час = 110;
                long ставка_за_точку = 150;
                long время_на_погрузку = 2;
                long премия = 2 * 110;

                if(price_type=="[20]" || price_type=="[20реф]" || price_type=="[30]" || price_type=="[30реф]" )
                {
                    ставка_за_час=160;
                    ставка_за_точку = 225;
                    время_на_погрузку = 3;

                }
                double время =  (kilometers1 / 50) + время_на_погрузку;
                price1.Text = ((long)(время * ставка_за_час + премия)).ToString();
                price_hours1.Text = ставка_за_час.ToString();
                price_addr1.Text = ставка_за_точку.ToString();
                normative_hours1.Text = ((long)время ).ToString();
                contora1.Text = "МОНЕТКА";
            }


            if (radioButton2.Checked)
            {

                string PRICE_NAME2 = radioButton2.Text;
                long kilometers1 = Convert.ToInt32(range2.Text);
                string price_type = PRICE_NAME2.Substring(0, PRICE_NAME2.LastIndexOf(']') + 1);
                long ставка_за_час = 110;
                long ставка_за_точку = 150;
                long время_на_погрузку = 2;
                long премия = 2 * 110;

                if (price_type == "[20]" || price_type == "[20реф]" || price_type == "[30]" || price_type == "[30реф]")
                {
                    ставка_за_час = 160;
                    ставка_за_точку = 225;
                    время_на_погрузку = 3;
                }
                double время =  (kilometers1 / 50)+ время_на_погрузку;
                price2.Text = ((long)(время * ставка_за_час + премия)).ToString();
                price_hours2.Text = ставка_за_час.ToString();
                price_addr2.Text = ставка_за_точку.ToString();
                normative_hours2.Text = ((long)время).ToString();
                contora1.Text = "МОНЕТКА";

            }


        }

        private void radioButton1_CheckedChanged(object sender, EventArgs e)
        {
            string PRICE_NAME1 = "";
            if (radioButton1.Checked)
            {
                if (range1.Text == "")
                {
                     PRICE_NAME1 = radioButton1.Text;
                }
            }
            else
            {
                if (range2.Text == "")
                {
                    {
                         PRICE_NAME1 = radioButton2.Text;
                    }
                }
            }

            if (PRICE_NAME1 == "") return;

                    string price_type = PRICE_NAME1.Substring(0, PRICE_NAME1.LastIndexOf(']') + 1);
                    PRICE_NAME1 = PRICE_NAME1.Replace(price_type , "" );
                    try
                    {
                        string strSQL = "select max(RANGE1) from RABAEV.RRL_TT_PATH where PATH1='" + PRICE_NAME1.ToUpper() + "' ";
                        string res1=_pparent.CachedQuerySingle(strSQL);

                        if (res1 != "") { 
                            label2.Text="расстояние("+res1+")";
                        }
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message);
                    }


        }




    }
}