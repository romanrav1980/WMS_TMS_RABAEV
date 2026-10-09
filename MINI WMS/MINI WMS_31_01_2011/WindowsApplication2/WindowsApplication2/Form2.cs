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
    public partial class Form2 : Form
    {

        public string WMS_CONNECTION_STRING_INST= "Server=DBWMS;Password=RABAEVWMS;User ID=RABAEV";
        public string MAIN_LOGIN;
        public long WARE_ID;
        public string MAIN_PASS;
        public string version = "от 28.01.2011";

        public Form2()
        {
            InitializeComponent();
        }

 
        private void button1_Click(object sender, EventArgs e)
        {
         

            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();


            MAIN_LOGIN = "";
            MAIN_PASS = "";


            try
            {
                ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = "RABAEV.RRL_AUTH2";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("login", OracleType.VarChar).Value = m_login.Text;
                ora_com.Parameters.Add("pass1", OracleType.VarChar).Value = m_pass.Text;
                ora_com.Parameters.Add("version1", OracleType.VarChar).Value = version;


                

                ora_com.Parameters.Add("ok", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
            }catch(Exception ex)
            {
                MessageBox.Show("нет соединения с базой данных" + ex.Message );
                return;
            }

            long ret1 = Convert.ToInt64( ora_com.Parameters["ok"].Value );
            if (ret1 > 0)
            {
                MAIN_LOGIN = m_login.Text;
                MAIN_PASS = m_pass.Text;
                WARE_ID = ret1;
                this.Close();
            }
            else {
                if (ret1 <= -3) {
                    MessageBox.Show(" Версия программы запрещена к ипользованию ");
                
                }
                else
                {
                    MessageBox.Show(" Неверный логин или пароль ");
                }
            }


        }

        private void Form2_Load(object sender, EventArgs e)
        {
            label1.Text = version;

        }
    }
}