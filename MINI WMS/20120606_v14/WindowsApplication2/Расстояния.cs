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
    public partial class Расстояния : Form
    {

//      List<object> X; 
//      List<object> Y;


        List<object> X = new List<object>();
        List<object> Y = new List<object>();


        public Form1 _parent;
        public Расстояния()
        {
            InitializeComponent();
        }

        private void Расстояния_Load(object sender, EventArgs e)
        {
            comboBox1.Items.Clear();
            comboBox1.Items.Add("РЕГИОНЫ");

            string strSQL = "select region from rrl_trp_regions ";
            List<object> regs= _parent.get_wms_sql_result_array(strSQL);
            foreach (object i in regs)
            {
                comboBox1.Items.Add(i);
            }

        }



        private void Отобразить_Click(object sender, EventArgs e)
        {
             X = new List<object>();
             Y = new List<object>();
            bool show_region = false;

            dataGridView1.Rows.Clear();
            dataGridView1.Columns.Clear();

            string strSQL_raiony = "";
            string region = comboBox1.Text;
            Dictionary<object, object> m_regions_dic = new Dictionary<object, object>();

            if (comboBox1.Text == "РЕГИОНЫ")
            {
                strSQL_raiony = " select  region from rrl_trp_regions order by ord ";
                show_region = true;
            }
            else {

                strSQL_raiony = " select distinct ADDR  from rrl_addr where region='" + region + "'  and deleted3=0  order by ord  ";
                m_regions_dic=_parent.get_wms_sql_result_dictionary(" select distinct ADDR , raion  from rrl_addr where region='" + region + "' and deleted3=0  ");
                show_region = false;
                
            }
            
            List<object> raions = _parent.get_wms_sql_result_array(strSQL_raiony);
            if (show_region == false)
            {
                raions.Add(region + "_OUT");
                raions.Add(region + "_IN");
                m_regions_dic[region + "_OUT"] = "_OUT";
                m_regions_dic[region + "_IN"] = "_IN";
            }
            else { 
                
            }

            dataGridView1.Columns.Add("Откуда/Куда", "Откуда/Куда");
            foreach (object r in raions)
            {
                dataGridView1.Columns.Add(r.ToString(), r.ToString());
                X.Add(r);
            }


            foreach (object r in raions)
            {
               int i= dataGridView1.Rows.Add(r.ToString());
               dataGridView1.Rows[i].Cells[0].Value = r.ToString();
                Y.Add(r);
            }


            #region Заполняем данные по расстояниям и цветам.
            // Цвет 
                string m_tip_izmerenya = ТИП_ИЗМЕРЕНИЯ.Text.Trim();
                foreach( DataGridViewRow r in dataGridView1.Rows )
                {


                    foreach (DataGridViewColumn c in dataGridView1.Columns)
                    {
                        if (c.Index == 1)
                        {
                            r.Cells[0].Style.BackColor = Color.Khaki;
                        }

                        if(c.Index!=0)
                        {
                        
                        string row_name = Y[r.Index].ToString();
                        string col_name = X[c.Index-1].ToString();
                        // если устанавливается расстояние между регионами, то ..
                        if (comboBox1.Text == "РЕГИОНЫ")
                        {
                            #region ЗАПРАШИВАЕМ РАССТОЯНИЕ МЕЖДУ РЕГИОНАМИ
                            Dictionary<string, object> values = new Dictionary<string, object>();
                            values["reg_f"] =  row_name;
                            values["rai_f"] =  "_";
                            values["reg_2"] = col_name;
                            values["rai_2"] =  "_";
                            if (m_tip_izmerenya == "ВРЕМЯ")
                            {
                                object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.get_time", values, OracleType.Int32, 0);
                                r.Cells[c.Index].Value = ret;
                            }
                            else {
                                object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.get_distance", values, OracleType.Int32, 0);
                                r.Cells[c.Index].Value = ret;
                            }
                            #endregion
                        }
                        else 
                        {
                            #region ЗАПРАШИВАЕМ РАССТОЯНИЕ МЕЖДУ МАГАЗИНАМИ
                            Dictionary<string, object> values = new Dictionary<string, object>();
                            values["AddrFrom"] = row_name;
                            values["AddrTo"] = col_name;


                            if (row_name != col_name)
                            {
                                if (m_tip_izmerenya == "ВРЕМЯ")
                                {
                                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.get_time_m", values, OracleType.Number, 0);
                                    r.Cells[c.Index].Value = ret;
                                }
                                else
                                {
                                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.get_dist_m", values, OracleType.Number, 0);
                                    r.Cells[c.Index].Value = ret;
                                }
                            }

                            #region ЦВЕТ ОДИНАКОВЫХ РАЙОНОВ
                            if (row_name == col_name)
                            {
                                r.Cells[c.Index].Style.BackColor = Color.Black;
                            }
                            else
                            {

                                if (m_regions_dic[row_name].ToString() == m_regions_dic[col_name].ToString())
                                {
                                    r.Cells[c.Index].Style.BackColor = Color.LightGreen;
                                }
                            }
                            #endregion

                            #endregion
                        }
                    }
                    }

                }
                
            #endregion

        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            double val = _parent.obj2double( dataGridView1.Rows[e.RowIndex].Cells[e.ColumnIndex].Value);
            string m_tip_izmerenya = ТИП_ИЗМЕРЕНИЯ.Text.Trim();
            if (comboBox1.Text == "РЕГИОНЫ")
            {// если редактируем расстояние между регионами
                string reg_from = Y[e.RowIndex].ToString() ;
                string reg_to = X[e.ColumnIndex-1].ToString();

                if (reg_from == reg_to) {
                    return;
                }

                /*function set_distance(reg_f varchar2 , rai_f varchar2 , 
                    reg_2 varchar2 , rai_2 varchar2 , dist number  ) return int ;
                function set_time(reg_f varchar2 , rai_f varchar2 , 
                    reg_2 varchar2 , rai_2 varchar2  , time1 number ) return int; */

                #region УСТАНАВЛИВАЕМ РАССТОЯНИЕ И ВРЕМЯ МЕЖДУ РЕГИОНАМИ
                Dictionary<string, object> values = new Dictionary<string, object>();
                values["reg_f"] = reg_from;
                values["rai_f"] = "_";
                values["reg_2"] = reg_to;
                values["rai_2"] = "_";
                

                if (m_tip_izmerenya == "ВРЕМЯ")
                {
                    values["time1"] = val;
                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_time", values, OracleType.Int32, 0);

                    #region Автоматический пересчет

                    if( _parent.obj2int32( Скорость.Text)>0 ){
                        double dist1 = val * _parent.obj2int32(Скорость.Text);
                        Dictionary<string, object> values2 = new Dictionary<string, object>();
                        values2["reg_f"] = reg_from;
                        values2["rai_f"] = "_";
                        values2["reg_2"] = reg_to;
                        values2["rai_2"] = "_";
                        values2["dist"] = dist1;
                        object ret4 = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_distance", values2, OracleType.Int32, 0);
                    }
                    #endregion
                }
                else
                {
                    values["dist"] = val;
                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_distance", values, OracleType.Int32, 0);



                    #region Автоматический пересчет

                    if (_parent.obj2int32(Скорость.Text) > 0)
                    {
                        double time2 = val / _parent.obj2int32(Скорость.Text);
                        Dictionary<string, object> values2 = new Dictionary<string, object>();
                        values2["reg_f"] = reg_from;
                        values2["rai_f"] = "_";
                        values2["reg_2"] = reg_to;
                        values2["rai_2"] = "_";
                        values2["time1"] = time2;
                        object ret5 = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_time", values2, OracleType.Int32, 0);
                    }
                    #endregion


                }
                #endregion

            }
            else 
            { // если редактируем расстояние между магазинами внутри одного региона
                /*function set_distance_m( AddrFrom varchar2 , AddrTo varchar2 , dist1 number   ) return int 
                 function set_time_m( AddrFrom varchar2 , AddrTo varchar2 , time1 number ) return int
                 */
                string m_from = Y[e.RowIndex].ToString();
                string m_to = X[e.ColumnIndex-1].ToString();

                if (m_from == m_to)
                {
                    return;
                }

                #region УСТАНАВЛИВАЕМ РАССТОЯНИЕ И ВРЕМЯ МЕЖДУ МАГАЗИНАМИ
                Dictionary<string, object> values = new Dictionary<string, object>();
                values["AddrFrom"] = m_from;
                values["AddrTo"] = m_to;

                if (m_tip_izmerenya == "ВРЕМЯ")
                {
                    values["time1"] = val;
                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_time_m", values, OracleType.Int32, 0);
                    
                    #region Автоматический пересчет
                    if (_parent.obj2int32(Скорость.Text) > 0)
                    {
                        double dist1 = val * _parent.obj2int32(Скорость.Text);
                        Dictionary<string, object> values2 = new Dictionary<string, object>();
                        values2["AddrFrom"] = m_from;
                        values2["AddrTo"] = m_to;
                        values2["dist1"] = dist1;
                        object ret3 = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_distance_m", values2, OracleType.Int32, 0);
                    }
                    
                    #endregion


                }
                else
                {
                    values["dist1"] = val;
                    object ret = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_distance_m", values, OracleType.Int32, 0);

                    #region Автоматический пересчет
                    if (_parent.obj2int32(Скорость.Text) > 0)
                    {
                        double time1 = val / _parent.obj2int32(Скорость.Text);
                        Dictionary<string, object> values2 = new Dictionary<string, object>();
                        values2["AddrFrom"] = m_from;
                        values2["AddrTo"] = m_to;
                        values2["time1"] = time1;
                        object ret2 = _parent.wms_get_spfunction_value2("TRANSPORT_PLN.set_time_m", values2, OracleType.Int32, 0);
                    }

                    #endregion

                }
                #endregion


            }
        }

        private void управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ВыбратьСтолбцы vs = new ВыбратьСтолбцы();
            vs._parent = _parent;
            vs.dgv = dataGridView1;
            vs.ShowDialog();
        }
    }
}
