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
    public partial class TRANSPORT : Form
    {
        public string WMS_CONNECTION_STRING_INST;
        public string CHOOSE;
        public string NUM_FILTER = "";


        public TRANSPORT()
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
            dgv1.Columns[0].ToolTipText = m_count.ToString() + " = êîëè÷åñòâî çàïèñåé";
            // dgv1.Columns[0].HeaderText = dgv1.Columns[0].HeaderText + "[" + m_count.ToString() +"]";

        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

            // ===================================================================================================
            OracleCommand ora_com;
            try
            {
                long ID ;
                string ÍÎÌÅÐÒÑ="";
                string ÒÈÏ="íåò";
                string ÌÀÐÊÀ="íåò";
                string ÐåôÐåæèì1="íåò";
                int ÐÀÁÎÒÀÅÒ1=1;
                int PALLETS = 0;
                int LOPATA = 0;
                

                    DataGridViewRow dr = this.dataGridView1.CurrentRow;
                    ID =  Convert.ToInt32(dr.Cells[0].Value);
                    ÍÎÌÅÐÒÑ = (dr.Cells[1].Value.ToString().ToUpper() );

                    string alfa = "QWERTYUIOPASDFGHJKLZXCVBNM";

                    if (ÍÎÌÅÐÒÑ.LastIndexOfAny(alfa.ToCharArray()) != -1)
                    {
                        MessageBox.Show(" Â íîìåðå ìàøèíû äîïóñòèìû òîëüêî ðóññêèå ñèìâîëû ");
                        return;
                    }

                    if (dr.Cells[2].Value!=null)
                    ÒÈÏ = (dr.Cells[2].Value.ToString());

                    if (dr.Cells[3].Value != null)
                    ÌÀÐÊÀ = (dr.Cells[3].Value.ToString());
                
                    if (dr.Cells[4].Value != null)
                    ÐåôÐåæèì1 = (dr.Cells[4].Value.ToString());

                    if ( Convert.ToBoolean( dr.Cells[5].Value ) == true)
                    {
                        ÐÀÁÎÒÀÅÒ1 = 1;
                    }
                    else {
                        ÐÀÁÎÒÀÅÒ1 = 0;
                    }

                    if (Convert.ToBoolean(dr.Cells[8].Value) == true)
                    {
                        LOPATA = 1;
                    }
                    else
                    {
                        LOPATA = 0;
                    }

                    

                    PALLETS  = Convert.ToInt32(dr.Cells[6].Value);

                    if (PALLETS <= 0)
                    {
                        //MessageBox.Show(" Êîëè÷åñòâî ïàëëåò äîëæíî áûòü áîëüøå 0 ");
                        return;
                    }

                    if (ÒÈÏ == "íåò")
                    {
                        MessageBox.Show("Óêàæèòå òèï òðàíñïîðòíîãî ñðåäñòâà");
                        return;
                    }
                    
                    OracleConnection ora_con = new OracleConnection();
                    ora_con.ConnectionString=WMS_CONNECTION_STRING_INST;
                    ora_con.Open();
                    
                    try
                    {
                        string strSQL = " select NORMA_PALLET from  RABAEV.RRL_TRANSPORT_TYPE where TRANSPORTTYPE='" + ÒÈÏ + "' ";
                        OracleCommand ora_com77 = new OracleCommand();
                        ora_com77.Connection = ora_con;
                        ora_com77.CommandText = strSQL;
                        int ÍÎÐÌÀ_ÏÀËËÅÒÈÇÀÖÈÈ = Convert.ToInt32( ora_com77.ExecuteScalar() );
                        if(ÍÎÐÌÀ_ÏÀËËÅÒÈÇÀÖÈÈ>0)
                            if (PALLETS < ÍÎÐÌÀ_ÏÀËËÅÒÈÇÀÖÈÈ)
                            {
                                MessageBox.Show("Äëÿ äàííîãî âèäà òðàíñïîðòà ïðèíÿòà íîðìà çàãðóçêè=" + ÍÎÐÌÀ_ÏÀËËÅÒÈÇÀÖÈÈ + " ïàëëåò. \n òðàíñïîðò íå ñîõðàíåí ");
                                return;
                            }
                    }catch(Exception ex)
                    {
                        string osh = ex.Message;
                    }
                    
                    
                    
                    ora_com = new OracleCommand();
                    ora_com.Connection = ora_con;
                    ora_com.CommandText = "ADD_RRL_TR_VEHICLE";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("ID1", OracleType.Int32).Value = ID;
                    ora_com.Parameters.Add("NUM1", OracleType.VarChar).Value = ÍÎÌÅÐÒÑ;
                    ora_com.Parameters.Add("TR_TYPE1", OracleType.VarChar).Value = ÒÈÏ;
                    ora_com.Parameters.Add("MARKA1", OracleType.VarChar).Value = ÌÀÐÊÀ;
                    ora_com.Parameters.Add("REF_REJIM1", OracleType.VarChar).Value = ÐåôÐåæèì1;
                    ora_com.Parameters.Add("WORKOINGNOW", OracleType.Int32).Value = ÐÀÁÎÒÀÅÒ1;
                    ora_com.Parameters.Add("PALLETS1", OracleType.Int32).Value = PALLETS;
                    ora_com.Parameters.Add("LOPATA", OracleType.Int32).Value = LOPATA;     
             

                
                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    dr.Cells[0].Value = ora_com.Parameters["ID"].Value;

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f37" + ex.Message);
            }

        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (this.dataGridView1.CurrentRow == null)
            {
                MessageBox.Show("Íå âûáðàíî ÒÑ!");
                return;
            }

            if (this.dataGridView1.CurrentRow.Cells[1].Value == null)
            {
                MessageBox.Show("Íå âûáðàíî ÒÑ!");
                return;
            }


            try
            {

                if (Convert.ToInt32(this.dataGridView1.CurrentRow.Cells[0].Value) == 0)
                {
                    MessageBox.Show("Íå âûáðàíî ÒÑ!");
                    return;
                }

            }
            catch { }

          this.CHOOSE=  this.dataGridView1.CurrentRow.Cells[1].Value.ToString();
          this.Close();
        }

        private void TRANSPORT_Load(object sender, EventArgs e)
        {
            string str_f = "";
            if (NUM_FILTER != "")
            {
                str_f = " where NUM like '%"+NUM_FILTER+"%' ";
                textBox1.Text = NUM_FILTER;
            }





            string strSQL = " select ID , NUM, TR_TYPE, MARKA, REF_REJIM , INT2BOOL( WORKING_NOW) , PALLETS , INT2BOOL( BLOCKED ) , INT2BOOL( Gidrobort )  from RABAEV.RRL_TR_VEHICLE  " + str_f + " order by ID desc ";
            fill_view_MINI_WMS(dataGridView1, strSQL, 9);

        }

        private void button2_Click(object sender, EventArgs e)
        {
            string add_sql = "";
            if (textBox1.Text != "")
            {
                add_sql = " and ( NUM like '%" + textBox1.Text + "%' ) ";
            }

            string add_sql2 = "";
            if (comboBox2.Text != "íåò")
            {
                add_sql2 = " and ( TR_TYPE = '" + comboBox2.Text + "' ) ";
            }


            string strSQL = " select ID , NUM, TR_TYPE, MARKA, REF_REJIM , INT2BOOL( WORKING_NOW) , PALLETS  from RABAEV.RRL_TR_VEHICLE where 1=1 " + add_sql + add_sql2;
            fill_view_MINI_WMS(dataGridView1, strSQL, 7);
        }

        private void dataGridView1_KeyPress(object sender, KeyPressEventArgs e)
        {
           

        }

        private void dataGridView1_KeyDown(object sender, KeyEventArgs e)
        {
            Keys k =e.KeyCode;
          
            if (  k == Keys.Enter  )
            { 
                button1_Click( null , null);
            }
        }
    }
}