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
using PPage2;
using System.Collections;

namespace WindowsApplication2
{
    public partial class ЗАПРОСЫ : Form
    {
        public string Header_Text="";
        public List<string> print_header_labels = new List<string>();
        public List<string> print_footer_labels = new List<string>();
        public bool print_labels_on_every_page = true;

        public List<int> width_of_print_columns = new List<int>();
        public Dictionary<string, string> print_table_column_styles = new Dictionary<string, string>();

        public Form1 _parent=null;
        public string WMS_CONNECTION_STRING_INST;
        public List<Dictionary<string, object>> res = null;
        public object[] CHOOSE= new object[0];
        public string sSQL="";
        public string search_text="";
        public int current_column=-1;
        public int current_row=-1;
        public Point Default_cell = new Point(0,0);
        public List<string> SubQueries = new List<string>();
        public Dictionary<string, string> ИменованныеЗапросы = new Dictionary<string, string>();
        private Dictionary<string, ToolStripMenuItem> menu_items = new Dictionary<string, ToolStripMenuItem>();

        List<PPage> PPages = new List<PPage>();
        public OracleConnection ora_conn = null;

        public string pivot_rowfields; //row fields separated by comma
        public string pivot_columnfield; //one column field
        public string pivot_function; //aggregate function ('SUM','AVG','COUNT','MIN','MAX')
        public string pivot_functionfield; //field for aggregate function
        public int repeat_time_in_seconds = 0;
        public bool hide_panel = false;
        public bool show_itogo_rows = false;
        public bool show_itogo_cols = false;


        // Условия мигания и подсветки. 
        public Dictionary<string, Color> flicker_conditions = new Dictionary<string, Color>();

        private void fill_view_MINI_WMS(DataGridView dgv1, string strSQL2 )
        {

            string strSQL = strSQL2;
            dgv1.Rows.Clear();
            long m_count = 0;
            double itogo_row_sum = 0;
            long last_added_row=0;
            Dictionary<long, string> m_headers = new Dictionary<long, string>();

            if (res == null)
            {
                OracleCommand ora_com = new OracleCommand();
                ora_com.CommandText = strSQL;
                
                try
                {
                    if (ora_conn == null)
                    {
                        if (_parent != null)
                        {
                            ora_conn = _parent.get_wms_connection();
                        }
                        else
                        {
                            ora_conn = new OracleConnection();
                            ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                            ora_conn.Open();
                        }
                    }

                    ora_com.Connection = ora_conn;

                    if (this.pivot_rowfields != "" && _parent!=null) // Сводная таблица
                    {
                        string str_p = strSQL.Replace( "'" , "''" );
                        string h = " select ( pk_pivot.PivotSQL( '" + str_p + "' , '" + pivot_rowfields + "'  , '" + pivot_columnfield + "'  , '" + pivot_function + "' , '" + pivot_functionfield + "'  ) ) from dual  ";
                        string g= _parent.obj2str( _parent.get_wms_sql_result_single( h ));
                        if (g != "")
                        {
                            strSQL = g;
                            ora_com.CommandText = strSQL;
                           // Запрос2.Text = strSQL;
                        }
                    }

                    OracleDataReader ora_reader = ora_com.ExecuteReader();
                    bool first = true;
//                    Dictionary<int, double> itogo_colls_sum = new Dictionary<int, double>();
                    object[] itogo_colls_sum = new object[1]; ;
                    Dictionary<long, double> itogo_rows_sum = new Dictionary<long, double>();
                    while (ora_reader.Read())
                    {
                        if (first)
                        {
                            itogo_colls_sum = new object[ora_reader.FieldCount];
                        }

                        object[] values1 = new object[ora_reader.FieldCount];
                        for (int yy = 0; yy < ora_reader.FieldCount; yy++)
                        {
                            #region ПЕРВЫЙ РАЗ
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
                               // if(show_itogo_cols){
                               //     itogo_colls_sum[yy]=0;
                               // }
                                m_headers[m_headers.Count ] = ora_reader.GetName(yy);

                            }
                            #endregion 

                            #region ЗАНЕСЕНИЕ ДАННЫХ
                            try
                            {
                                
                                    values1[yy] = ora_reader.GetValue(yy);
                                    if ((show_itogo_cols || show_itogo_rows ) && _parent != null)
                                    {
                                        string t=values1[yy].GetType().FullName;
                                        if ( t == "System.Int16" || t == "System.Int32" || t == "System.Int64" || t == "System.Double" || t == "System.Decimal" )
                                        {
                                            double dd= _parent.obj2double(values1[yy]);
                                            if (show_itogo_cols)
                                            itogo_colls_sum[yy] = _parent.obj2double(itogo_colls_sum[yy]) + dd;

                                            if (show_itogo_rows)
                                            {
                                                if (!itogo_rows_sum.ContainsKey(last_added_row))
                                                    itogo_rows_sum[last_added_row] = dd;
                                                else
                                                    itogo_rows_sum[last_added_row] = itogo_rows_sum[last_added_row] + dd;

                                            }

                                        }

                                    }

                            }
                            catch { }
                            #endregion 

                        }



                        last_added_row=dgv1.Rows.Add(values1);
                        
                        if (flicker_conditions!=null)
                            if (flicker_conditions.Count>0)
                                for (long ii = 0; ii<values1.Length  ; ii++ )
                                {// если 
                                    string key= m_headers[ii] + "=" + values1[ii].ToString();
                                    if (flicker_conditions.ContainsKey(key))
                                    {
                                        for (long iii = 0; iii < values1.Length ; iii++ )
                                        dgv1.Rows[(int)last_added_row].Cells[(int)iii].Style.BackColor = flicker_conditions[key];
                                    }
                                }

                        last_added_row++;
                        m_count++;
                        first = false;
                    }

                    if (last_added_row > 0)
                    if (show_itogo_cols && _parent != null)
                    {
                       int r= dgv1.Rows.Add();
                       dgv1.Rows[r].Cells[0].Value = "Итого";
                       dgv1.Rows[r].Cells[0].Style.BackColor = Color.BlueViolet;
                       for (int i = 0; i < itogo_colls_sum.Length; i++)
                       {
                           if (itogo_colls_sum[i] != null)
                           {
                               dgv1.Rows[r].Cells[i].Value = itogo_colls_sum[i];
                               dgv1.Rows[r].Cells[i].Style.BackColor = Color.Khaki;
                           }
                       }
                    }

                    if (last_added_row>0)
                    if (show_itogo_rows && _parent != null)
                    {
                        double itogo_itogo = 0;
                        int cc = dgv1.Columns.Add("ИТОГО", "ИТОГО");
                        dgv1.Columns[cc].AutoSizeMode = DataGridViewAutoSizeColumnMode.AllCells;

                        foreach (long ck in itogo_rows_sum.Keys)
                        {
                            if ( itogo_rows_sum[ck] != null )
                            {
                                dgv1.Rows[(int)ck].Cells[cc].Value = itogo_rows_sum[ck];
                                itogo_itogo = itogo_itogo + _parent.obj2double(itogo_rows_sum[ck]);
                                dgv1.Rows[(int) ck].Cells[cc].Style.BackColor = Color.Khaki;
                            }
                        }

                        if (show_itogo_cols)
                        {
                            dgv1.Rows[(int)itogo_rows_sum.Keys.Count ].Cells[cc].Value = itogo_itogo;
                        }
                    }

                    

                    ora_reader.Close();
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


        private void pd_PrintPage_SBOR(object sender, PrintPageEventArgs ev)
        {
            float leftMargin = ev.MarginBounds.Left;
            float topMargin = ev.MarginBounds.Top;


            ev.HasMorePages = false;

            PPage _page_2_print = PPages[PPages.Count - 1];
            _page_2_print.print(ev);


            PPages.Remove(_page_2_print);

            if (PPages.Count >= 1)
            {
                ev.HasMorePages = true;
            }

        }


        public void set_table( Dictionary< object ,Dictionary<object, object>>  m_table)
        {
            this.res = new List<Dictionary<string, object>>();
            foreach( object key in m_table.Keys  )
            {
                Dictionary<string, object> row1= new Dictionary<string,object>();
                foreach (object key2 in m_table[key].Keys)
                {
                    row1[key2.ToString()] = m_table[key][key2];
                }
                this.res.Add( row1 );
            }
        
        }

        public ЗАПРОСЫ()
        {
            InitializeComponent();
        }

        private void ЗАПРОСЫ_Load(object sender, EventArgs e)
        {
            if (_parent != null)
            {
                if (!_parent.has_right("CUSTOM_SQL"))
                {
                    hide_panel = true;
                }
            }


          //  contextMenuStrip1.I

            if( hide_panel )
            {
                tabControl1.Visible = false;
            }

            if (Header_Text != "")
            {
                this.Text = Header_Text;
            }

            
            fill_view_MINI_WMS(dataGridView1, sSQL);
            

            if ((Default_cell != null) && (dataGridView1.Rows.Count > Default_cell.Y))
            {
                dataGridView1.CurrentCell = dataGridView1.Rows[Default_cell.Y].Cells[Default_cell.X];
            }

            Запрос2.Text = sSQL; 

            if( search_text!="" )
            dataGridView1_KeyPress(null, null);

            if (repeat_time_in_seconds > 0)
            {
                timer1.Interval = 1000 * repeat_time_in_seconds;
                timer1.Enabled = true;
            }


            #region MENU
           
            int i=this.contextMenuStrip1.Items.Count;
            foreach (string zapros_name in ИменованныеЗапросы.Keys)
            {
                i++;
                ToolStripMenuItem m_item = new ToolStripMenuItem();


                m_item.Name = zapros_name;
                m_item.Size = new System.Drawing.Size(218, 22);
                m_item.Text = zapros_name;
                m_item.Click += new System.EventHandler(this.menu_event_catcher);
                this.contextMenuStrip1.Size = new System.Drawing.Size(219, 26 * i);


                this.contextMenuStrip1.Items.Add(m_item);



            }



            #endregion

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
                        if (dgvc2.Value != null)
                        {
                            oExcelApp.Cells[pos2, pos] = dgvc2.Value.ToString().Replace('=', '#');
                        }
                        else {
                            oExcelApp.Cells[pos2, pos] = "";
                        }
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
            if (_parent != null)
            {
                _parent.grid_2_excel(dataGridView1);
            }
            else
            {
                grid_2_excel(dataGridView1);
            }

        }

        private void dataGridView1_SelectionChanged(object sender, EventArgs e)
        {

            Dictionary< string , double > vals =  new Dictionary<string,double>();

            foreach( DataGridViewRow dr in dataGridView1.Rows )
            {
                for (int i = 0; i < dataGridView1.ColumnCount; i++)
                {
                    if (dr.Cells[i].Selected &&  dr.Cells[i].Value!=null )
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
                if (e != null)
                {
                    if (e.KeyChar != '\b')
                    {
                        search_text = search_text + e.KeyChar;
                    }
                    else
                    {
                        if (search_text.Length > 0)
                        {
                            search_text = search_text.Substring(0, search_text.Length - 1);
                        }
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
                
                if (e.ColumnIndex != 0 && current_column!=0) search_text = "";
                current_column = e.ColumnIndex;
                

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
            if (this.WMS_CONNECTION_STRING_INST != "")
            {
                q.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
            }
            else {
                
            }

            q._parent = this._parent;
            if (_parent!=null)
            q.ora_conn = _parent.get_wms_connection();

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
                        if (dc.Value!= null )
                        s2 = s2.Replace("[" + dc.OwningColumn.Name + "]", dc.Value.ToString());
                    }
                    q.sSQL = s2;
                }
            }
            
            q.Show();

        }

        public void Print()
        {


            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ
            int _X = 10, _Y = 80;
            #endregion

            #region ПОДГОТОВКА ПЕЧАТИ

            string strSQL2 = this.sSQL;
            long in_page = 60;
            long in_first_page = in_page;



            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = _parent.get_wms_connection();
            ora_com.CommandText = strSQL2;
            OracleDataReader ora_read3 = ora_com.ExecuteReader();
            

            
            


            #region СОЗДАНИЕ СТРАНИЦЫ
            PPage _page = new PPage();
            _page.column_styles = this.print_table_column_styles;
            _page.start_point_4_table.X = 10;
            _page.start_point_4_table.Y = 70;
            _page.font_size_4_table = 12;
            _page.height_of_column = 24;


 //                   public List<string> print_header_labels = new List<string>();
 //       public List<string> print_footer_labels = new List<string>();
//        public bool print_labels_on_every_page = true;

            in_first_page = in_first_page - (print_footer_labels.Count + print_header_labels.Count);
            int l_header_iterator=0;
            foreach( string it in print_header_labels )
            {
                l_header_iterator++;
                _page.labels.Add(new PPage.PLabel( it , new Point(10, _page.font_size_4_table*l_header_iterator + 24 ), _page.font_size_4_table));

                _page.start_point_4_table.Y = _page.font_size_4_table * (l_header_iterator+4) ;
            }
    
            foreach( string it in print_footer_labels )
            {
                l_header_iterator++;
                _page.labels.Add(new PPage.PLabel( it , new Point(10,600-( _page.font_size_4_table*l_header_iterator ) ), _page.font_size_4_table));            
            }


            //_page.labels.Add(new PPage.PLabel("Лист инвентаризации пустых паллето-мест", new Point(10, 10), 24));
            //_page.labels.Add(new PPage.PLabel("Пройдите по ячейкам согласно списка. сканируйте штрих-код ячейки, затем штрих-код паллета, ", new Point(10, 36), 12));
            //_page.labels.Add(new PPage.PLabel("Если ячейка пустая, нажмите кнопку 'NO_PALL'. Затем нажмите 'Подтвертить перемещение' на сканнере.", new Point(10, 50), 12));
            //_page.labels.Add(new PPage.PLabel("Подпись ответственного лица:  ________________(_______________)", new Point(10, 1110), 22));

            for( int i=0 ; i<ora_read3.FieldCount ; i++ )
            {
                string column_name = ora_read3.GetName(i);
                int column_width = 7;
                if (width_of_print_columns.Count > i)
                { 
                    column_width = width_of_print_columns[i];
                }
                _page.add_column(column_name, "string", column_name, column_width);
            }

            #endregion

            _page.labels.Add(new PPage.PLabel("стр. 1"  , new Point(750, 10), 12));
            _page.labels.Add(new PPage.PLabel(this.Header_Text, new Point(10, 10), 24));
           

            


            long КОЛИЧЕСТВО_ПАЛЛЕТ1 = 0;
            while (ora_read3.Read())
            {
                Dictionary<string, string> _row = new Dictionary<string, string>();
 
                for (int i = 0; i < ora_read3.FieldCount; i++)
                {
                    string column_name = ora_read3.GetName(i);
                    _row[column_name] = _parent.obj2str(ora_read3.GetValue(i));
                }

                _page.add_row(_row);
                КОЛИЧЕСТВО_ПАЛЛЕТ1++;

                if (КОЛИЧЕСТВО_ПАЛЛЕТ1 >= in_first_page)
                {
                    in_first_page = in_page;
                    КОЛИЧЕСТВО_ПАЛЛЕТ1 = 0;
                    PPages.Add(_page);
                    #region СОЗДАНИЕ СТРАНИЦЫ
                    _page = new PPage();
                    _page.column_styles = this.print_table_column_styles;
                    _page.start_point_4_table.X = 10;
                    _page.start_point_4_table.Y = 48;
                    _page.font_size_4_table = 12;

                    _page.labels.Add(new PPage.PLabel(this.Header_Text, new Point(10, 10), 24));
                    _page.labels.Add(new PPage.PLabel( "стр. "+(PPages.Count+1).ToString(), new Point(700, 10), 12));
                    for (int i = 0; i < ora_read3.FieldCount; i++)
                    {
                        string column_name = ora_read3.GetName(i);
                        int column_width = 7;
                        if (width_of_print_columns.Count > i)
                        {
                            column_width = width_of_print_columns[i];
                        }
                        _page.add_column(column_name, "string", column_name, column_width);
                    }

                    #endregion
                }
                
            }

            if (КОЛИЧЕСТВО_ПАЛЛЕТ1 != 0)
            {
                PPages.Add(_page);
            }

            #endregion

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {
                pd.DefaultPageSettings.Landscape = false;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion


        }

        private void Переделать_запрос_Click(object sender, EventArgs e)
        {
            dataGridView1.Columns.Clear();
            sSQL=Запрос2.Text  ; 
            fill_view_MINI_WMS(dataGridView1, sSQL);

        }

        private void timer1_Tick(object sender, EventArgs e)
        {

            if (Header_Text != "")
            {
                DateTime time = DateTime.Now;
                this.Text = Header_Text+" Обновление "+time.ToLongTimeString();
            }
            Переделать_запрос_Click(null, null);
        }

        private void перевестиДанныеВExcelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView1);
        }

        private void button4_Click(object sender, EventArgs e)
        {

        }

        private void СкрытьПанель_Click(object sender, EventArgs e)
        {
            tabControl1.Visible = false;
        }

        private void menu_event_catcher(object sender, EventArgs e)
        {
            string name = ((System.Windows.Forms.ToolStripMenuItem)(sender)).Name;
            if (ИменованныеЗапросы.ContainsKey(name))
            {
                string SQL = ИменованныеЗапросы[name];
                #region 4

                ЗАПРОСЫ q = new ЗАПРОСЫ();
                q._parent = this._parent;
                if (_parent != null)
                    q.ora_conn = _parent.get_wms_connection();

                string s2 = SQL;
                foreach (DataGridViewCell dc in dataGridView1.CurrentRow.Cells)
                {
                    if (dc.Value != null)
                        s2 = s2.Replace("[" + dc.OwningColumn.Name + "]", dc.Value.ToString());
                }

                q.sSQL = s2;
                q.Show();

                #endregion
            }
            else {
                MessageBox.Show("Нет запроса "+name);
            }

        }





    }
}