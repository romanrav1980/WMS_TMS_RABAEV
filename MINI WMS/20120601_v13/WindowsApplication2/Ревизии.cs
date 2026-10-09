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
    public partial class Ревизии : Form
    {
        public Form1 _parent;
        public int initial_revizion_id;
        Dictionary<object, object> modifications = new Dictionary<object, object>();

        public Ревизии()
        {
            InitializeComponent();
        }

        private void ПоказатьРевизию_Click(object sender, EventArgs e)
        {
   
            if ( (НомерРев.Text != "") )
            {
                // НомерРев
                string strSQL = " select  ID , USER_ID, CREATE_DATE,CONDITION , WARE_ID , REV_NAKLAD_ID , SNAPSHOT_BEFORE , SNAPSHOT_AFTER " +
                    " from RABAEV.RRL_REVIZION where ID=" + НомерРев.Text.ToString();

                _parent.fill_view_MINI_WMS(dataGridView1, strSQL, 8);
            }
            else {
                string strSQL = " select  ID , USER_ID, CREATE_DATE,CONDITION , WARE_ID , REV_NAKLAD_ID , SNAPSHOT_BEFORE , SNAPSHOT_AFTER  " +
                    " from RABAEV.RRL_REVIZION  "  ;

                _parent.fill_view_MINI_WMS(dataGridView1, strSQL, 8);
            
            }
   

        }

        private void dataGridView1_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            int current_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
            if (current_id == 0) return;
            string strSQL = "select  RR.ID,RR.CELL , RR.COUNT1, COUNT_KOR, REMARK1 "+
                " , CEL.X , CEL.Y , CEL.Z , RR.ARTICUL1  ,  RR.NUM_OF_PALL , REVIZION.articul_name( RR.ARTICUL1)" +
                " from RABAEV.RRL_REVISION_ROW RR , RRL_CELLS CEL "+
                " where RR.CELL=CEL.CELL and REVISION_ID= " + current_id.ToString() + " order by REVIZION.articul_name( RR.ARTICUL1) ";
            _parent.fill_view_MINI_WMS(dataGridView2, strSQL, 11);


        }

        private void Ревизии_Load(object sender, EventArgs e)
        {
            if (НомерРев.Text == "")
            {
                НомерРев.Text = initial_revizion_id.ToString();

            }
        }

        private void dataGridView2_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

            string cell="";
            int revision_id1 = 0;
            int revision_row_id1 = 0;
            double count_kor = 0;
            string user_id3 = "";
            bool Обработать_собрытие_изменения_штук = false;

            if (dataGridView1.CurrentRow == null)
            { return; }

            if (dataGridView2.CurrentRow == null)
            { return; }
            

            revision_id1= _parent.obj2int32( dataGridView1.CurrentRow.Cells[0].Value );
            revision_row_id1 = _parent.obj2int32(dataGridView2.CurrentRow.Cells[0].Value);

            if (e.ColumnIndex == 3){ 

            #region  КОЛИЧЕСТВО КОРОБОК
              // проводим ревизии.
                if (dataGridView2.CurrentRow == null) return;
                
                count_kor = _parent.obj2double(dataGridView2.CurrentRow.Cells[3].Value);
                cell = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
                user_id3 = _parent.wms_user.user_id;
                string art1 = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);

                int COUNT_SHT_IN_KOR= _parent.obj2int32( _parent.CachedQuerySingle(" select  COUNT_SHT_IN_KOR  from rrl_articuls where acticul='" + art1 + "' "));
                if (COUNT_SHT_IN_KOR>0)
                {
                    dataGridView2.CurrentRow.Cells[2].Value = COUNT_SHT_IN_KOR * count_kor;
                    Обработать_собрытие_изменения_штук = true;
                }
                else {
                    MessageBox.Show("У артикула " + art1 + " не указана вложенность ");
                    return;
                }
                /*
                Dictionary<string, object> values = new Dictionary<string, object>();
                values["cell1"] = cell;
                values["revision_id1"] = revision_id1;
                values["count2"] = count_kor;
                values["user_id3"] = user_id3;
                string ret = _parent.obj2str(
                    _parent.wms_get_spfunction_value2("REVIZION.revision_cell_kor", values, OracleType.VarChar, 1025));
                dataGridView2.CurrentRow.Cells[4].Value = ret;
                 */

            #endregion
            
            }


            if (e.ColumnIndex == 2 || Обработать_собрытие_изменения_штук)
            {
                #region  КОЛИЧЕСТВО ШТУК
                // проводим ревизии.
                if (dataGridView2.CurrentRow == null) return;

                double count_sht = _parent.obj2double(dataGridView2.CurrentRow.Cells[2].Value);
                cell = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
                string art1 = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);
                revision_row_id1 = _parent.obj2int32(dataGridView2.CurrentRow.Cells[0].Value);

                user_id3 = _parent.wms_user.user_id;

                Dictionary<string, object> values = new Dictionary<string, object>();
                values["articul1"] = art1;
                values["CELL1"] = cell;
                values["revision_row_id1"] = revision_row_id1;
                values["count_sht"] = count_sht;
                values["user_id1"] = user_id3;
                string ret = _parent.obj2str(
                    _parent.wms_get_spfunction_value2("REVIZION.RRL_REVIZION_CELL_SHT", values, OracleType.VarChar, 1025));
                dataGridView2.CurrentRow.Cells[4].Value = ret;


                // REVIZION.RRL_REVIZION_CELL_SHT(articul1 => 'Т0000032916' , CELL1 => 'O-1-1-1-1' , 
                // count_sht => 465 ,revision_row_id1 => 5435 ,user_id1 => 'R');
  
                // RRL_REVIZION_CELL_SHT( 
                // articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , 
                // user_id1 varchar2 )


                #endregion
            }

            
            if (e.ColumnIndex == 9) 
            {
            #region  КОЛИЧЕСТВО ПАЛЛЕТ 
                if (dataGridView2.CurrentRow == null) return;

                string art1 = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);
                if (art1 != "")
                {
                    if (dataGridView2.CurrentRow.Cells[9].Value == null)
                        return;

                    if (dataGridView2.CurrentRow.Cells[9].Value == "")
                        return;


                    int count_pal = _parent.obj2int32(dataGridView2.CurrentRow.Cells[9].Value);
                    cell = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
                    user_id3 = _parent.wms_user.user_id;

                    Dictionary<string, object> values = new Dictionary<string, object>();
                    values["articul1"] = art1;

                    values["CELL1"] = cell;
                    values["count_pal"] = count_pal;
                    values["revision_row_id1"] = revision_row_id1;

                    values["user_id1"] = user_id3;
                    string ret = _parent.obj2str(
                        _parent.wms_get_spfunction_value2("REVIZION.RRL_REVIZION_CELL_PALL", values, OracleType.VarChar, 1025));
                    dataGridView2.CurrentRow.Cells[4].Value = ret;
                }
//                function  RRL_REVIZION_CELL_PALL( 
//   articul1 varchar2, CELL1 varchar2 , count_pal varchar2 , user_id1 varchar2 ) return varchar2
            #endregion 
            }

            if (e.ColumnIndex == 1)
            {
                #region Изменилась ячейка отбора




                #endregion
            }


            if (e.ColumnIndex == 8)
            {
                #region Изменился артикул

                string art = _parent.obj2str( dataGridView2.CurrentRow.Cells[8].Value);
                string cell2= _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
                int row_id = _parent.obj2int32 (dataGridView2.CurrentRow.Cells[0].Value);
                int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);

                if (row_id == 0 && rev_id == 0) { return; }

                if (art == "") { return; }

                string strSQL = "select count(CELL)  from RRL_CELLS  where CELL='" + cell2 + "'   ";
                long count_of_cell2 = _parent.obj2int(_parent.get_wms_sql_result_single(strSQL));
                if (count_of_cell2 != 1)
                {
                    return;
                }

                strSQL = "select count(ACTICUL)  from RRL_ARTICULS  where ACTICUL  like '%" + art + "%' or Name like '%" + art + "%'    ";
                long count_of_c = _parent.obj2int( _parent.get_wms_sql_result_single(strSQL) );     
                 
                if (count_of_c == 0) // Если Артикул существует и единственный
                {
                }else{

                    strSQL = "select ACTICUL , NAME from RRL_ARTICULS  where ACTICUL like '%" + art + "%' or Name like '%" + art + "%'  ";
                    object[] g = _parent.ShowQuery(strSQL, "Выберите артикул " + art, new Point(0, 1), art);
                    if (g.Length > 0) // Выбрали артикул
                    {
                        string ACTICUL = _parent.obj2str(g[0]);
                        string name_ = _parent.obj2str(g[1]);
                        
                        Dictionary<string, object> values = new Dictionary<string, object>();
                        values["cell1"] = cell2;
                        values["articul2"] = ACTICUL;
                        values["revision_rowid"] = row_id;
                        values["rev_id2"] = rev_id;
                        
                        int номер_строки_ревизии = _parent.obj2int32(
                            _parent.wms_get_spfunction_value2("REVIZION.update_revision_row", values, OracleType.Int32, 0));
                        // update_revision_row( cell1 varchar2 , articul2 varchar2 , revision_rowid int rev_id2  ) return int
                        if (row_id>=0)
                        dataGridView2.CurrentRow.Cells[0].Value = номер_строки_ревизии;
                        dataGridView2.CurrentRow.Cells[8].Value = ACTICUL; 
                        dataGridView2.CurrentRow.Cells[10].Value = name_; 
                    }
                }
                #endregion
            }




        }

        private void вExcelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            _parent.grid_2_excel(dataGridView2);
        }

        private void ДобавитьВРевизию_Click(object sender, EventArgs e)
        {


            if (Артикул1.Text == "" && Ячейка1.Text!="" && _parent.obj2int32(НомерРев.Text) > 0)
            {
                // Добавляем все артикула
                Dictionary<string, object> values2 = new Dictionary<string, object>();
                values2["cell1"] = Ячейка1.Text;
                values2["revision_id1"] = _parent.obj2int32(НомерРев.Text);
                _parent.wms_get_spfunction_value2("REVIZION.add_row_2_reviz_type_art", values2, OracleType.Int32, 0);
                ПоказатьРевизию_Click(null, null);

            }


            if (Артикул1.Text != "" && Ячейка1.Text != "" && _parent.obj2int32(НомерРев.Text) > 0)
            {
                // Добавляем все артикула
                Dictionary<string, object> values2 = new Dictionary<string, object>();
                values2["cell1"] = Ячейка1.Text;
                values2["articul2"] = Артикул1.Text ;
                values2["revision_id1"] = _parent.obj2int32(НомерРев.Text);
                _parent.wms_get_spfunction_value2("REVIZION.add_row_2_reviz_type_art2", values2, OracleType.Int32, 0);
                ПоказатьРевизию_Click(null, null);

            }


        }

        private void dataGridView2_CellEnter(object sender, DataGridViewCellEventArgs e)
        {


            if (dataGridView1.CurrentRow == null)
            { return; }

            if (dataGridView2.CurrentRow == null)
            { return; }

            string art = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);
            string cell2 = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
            int row_id = _parent.obj2int32(dataGridView2.CurrentRow.Cells[0].Value);
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);

            if (art != "")
            { 
             t_fasovka.Items.Clear();
             Dictionary<object, object> mods = _parent.get_wms_sql_result_dictionary("select name , ID  from rrl_articul_mods where articul='" + art + "' AND DELETED=0 ");
             modifications=mods;
                foreach( object i in modifications.Keys  )
                {
                    t_fasovka.Items.Add(i);
                }
            }

            if (!ПоказыватьОстатки.Checked)
                return;

            // Показываем остатки.


            if (art == "") return;

            string strSQL = "";
            if (cell2 == "")
            {

                strSQL = "  select r.REMAIN ,   pts.EXPIRY_DATE , pts.UID_PALLET , r.CELL , RRL_GET_MOD_INFO(MOD_ID) , DEFECT_PERC   " +
                    " from rrl_remains r , rrl_pallets pts  " +
                  " where pts.UID_PALLET = r.UID_POLETA  and pts.articul='" + art + "' ";
       
            }
            else {
                strSQL = "  select r.REMAIN ,   pts.EXPIRY_DATE , pts.UID_PALLET , r.CELL , RRL_GET_MOD_INFO(MOD_ID) , DEFECT_PERC   " +
                    "   from rrl_remains r , rrl_pallets pts  " +
                    " where pts.UID_PALLET = r.UID_POLETA and r.cell='" + cell2 + "' and pts.articul='" + art + "' ";
            }
            _parent.fill_view_MINI_WMS(dataGridView3, strSQL, 6);

            double cnt=0;
            foreach( DataGridViewRow dr in dataGridView3.Rows )
            {
                cnt=cnt+ _parent.obj2double(  dr.Cells[0].Value);
            }

            dataGridView2.CurrentRow.Cells[11].Value = cnt;

        }

        private void создатьНакладнуюПоРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (dataGridView1.CurrentRow == null)
            { return; }
            

            long rev_id = _parent.obj2int(dataGridView1.CurrentRow.Cells[0].Value);
            
            if (_parent.obj2int32(dataGridView1.CurrentRow.Cells[5].Value)<=0)
            {
                Dictionary<string, object> values2 = new Dictionary<string, object>();

                values2["rev_id1"] = rev_id;
                int naklad_id = _parent.obj2int32(_parent.wms_get_spfunction_value2("REVIZION.CreateNaklad_2_revizion", values2, OracleType.Int32, 0));
                if (naklad_id > 0)
                {
                    dataGridView1.CurrentRow.Cells[5].Value = naklad_id;
                }
            }

            // ------------------ rev_create_snap_shot_before( rev_id int )
            Dictionary<string, object> values3 = new Dictionary<string, object>();
            values3["rev_id"] = rev_id;
            //values2["user_id1"] = _parent.wms_user.user_id;
            long s = _parent.obj2int(_parent.wms_get_spfunction_value2("REVIZION.rev_create_snap_shot_before", values3, OracleType.Int32 ,0 ));



            //CreateNaklad_2_revizion( rev_id1 int ) return int


        }

        private void СоздатьПаллет_Click(object sender, EventArgs e)
        {

            if (dataGridView1.CurrentRow == null)
            { return; }

            if (dataGridView2.CurrentRow == null)
            { return; }



            // Показываем остатки.
            string articul2 = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);
 
            string cell1 = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
            int row_id = _parent.obj2int32(dataGridView2.CurrentRow.Cells[0].Value);
            int NAKLAD_ID = _parent.obj2int32(dataGridView1.CurrentRow.Cells[5].Value);

            if (NAKLAD_ID == 0)
            {
                MessageBox.Show("Не создана накладная для ревизии.");
                return;
            }
            if (articul2 == "") return;
            double count1 = _parent.obj2double (t_count1.Text);
            DateTime expiury_date = (t_expiury_date.Value);
            double brak_perc1 = _parent.obj2double(t_brak_perc1.Text);
            int pall_n = _parent.obj2int32(t_pall_n.Text);
            double pall_weight1 = _parent.obj2double(t_pall_weight1.Text);
            double tn_weight1 = _parent.obj2double(t_tn_weight1.Text);
            int count_kor1 = _parent.obj2int32(t_count_kor1.Text);
            int fasovka_id1 = 0;
            if (modifications.ContainsKey(t_fasovka.Text))
            {
                fasovka_id1 = _parent.obj2int32( modifications[t_fasovka.Text]);
            }


            Dictionary<string, object> values2 = new Dictionary<string, object>();
            values2["cell1"] = cell1;
            values2["articul2"] = articul2;
            values2["count1"] = count1;
            values2["expiury_date"] = expiury_date;
            values2["fasovka_id1"] = fasovka_id1;
            values2["brak_perc1"] = brak_perc1;
            values2["pall_weight1"] = pall_weight1;
            values2["pall_n"] = pall_n;
            values2["tn_weight1"] = tn_weight1;
            values2["count_kor1"] = count_kor1;
            values2["user_id2"] = _parent.wms_user.user_id;
            values2["NAKLAD_ID"] = NAKLAD_ID;

            string pall_number3 = _parent.obj2str(_parent.wms_get_spfunction_value2("REVIZION.RRL_INV_CREATE_LINE5", 
                values2, OracleType.VarChar, 255));

            if (pall_number3 == "EXISTS")
            {
                MessageBox.Show("такой паллет уже существует. Выберите другой номер");
            }



        }

        private void dataGridView2_RowsAdded(object sender, DataGridViewRowsAddedEventArgs e)
        {
            /*
            try
            {
                if (dataGridView1.Rows[e.RowIndex - 1] == null)
                { return; }

                dataGridView1.Rows[e.RowIndex - 1].Cells[1].Value = dataGridView1.Rows[ e.RowIndex ].Cells[1].Value;

            }
            catch { }
            */
        }

        private void dataGridView2_UserAddedRow(object sender, DataGridViewRowEventArgs e)
        {

            try
            {
                e.Row.Cells[1].Value = dataGridView2.Rows[dataGridView2.Rows.Count - 2].Cells[1].Value;

            
            }
            catch { }
        }

        private void groupBox1_Enter(object sender, EventArgs e)
        {

        }

        private void очиститьОтрицаткельныеОстаткиПоДаннойРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {

            Dictionary<string, object> values2 = new Dictionary<string, object>();
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
            values2["revision_id1"] = rev_id ;
            values2["user_id1"] = _parent.wms_user.user_id;

            long s = _parent.obj2int( _parent.wms_get_spfunction_value2("REVIZION.RRL_REVIZION_CLEAR_MINUS",
                values2, OracleType.VarChar, 255));

        }

        private void распечататьФормуРевизииПоЯчейкамToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
            Dictionary<string, string> constants = new Dictionary<string, string>();
            constants["rev_id"] = rev_id.ToString();
            _parent.PrintFromXMLFile("revision_task.xml", null, constants);  

        }

        private void списокНепроведенныхЗаявокСПрошлойРевизиToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string articul2 = _parent.obj2str(dataGridView2.CurrentRow.Cells[8].Value);

            string strSQL = " select max( close_date ) from RABAEV.RRL_REVIZION rv , RABAEV.RRL_REVISION_ROW rs where rv.ID = rs.REVISION_ID and "+
                " rs.ARTICUL1='" + articul2 + "' ";
            object date1=_parent.get_wms_sql_result_single( strSQL );
            if (date1 == null) return;
            DateTime td = _parent.obj2DateTime(date1);

            if (td.Year<2011)
            {
                return;
            }

            string strSQL2 = " select rs.ARTICUL , pts.PALLET_UID , rs.QUANTITY , pts.ADDR , pts.CONDITION "+
                " from RABAEV.RRL_SBORKA_PALLETS pts , RABAEV.RRL_SBORKA_PALLET_ROWS rs where " +
                "  ( pts.PALLET_UID  = rs.PALLET_UID ) and ( rs.ARTICUL='" + articul2  + "' ) " +
                " and ( pts.CHECKING_TIME > to_timestamp( " + _parent.datetime2sql_ora(td) + " ) ) and (rs.PRIHOD_PALLET_UID is null) " +
                "   and pts.ware_id=" + _parent.wms_user.ware_id + " and rs.WARE_ID=" + _parent.wms_user.ware_id + "     ";

            _parent.ShowQuery( strSQL2 , "Список не проведенных строк заявок с прошлой ревизии" );
            //string cell1 = _parent.obj2str(dataGridView2.CurrentRow.Cells[1].Value);
            
        }

        private void спосокПроводокВОтборИИзНегоСПрошлойРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {

        }

        private void закрытьРевизиюИСнимокПослеРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {
            
            Dictionary<string, object> values2 = new Dictionary<string, object>();
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
            values2["rev_id"] = rev_id;
            //values2["user_id1"] = _parent.wms_user.user_id;
            long s = _parent.obj2int(_parent.wms_get_spfunction_value2("REVIZION.close_revision", values2, OracleType.Int32 , 0 ));
            dataGridView1.CurrentRow.Cells[3].Value = 2;

        }

        private void остаткиДоРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
           // string strSQL = " select ID, ARTICUL1 ,  CELL , COUNT1  , COUNT_KOR , NUM_OF_PALL , COUNT_PAL , REMARK1 , REVIZION.articul_name( RR.ARTICUL1) " + 
           // " REV_DATE from RABAEV.RRL_REVISION_ROW where REVISION_ID="+rev_id.ToString()+" "; 
            int SNAPSHOT_BEFORE =_parent.obj2int32( _parent.CachedQuerySingle(" select SNAPSHOT_BEFORE from RRL_REVIZION where id="+rev_id.ToString()+" ") );
            if(SNAPSHOT_BEFORE<=0 )
            {
                MessageBox.Show("Снимок остатков до ревизии не создан");
                return;
            }
            string strSQL = "  select ARTICUL , PALLET_UID , CELL , REMAIN , WARE_ID , SNAP_TIME , "+
                " CONDITION , REVIZION.articul_name( ARTICUL ) Имя  from  RABAEV.RRL_REMAIN_SNAPSHOT_ROWS where SNAP_SHOT_ID=" + SNAPSHOT_BEFORE.ToString();

            _parent.ShowQuery( strSQL , "Фотография остатков до ревизии" );


        }

        private void остаткиПослеРевизииToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int rev_id = _parent.obj2int32(dataGridView1.CurrentRow.Cells[0].Value);
            // string strSQL = " select ID, ARTICUL1 ,  CELL , COUNT1  , COUNT_KOR , NUM_OF_PALL , COUNT_PAL , REMARK1 , REVIZION.articul_name( RR.ARTICUL1) " + 
            // " REV_DATE from RABAEV.RRL_REVISION_ROW where REVISION_ID="+rev_id.ToString()+" "; 
            int SNAPSHOT_BEFORE = _parent.obj2int32( _parent.CachedQuerySingle(" select SNAPSHOT_AFTER from RRL_REVIZION where id=" + rev_id.ToString() + " ") );
            if (SNAPSHOT_BEFORE <= 0)
            {
                MessageBox.Show("Снимок остатков после ревизии не создан");
                return;
            }
            string strSQL = "  select ARTICUL , PALLET_UID , CELL , REMAIN , WARE_ID , SNAP_TIME , " +
                " CONDITION , REVIZION.articul_name( ARTICUL ) Имя from  RABAEV.RRL_REMAIN_SNAPSHOT_ROWS where SNAP_SHOT_ID=" + SNAPSHOT_BEFORE.ToString();

            _parent.ShowQuery(strSQL, "Фотография остатков после ревизии");


        }

        private void СоздатьРевизию_Click(object sender, EventArgs e)
        {
            int номер_ревизии=0;
            
            // Создаем ревизию.
                Dictionary<string, object> values = new Dictionary<string, object>();
                values["ware_id1"] = _parent.wms_user.ware_id;
                values["user_id1"] = _parent.wms_user.user_id;
                номер_ревизии = _parent.obj2int32(
                    _parent.wms_get_spfunction_value2("REVIZION.create_revizion", values, OracleType.Int32, 0));
            
            //function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
                if (Артикул1.Text == "")
                {
                    Dictionary<string, object> values2 = new Dictionary<string, object>();
                    values2["cell1"] = Ячейка1.Text;
                    values2["revision_id1"] = номер_ревизии;
                    _parent.wms_get_spfunction_value2("REVIZION.add_row_2_revizion", values2, OracleType.Int32, 0);
                }
                else {
                    Dictionary<string, object> values2 = new Dictionary<string, object>();
                    values2["cell1"] = Ячейка1.Text;
                    values2["articul2"] = Артикул1.Text;
                    values2["revision_id1"] = номер_ревизии;
                    _parent.wms_get_spfunction_value2("REVIZION.add_row_2_reviz_type_art2", values2, OracleType.Int32, 0);
                
                
                }
                НомерРев.Text = номер_ревизии.ToString();
            //function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int is
                ПоказатьРевизию_Click(null, null);

        }

 





   
    }
}