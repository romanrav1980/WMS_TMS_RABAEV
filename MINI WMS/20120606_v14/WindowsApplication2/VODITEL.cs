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
    public partial class VODITEL : Form
    {

        public string WMS_CONNECTION_STRING_INST;
        public string CHOOSE;
        public int CHOOSE_ID;
        public string CHOOSE_NUM="";
        public string Filter_FIO;
        public string Filter_NUM;
        public Form1 _pparent;

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
                MessageBox.Show(" f342 " + Ex.Message);
            }
            dgv1.Columns[0].ToolTipText = m_count.ToString() + " = количество записей";
            // dgv1.Columns[0].HeaderText = dgv1.Columns[0].HeaderText + "[" + m_count.ToString() +"]";

        }


        public VODITEL( Form1 _pr )
        {
            _pparent = _pr;
            InitializeComponent();
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void button2_Click(object sender, EventArgs e)
        {

            bool EDIT_INNER_TT = false , EDIT_IMPORT_TT=false;

            if(_pparent.has_right("EDIT_IMPORT_TT"))
            {
                EDIT_IMPORT_TT=true;
            }

            if (_pparent.has_right("EDIT_INNER_TT"))
            {
                EDIT_INNER_TT = true ;
            }


            string add_sql1 = "";
            if (НОМЕР_МАШ.Text != "")
            {
                add_sql1 = " and TRANSPORT_NUM like '%" + НОМЕР_МАШ.Text + "%' "; 
            }

            string add_sql2 = "";
            if (ФИО.Text != "")
            {
                add_sql2 = " and  ( ( F like '%" + ФИО.Text + "%'  ) or (  Concat(Concat(F , ' ') , Concat( Concat(I,' ') , O ) ) = '" + ФИО.Text + "'  ) )  ";
            }
            
            string strSQL = " select ID , F, I, O,  INT2BOOL( DELETED) , INT2BOOL( SOBSTVENNYY) ,"+
                "  TRANSPORT_NUM , TEL , ADDR , DOVERENNOST_OT , PASSPORT ,  TRANSPORT_TASK.voditel_get_tabel_numb(ID) , "+
                " TRANSPORT_TASK.voditel_get_inn(ID)     from RABAEV.RRL_TR_VODITEL  where 1=1  " + add_sql1 + add_sql2;
            fill_view_MINI_WMS(dataGridView1, strSQL, 13);

        }

        private void VODITEL_Load(object sender, EventArgs e)
        {

            try
            {
                //Filter_company.Items.Add("Выберите компанию");
                ДоверенностьОт.Items.Clear();
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
                    ((DataGridViewComboBoxColumn)dataGridView1.Columns[9]).Items.Add(ora_read.GetValue(0).ToString());
                    //ДоверенностьОт.Items.Add(ora_read.GetValue(0).ToString());
                }


            }
            catch (Exception ex) { MessageBox.Show(ex.Message); }



            if (Filter_FIO != null)
            {
                if (Filter_FIO != "")
                {
                    ФИО.Text = Filter_FIO;
                }
            }

            if (Filter_NUM != null)
            {
                if (Filter_NUM != "") {
                    НОМЕР_МАШ.Text = Filter_NUM;
                }
            }

            button2_Click(null, null);
        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

              // ===================================================================================================
            OracleCommand ora_com;
            try
            {

                long    ID1              = 0;
                string  F1               ="";
                string  I1               ="";
                string  O1               ="";
                long  DELETED1           = 0;
                long  SOBSTVENNYY1       = 0;
                string  PASSPORT1        ="";
                string  DOVERENNOST_OT1  ="";
                string  TRANSPORT_NUM1   ="";
                string  ADDR1            ="";
                string  TEL1             ="";
                string inn = "";
                string tab_nom = "";

                OracleConnection ora_con = new OracleConnection();
                ora_con.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_con.Open();

                DataGridViewRow dr = this.dataGridView1.CurrentRow;

                ID1 = Convert.ToInt32(dr.Cells[0].Value);

                if (dr.Cells[6].Value!=null)
                TRANSPORT_NUM1 = (dr.Cells[6].Value.ToString());

            if (dr.Cells[7].Value != null)
                TEL1  = (dr.Cells[7].Value.ToString());

            if (dr.Cells[8].Value != null)
                ADDR1 = (dr.Cells[8].Value.ToString());

            if (dr.Cells[9].Value != null)
                DOVERENNOST_OT1 = (dr.Cells[9].Value.ToString());

            if (dr.Cells[10].Value != null)
                PASSPORT1 = (dr.Cells[10].Value.ToString());

            if (dr.Cells[1].Value!=null)
                F1 = ( dr.Cells[1].Value.ToString() );
            
            if (dr.Cells[2].Value != null)
                I1 = (dr.Cells[2].Value.ToString());
            
            if (dr.Cells[3].Value != null)
                O1 = (dr.Cells[3].Value.ToString());

                if (Convert.ToBoolean(dr.Cells[4].Value) == true)
                { DELETED1 = 1; } else { DELETED1 = 0; }

                if (Convert.ToBoolean(dr.Cells[5].Value) == true)
                { SOBSTVENNYY1 = 1; }  else { SOBSTVENNYY1 = 0; }


                tab_nom = _pparent.obj2str(dr.Cells[11].Value);
                inn = _pparent.obj2str(dr.Cells[12].Value);


                #region ИЗМЕНЕНИЕ МАШИНЫ
                if ((e.ColumnIndex == 6) && (TRANSPORT_NUM1 != ""))
                { // Если изменилась машина
                    OracleCommand ora_com2 = new OracleCommand();
                    ora_com2.Connection = ora_con ;
                    ora_com2.CommandText = " select NUM from RRL_TR_VEHICLE where NUM like '%" + TRANSPORT_NUM1 + "%' ";
                    int count_of_tr = 0;
                    OracleDataReader ora_read2 = ora_com2.ExecuteReader();
                    string TRANSPORT_NUM2 = TRANSPORT_NUM1;
                    while (ora_read2.Read())
                    {
                        count_of_tr++;
                        TRANSPORT_NUM2 = ora_read2.GetValue(0).ToString();
                    }
                    if (count_of_tr != 1)
                    { // открываем форму для выбора транспорта 

                        TRANSPORT ftr = new TRANSPORT();
                        ftr.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
                        ftr.NUM_FILTER = TRANSPORT_NUM1;
                        ftr.ShowDialog();

                        string h = ftr.CHOOSE;
                        if (h == null)
                            return;
                        if (h == "")
                            return;
                        dr.Cells[6].Value = h;
                        TRANSPORT_NUM1 = h;

                    }
                    else
                    {
                        TRANSPORT_NUM1 = TRANSPORT_NUM2;
                    }

                }
                #endregion


                ora_com = new OracleCommand();
                ora_com.Connection = ora_con;
                ora_com.CommandText = "RABAEV.ADD_RRL_VOD";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("ID1", OracleType.Int32).Value = ID1;
                ora_com.Parameters.Add("F1", OracleType.VarChar).Value = F1;
                ora_com.Parameters.Add("I1", OracleType.VarChar).Value = I1;
                ora_com.Parameters.Add("O1", OracleType.VarChar).Value = O1;
                ora_com.Parameters.Add("DELETED1", OracleType.Int32).Value = DELETED1;
                ora_com.Parameters.Add("SOBSTVENNYY1", OracleType.Int32).Value = SOBSTVENNYY1;
                ora_com.Parameters.Add("PASSPORT1", OracleType.VarChar).Value = PASSPORT1;
                ora_com.Parameters.Add("DOVERENNOST_OT1", OracleType.VarChar).Value = DOVERENNOST_OT1;
                ora_com.Parameters.Add("TRANSPORT_NUM1", OracleType.VarChar).Value = TRANSPORT_NUM1;
                ora_com.Parameters.Add("ADDR1", OracleType.VarChar).Value = ADDR1;
                ora_com.Parameters.Add("TEL1", OracleType.VarChar).Value = TEL1;
                ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                   
                int rowsAffected = ora_com.ExecuteNonQuery();
                dr.Cells[0].Value = ora_com.Parameters["ID"].Value;



                if (tab_nom != "" && inn != "")
                {
                    Dictionary<string, object> values = new Dictionary<string, object>();
                    values["vod_id"] = ID1;
                    values["tabel_numb1"] = tab_nom;
                    values["inn1"] = inn;
                    object ret = _pparent.wms_get_spfunction_value2("TRANSPORT_TASK.voditel_set_tabel_numb", values, OracleType.Int32, 0);
                }

            }catch( Exception ex )
            {
                MessageBox.Show(ex.Message );
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                if (this.dataGridView1.CurrentRow == null)
                {
                    MessageBox.Show("Не выбран водитель!");
                    return;
                }
                this.CHOOSE_ID = Convert.ToInt32(this.dataGridView1.CurrentRow.Cells[0].Value);
                this.CHOOSE = (this.dataGridView1.CurrentRow.Cells[1].Value.ToString()) + " " +
                    (this.dataGridView1.CurrentRow.Cells[2].Value.ToString()) + " " +
                    (this.dataGridView1.CurrentRow.Cells[3].Value.ToString())
                    ;
                this.CHOOSE_NUM = this.dataGridView1.CurrentRow.Cells[6].Value.ToString();
                this.Close();
            }catch(Exception ex)
            {

            }
        }

        private void dataGridView1_KeyDown(object sender, KeyEventArgs e)
        {
            Keys k = e.KeyCode;

            if (k == Keys.Enter)
            {
                button1_Click(null, null);
            }
        }

        private void splitContainer1_Panel2_Paint(object sender, PaintEventArgs e)
        {

        }

        private void dataGridView1_DataError(object sender, DataGridViewDataErrorEventArgs e)
        {

        }

        private void рейсыДаннойМашиныToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (dataGridView1.CurrentRow == null) return;
            if (dataGridView1.CurrentRow.Cells[0].Value == null) return;

            string vod_id = dataGridView1.CurrentRow.Cells[0].Value.ToString() ;

            string strSQL2 = " SELECT  price Сумма , t.user_id ЛОГИСТ , t.transport МАШИНА , " +
            "    rrl_tt_regions (t.ID),  t.transtype ТИП_ТР  , " +
            " shipment_date ДАТА  " +
            "    FROM rrl_transport_task t  " +
            "   WHERE  t.VODITEL_ID ="+vod_id+" " +
            "  AND t.deleted <> 1 "  +
            "      ";
            _pparent.ShowQuery( strSQL2 , "Рейсы данного авто" );

        }

        private void button3_Click(object sender, EventArgs e)
        {
            _pparent.grid_2_excel(dataGridView1);
        }

        private void закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ВыбратьСтолбцы vs = new ВыбратьСтолбцы();
            vs._parent = _pparent;
            vs.dgv = dataGridView1;
            vs.ShowDialog();

        }
    }
}