using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Data;
using System.Data.SqlClient;
using System.Data.OracleClient;
using System.Data.OleDb;


namespace WindowsApplication2
{
    public partial class rrl_objects : Form
    {


        public Form1 _parent;
        string node_parent = " is null  ";
        string last_parent = null;

        public rrl_objects()
        {
            InitializeComponent();
        }

        private void rrl_objects_Load(object sender, EventArgs e)
        {
            string strSQL = " select OBJECT_NAME , TYPE1 from RABAEV.RRL_OBJECT where PARENT_OBJECT " + node_parent + "  ";
            Dictionary< object ,Dictionary<object, object>>  nds  = _parent.get_wms_sql_result_dictionary2(strSQL);
            foreach( object key in nds.Keys )
            {
                string type1 = nds[key]["TYPE1"].ToString();
                treeView1.Nodes.Add(key.ToString() , key.ToString() /*+" "+type1*/ );
            }
        }

        private void treeView1_BeforeExpand(object sender, TreeViewCancelEventArgs e)
        {

        }

        private void treeView1_LocationChanged(object sender, EventArgs e)
        {

            try
            {
                last_parent = treeView1.SelectedNode.Text;
                string strSQL = " select OBJECT_NAME ,BUSINESS_FIELD , TYPE1 ,COMMENT1,ARTICLE1  " +
                " from RABAEV.RRL_OBJECT where PARENT_OBJECT " + last_parent + "  ";
                _parent.fill_view_MINI_WMS(dataGridView1, strSQL, 5);

            }
            catch { }

        }

        private void dataGridView1_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView1.CurrentRow == null)
                return;

            

            string OBJECT_NAME = _parent.obj2str( dataGridView1.CurrentRow.Cells[0].Value ) ;
            string BUSINESS_FIELD = _parent.obj2str(dataGridView1.CurrentRow.Cells[1].Value);
            string TYPE1 = _parent.obj2str(dataGridView1.CurrentRow.Cells[2].Value);
            string COMMENT1 = _parent.obj2str(dataGridView1.CurrentRow.Cells[3].Value);
            string ARTICLE1 = _parent.obj2str(dataGridView1.CurrentRow.Cells[4].Value);
           // string strSQL = " update ";


            Dictionary<string, object> values = new Dictionary<string, object>();
            values["OBJECT_NAME1"] = OBJECT_NAME;
            values["BUSINESS_FIELD1"] = BUSINESS_FIELD;
            values["PARENT_OBJECT1"] = last_parent;
            values["COMMENT11"] = COMMENT1;
            values["TYPE2"] = TYPE1;
            values["ARTICLE2"] = ARTICLE1;

            object ret = _parent.wms_get_spfunction_value2("HELP.update_object", values, OracleType.Int32, 0);





        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {

        }
    }
}
