using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace WindowsApplication2
{
    static class Program
    {

        
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Form2 f2 = new Form2();
            //f2.WMS_CONNECTION_STRING_INST = "Server=DBWMS;Password=RABAEVWMS;User ID=RABAEV";
         
            Application.Run(f2);

            //MAIN_LOGIN;
            //MAIN_PASS;
            if((f2.MAIN_LOGIN!="") && (f2.MAIN_LOGIN!=null) )
            {
                Form1 f1 = new Form1();
                f1.WMS_CONNECTION_STRING_INST = f2.WMS_CONNECTION_STRING_INST ;
                f1.wms_user.user_id = f2.MAIN_LOGIN;
                f1.wms_user.ware_id=f2.WARE_ID ;
                f1.version = f2.version;
                Application.Run(f1);
            }

        }



    }
}