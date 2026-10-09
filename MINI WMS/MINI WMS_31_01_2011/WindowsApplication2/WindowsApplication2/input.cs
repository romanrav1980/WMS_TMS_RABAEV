using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace WindowsApplication2
{
    public partial class input : Form
    {
        public string Message;
        public string ret;


        public input()
        {
            InitializeComponent();
        }



        private void input_Load(object sender, EventArgs e)
        {
            textBox1.Text = ret;
            label1.Text = Message;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            ret = textBox1.Text.Trim();
            this.Close();
        }

        private void Cancel_Click(object sender, EventArgs e)
        {
            ret = "";
        }
    }
}