using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Media;//подключили пространство имен SoundPlayer  

using System.Threading;

namespace WindowsFormsApplication1
{






    public partial class Form1 : Form
    {
        SoundPlayer sp;

        public Form1()
        {
            InitializeComponent();


             sp = new SoundPlayer();//создаем экземпляр класса SoundPlayer             
        }


        public void VOICE_say_number(long  m_number)
        {
            
            if (m_number > 9999) {
                return;
            }

            string m_numbers = Convert.ToString(m_number);
            if (m_numbers.Length >= 4)
            { // Количество тысяч
                string kt = m_numbers.Substring(0,1);
                sp.SoundLocation = "C:\\r\\irina\\" + kt + "000.wav";
                sp.PlaySync();
            }

            if (m_numbers.Length >= 3)
            { // Количество тысяч
                string kt = m_numbers.Substring(1, 1);
                sp.SoundLocation = "C:\\r\\irina\\" + kt + "00.wav";
                sp.PlaySync();
            }


            if (m_numbers.Length >= 2)
            { // Количество тысяч
                string kt = m_numbers.Substring(2, 1);
                sp.SoundLocation = "C:\\r\\irina\\" + kt + "0.wav";
                sp.PlaySync();
            }


            if (m_numbers.Length >= 1)
            { // Количество тысяч
                string kt = m_numbers.Substring(3, 1);
                sp.SoundLocation = "C:\\r\\irina\\" + kt + ".wav";
                sp.PlaySync();
            }


        

        }


        public void Run1()
        {

          //  VOICE_say_number(9876);

            string str1 = "";
            str1 = textBox1.Text;

            foreach (string m_sline in textBox1.Lines )
            {
               string[] m_h2= m_sline.Trim().Split('-');

               if (m_h2.Count() > 1)
               {
                   sp.SoundLocation = "C:\\r\\irina\\" + m_h2[0] + ".wav";
                   sp.PlaySync();
               }
               else {
                   if (m_sline != "")
                   {
                       sp.SoundLocation = "C:\\r\\irina\\" + m_sline + ".wav";
                       sp.PlaySync();
                   }
               }


            }


             
        
        }
        private void button1_Click(object sender, EventArgs e)
        {

            



            System.Threading.Thread t2 = new System.Threading.Thread(new System.Threading.ThreadStart(this.Run1));
            t2.Start(); 

        }
    }
}
