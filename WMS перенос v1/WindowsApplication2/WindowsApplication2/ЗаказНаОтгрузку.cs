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
    public partial class ЗаказНаОтгрузку : Form
    {
        public Form1 _parent;

        public ЗаказНаОтгрузку()
        {
            InitializeComponent();
        }

        private void ЗаказНаОтгрузку_Load(object sender, EventArgs e)
        {
            // 
        }

        private void данныеExcelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            ВыбратьСтолбцы форма = new ВыбратьСтолбцы();
            форма._parent = _parent;
            форма.dgv = this.dataGridView1;
            форма.Show();

        }
    }
}
