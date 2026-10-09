using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class Поставщики : Form
    {

        public Form1 _parent;
        string choose_supp_id="" ;
        string choose_supp_name="" ;

        public Поставщики()
        {
            InitializeComponent();
        }

        private void Поставщики_Load(object sender, EventArgs e)
        {
            AddKids("");
        }


        private void AddKids(string parentid)
        {

            string filt = "  PARENT_ID  is null ";
            if (parentid != "")
            {
                filt = "  PARENT_ID = '" + parentid + "' ";
            }

            TreeNode[] parentNode = treeView1.Nodes.Find(parentid, true);
            if (parentid != "")
                if (parentNode.Length == 0)
                    return;

            Dictionary<object, object> res = _parent.get_wms_sql_result_dictionary(
                "select  ID , NAME from  RABAEV.RRL_SUPPLIER_GROUP  where  " + filt);
            foreach (object r in res.Keys)
            {
                TreeNode node = new TreeNode();
                node.Text = /* "["+r.ToString()+"] " + */ res[r].ToString();
                node.Name = r.ToString();

                if (parentid == "")
                    treeView1.Nodes.Add(node); // Top Level
                else
                    parentNode[0].Nodes.Add(node); // Add children under parent

                AddKids(node.Name);
            }
            return;
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
            this.Text = "Выбрана группа '" + e.Node.Name + "'  " + e.Node.Text;
            choose_supp_id = e.Node.Name;
            choose_supp_name = e.Node.Text;
            string strSQL = " select NAME  ,INN , KPP, SUPPLIER_GROUP , UR_ADDR , "+
                " ADDR , ID from  RABAEV.RRL_SUPPLIERS where SUPPLIER_GROUP='" + choose_supp_id + "' ";
            
            _parent.fill_view_MINI_WMS(this.ТаблицаПоставщиков , strSQL , 7 );



 
        }

        private void ТаблицаПоставщиков_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            if(ТаблицаПоставщиков.CurrentRow == null) return;
             
            string ID= ТаблицаПоставщиков.CurrentRow.Cells[6].Value.ToString();



            string strSQL = " select ID , DOG_NAME  , TYPE_OF_CONTRACT , START_DATE , END_DATE , POST_OPLATA , FEDERAL " +
    "   from  RABAEV.RRL_SUPPLIER_CONTRACT where SUPP_ID=" + ID + " ";

            _parent.fill_view_MINI_WMS(this.dataGridView1, strSQL, 6);
 

        }




    }
}
