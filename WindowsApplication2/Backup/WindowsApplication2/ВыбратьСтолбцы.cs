using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

// using System. ;


namespace WindowsApplication2
{
    public partial class ВыбратьСтолбцы : Form
    {

        public Form1 _parent;
        public DataGridView dgv;

        public ВыбратьСтолбцы()
        {
            InitializeComponent();
        }

        private void OK_Click(object sender, EventArgs e)
        {
           foreach( DataGridViewColumn col in dgv.Columns  )
            col.Visible=false;

            foreach( DataGridViewColumn col in dgv.Columns  )
            {

                if (this.checkedListBox1.CheckedItems.IndexOf(col.HeaderText) != -1)
                    col.Visible = true;


            }

            this.Close();
        }

        private void ВыбратьСтолбцы_Load(object sender, EventArgs e)
        {
            this.checkedListBox1.Items.Clear();
            foreach( DataGridViewColumn col in dgv.Columns  )
            {
                
                this.checkedListBox1.Items.Add( col.HeaderText ,col.Visible );
            }
        }

        private void Закрыть_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void Загрузить_Excel_Click(object sender, EventArgs e)
        {
            
            
            Dictionary< int , string > headers =  new Dictionary<int,string>();
            List<Dictionary<string, string>> values = new List<Dictionary<string, string>>();

            OpenFileDialog ofd = new OpenFileDialog();
            DialogResult dr= ofd.ShowDialog();
            #region  ОТКРЫТИЕ ФАЙЛА EXCEL
            if (dr == DialogResult.OK)
            {
                dataGridView1.Rows.Clear();
                int pos = 1;
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;


                string Filename =  ofd.FileName;



                oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);
                #region Получаем заголовки столбцов
                
                while (_parent.obj2str(((Excel.Range)oExcelApp.Cells[1,pos ]).Value2) != "")
                { 
                    headers[pos]=_parent.obj2str(((Excel.Range)oExcelApp.Cells[1,pos ]).Value2);
                    pos++;
                }
                    

                #endregion

                pos=2;
                
                while (    _parent.obj2str( ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2 ) != "")
                {
                    Dictionary<string, string> vrow = new Dictionary<string, string>();


                    foreach (int key2 in headers.Keys)
                    {
                        vrow[headers[key2]] = _parent.obj2str(((Excel.Range)oExcelApp.Cells[pos, key2]).Value2);
                    }

                    values.Add(vrow);
                    pos++;
                }

            }
            #endregion 


            #region ЗАПОЛНЕНИЕ ТАБЛИЦЫ С РЕЗУЛЬТАТАМИ

            // Dictionary<int, string> headers = new Dictionary<int, string>();
            // List<Dictionary<string, string>> values = new List<Dictionary<string, string>>();
            КлючиСопоставленияСтрок.Items.Clear();
            foreach( int key1 in headers.Keys ){
                dataGridView1.Columns.Add(headers[key1], headers[key1]);
                КлючиСопоставленияСтрок.Items.Add(headers[key1]);
            }

            foreach (Dictionary<string, string> row in values)
            {
                object[] p = new object[row.Count];
                for (int i = 0; i<row.Count ; i++)
                {
                    p[i] = row[dataGridView1.Columns[i].HeaderText];
                }
                    dataGridView1.Rows.Add(p);
            }

            #endregion

            


        }

        private void button1_Click(object sender, EventArgs e)
        {



            if (КлючиСопоставленияСтрок.CheckedItems.Count < 1)
            {
                MessageBox.Show("Выберите ключи сопоставления строк");
                return;
            }
            Dictionary<string, string> keys3 = new Dictionary<string, string>();
            for (int i = 0; i < КлючиСопоставленияСтрок.CheckedItems.Count; i++)
            {
                keys3.Add(КлючиСопоставленияСтрок.CheckedItems[i].ToString(), "");
            }

            Dictionary<string, int> parent_headers = new Dictionary<string, int>(); // Из Имен заголовков в номера колонок родительской таблицы.
            Dictionary<string, int> headers2 = new Dictionary<string, int>(); // Из Имен заголовков в номера колонок таблицы.

            for( int i=0; i< dgv.ColumnCount ;i++ )
            {
                parent_headers[dgv.Columns[i].HeaderText] = i;
            }

            #region Проверяем соответствие заголовков в таблице заголовкам в родительской
            for (int i = 0; i < dataGridView1.ColumnCount; i++)
            {
                if(! parent_headers.ContainsKey( dataGridView1.Columns[i].HeaderText) )
                {
                    MessageBox.Show(" В родительской таблице нет столбца с названием "+ dataGridView1.Columns[i].HeaderText+" ");
                    return;
                }
                headers2[dataGridView1.Columns[i].HeaderText] = i;
            }

            #endregion


                #region Иммитируем ввод с клавиатуры
            int сколько_столбцов_обновлено = 0;


            if (keys3.Keys.Count > 1)
            {
                #region ЕСЛИ КЛЮЧЕЙ БОЛЕЕ 1
                // По всем строкам таблицы с промежуточными данными.
                foreach (DataGridViewRow dr in dataGridView1.Rows)
                {
                    // Находим строку в родительской таблице с таким-же сочетанием ключей
                    //Dictionary<string, string> current_key = new Dictionary<string, string>();
                    Dictionary<string, string> _keys3 = new Dictionary<string, string>();
                    foreach (string key4 in keys3.Keys)
                        _keys3[key4] = _parent.obj2str(dr.Cells[headers2[key4]].Value); // Теперь в данной коллекции содержатся ключи!!!

                    foreach (string key4 in _keys3.Keys)
                        keys3[key4] = _keys3[key4];


                    // Бежим по всем строкам Таблицы , куда вводятся данные.
                    foreach (DataGridViewRow dr2 in dgv.Rows)
                    {
                        bool find = true;
                        foreach (string key5 in keys3.Keys)
                        { // если значение очередной записи ключа совпадает с родительской таблицей, то продолжаем , иначе - ошибка
                            if (find)
                                if (_parent.obj2str(dr2.Cells[parent_headers[key5]].Value) != keys3[key5])
                                {
                                    find = false;
                                }
                        }

                        if (find) // ! Строка найдена !!!!!
                        {// Иммитируем ввод с клавиатуры !!!!!
                            //
                            for (int i = 0; i < dr.Cells.Count; i++)
                            {
                                int column_number_in_parent_table = parent_headers[dataGridView1.Columns[i].HeaderText];
                                string value = _parent.obj2str(dr.Cells[i].Value);
                                dr2.Cells[column_number_in_parent_table].Value = value;
                                сколько_столбцов_обновлено++;
                                if (i == dr.Cells.Count - 1)
                                {
                                    dgv.CurrentCell = dr2.Cells[column_number_in_parent_table];
                                    dgv.BeginEdit(true);
                                    dgv.EndEdit();
                                }
                            }
                        }




                    }
                }
                #endregion
            }
            else
            {
                string Main_Key_name ="";
                foreach (string s in keys3.Keys)
                {
                    Main_Key_name = s;
                }
                #region ЕСЛИ КЛЮЧЕЙ =1 
                // Составляем соответствие 
                Dictionary< string , DataGridViewRow > target_rows =  new Dictionary<string,DataGridViewRow>();

                 foreach (DataGridViewRow dr2 in dgv.Rows)
                 {
                     target_rows[_parent.obj2str(dr2.Cells[parent_headers[Main_Key_name]].Value)] = dr2;                                
                 }

                 foreach (DataGridViewRow dr in dataGridView1.Rows)
                 {

                     string main_key_value = _parent.obj2str(dr.Cells[headers2[Main_Key_name]].Value); // Теперь в данной коллекции содержатся ключи!!!
                     if (main_key_value!="")
                     if (target_rows.ContainsKey(main_key_value))
                     {
                         // Иммитируем ввод с клавиатуры !!!!!
                         //
                         DataGridViewRow dr2 = target_rows[main_key_value];
                         for (int i = 0; i < dr.Cells.Count; i++)
                         {
                             int column_number_in_parent_table = parent_headers[dataGridView1.Columns[i].HeaderText];
                             string value = _parent.obj2str(dr.Cells[i].Value);

                             if (dr2.Cells[column_number_in_parent_table].GetType().FullName != "System.Windows.Forms.DataGridViewCheckBoxCell")
                             {
                                 dr2.Cells[column_number_in_parent_table].Value = value;
                             }
                             else {
                                 dr2.Cells[column_number_in_parent_table].Value = _parent.obj2bool( value );
                             }

                            
                             сколько_столбцов_обновлено++;
                             if (i == dr.Cells.Count - 1)
                             {
                                 dgv.CurrentCell = dr2.Cells[column_number_in_parent_table];
                                 dgv.BeginEdit(true);
                                 dgv.EndEdit();
                             }
                         }
                     }
                 }
                #endregion
            }


            #endregion


                MessageBox.Show("Процедура успешно завершена. Обновлено " + сколько_столбцов_обновлено.ToString()+" столбцов. ");
        
        }

        private void ВыгрузитьРодительскуютаблицувExcel_Click(object sender, EventArgs e)
        {
            _parent.grid_2_excel(dgv);
        }
    }
}
