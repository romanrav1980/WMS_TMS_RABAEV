using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Data.OracleClient;
using System.Data.OleDb;
using System.Net;
using System.Net.Sockets;
using System.Diagnostics;
using System.Runtime.InteropServices; 
using System.Configuration;




namespace WindowsApplication2
{



    public partial class Form2 : Form
    {
        private const string DefaultWmsDataSource = "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=127.0.0.1)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=orcl)))";
        public string WMS_CONNECTION_STRING_INST = BuildWmsConnectionString("DBWMS");
        public string MAIN_LOGIN;
        public long WARE_ID;
        public string MAIN_PASS;
        public string version = "xp12";
     //   HookDemoHelper hook;

        public Form2()
        {

            InitializeComponent();
            WMS_CONNECTION_STRING_INST = BuildWmsConnectionString(DBNAME.Text);
        }

        private static string ResolveConfiguredDataSource(string environmentName)
        {
            string key = "WmsDataSource." + environmentName;
            string configuredValue = ConfigurationManager.AppSettings[key];
            if (!string.IsNullOrWhiteSpace(configuredValue))
            {
                return configuredValue;
            }

            configuredValue = ConfigurationManager.AppSettings["WmsDataSource.Default"];
            if (!string.IsNullOrWhiteSpace(configuredValue))
            {
                return configuredValue;
            }

            return DefaultWmsDataSource;
        }

        private static string BuildWmsConnectionString(string environmentName)
        {
            string dataSource = (environmentName ?? string.Empty).Trim();

            if (!string.IsNullOrWhiteSpace(dataSource) &&
                dataSource.IndexOf("(DESCRIPTION=", StringComparison.OrdinalIgnoreCase) < 0 &&
                dataSource.IndexOf('/') < 0)
            {
                dataSource = ResolveConfiguredDataSource(dataSource);
            }

            if (string.IsNullOrWhiteSpace(dataSource))
            {
                dataSource = DefaultWmsDataSource;
            }

            return "Data Source=" + dataSource + ";Password=RABAEVWMS;User ID=RABAEV";
        }

        
        private void button1_Click(object sender, EventArgs e)
        {


            if (DateTime.Today <  Convert.ToDateTime("04.04.2012"))
            {
                MessageBox.Show("Не корректное время.");
                return;
            }



            

            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();


            MAIN_LOGIN = "";
            MAIN_PASS = "";


            try
            {
                ora_conn.ConnectionString = WMS_CONNECTION_STRING_INST;
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = "RABAEV.RRL_AUTH3";
                ora_com.CommandType = CommandType.StoredProcedure;

                String strHostName = Dns.GetHostName();
           
                IPHostEntry iphostentry = Dns.GetHostByName(strHostName);
                string sss = "IP=";
                foreach (IPAddress ipaddress in iphostentry.AddressList)
                {
                   sss= sss + ipaddress.ToString()+";";
                }

                if (sss.Length > 49) sss = sss.Substring(0, 48);


                string ip_addr1 = sss;

                ora_com.Parameters.Add("login", OracleType.VarChar).Value = m_login.Text;
                ora_com.Parameters.Add("pass1", OracleType.VarChar).Value = m_pass.Text;
                ora_com.Parameters.Add("version1", OracleType.VarChar).Value = version;
                ora_com.Parameters.Add("ip_addr1", OracleType.VarChar).Value = ip_addr1;


                

                ora_com.Parameters.Add("ok", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
            }catch(Exception ex)
            {
                MessageBox.Show("нет соединения с базой данных" + ex.Message );
                return;
            }

            long ret1 = Convert.ToInt64( ora_com.Parameters["ok"].Value );
            if (ret1 > 0)
            {
                MAIN_LOGIN = m_login.Text;
                MAIN_PASS = m_pass.Text;
                WARE_ID = ret1;
                this.Close();
            }
            else {
                if (ret1 <= -3) {
                    MessageBox.Show(" Версия программы запрещена к ипользованию ");
                
                }
                else
                {
                    MessageBox.Show(" Неверный логин или пароль ");
                }
            }


        }

        private void Form2_Load(object sender, EventArgs e)
        {
            label1.Text = version;
            WMS_CONNECTION_STRING_INST = BuildWmsConnectionString(DBNAME.Text);

        }

        private void DBNAME_TextChanged(object sender, EventArgs e)
        {
            WMS_CONNECTION_STRING_INST = BuildWmsConnectionString(DBNAME.Text);
        }
    }

    internal class HookDemoHelper
    {

        private const int WH_KEYBOARD_LL = 13;
        private const int WM_KEYDOWN = 0x0100;
        public static Byte[] IpKeyState = new byte[256];
        public static IntPtr hwnd;
        public static IntPtr dwLayout;
        public static int GL;
        public static char pwszBuff;

        private LowLevelKeyboardProcDelegate m_callback;
        private IntPtr m_hHook;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr SetWindowsHookEx(
            int idHook,
            LowLevelKeyboardProcDelegate lpfn,
            IntPtr hMod, int dwThreadId);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool UnhookWindowsHookEx(IntPtr hhk);

        [DllImport("Kernel32.dll", SetLastError = true)]
        private static extern IntPtr GetModuleHandle(IntPtr lpModuleName);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr CallNextHookEx(
            IntPtr hhk,
            int nCode, IntPtr wParam, IntPtr lParam);

        [DllImport("kernel32.dll")]
        static extern IntPtr LoadLibrary(string lpFileName);
        [DllImport("user32.dll")]
        private static extern int GetKeyboardLayout(IntPtr dwLayout);
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetWindowThreadProcessId(IntPtr HWND, IntPtr IpdwProcessID);
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetWindowText(IntPtr HWND, string LpString, int maxCount);
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int ToAsciiEx(uint wVirtKey, uint vScanCode, Byte[] IpKeyState, out char pwszBuff, uint wFlags, int gl);
        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int GetKeyboardState(Byte[] IpKeyState);
        [DllImport("USER32.DLL")]
        public static extern int GetKeyState(byte keys);
        [DllImport("USER32.DLL")]
        private static extern int MapVirtualKey(int uCode, int uMapType);
        [DllImport("USER32.DLL")]
        private static extern int ToUnicodeEx(uint wVirtKey, uint vScanCode, Byte[] IpKeyState, out char pwszBuff, int cchBuff, uint wFlags, IntPtr gl);



        private IntPtr LowLevelKeyboardHookProc(
            int nCode, IntPtr wParam, IntPtr lParam)
        {

            if (nCode < 0)
            {
                return CallNextHookEx(m_hHook, nCode, wParam, lParam);
            }

            else
            {


                if ((nCode >= 0) && (wParam == (IntPtr)WM_KEYDOWN))
                {
                    var khs = (KeyboardHookStruct)Marshal.PtrToStructure(lParam, typeof(KeyboardHookStruct));
                    GetKeyboardState(IpKeyState);
                    hwnd = GetForegroundWindow();
                    dwLayout = GetWindowThreadProcessId(hwnd, IntPtr.Zero);
                    GL = GetKeyboardLayout(dwLayout);
                    ToAsciiEx((uint)khs.VirtualKeyCode, (uint)(khs.ScanCode >> 16) & 0Xff, IpKeyState, out pwszBuff, (uint)khs.Flags, GL);

                    /*
                    using (StreamWriter F = new StreamWriter(@"D:\1.txt", true, Encoding.GetEncoding(1251)))
                    {

                        F.Write("" + pwszBuff);
                    }*/
                }




            }

            return CallNextHookEx(m_hHook, nCode, wParam, lParam);

        }



        [StructLayout(LayoutKind.Sequential)]

        private struct KeyboardHookStruct
        {
            public readonly int VirtualKeyCode;
            public readonly int ScanCode;
            public readonly int Flags;
            public readonly int Time;
            public readonly IntPtr ExtraInfo;
        }



        private delegate IntPtr LowLevelKeyboardProcDelegate(
            int nCode, IntPtr wParam, IntPtr lParam);



        public void SetHook()
        {
            m_callback = LowLevelKeyboardHookProc;
            m_hHook = SetWindowsHookEx(WH_KEYBOARD_LL,
                m_callback,
                GetModuleHandle(IntPtr.Zero), 0);
        }



        public void Unhook()
        {
            UnhookWindowsHookEx(m_hHook);
        }



    } 



}
