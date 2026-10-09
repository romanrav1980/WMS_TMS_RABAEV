using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class ОшибкиСборки : Form
    {

        public string type = "";
        public int count_of_errors = 0;
        public string prim = "";

        public ОшибкиСборки()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try
            {
                if (Convert.ToInt32(textBox1.Text) > 0)
                {
                    type = "ОШИБКА СБОРКИ";
                    count_of_errors = Convert.ToInt32(textBox1.Text);
                    this.Close();
                    return;
                }
            }
            catch { }

            MessageBox.Show("Укажите количество ошибок");

        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (textBox2.Text.Trim().ToString() == "")
            {
                MessageBox.Show("Укажите артикулы, у которых некорректно забит вес.");
                return;
            }
            prim = textBox2.Text;

            type = "ЛОГО-ПАРАМЕТРЫ";
            this.Close();

        }
    }
}