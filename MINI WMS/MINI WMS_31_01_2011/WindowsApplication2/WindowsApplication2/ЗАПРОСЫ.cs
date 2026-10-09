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
    public partial class ЗАПРОСЫ : Form
    {
        public string Header_Text="";
        public string WMS_CONNECTION_STRING_INST;
        public List<Dictionary<string, object>> res = null;
        public object[] CHOOSE= new object[0];
        public string sSQL="";
        public string search_text="";
        public int current_column=-1;
        public int current_row=-1;
        public Point Default_cell = new Point(0,0);
        public List<string> SubQueries = new List<string>();

        private void fill_view_MINI_WMS(DataGridView dgv1, string strSQL )
        {
            dgv1.Rows.Clear();
            long m_count = 0;
            if (res == null)
            {
                OracleCommand ora_com = new OracleCommand();
                ora_com.CommandText = strSQL;
                
                try
                {
                    OracleConnection ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                    ora_conn.Open();
                    ora_com.Connection = ora_conn;
                    OracleDataReader ora_reader = ora_com.ExecuteReader();
                    bool first = true;

                    while (ora_reader.Read())
                    {
                        object[] values1 = new object[ora_reader.FieldCount];
                        for (int yy = 0; yy < ora_reader.FieldCount; yy++)
                        {
                            if (first)
                            {
                                DataGridViewColumn dgvc = new DataGridViewColumn();

                                DataGridViewCell cell = new DataGridViewTextBoxCell();
                                cell.Style.BackColor = Color.Wheat;

                                dgvc.CellTemplate = cell;

                                dgvc.HeaderText = ora_reader.GetName(yy);
                                dgvc.Name = ora_reader.GetName(yy);
                                dgvc.AutoSizeMode = DataGridViewAutoSizeColumnMode.AllCells;
                                dgv1.Columns.Add(dgvc);
                            }
                            values1[yy] = ora_reader.GetValue(yy).ToString();
                        }



                        dgv1.Rows.Add(values1);
                        m_count++;
                        first = false;
                    }

                    ora_reader.Close();
                    ora_conn.Close();
                }
                catch (Exception Ex)
                {
                    MessageBox.Show(" f341 " + Ex.Message);
                }

            }
            else
            {
                #region Показываем таблицу

                bool first = true;
                foreach (Dictionary<string, object> roww in res)
                {

                    object[] values1 = new object[roww.Count];
                    int yy = 0;
                    foreach (string kkey in roww.Keys)
                    {
                        if (first)
                        {
                            DataGridViewColumn dgvc = new DataGridViewColumn();
                            DataGridViewCell cell = new DataGridViewTextBoxCell();
                            cell.Style.BackColor = Color.Wheat;
                            dgvc.CellTemplate = cell;
                            dgvc.HeaderText = kkey;
                            dgvc.Name = kkey;
                            dgvc.AutoSizeMode = DataGridViewAutoSizeColumnMode.AllCells;
                            dgv1.Columns.Add(dgvc);
                        }
                        values1[yy] = roww[kkey];
                        yy++;
                    }



                    dgv1.Rows.Add(values1);
                    m_count++;
                    first = false;


                    #endregion
                }
            }

            if (dgv1.Columns.Count>=1)
            dgv1.Columns[0].ToolTipText = m_count.ToString() + " = количество записей";
            

        }



        public ЗАПРОСЫ()
        {
            InitializeComponent();
        }

        private void ЗАПРОСЫ_Load(object sender, EventArgs e)
        {
            if (Header_Text != "")
            {
                this.Text = Header_Text;
            }
            fill_view_MINI_WMS(dataGridView1, sSQL);
            if ((Default_cell != null) && (dataGridView1.Rows.Count > Default_cell.Y))
            {
                dataGridView1.CurrentCell = dataGridView1.Rows[Default_cell.Y].Cells[Default_cell.X];
            }
        }

        private void grid_2_excel(DataGridView dgv)
        {

            try
            {

                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                oExcelApp.Workbooks.Add("");

                long pos = 0;
                foreach (DataGridViewColumn dgvc in dgv.Columns)
                {
                    pos++;
                    oExcelApp.Cells[1, pos] = dgvc.HeaderText;
                }

                long pos2 = 1;
                foreach (DataGridViewRow dr in dgv.Rows)
                {
                    pos2++;
                    pos = 0;
                    foreach (DataGridViewCell dgvc2 in dr.Cells)
                    {
                        pos++;
                        oExcelApp.Cells[pos2, pos] = dgvc2.Value.ToString().Replace( '=' , '#'  );
                    }
                }
                MessageBox.Show("Данные выгружены в Excel");
            }
            catch (Exception ex)
            {
                MessageBox.Show("rtg " + ex.Message);
            }


        }


        private void button1_Click(object sender, EventArgs e)
        {

            if (this.dataGridView1.CurrentRow == null)
            {
                MessageBox.Show("Не выбрана строка!");
                return;
            }
            
            this.CHOOSE = new object[this.dataGridView1.CurrentRow.Cells.Count] ;
            int pos=0;
            foreach (DataGridViewCell c in this.dataGridView1.CurrentRow.Cells)
            {
                this.CHOOSE[pos] = c.Value;
                pos++;
            }

            this.Close();

        }

        private void button2_Click(object sender, EventArgs e)
        {
            this.CHOOSE = new object[0];
            this.Close();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView1);
        }

        private void dataGridView1_SelectionChanged(object sender, EventArgs e)
        {

            Dictionary< string , double > vals =  new Dictionary<string,double>();

            foreach( DataGridViewRow dr in dataGridView1.Rows )
            {
                for (int i = 0; i < dataGridView1.ColumnCount; i++)
                {
                    if (dr.Cells[i].Selected)
                    {
                        try
                        {
                            vals[dr.Cells[i].OwningColumn.HeaderText] = vals[dr.Cells[i].OwningColumn.HeaderText] + Convert.ToDouble(dr.Cells[i].Value);
                        }
                        catch (Exception ex)
                        {
                            try
                            {
                                vals[dr.Cells[i].OwningColumn.HeaderText] = 0 + Convert.ToDouble(dr.Cells[i].Value);
                            }catch(Exception ex2)
                            {
                                vals[dr.Cells[i].OwningColumn.HeaderText] = 0;
                            }
                        }
                    }

                }

            }
            label1.Text = "";
            foreach (string key in vals.Keys)
            {
                label1.Text = label1.Text + key + " = "+vals[key].ToString() + ";";
            }

        }

        private void dataGridView1_KeyPress(object sender, KeyPressEventArgs e)
        {
            if ( (current_column >= 0 ) && ( current_row >=0 ) )
            {

                if (e.KeyChar != '\b')
                {
                    search_text = search_text + e.KeyChar;
                }
                else {
                    if (search_text.Length > 0)
                    {
                        search_text = search_text.Substring(0, search_text.Length - 1);
                    }
                }


                #region ПОИСК
                label2.Text = search_text;
                if (search_text.Length == 0) return;
                for (int y = current_row+1; y<dataGridView1.Rows.Count ;y++  )
                {

                    if (dataGridView1.Rows[y].Cells[current_column] != null)
                    {
                        string s = dataGridView1.Rows[y].Cells[current_column].Value.ToString().ToUpper();
                        
                        if(s.IndexOf( search_text.ToUpper() )!=-1)
                        {
                            dataGridView1.CurrentCell = dataGridView1.Rows[y].Cells[current_column];
                            current_row = y;
                            return;
                        }
                    }
                }
                for (int y = 0; y < current_row; y++)
                {
                    if (dataGridView1.Rows[y].Cells[current_column] != null)
                    {
                        string s = dataGridView1.Rows[y].Cells[current_column].Value.ToString().ToUpper();

                        if (s.IndexOf(search_text.ToUpper()) != -1)
                        {
                            dataGridView1.CurrentCell = dataGridView1.Rows[y].Cells[current_column];
                            current_row = y;
                            return;
                        }
                    }
                }
                #endregion

            }
        }

        private void dataGridView1_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode== Keys.Enter)
            { 
                button1_Click(null, null );
                return;
            }

            if (e.KeyCode== Keys.Escape)
            {
                button2_Click(null, null);
                return;
            }
        }

        private void dataGridView1_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            if (current_column != e.ColumnIndex)
            {

                current_column = e.ColumnIndex;
                search_text = "";
            }

              if(  current_row!=e.RowIndex)
              {
                  current_row = e.RowIndex;
              }

        }

   

        private void dataGridView1_MouseDoubleClick(object sender, MouseEventArgs e)
        {

            if (this.SubQueries == null) return;
            if (this.SubQueries.Count == 0) { return; }

            ЗАПРОСЫ q = new ЗАПРОСЫ();
            q.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
            
            int i = 0;
            foreach(string s in  this.SubQueries)
            {
                string s2 = s;
                i++;
                if(i>1)
                    q.SubQueries.Add(s2);
                else{
                    foreach (DataGridViewCell dc in dataGridView1.CurrentRow.Cells)
                    {
                        s2 = s2.Replace("[" + dc.OwningColumn.Name + "]", dc.Value.ToString());
                    }
                    q.sSQL = s2;
                }
            }
            
            q.Show();

        }






    }
}