using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class ГруппаТоваров : Form
    {
       public Form1 _parent ;
       public string choose_gr_id ="";
       public string choose_gr_name="";
       public bool choosed = false;



        private void AddKids(string parentid )
        {
           
            string filt ="  PARENT_ID  is null ";
            if (parentid != "")
            {
                filt = "  PARENT_ID = '" + parentid + "' ";
            }

            TreeNode[] parentNode = treeView1.Nodes.Find(parentid, true);
            if (parentid !="")
                if (parentNode.Length == 0)
                    return;

            Dictionary<object,object> res= _parent.get_wms_sql_result_dictionary(
                "select GROUP_ID , GROUP_NAME from RRL_ARTICUL_GROUP where  "+filt);
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


        public ГруппаТоваров()
        {

           
            InitializeComponent();
        }

        private void Выбрать_Click(object sender, EventArgs e)
        {

            if (this.choose_gr_id != "")
            {
                choosed = true;
                this.Close();
                return;
            }
        }

        private void ГруппаТоваров_Load(object sender, EventArgs e)
        {
             AddKids("");
        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {
           
            this.Text = "Выбрана группа '" + e.Node.Name + "'  " +  e.Node.Text ;
            choose_gr_id =e.Node.Name   ;
            choose_gr_name =   e.Node.Text  ;
 

        }
    }
}
