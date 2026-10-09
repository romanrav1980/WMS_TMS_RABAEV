using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Drawing.Printing;
using System.Data.SqlClient;




using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Data.OracleClient;
using System.Data.OleDb;
using System.IO;

using System.Reflection;
//using usingInterop.Excel;



using System.Security.AccessControl;

using GenCode128;




using MapType = System.Collections.Generic.Dictionary<string, string>;
using PairType = System.Collections.Generic.KeyValuePair<string, string>;

namespace WindowsApplication2
{

    

    public partial class Form1 : Form
    {
        public bool ACTIVE_INCOMING_MESSAGES = true;
        // =======================================
        bool block_change_warehouse_options = false; // Служебная переменная


        private NotifyEvents notifyEvent;
        Object notifyRcvdData = null;
        Object notifySentData = null;
        Object notifyIp = null;
        public ThreadedTcpSrvr hs = null;
        List<funct> F_TO_DO = new List<funct>();
        List< PPage > PPages = new List<PPage>();
        Dictionary<string, bool> WRIGHT_CACHE= new Dictionary<string,bool>();
        // =======================================
        public MINI_WMS_USER wms_user = new MINI_WMS_USER();
        OracleConnection WMS_CONNECTION;
        public string version="";
        double m_map_V=0 ;
        double m_map_WEIGHT=0;
        double m_map_P=0;
        double m_map2_V = 0;
        double m_map2_WEIGHT = 0;
        double m_map2_P = 0;

        bool m_stop_selection_event = false;



        private Dictionary<string, string> CachedSingleQueryResults = new Dictionary<string, string>(); // Переменная содержит кэшированные результаты запросов к базе данных - для переменных, которые не меняются в течение сеанса.

        // Кэшированный запрос
        public string CachedQuerySingle(string strSQL)
        {
            string res="";
            if( CachedSingleQueryResults.TryGetValue( strSQL , out res ) )
            {
                return res;
            }else{
                try
                {
                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = strSQL;
                    object ret11 = ora_com.ExecuteScalar();
                    if (ret11 == null) res = "";
                    else res = ret11.ToString();
                }
                catch { }
                CachedSingleQueryResults[strSQL] = res;
            }
            return res;
        }

        public int ExecuteOracleNonQuery(string strSQL )
        {
            OracleCommand ora_com =  new OracleCommand();
            ora_com.Connection=get_wms_connection();
            ora_com.CommandText = strSQL;
            return ora_com.ExecuteNonQuery();

        }

        private string MDB_CONNECTION_STRING()
        {
            return "Provider=Microsoft.Jet.OLEDB.4.0; Data Source=\\\\adserv30\\Files\\_Общие\\Рабаев\\OD\\БД.mdb";
        }

        private string SFERA_CONNECTION_STRING()
        {
            return "Server=RM;Password=Irokez1983;User ID=ROUTEPLANNER";
            return "Server=RM;Password=Irokez1983;User ID=ROUTEPLANNER";
        }

        public string WMS_CONNECTION_STRING_INST  ; 

        private string WMS_CONNECTION_STRING()
        {
            //         return    "Server=refstock;Password=Rabaev11;User ID=Rabaev";
            //   return "Server=DBWMS;Password=RABAEVWMS;User ID=RABAEV";
            //      return "Server=192.168.208.9/DBWMS;Password=Rabaev;User ID=Qwerty01";
            return WMS_CONNECTION_STRING_INST;

        }


        private string SM_CONNECTION_STRING()
        {
            return "Server=office;Password=dsgjkybnm123;User ID=oramag";
        }

        /*
          Set cn = CreateObject("ADODB.Connection")
cn.ConnectionString = "DRIVER={Microsoft ODBC for Oracle};UID=oramag;PWD=dsgjkybnm123;SERVER=office;"
cn.Open
cn.Execute Sql
         
         */

        private string MINI_WMS_CONNECTION_STRING()
        {
            return WMS_CONNECTION_STRING();
            //return "Server=refstock;Password=Rabaev11;User ID=Rabaev";
            //return "Server=192.168.208.9/DBWMS;Password=Rabaev;User ID=Qwerty01";
        }


        public Form1()
        {
            InitializeComponent();
            
            if( ACTIVE_INCOMING_MESSAGES  ){
            // ПРОСЛУШИВАТЕЛЬ ВНЕШНИХ СОБЫТИЙ =====================================================

            string IP_listen = "192.168.208.200";
            //hs = new ThreadedTcpSrvr(IPAddress.Any, 20001 , this); // IPAddress.Parse(IP_listen);
            hs = new ThreadedTcpSrvr(IPAddress.Parse(IP_listen), 20001, this); // IPAddress.Parse(IP_listen);
            hs.Start();
            
            // ПРОСЛУШИВАТЕЛЬ ВНЕШНИХ СОБЫТИЙ =====================================================
                }

        }


        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            //hs.Stop();
           // hs = null;

        }


        /*
         * 
         * Закачать штрих-коды в ТАБЛИЦУ sfera_ean
         * 
         * 
         */

        private void button1_Click(object sender, EventArgs e)
        {
            /*
            string strSQL=" select from   ";
           
             RABAEV.SFERA_EAN
(
  TMC_UID      VARCHAR2(50 CHAR)                NOT NULL,
  EAN_SHT      VARCHAR2(20 CHAR),
  EAN_BL       VARCHAR2(20 CHAR),
  EAN_KOR      VARCHAR2(20 CHAR),
  MANUALENTER  CHAR(1 CHAR)                     DEFAULT 'Y',
  SHT_IN_BL    INTEGER                          NOT NULL,
  BL_IN_KOR    INTEGER                          NOT NULL,
  УИД          INTEGER,
  NAME         VARCHAR2(255 CHAR)
)

            */




        }


        #region РАБОТА_С_СЕТЬЮ

        // Catch socket notification events
        private void OnSocket(NotifyEvents nEvent, object ip, object rcvdData, object sentData)
        {
            try
            {
                lock (this)
                {
                    // save arguments to class fields				
                    notifyEvent = nEvent;
                    notifyRcvdData = rcvdData;
                    notifySentData = sentData;
                    notifyIp = ip;

                    Invoke(new EventHandler(ProcessNotifications));
                }
            }
            catch
            {
            }
        }

        // Process socket notifications
        private void ProcessNotifications(object sender, EventArgs args)
        {
            switch (notifyEvent)
            {
                case NotifyEvents.Waiting:
                  // statusBar2.Text = "Waiting... ";
                    break;

                case NotifyEvents.Connected:
                  
                   // statusBar2.Text = "Connected to client: " + notifyIp.ToString();
                    break;

                case NotifyEvents.DataSent:
                   // DisplayData(notifyIp.ToString(), notifyRcvdData.ToString(), notifySentData.ToString());
                   // statusBar2.Text = "Data sent to client: " + notifySentData.ToString();
                    break;

                case NotifyEvents.DataReceived:
                   // DisplayData(notifyIp.ToString(), notifyRcvdData.ToString(), notifySentData.ToString());
                  //  statusBar2.Text = "Data from client: " + notifyRcvdData.ToString();
                    break;

                case NotifyEvents.Disconnected:
                   // DisplayData(notifyIp.ToString(), "Disconnected...", "...");
                  //  statusBar2.Text = "Disconnected from client: " + notifyIp.ToString();
                    break;

                case NotifyEvents.ConnectError:
                case NotifyEvents.SendError:
                case NotifyEvents.ReceiveError:
                case NotifyEvents.OtherError:
                  //  statusBar2.Text = "Socket error\r\n" + notifyRcvdData.ToString() + ";" + notifySentData.ToString();
                    break;
            }

            Application.DoEvents();

        }



        // Socket notification events.
        public enum NotifyEvents
        {
            Waiting,
            Connected,
            DataSent,
            DataReceived,
            Disconnected,
            ConnectError,
            SendError,
            ReceiveError,
            OtherError
        }



 

    class funct
    {
        public string function_name = "dummy";
        public MapType strToIntMap = new MapType();
        




        // FUNC=funcname;var=val1;var2=val2
        public void split(string inp)
        {
            string[] t1 = inp.Split('|');
            
            foreach (string t2 in t1)
            {
                string[] pair = t2.Split('=');
                if (pair.Length == 2)
                {
                    if (pair[0] == "FUNC")
                    {
                        this.function_name = pair[1];
                    }
                    else
                    {
                        this.add_value(pair[0], pair[1]);
                    }
                }
            }
        }

        public List<funct> split_program(string inp)
        {
            List<funct> program_= new List<funct>();
            funct f;

            string[] t1 = inp.Split('|');

            foreach (string t2 in t1)
            {
                string[] pair = t2.Split('=');
                if (pair.Length == 2)
                {
                    if (pair[0] == "FUNC")
                    {
                        f = new funct();
                        f.function_name = pair[1];
                        program_.Add(f);
                    }
                    else
                    {
                        program_[(program_.Count-1)].add_value(pair[0], pair[1]);
                    }
                }
            }
            return program_;
        }


        public string encode()
        {
            string outp = "FUNC=" + this.function_name + "|";
            foreach (KeyValuePair<string, string> pair in strToIntMap)
            {
                outp = outp + pair.Key + "=" + pair.Value.Replace("|", "!").Replace("=", "#") + "|";
            }
            return outp;
        }

        public string get_value( string vname )
        {
            return  strToIntMap[vname];
        }

        public void add_value(string vname, string value1)
        {
            if (value1 == null)
                value1 = "";
            vname.Replace("|", "!");
            vname.Replace("=", "#");
            value1.Replace("|", "!");
            value1.Replace("=", "#");
            strToIntMap[vname] = value1;
        }



        public void add_value(string vname, long value2)
        {
            string value1 = Convert.ToString(value2);
            vname.Replace("|", "!");
            vname.Replace("=", "#");
            value1.Replace("|", "!");
            value1.Replace("=", "#");
            strToIntMap[vname] = value1;
        }

        public void add_value(string vname, OracleString  value2)
        {
            string value1;
            if (value2.IsNull == true)
            {
                value1 = "";
            }
            else { 
                value1 = Convert.ToString(value2);
            }
            vname.Replace("|", "!");
            vname.Replace("=", "#");
            value1.Replace("|", "!");
            value1.Replace("=", "#");
            strToIntMap[vname] = value1;
        }


        public void add_value(string vname, OracleNumber value2)
        {
            string  value1;
            if (value2.IsNull == true)
            {
                value1 = "0";
            }
            else
            {
                value1 = Convert.ToString(value2.Value );
            }

            strToIntMap[vname] = value1;

        }



    }


        public class ThreadedTcpSrvr
        {
            private const int portNum = 10200;
            internal bool stopListenerThread = false;
            Thread m_thread;

            private TcpListener hostSocket;
            private IPAddress address;
            private int port;
            public long NumberOfRequests = 0;
            Form1 m_parent_form = null;

           
            //ConnectionThread newconnection = null;

            public  ThreadedTcpSrvr(IPAddress ip_addr, int port_1 , Form1 parent_form )
            {
                address = ip_addr;
                port = port_1;
                m_parent_form = parent_form;
            }

            public void Start()
            {
                m_thread=new Thread(new ThreadStart(StartThread));
                m_thread.Start();
            }

            public void Stop()
            {
                lock ((object)stopListenerThread)
                {
                    stopListenerThread = true;
                }
                
                m_thread.Abort();
                m_thread = null;

            }


            private bool SetupServer()
            {
                try
                {
                    IPEndPoint endPoint = new IPEndPoint(address, port);
                    hostSocket = new TcpListener(endPoint);
                    hostSocket.Start(10);
                }
                catch (Exception ex)
                {
                    MessageBox.Show ("error f11" + ex.Message);
                    return false;
                }
                return true;
            }

            public void StartRead()
            {

                if (!SetupServer())
                {
                    MessageBox.Show("Сервер не стартовал.");
                    return;
                }
                while (true)
                {
                    AcceptConnections();

                }
                
            }


            private void StartThread()
            {
                try
                {
                    StartRead();
                }
                catch (Exception ex)
                {
                    String msg = ex.Message;
                }
            }

            private void AcceptConnections()
            {

                TcpClient handleSocket = hostSocket.AcceptTcpClient();
                ((IPEndPoint)handleSocket.Client.RemoteEndPoint).Port = ++port;
                handleSocket.ReceiveTimeout = 1000;
                StringBuilder myCompleteMessage = new StringBuilder();
                
                NetworkStream socketStream = handleSocket.GetStream();
                funct F_Request1 = new funct();
                List<funct> F_Request = new List<funct>();

                try
                {
                    #region ЧИТАЕМ_ЗАПРОС_ОТ_КЛИЕНТА
                    //------------------------------------------------------------------
                    // СНАЧАЛА ИДЕТ ЗАПРОС - ПОТОМ ОТВЕТ
                    NumberOfRequests++;
                    if (socketStream.CanRead)
                    {
                        int len = 1024;
                        byte[] data1 = new byte[len * 3];
                        int size = 0;
                        int numberOfBytesRead = 1;
                        StringBuilder l_header = new StringBuilder();

                        // ПРОЧИТАЛИ ХЕДЕР
                        numberOfBytesRead = socketStream.Read(data1, 0, 40);

                        l_header.Append(Encoding.Unicode.GetString(data1, 0, numberOfBytesRead));
                        long len_from_header = Convert.ToInt64(l_header.ToString());


                        do
                        {
                            numberOfBytesRead = socketStream.Read(data1, 0, len);
                            size += numberOfBytesRead;
                            myCompleteMessage.AppendFormat("{0}", Encoding.Unicode.GetString(data1, 0, numberOfBytesRead));
                        } while (size < len_from_header);

                        
                    }

                    //socketStream.Close();

                    string f1 = myCompleteMessage.ToString();
                    F_Request = F_Request1.split_program(f1);
                    //F_Request.split(f1);
                    //foreach (funct r9 in F_Request)
                    //{
                        //Console.WriteLine(r9.encode());
                    //}

                    #endregion
                }
                catch (Exception ex)
                {
                    
                   // this.m_parent_form.m_ConsoleTextBox.Text += (" \n\t F1:" + ex.Message);
                }

                #region ОБЩЕНИЕ_С_КЛИЕНТОМ_ОТВЕТ

                string summary = "";
                funct r = new funct();

                F_Request1 = F_Request[0];

                if (summary == "") { summary = "FUNC=ZERO|"; }

                //string message = "получи результаты : " + myCompleteMessage + " // " + Convert.ToString(NumberOfRequests);
                string message = summary;// F_Response.encode();
                int dlina = Encoding.Unicode.GetBytes(message).GetLength(0);

                // ПИШЕМ ХЕДЕР
                string get_len;
                get_len = Convert.ToString(dlina);
                for (int i3 = get_len.Length; i3 < 20; i3++)
                    get_len = "0" + get_len;

                message = get_len + message;
                dlina = Encoding.Unicode.GetBytes(message).GetLength(0);
                Byte[] data = Encoding.Unicode.GetBytes(message);

                socketStream.Write(data, 0, dlina);
                #endregion



                #region ОБРАБОТКА_ФУНКЦИЙ_ПОСЛЕ_ЗАВЕРШЕНИЯ_ОБЩЕНИЯ_С_СЕРВЕРОМ
    

                switch (F_Request1.function_name)
                {
                    case "PRINT_ERROR_LIST":
                        string UID_USSCC = F_Request1.strToIntMap["UID_USSCC"];
                        this.m_parent_form.print_ispravitelnyi_list(UID_USSCC, true);
                        break;
                    default:
                        break;
                }

                /* 
                 * foreach (funct r9 in F_Request)
                {
                     
                           try{
                                lock (this.m_parent_form.F_TO_DO )
                                {
                                    this.m_parent_form.F_TO_DO.Add(r9);
                                }
                            }catch(Exception ex)
                            {
                               // this.m_parent_form.m_ConsoleTextBox.Text += (" \n\t F1:" + ex.Message);
                            }

 
                }
                */
                #endregion


            }





        }


        #endregion


        public void check_tab_page(TabPage t)
        {
            #region TAB

            if (t.Tag != null)
            {
                if (has_right(t.Tag.ToString()))
                {
                    foreach (Control c in t.Controls)
                    {
                        if (c.Tag != null)
                        {


                            if (has_right(c.Tag.ToString()))
                            { }
                            else
                            {
                                c.Visible = false;
                            }


                        }
                        #region РАБОТА С ПРАВАМИ В ТАБЛИЦАХ
                        try
                        {
                            if (((DataGridView)c).Columns.Count > 0)
                            {
                                for (int i = 0; i < ((DataGridView)c).Columns.Count; i++)
                                {
                                    if (((DataGridView)c).Columns[i].ToolTipText != "")
                                    {
                                        if (has_right(((DataGridView)c).Columns[i].ToolTipText.ToString()) == false)
                                        {
                                            ((DataGridView)c).Columns[i].ReadOnly = true;
                                        }
                                        ((DataGridView)c).Columns[i].ToolTipText = "";
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {

                        }
                        #endregion

                        #region РАБОТА С ТАБ_ПЭЙДЖ
                            try 
                            {
                                if (((TabControl)c).TabCount > 0)
                                {
                                    foreach (TabPage p2 in ((TabControl)c).TabPages)
                                    {
                                        check_tab_page(p2);
                                    }
                                }

                            }catch( Exception ex )
                            {
                            
                            }


                        #endregion
                    }
                }
                else
                {
                    tab2.TabPages.Remove(t);
                }
            }

            #endregion
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // Сервер стартовал ===========================================================

     //for( int i= 0; i<tab2.TabPages.Count ;i++ )

            ware_id_cell.Text = this.wms_user.ware_id.ToString();
            m_выбранный_склад.Text = this.wms_user.ware_id.ToString();

            this.Text = "Рабочее место " + this.wms_user.user_id+" склад "+this.wms_user.ware_id.ToString()+" (Версия: "+this.version+") ";

     foreach( TabPage t in tab2.TabPages )
     {
         check_tab_page(t);

      

     }

            // Сервер стартовал ===========================================================

           // refresh_alt_view();

        }

        private void dataGridView1_UserDeletedRow(object sender, DataGridViewRowEventArgs e)
        {

        }

        private void dataGridView1_UserAddedRow(object sender, DataGridViewRowEventArgs e)
        {

        }



        private string str2str(OracleString os)
        {
            if (os.IsNull) return "";
            return os.Value;
        }

    

        public long str2int(string v)
        {
            if (v == "") return 0;
            return Convert.ToInt64(v);
        }

        public long str2int(OracleString v)
        {
            if (v.IsNull)
                return 0;
            return Convert.ToInt64( str2str(v) );
        }


        public string obj2str(object o)
        {
            if (o == null) return "";
            return o.ToString();
        }

        public long obj2int(object o)
        {
            if (o == null) return 0;
            try
            {
                return Convert.ToInt64(o.ToString());
            }
            catch (Exception ex)
            {
            
            }

            return 0;
        }


        public bool obj2bool(object o)
        {
            if (o == null) return false;
            try
            {
                return Convert.ToBoolean(o );
            }
            catch  
            {

            }

            return false;
        }

        public double obj2double(object o)
        {
            try
            {
                if (o == null) return 0;
                return Convert.ToDouble(o.ToString().Replace(".",","));
            }
            catch { }

            return 0;
            

        }


        public OracleConnection get_wms_connection()
        {

            try
            {
                if (WMS_CONNECTION == null)
                {
                    this.WMS_CONNECTION = new OracleConnection();
                    WMS_CONNECTION.ConnectionString = MINI_WMS_CONNECTION_STRING();
                    WMS_CONNECTION.Open();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message );
            }

            //if (WMS_CONNECTION.Clo)
            try{
                if (this.WMS_CONNECTION.State == ConnectionState.Broken)
                {
                    this.WMS_CONNECTION = new OracleConnection();
                    WMS_CONNECTION.ConnectionString = MINI_WMS_CONNECTION_STRING();
                    WMS_CONNECTION.Open();
                }

                return this.WMS_CONNECTION ;
            }catch
            {
                this.WMS_CONNECTION = new OracleConnection();
                WMS_CONNECTION.ConnectionString = MINI_WMS_CONNECTION_STRING();
                WMS_CONNECTION.Open();
            }

            return this.WMS_CONNECTION;

        }

        private void dataGridView1_CellEndEdit_1(object sender, DataGridViewCellEventArgs e)
        {

            OracleCommand ora_com;
            try
            {
                DataGridViewRow dr = ((System.Windows.Forms.DataGridView)(sender)).CurrentRow;
                    
                //dr.DataBoundItem;
                // TMC_UID,   SHT_IN_BL, BL_IN_KOR, EAN_SHT,EAN_BL, EAN_KOR, УИД
                string TMC_UID = obj2str( dr.Cells[0].Value ) ;
                long SHT_IN_BL = obj2int ( dr.Cells[1].Value  );
                long BL_IN_KOR = obj2int(dr.Cells[2].Value   );
                string EAN_SHT = obj2str( dr.Cells[3].Value ) ;
                string EAN_BL = obj2str( dr.Cells[4].Value ) ;
                string EAN_KOR = obj2str( dr.Cells[5].Value ) ;
                long УИД = obj2int(dr.Cells[6].Value);

                    if (УИД <= 0) { // ЕСЛИ товар новый
                        if ((TMC_UID != "") && (SHT_IN_BL > 0) && (BL_IN_KOR > 0) && (EAN_SHT != "")  )
                        {// ЕСЛи Есть чего записывать

                           ora_com = new OracleCommand();
                           ora_com.Connection = get_wms_connection();
                           //ora_com.CommandText = "insert into RABAEV.SFERA_EAN ( tmc_uid , SHT_IN_BL, BL_IN_KOR , EAN_SHT  , EAN_BL  , EAN_KOR) values ('"
                           // + Convert.ToString(TMC_UID) + "' , " + Convert.ToString(SHT_IN_BL) + " , " + Convert.ToString(BL_IN_KOR) + " , '" + EAN_SHT + "'  , '" + EAN_BL + "' , '" + EAN_KOR + "' ) ";
                           ora_com.CommandText = "ADD_SFERA_EAN2";
                           ora_com.CommandType = CommandType.StoredProcedure;
                          
                           ora_com.Parameters.Add("TMC_UID", OracleType.VarChar).Value = TMC_UID;
                           ora_com.Parameters.Add("EAN_SHT", OracleType.VarChar).Value = EAN_SHT;
                           ora_com.Parameters.Add("EAN_BL", OracleType.VarChar).Value = EAN_BL;
                           ora_com.Parameters.Add("EAN_KOR", OracleType.VarChar).Value = EAN_KOR;
                           ora_com.Parameters.Add("MANUALENTER", OracleType.Char).Value = 'Y';
                           ora_com.Parameters.Add("SHT_IN_BL", OracleType.Int32).Value = SHT_IN_BL;
                           ora_com.Parameters.Add("BL_IN_KOR", OracleType.Int32).Value = BL_IN_KOR;
                           ora_com.Parameters.Add("NAME", OracleType.VarChar).Value = "";
                           ora_com.Parameters.Add("row_uid", OracleType.Int32).Direction = ParameterDirection.ReturnValue;


                            int rowsAffected = ora_com.ExecuteNonQuery();
                            dr.Cells[6].Value = ora_com.Parameters["row_uid"].Value;

                       }

                        return;
                    }

                    
                
                ora_com= new OracleCommand() ;
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "update RABAEV.SFERA_EAN set  SHT_IN_BL =" + Convert.ToString(SHT_IN_BL) + " , BL_IN_KOR = '" + Convert.ToString(BL_IN_KOR) + "'  , EAN_SHT = '" + EAN_SHT + "'  , EAN_BL='" + EAN_BL + "' , EAN_KOR='" + EAN_KOR + "'  " +
                " where УИД=" + Convert.ToString(УИД) + "   ";
                ora_com.ExecuteNonQuery();

            }
            catch (Exception ex)
            {
                MessageBox.Show("f13^ "+ex.Message);
            }



        }

       

        private void dataGridView1_CellBeginEdit(object sender, DataGridViewCellCancelEventArgs e)
        {

        }

      
        private void tab2_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private string str2pickingAdressFormat(string pa)
        {
            string ret = pa.Substring(0, 3) + "-" + pa.Substring(3, 2) + "-" + pa.Substring(5, 3) + "-" + pa.Substring(8, 3);
            return ret;
        }

        private void print_ispravitelnyi_list(string UID_ZAK , bool print1)
        {
            try
            {
            PPage _page = new PPage();
           

            string strSQL = "  select " +
              " err.SSCC , " +
              " err.CONDITION , " +
              " err.UNIT_COUNT , " +
              " err.UID1 , " +
              " err.EAN , " +
              " pr.SHORTNAME , " +
              " pr.PATH , " +
              " DOCID , " +
              " sysdate , " +
              " TIME_OF_AUDIT , PLAN_COUNT , SORTFIELD " +
              " from RABAEV.LOT_AUDIT_ERROR_LINES err  , RRL_SBORKA_PALLET_ROWS pr where ( err.UID1=pr.ARTICUL(+)  ) " +
              " and (pr.PALLET_UID= '" + UID_ZAK + "'  ) "+
              " and ( err.SSCC = '" + UID_ZAK + "' ) " +
              " order by CONDITION    ,SORTFIELD        ";

            textBox_Запрос.Text = textBox_Запрос.Text + "  " + strSQL + " ; ";
            
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = WMS_CONNECTION_STRING();
                ora_conn.Open();
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                _page.start_point_4_table.X=10;
                _page.start_point_4_table.Y=50;

                _page.add_column("ПОР", "string", "ПОР", 3);
                _page.add_column("АДРЕС", "string" , "АДРЕС" , 7 );
                _page.add_column("АРТИКУЛ", "string" ,"АРТИКУЛ" , 7 );
                _page.add_column("НАИМЕНОВАНИЕ", "string" , "НАИМЕНОВАНИЕ" , 20 );
                _page.add_column("СОСТОЯНИЕ", "string"  ,"СОСТОЯНИЕ" , 7);
                _page.add_column("ПО ПЛАНУ", "string" , "ПО ПЛАНУ" , 6 );
                _page.add_column("ПО ФАКТУ", "string", "ПО ФАКТУ" ,  6);
                _page.add_column("РАЗНИЦА", "string", "РАНИЦА" ,  6);

                string st_num = "";

                while (ora_reader.Read())
                {

                    object[] values1 = new object[12];
                    values1[0] = str2str(ora_reader.GetOracleString(0));
                    values1[1] = str2str(ora_reader.GetOracleString(1));
                    values1[2] = (ora_reader.GetOracleNumber(2).ToString());
                    values1[3] = str2str(ora_reader.GetOracleString(3));
                    values1[4] = str2str(ora_reader.GetOracleString(4));
                    values1[5] = str2str(ora_reader.GetOracleString(5));
                    values1[6] = str2str(ora_reader.GetOracleString(6));
                    values1[7] = str2str(ora_reader.GetOracleString(7));
                    values1[8] = (ora_reader.GetOracleValue(8).ToString());
                    values1[9] = (ora_reader.GetOracleValue(9).ToString());
                    values1[10] = ((ora_reader.GetOracleValue(10).ToString()));
                    values1[11] = ora_reader.GetOracleValue(11).ToString();

                    if (values1[10].ToString() == "Null")
                    {
                        values1[10] = 0;
                    }


                    string h_tovar_uid = values1[3].ToString();
                    string h_piking_addr = values1[6].ToString();
                    string h_product_name = values1[5].ToString();
                    st_num = values1[0].ToString();
                    Dictionary<string, string> _row = new Dictionary<string, string>();
                    _row["АДРЕС"] = values1[6].ToString();
                    _row["АРТИКУЛ"] = values1[3].ToString();
                    _row["НАИМЕНОВАНИЕ"] = values1[5].ToString();
                    _row["СОСТОЯНИЕ"] = values1[1].ToString();
                    _row["ПО ПЛАНУ"] = values1[10].ToString();
                    _row["ПО ФАКТУ"] = values1[2].ToString();
                    _row["ПОР"] = values1[11].ToString();
                    _row["РАЗНИЦА"] = Convert.ToString( (str2int( values1[10].ToString()) - str2int(values1[2].ToString())) ) ;                    
                    _page.add_row(_row);
                    

                }
                _page.labels.Add( new PPage.PLabel("Исправительный лист по паллету:"+st_num, new Point(10,10) , 14 ));
                ora_reader.Close();
                ora_conn.Close();
           

            PPages.Add(_page);

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {
                pd.DefaultPageSettings.Landscape = false;
                //if( pd.DefaultPageSettings.PrinterSettings.CanDuplex )
                // pd.DefaultPageSettings.PrinterSettings.Duplex = Duplex.Horizontal;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion

        }
        catch (Exception Ex)
        {
            MessageBox.Show("f15^ " + Ex.Message);
        }
        
        }




      

        private string double2sql_ora(double dt)
        {
            return dt.ToString().Replace(',','.') ;
        }
        
        private string date2sql(DateTime dt)
        {
            return "#" + dt.Month + "/" + dt.Day + "/" + dt.Year + "#";
        }

        private string date2sql_ora(DateTime dt)
        {

            
            return "'" + dt.Day + "." + dt.Month + "." + dt.Year + "'";

        }

        private DateTime  date2strip_time(DateTime dt)
        {
            return  Convert.ToDateTime("" + dt.Day + "." + dt.Month + "." + dt.Year + "");
        }

        private string datetime2sql_ora(DateTime dt)
        {
            return "'" + dt.Day + "." + dt.Month + "." + dt.Year + " "+dt.Second +":"+dt.Minute +":"+dt.Hour +"'";
        }

  


        private void ROUTEGridView2_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            try
            {

                DataGridViewRow dr = ((System.Windows.Forms.DataGridView)(sender)).CurrentRow;
                if (dr != null)
                {

                    string ROUTE_UID = obj2str(dr.Cells[0].Value);
                    string date1 = obj2str(dr.Cells[8].Value);
                    DateTime dt = Convert.ToDateTime(date1);

                    // ------------------------------------------------------------------------------------

                    dataGridView2.Rows.Clear();
                    try
                    {
                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;

                        mdb_comm.CommandText = " select УИД, НОМЕР, СБОРЩИК, КоличествоСтрочек , СТАТУС , ЗОНА_ФАКТИЧЕСКАЯ " +
                        " from ТранспортныеЗаданияСтроки   " +
                            "   where  ИДЕНТИФИКАТОР='" + ROUTE_UID + "' and ДатаТЗ=" + date2sql(dt) + "     ";

                        // textBox1.Text = mdb_comm.CommandText;

                        OleDbDataReader reader = mdb_comm.ExecuteReader();
                        while (reader.Read())
                        {
                            /*
                            int КоличествоСтрочек = Convert.ToInt32(reader[3].ToString() + "0");

                            if (КоличествоСтрочек == 0)
                            {
                                OracleConnection ora_conn3 = new OracleConnection();
                                ora_conn3.ConnectionString = SFERA_CONNECTION_STRING();
                                ora_conn3.Open();
                                OracleCommand ora_comm3 = new OracleCommand();
                                ora_comm3.Connection = ora_conn3;

                            }*/
                            object[] ob = new object[6];
                            ob[0] = reader[0].ToString();
                            ob[1] = reader[1].ToString();
                            ob[2] = reader[2].ToString();
                            ob[3] = reader[3].ToString();
                            ob[4] = reader[4].ToString();
                            ob[5] = reader[5].ToString();
                            dataGridView2.Rows.Add(ob);

                        }
                        reader.Close();
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show( "f18^"+ex.Message);
                    }



                }

            }
            catch (Exception ex)
            {
                MessageBox.Show("f23 "+ex.Message);
            }

        }

        private void timer1_Tick(object sender, EventArgs e)
        {

            // this.m_ConsoleTextBox.Text += Convert.ToString(  F_TO_DO.Count ) ;

            try {
                this.timer1.Enabled = false;

                lock (this.F_TO_DO)
                {
                    if (F_TO_DO.Count > 0) {
                        funct ft1= F_TO_DO[0];
                        F_TO_DO.Remove(ft1);
                       // this.m_ConsoleTextBox.Text += " \n\t "+ ft1.encode();
                        switch( ft1.function_name  )
                        {
                            case "PRINT_ERROR_LIST":
                                string UID_ORD = ft1.strToIntMap["UID_ORD"];
                                this.print_ispravitelnyi_list(UID_ORD , true );
                                break;
                            default:
                                break;
                        }

                    }
                
                }

                this.timer1.Enabled = true;

            }
            catch (Exception ex) {
               // this.m_ConsoleTextBox.Text += ex.Message;
            }


        }

        private void ROUTEGridView2_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {
            if ((e.ColumnIndex == 1 ) && (e.RowIndex>0))
            {

                 DataGridViewRow dr =((DataGridView)sender).Rows[e.RowIndex];
                 string ROUTE_UID = obj2str(dr.Cells[0].Value);
                 string vorota = obj2str(dr.Cells[1].Value);
                 DateTime date1 = Convert.ToDateTime(dr.Cells[8].Value);
                    try
                    {
                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;
                        mdb_comm.CommandText = " update ТранспортныеЗадания set ЗонаОтгрузочной='" + vorota + "'  " +
                            "   where  ИДЕНТИФИКАТОРМАРШРУТА='" + ROUTE_UID + "' and ДатаТЗ=" + date2sql(date1) + "     ";
                       mdb_comm.ExecuteNonQuery ();
                    }catch(Exception ex)
                    {
                        MessageBox.Show ( "f2r4 "+ex.Message );
                    }
            }
        }



        #region СРАВНЕНИЕ_ОСТАТКОВ

        private void button6_Click(object sender, EventArgs e)
        {

            // ************************************************************************************************
            // ************************************************************************************************
            // ************************************************************************************************
        

            dataGridCompare.Rows.Clear();

            string strSQL = "  select " +
              " М.ГР_ТМЦ_УИД , " +
              " ОТ.КОЛИЧЕСТВО , " +
              " ОТ.РЕЗЕРВ , (ОТ.КОЛИЧЕСТВО )  КОЛИЧЕСТВО_ИТОГО , " +
              " М.УИД  , М.Наименование  , О.НАИМЕНОВАНИЕ " +
              " from " +
              "     R.ТЕКУЩИЕ_ОСТАТКИ ОТ, " +
              "    R.МАТЕРИАЛЫ М, " +
              "     R.ОРГАНИЗАЦИИ О   " +
              "  where  " +
              "  ОТ.ТМЦ_УИД=М.УИД and " +
              "  ОТ.ОРГ_УИД=О.УИД  " +
              " and ( О.НАИМЕНОВАНИЕ = 'скл. отв. хранения' )  ";
            // Присоединяемся к сфере, делаем запрос
// ==========================================================================================================
// ==========================================================================================================
// ==========================================================================================================

            OracleCommand ora_com = new OracleCommand();
            Dictionary<long, long> СоответствиеСтрокИУидов = new Dictionary<long, long>();




           
            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = SFERA_CONNECTION_STRING ();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {

                    object[] ob = new object[6];
                    long СФЕРА_ГР_ТМЦ_УИД = (ora_reader.GetInt64 (0));
                    long СФЕРА_КОЛИЧЕСТВО_ШТУК = (ora_reader.GetInt64(3));
                    long СФЕРА_ПРОДУКТ_УИД = (ora_reader.GetInt64(4));
                    string СФЕРА_ПРОДУКТ_НАИМЕНОВАНИЕ = str2str(ora_reader.GetOracleString(5));

                    // ============================ ******************* =============================

                    ob[0] = СФЕРА_ПРОДУКТ_УИД;
                    ob[1]  = СФЕРА_КОЛИЧЕСТВО_ШТУК;
                    ob[2] =0;
                    ob[3]  = СФЕРА_ПРОДУКТ_НАИМЕНОВАНИЕ;
                    ob[4]  = СФЕРА_ГР_ТМЦ_УИД;
                    ob[5] = "есть В СФЕРЕ нет в WMS";
                    long п_НомерСтроки =  dataGridCompare.Rows.Add(ob);

                    СоответствиеСтрокИУидов.Add(СФЕРА_ПРОДУКТ_УИД,   п_НомерСтроки);
                }

                ora_reader.Close();


                // БЕРЕМ ИЗ СФЕРЫ ВСЕ ТОВАРЫ ПО ОТВЕТ-ХРАНЕНИЮ 
                strSQL = " select  УИД  from  R.МАТЕРИАЛЫ WHERE   ГР_ТМЦ_УИД = 2950  ";
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader4 = ora_com.ExecuteReader();
                string sqlAdd = "";
                while (ora_reader4.Read())
                {
                    sqlAdd = sqlAdd + "," + Convert.ToString  (ora_reader4.GetInt64(0)) ;
                }
                sqlAdd= sqlAdd.Trim(',');
                // ВЗЯЛИ ВСЕ ТОВАРЫ



                // ТЕПЕРЬ ИДЕМ В WMS
                string strSQL2 = "select  " + 
                "  UL_CPROIN УИД ,  " + 
                "  sum(UL_NQTUVC) КОЛИЧЕСТВО ,  " + 
                "  AR_LIBPRO  НАИМЕНОВАНИЕ  " + 
                " from refstock.TB_LCUMS   " + 
                " left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM'  " + 
                " left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM'  " + 
                " left join refstock.tb_traums on ue_usscc=ut_usscc and ul_numlig=ut_numlig  " + 
                " left join refstock.TB_RACK on rk_depot='01' and ue_zone=rk_zone and ue_allee=rk_allee and ue_travee=rk_travee and rk_niveau=ue_niveau  " + 
                " left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID  " + 
                " where ul_donord='RM'  " + 
                " and ul_numorl is null   " +
                " and ul_nqtuvc<>0  " +
                " and   UL_CPROIN in (" + sqlAdd + ")  " +
                " group by   UL_CPROIN ,  AR_LIBPRO ";
                OracleCommand ora_com_WMS = new OracleCommand();
                OracleConnection ora_conn_WMS = new OracleConnection();
                ora_conn_WMS.ConnectionString = WMS_CONNECTION_STRING();
                ora_conn_WMS.Open();
                ora_com_WMS.Connection = ora_conn_WMS;
                ora_com_WMS.CommandText = strSQL2;
                OracleDataReader ora_reader_WMS = ora_com_WMS.ExecuteReader();

                while (ora_reader_WMS.Read())
                { 
                    // ========================================================================

                    object[] ob = new object[6];
                    long УИД =    Convert.ToInt64(ora_reader_WMS.GetValue(0).ToString());
                    long WMS_КОЛИЧЕСТВО_ШТУК =  Convert.ToInt64( (ora_reader_WMS.GetValue(1).ToString()));
                    string WMS_ПРОДУКТ_НАИМЕНОВАНИЕ = str2str(ora_reader_WMS.GetOracleString(2));


                    long л_номерСтроки =0 ;
                    if (СоответствиеСтрокИУидов.TryGetValue(УИД, out л_номерСтроки))
                    {
                        dataGridCompare.Rows[(int)л_номерСтроки].Cells[2].Value  = WMS_КОЛИЧЕСТВО_ШТУК;
                        long C_КОЛИЧЕСТВО_ШТУК =Convert.ToInt64( dataGridCompare.Rows[(int)л_номерСтроки].Cells[1].Value.ToString());
                        if (C_КОЛИЧЕСТВО_ШТУК > WMS_КОЛИЧЕСТВО_ШТУК) {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "СФЕРА>WMS";
                        }

                        if (C_КОЛИЧЕСТВО_ШТУК < WMS_КОЛИЧЕСТВО_ШТУК)
                        {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "WMS>СФЕРА";
                        }

                        if (C_КОЛИЧЕСТВО_ШТУК == WMS_КОЛИЧЕСТВО_ШТУК)
                        {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "=";
                        }


                    }else{ // Если продукт в остатках сферы не значится
                        ob[0] = УИД;
                        ob[1] = 0;
                        ob[2] = WMS_КОЛИЧЕСТВО_ШТУК;
                        ob[3] = WMS_ПРОДУКТ_НАИМЕНОВАНИЕ;
                        ob[4] = 0;
                        ob[5] = "НЕТ В СФЕРЕ ЕСТЬ В WMS";
                        dataGridCompare.Rows.Add(ob);
                    }


                    // ========================================================================
                }

                ora_conn_WMS.Close();
                ora_conn.Close();


                foreach( DataGridViewRow dr in  dataGridCompare.Rows)
                {
                    if ((  Convert.ToInt64( dr.Cells[1].Value) == 0) && ( Convert.ToInt64( dr.Cells[2].Value ) == 0))
                    {
                        dataGridCompare.Rows.Remove(dr);
                    }

                }
                

                MessageBox.Show("Процедура сравнения остатков закончена.");
            }
            catch (Exception Ex)
            {
                MessageBox.Show( "f67 "+Ex.Message);
            }

        // ************************************************************************************************
        // ************************************************************************************************
        // ************************************************************************************************

        }


        #region ЗАПРОС_ОСТАТКОВ_ПО_СКЛ_РМ

        private void button8_Click(object sender, EventArgs e)
        {

            // ************************************************************************************************
            // ************************************************************************************************
            // ************************************************************************************************


            dataGridCompare.Rows.Clear();

            string strSQL = "  select " +
              " М.ГР_ТМЦ_УИД , " +
              " sum (ОТ.КОЛИЧЕСТВО) КОЛИЧЕСТВО , " +
              " sum(ОТ.РЕЗЕРВ) , sum (ОТ.КОЛИЧЕСТВО ) КОЛИЧЕСТВО_ИТОГО , " +
              " М.УИД  , М.Наименование , R.RRL_FGET_PRICE(М.УИД ) as ЦЕНА1  " +
              " from " +
              "     R.ТЕКУЩИЕ_ОСТАТКИ ОТ, " +
              "    R.МАТЕРИАЛЫ М, " +
              "     R.ОРГАНИЗАЦИИ О   " +
              "  where  " +
              "  ОТ.ТМЦ_УИД=М.УИД and " +
              "  ОТ.ОРГ_УИД=О.УИД  " +
              " and ( (О.НАИМЕНОВАНИЕ = 'скл.РМ') or ( О.НАИМЕНОВАНИЕ = 'скл. отв. хранения' ) ) "+
              " group by М.ГР_ТМЦ_УИД ,   М.УИД  , М.Наименование   ";
            // Присоединяемся к сфере, делаем запрос
            // ==========================================================================================================
            // ==========================================================================================================
            // ==========================================================================================================

            OracleCommand ora_com = new OracleCommand();
            Dictionary<long, long> СоответствиеСтрокИУидов = new Dictionary<long, long>();





            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = SFERA_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {

                    object[] ob = new object[7];
                    long СФЕРА_ГР_ТМЦ_УИД = (ora_reader.GetInt64(0));
                    long СФЕРА_КОЛИЧЕСТВО_ШТУК = (ora_reader.GetInt64(3));
                    long СФЕРА_ПРОДУКТ_УИД = (ora_reader.GetInt64(4));
                    string СФЕРА_ПРОДУКТ_НАИМЕНОВАНИЕ = str2str(ora_reader.GetOracleString(5));

                    // ============================ ******************* =============================

                    ob[0] = СФЕРА_ПРОДУКТ_УИД;
                    ob[1] = СФЕРА_КОЛИЧЕСТВО_ШТУК;
                    ob[2] = 0;
                    ob[3] = СФЕРА_ПРОДУКТ_НАИМЕНОВАНИЕ;
                    ob[4] = СФЕРА_ГР_ТМЦ_УИД;
                    ob[5] = "есть В СФЕРЕ нет в WMS";
                    ob[6] = (ora_reader.GetDouble(6));
                    
                    long п_НомерСтроки = dataGridCompare.Rows.Add(ob);

                    СоответствиеСтрокИУидов.Add(СФЕРА_ПРОДУКТ_УИД, п_НомерСтроки);
                }

                ora_reader.Close();

                /*
                // БЕРЕМ ИЗ СФЕРЫ ВСЕ ТОВАРЫ ПО ОТВЕТ-ХРАНЕНИЮ 
                strSQL = " select  УИД  from  R.МАТЕРИАЛЫ WHERE   ГР_ТМЦ_УИД = 2950  ";
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader4 = ora_com.ExecuteReader();
                string sqlAdd = "";
                while (ora_reader4.Read())
                {
                    sqlAdd = sqlAdd + "," + Convert.ToString(ora_reader4.GetInt64(0));
                }
                sqlAdd = sqlAdd.Trim(',');
                // ВЗЯЛИ ВСЕ ТОВАРЫ
                */


                // ТЕПЕРЬ ИДЕМ В WMS
                string strSQL2 = "select  " +
                "  UL_CPROIN УИД ,  " +
                "  sum(UL_NQTUVC) КОЛИЧЕСТВО ,  " +
                "  AR_LIBPRO  НАИМЕНОВАНИЕ  " +
                " from refstock.TB_LCUMS   " +
                " left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM'  " +
                " left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM'  " +
                " left join refstock.tb_traums on ue_usscc=ut_usscc and ul_numlig=ut_numlig  " +
                " left join refstock.TB_RACK on rk_depot='01' and ue_zone=rk_zone and ue_allee=rk_allee and ue_travee=rk_travee and rk_niveau=ue_niveau  " +
                " where ul_donord='RM'  " +
                " and ul_numorl is null   " +
                " and ul_nqtuvc<>0  " +
                " group by   UL_CPROIN ,  AR_LIBPRO ";
                OracleCommand ora_com_WMS = new OracleCommand();
                OracleConnection ora_conn_WMS = new OracleConnection();
                ora_conn_WMS.ConnectionString = WMS_CONNECTION_STRING();
                ora_conn_WMS.Open();
                ora_com_WMS.Connection = ora_conn_WMS;
                ora_com_WMS.CommandText = strSQL2;
                OracleDataReader ora_reader_WMS = ora_com_WMS.ExecuteReader();

                while (ora_reader_WMS.Read())
                {
                    // ========================================================================

                    object[] ob = new object[6];
                    long УИД = Convert.ToInt64(ora_reader_WMS.GetValue(0).ToString());
                    long WMS_КОЛИЧЕСТВО_ШТУК = Convert.ToInt64((ora_reader_WMS.GetValue(1).ToString()));
                    string WMS_ПРОДУКТ_НАИМЕНОВАНИЕ = str2str(ora_reader_WMS.GetOracleString(2));


                    long л_номерСтроки = 0;
                    if (СоответствиеСтрокИУидов.TryGetValue(УИД, out л_номерСтроки))
                    {
                        dataGridCompare.Rows[(int)л_номерСтроки].Cells[2].Value = WMS_КОЛИЧЕСТВО_ШТУК;
                        long C_КОЛИЧЕСТВО_ШТУК = Convert.ToInt64(dataGridCompare.Rows[(int)л_номерСтроки].Cells[1].Value.ToString());
                        if (C_КОЛИЧЕСТВО_ШТУК > WMS_КОЛИЧЕСТВО_ШТУК)
                        {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "СФЕРА>WMS";
                        }

                        if (C_КОЛИЧЕСТВО_ШТУК < WMS_КОЛИЧЕСТВО_ШТУК)
                        {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "WMS>СФЕРА";
                        }

                        if (C_КОЛИЧЕСТВО_ШТУК == WMS_КОЛИЧЕСТВО_ШТУК)
                        {
                            dataGridCompare.Rows[(int)л_номерСтроки].Cells[5].Value = "=";
                        }

                    }
                    else
                    { // Если продукт в остатках сферы не значится
                        ob[0] = УИД;
                        ob[1] = 0;
                        ob[2] = WMS_КОЛИЧЕСТВО_ШТУК;
                        ob[3] = WMS_ПРОДУКТ_НАИМЕНОВАНИЕ;
                        ob[4] = 0;
                        ob[5] = "НЕТ В СФЕРЕ ЕСТЬ В WMS";
                        dataGridCompare.Rows.Add(ob);
                    }
                    

                    // ========================================================================
                }

                ora_conn_WMS.Close();
                ora_conn.Close();



                //=========================================================================================

                 ora_conn = new OracleConnection();
                ora_conn.ConnectionString = SFERA_CONNECTION_STRING();
                ora_conn.Open();

 

                //=========================================================================================

                foreach (DataGridViewRow dr in dataGridCompare.Rows)
                {
                    if ((Convert.ToInt64(dr.Cells[1].Value) == 0) && (Convert.ToInt64(dr.Cells[2].Value) == 0))
                    {
                        dataGridCompare.Rows.Remove(dr);
                    }
                    else {  

                    }      

                }


                MessageBox.Show("Процедура сравнения остатков закончена.");
            }
            catch (Exception Ex)
            {
                MessageBox.Show("fyh "+Ex.Message);
            }

            // ************************************************************************************************
            // ************************************************************************************************
            // ************************************************************************************************


        }

        #endregion


        #endregion

        private void button7_Click(object sender, EventArgs e)
        {
            grid_2_excel( dataGridCompare  );
        }

        private void grid_2_excel(DataGridView dgv)
        {

            try
            {

                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                oExcelApp.Workbooks.Add("");

                long pos = 0;
                foreach (DataGridViewColumn dgvc in dgv.Columns)
                {
                    pos++;
                    oExcelApp.Cells[1, pos] = dgvc.HeaderText;
                }

                long pos2 = 1;
                foreach (DataGridViewRow dr in dgv.Rows)
                {
                    pos2++;
                    pos = 0;
                    foreach (DataGridViewCell dgvc2 in dr.Cells)
                    {
                        pos++;
                        oExcelApp.Cells[pos2, pos] = dgvc2.Value;
                    }
                }
                MessageBox.Show("Данные выгружены в Excel");
            }catch(Exception ex)
            {
                MessageBox.Show( "rtg "+ex.Message );
            }

        
        }

        private void button10_Click(object sender, EventArgs e)
        {

            string TTT = textBox2.Text ;
            Image r = Code128Rendering.MakeBarcodeImage(TTT, 3, true);
            ZONEpictureBox1.Image = r;
            string filename="C://g//" + TTT + ".gif" ;
            r.Save(filename, System.Drawing.Imaging.ImageFormat.Gif);
            MessageBox.Show(" Файл сохранен: "+filename);
          
        }

       
        private void dateTimePicker3_ValueChanged(object sender, EventArgs e)
        {

        }


        public void fill_view_MINI_WMS( DataGridView dgv1 , string strSQL , int column_fill_count )
        {
            dgv1.Rows.Clear();
            OracleCommand ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;
            long m_count = 0;
            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = MINI_WMS_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {
                    object[] values1 = new object[column_fill_count];
                    for (int yy = 0;yy < column_fill_count ;yy++ )
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }
                    dgv1.Rows.Add(values1);
                    m_count++;
                }

                ora_reader.Close();
                ora_conn.Close();
            }
            catch (Exception Ex)
            {
                MessageBox.Show( " f344 "+Ex.Message);
            }
            dgv1.Columns[0].ToolTipText = m_count.ToString()+" = количество записей";
       
        }

        /*

        private void fill_view_MINI_WMS2(DataGridView dgv1, string strSQL, int column_fill_count , List< List<string> > l_options )
        {
            dgv1.Rows.Clear();
            OracleCommand ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;
            long m_count = 0;
            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = MINI_WMS_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {
                    object[] values1 = new object[column_fill_count];
                    for (int yy = 0; yy < column_fill_count; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }
                    dgv1.Rows.Add(values1);
                    foreach (List<string> l_opt in l_options)
                    {
                        if (l_opt.Count == 3)
                        {
                            if (values1[Convert.ToInt32(l_opt[0])] == l_opt[1])
                            { 
                                dgv1.Rows[dgv1.Rows.Count-1].Cells[Convert.ToInt32(l_opt[0])].Style.ForeColor = new Color
                            }
                        }
                    }
                    m_count++;
                }

                ora_reader.Close();
                ora_conn.Close();
            }
            catch (Exception Ex)
            {
                MessageBox.Show(" f344 " + Ex.Message);
            }
            dgv1.Columns[0].ToolTipText = m_count.ToString() + " = количество записей";

        }
        */

        


        // Выводим список приходов
        private void prihod_button_Click(object sender, EventArgs e)
        {
            
            
            
            string strSQL = " SELECT SM_NAKLAD_NUMBER , DATE_OF_NAKLAD , ZAKAZ_NUMBER , POSTAVSHIK_NAME , NAKLAD_NUMBER, CONDITION , ID , DATE_OF_ACCEPT  " +
            "  FROM rabaev.RRL_prihod_naklad where ( DATE_OF_ACCEPT >= " + date2sql_ora(Prihod_from.Value ) + " ) and ( DATE_OF_ACCEPT <= " + date2sql_ora(prihod_to.Value ) +" ) and ware_id="+this.wms_user.ware_id.ToString();

            try
            {
                if (Convert.ToInt32(id_search_prihod.Text)>0)
                {
                    strSQL = " SELECT SM_NAKLAD_NUMBER , DATE_OF_NAKLAD , ZAKAZ_NUMBER , POSTAVSHIK_NAME , NAKLAD_NUMBER, CONDITION , ID , DATE_OF_ACCEPT  " +
                    "  FROM rabaev.RRL_prihod_naklad where   ID=" + id_search_prihod.Text.ToString();

                }

            }
            catch { 
            
            }

            
            fill_view_MINI_WMS(dataGridView_prihod, strSQL, 8);
            return;
        }






        // Добавление Новой накладной
        private void dataGridView_prihod_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            // ===================================================================================================


            OracleCommand ora_com;
            try
            {

                string SM_naklad ;
                string SM_zakaz;

                DateTime Date_naklad ;
                DateTime Date_acc ;
                string postavshik ;
                string Naklad_postavshik ;

                DataGridViewRow dr = dataGridView_prihod.CurrentRow;
                try
                {
                     SM_naklad = obj2str(dr.Cells[0].Value);
                     Date_naklad = Convert.ToDateTime(dr.Cells[1].Value);
                     SM_zakaz = obj2str(dr.Cells[2].Value);
                     Date_acc = DateTime.Today;
                     postavshik = obj2str(dr.Cells[3].Value);
                     Naklad_postavshik = obj2str(dr.Cells[4].Value);
                     if (Date_naklad.Year < 2009)
                     {
                         Date_naklad = DateTime.Today;
                     }
                }catch
                {
                    return;
                }


                if (dr.Cells[6].Value == null )
                { // Инсертим
                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "ADD_RRL_PRIH_NAKLAD2";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    if (SM_naklad == "" || SM_naklad == null)
                    {

                        SM_naklad = Nomer_naklad_po_nomeru_zakaza(SM_zakaz);
                        if (SM_naklad == "" || SM_naklad == null)
                        SM_naklad = SM_zakaz;
                    }
                    ora_com.Parameters.Add("NAKLAD_NUMBER", OracleType.VarChar).Value = Naklad_postavshik;
                    ora_com.Parameters.Add("DATE_OF_NAKLAD", OracleType.DateTime).Value = Date_naklad;
                    ora_com.Parameters.Add("DATE_OF_ACCEPT", OracleType.DateTime).Value = Date_acc;
                    ora_com.Parameters.Add("POSTAVSHIK_NAME", OracleType.VarChar).Value = postavshik;
                    ora_com.Parameters.Add("SM_NAKLAD_NUMBER", OracleType.Char).Value = SM_naklad;
                    ora_com.Parameters.Add("ZAKAZ_NUMBER1", OracleType.Char).Value = SM_zakaz;

                    
                    ora_com.Parameters.Add("ware_id1", OracleType.Int32  ).Value = this.wms_user.ware_id ;

                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    dr.Cells[6].Value = ora_com.Parameters["ID"].Value;

                    // инсертим
                }else { // Апдейтим


                    if (SM_naklad == "" || SM_naklad == null)
                    {

                        SM_naklad = Nomer_naklad_po_nomeru_zakaza(SM_zakaz);
                        if (SM_naklad == "" || SM_naklad == null)
                            SM_naklad = SM_zakaz;
                    }

                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "update RABAEV.RRL_PRIHOD_NAKLAD set ZAKAZ_NUMBER='" + SM_zakaz + "' , SM_NAKLAD_NUMBER ='" + Convert.ToString(SM_naklad) + "' , NAKLAD_NUMBER = '" + Convert.ToString(Naklad_postavshik) + "'  , DATE_OF_NAKLAD = " + date2sql_ora(Date_naklad) + " , POSTAVSHIK_NAME='" + postavshik + "'    " +
                    " where ID=" + Convert.ToString(dr.Cells[6].Value.ToString()) + "   ";
                    ora_com.ExecuteNonQuery();

                } // Апдейтим

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f35 " + ex.Message);
            }


            // ===================================================================================================
        }

        private void dataGridView5_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            OracleCommand ora_com;

            DataGridViewRow parent_dr =  dataGridView_prihod.CurrentRow;
            if ( Convert.ToInt64( parent_dr.Cells[5].Value) > 0)
            {
                MessageBox.Show("Накладная закрыта, изменения не возможны");
                return; }
            DataGridViewRow dr = ((System.Windows.Forms.DataGridView)(sender)).CurrentRow;
            

            try
            {

            string articul = obj2str(dr.Cells[0].Value);
            double count1 = Convert.ToDouble (dr.Cells[1].Value);
            double price = Convert.ToDouble(dr.Cells[2].Value);

            int NU = 0;
            try
            {
                NU = Convert.ToInt32(dr.Cells[5].Value);
            }
            catch { }
                
            DateTime expiry_date = DateTime.Today.AddDays(365);
            try
            {
                 expiry_date = Convert.ToDateTime(dr.Cells[3].Value);
            }
            catch { 
            
            }

                if(   dr.Cells[4].Value==null ){
                if (articul.Length>1)
                    if ((Convert.ToInt64(parent_dr.Cells[6].Value.ToString()) > 0) && (expiry_date > DateTime.Today) && (count1 > 0) && ((articul.Substring(0, 1) == "Т") || (articul.Substring(0, 1) == "Т")))
                {   // ===============================================================================================
                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "ADD_RRL_PRIH_NAKLAD_ROW";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    long Naklad_ID = Convert.ToInt64(parent_dr.Cells[6].Value.ToString());

                    ora_com.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = Naklad_ID;
                    ora_com.Parameters.Add("articul", OracleType.VarChar).Value = articul;
                    ora_com.Parameters.Add("expiury_date", OracleType.DateTime).Value = expiry_date;
                    ora_com.Parameters.Add("count1", OracleType.Number).Value = count1;
                    ora_com.Parameters.Add("price", OracleType.Number).Value = price;


                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    dr.Cells[4].Value = ora_com.Parameters["ID"].Value;

                    // ===============================================================================================
                }
                }else{
                // обновление строчек накладных 
                    string row_id = dr.Cells[4].Value.ToString();
                    string sql23 = "";
                    if(NU>0) sql23=" , KOLPAL= " + NU.ToString() + " ";

                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "update RABAEV.RRL_PRIHOD_NAKLAD_ROWS set "+
                        " ARTICUL ='" + Convert.ToString(articul) + "' , " +
                        " COUNT1 = '" + Convert.ToString(count1) + "'  , " +
                        " EXPIRY_DATE = " + date2sql_ora(expiry_date) + " , " +
                        " PRICE='" + Convert.ToString(price) + "'    " +
                        sql23 +
                        " where ID=" + row_id + "   ";
                    ora_com.ExecuteNonQuery();




                // обновление строчек накладных
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f36 " + ex.Message);
            }

        }

        private void dataGridView_prihod_CellEnter(object sender, DataGridViewCellEventArgs e)
        {


            DataGridViewRow dr = (dataGridView_prihod).CurrentRow;
            string order_id = obj2str(dr.Cells[6].Value);
            long condition = Convert.ToInt64  (dr.Cells[5].Value);

            if (condition == 0) // Редактируется
            {
                Закрыть.Enabled = true;
                Разместить.Enabled = false ;
                Откатить.Enabled = false ;
                Сторнировать_приход.Enabled = false;
            }

            if (condition == 1) // закрыта
            {
                Закрыть.Enabled = false;
                Разместить.Enabled = true;
                Откатить.Enabled = true ;
                Сторнировать_приход.Enabled = false;
            }

            if (condition == 2) // Размещена
            {
                Закрыть.Enabled = false;
                Разместить.Enabled = false;
                Откатить.Enabled = false;
                Сторнировать_приход.Enabled = has_right("STORNO_PRIHOD");
            }

            if (condition == 3) // Сторнирована
            {
                Закрыть.Enabled = false;
                Разместить.Enabled = false;
                Откатить.Enabled = false;
                Сторнировать_приход.Enabled = false;
            }


            if (order_id != "")
            {
                string strSQL = " SELECT RR.ARTICUL , RR.COUNT1 , RR.PRICE , RR.EXPIRY_DATE , RR.ID , RR.kolpal , rrl_articuls.NAME " +
               "  FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS RR , rrl_articuls where ORDID = " + order_id + " and  "+
               " rrl_articuls.acticul=RR.ARTICUL ";
                fill_view_MINI_WMS(dataGridView5, strSQL, 7);
            }
            else {
                dataGridView5.Rows.Clear();
            }

            #region ОБНОВЛЕНИЕ СТРОК ПАЛЛЕТ
                
                if (dataGridView_prihod.CurrentRow.Cells[0].Value == null)
                {
                    dataGrid_pallets.Rows.Clear();
                    return;
                }

                if (dataGridView_prihod.CurrentRow != null)
                {
                    if (dataGridView_prihod.CurrentRow.Cells[6].Value!=null)
                    {
                    string h_order_id = dataGridView_prihod.CurrentRow.Cells[6].Value.ToString();
                    string strSQL7 = " select RR.UID_PALLET  , RR.ARTICUL , RR.UNIT_COUNT  , RR.PRIHOD_NAKLAD_ID , RR.EXPIRY_DATE , "+
                        " RR.CREATION_DATE , RABAEV.RRL_INFO_PALLET_RESTS(UID_PALLET) , " +
                        " int2bool(PRINTED) , RR.CREATION_DATE , AA.Name from  RABAEV.RRL_PALLETS RR , rrl_articuls AA " +
                         " where PRIHOD_NAKLAD_ID=" + h_order_id + " and RR.ARTICUL=AA.acticul order by  AA.Name , RR.CREATION_DATE   ";

                    fill_view_MINI_WMS(dataGrid_pallets, strSQL7, 10 );

                    }
                }
            #endregion

        }

        private void dataGridView_prihod_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void Закрыть_Click(object sender, EventArgs e)
        {
            try
            {
                dataGridView_prihod.CurrentRow.Cells[5].Value = 1;
                int order_id = Convert.ToInt32(dataGridView_prihod.CurrentRow.Cells[6].Value.ToString());

                // ===========================================================

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();

                ora_com.CommandText = "RRL_ACCEPT_ORDER2_3";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("order_id", OracleType.Int32).Value = order_id;
                ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;

                ora_com.Parameters.Add("ret", OracleType.Int32 ).Direction =  ParameterDirection.ReturnValue;

                int rowsAffected = ora_com.ExecuteNonQuery();

            }catch(Exception ex)
            {
                MessageBox.Show(" f37 " + ex.Message);
            }

            dataGridView_prihod_CellEnter(null, null);

        }

        private void Откатить_Click(object sender, EventArgs e)
        {

            OracleCommand ora_com;
            dataGridView_prihod.CurrentRow.Cells[5].Value = 0;
            string order_id = dataGridView_prihod.CurrentRow.Cells[6].Value.ToString();


            OracleCommand ora_com2 = new OracleCommand();
            ora_com2.Connection = get_wms_connection();

            ora_com2.CommandText = "RRL_OTKAT_ORDER2";
            ora_com2.CommandType = CommandType.StoredProcedure;
            ora_com2.Parameters.Add("order_id", OracleType.Int32).Value = order_id;
            int rowsAffected = ora_com2.ExecuteNonQuery();

            dataGridView_prihod_CellEnter(null, null);


        }



        private void Разместить_Click(object sender, EventArgs e)
        {
            try
            {
                dataGridView_prihod.CurrentRow.Cells[5].Value = 2;
                int order_id = Convert.ToInt32(dataGridView_prihod.CurrentRow.Cells[6].Value.ToString());

                // ===========================================================

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();

                ora_com.CommandText = "RRL_ACCEPT_ORDER3";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("order_id", OracleType.Int32).Value = order_id;
                ora_com.Parameters.Add("user_id1", OracleType.VarChar ).Value = "KLAD_RABAEV";

                int rowsAffected = ora_com.ExecuteNonQuery();

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f38 " + ex.Message);
            }
            dataGridView_prihod_CellEnter(null, null);

        }

        private void dataGridView5_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            /*
            if (dataGridView5.CurrentRow.Cells[0].Value == null)
            {
                dataGrid_pallets.Rows.Clear();
                return;
            }


            string h_articul = dataGridView5.CurrentRow.Cells[0].Value.ToString();
            string h_order_id = dataGridView_prihod.CurrentRow.Cells[6].Value.ToString();
            string strSQL = " select UID_PALLET  , ARTICUL , UNIT_COUNT  , PRIHOD_NAKLAD_ID , EXPIRY_DATE , CREATION_DATE , RABAEV.RRL_INFO_PALLET_RESTS(UID_PALLET)  from  RABAEV.RRL_PALLETS  " +
                " where PRIHOD_NAKLAD_ID=" + h_order_id + "  and ARTICUL='" + h_articul + "' ";

            fill_view_MINI_WMS(dataGrid_pallets, strSQL, 7);
            */
        }



        private  void pd_PrintPage(object sender, PrintPageEventArgs ev)
        {

            // НУЖНО Добавить:
            // НАИМЕНОВАНИЕ ,  АДРЕС ОТБОРА , СРОК ГОДНОСТИ ,

            float leftMargin = ev.MarginBounds.Left;
            float topMargin = ev.MarginBounds.Top;

            // Calculate the number of lines per page.


            Font printFont = new Font("ARIAL", 42, FontStyle.Bold, GraphicsUnit.Pixel );
            Font printFont_small = new Font("ARIAL", 24, FontStyle.Bold, GraphicsUnit.Pixel);
            Font printFont_BIG = new Font("ARIAL", 120, FontStyle.Bold, GraphicsUnit.Pixel);


            ev.HasMorePages = false;

            string h_UID_PALLET="";
            if( dataGrid_pallets.CurrentRow!= null ){
                 h_UID_PALLET = dataGrid_pallets.CurrentRow.Cells[0].Value.ToString();
            }

            if ( (dataGridView8.RowCount > 0) &&  ( dataGridView8.Rows[0].Cells[0].Value!=null  ) )
            {
                h_UID_PALLET = dataGridView8.Rows[0].Cells[0].Value.ToString();
                dataGridView8.Rows.Remove(dataGridView8.Rows[0]);
                if (dataGridView8.Rows.Count >0)
                ev.HasMorePages = true;
            }

            if (h_UID_PALLET == "")
            {
                MessageBox.Show("нечего печатать");
                return;
            }



            string strSQL = " select UID_PALLET  , RRL_PALLETS.ARTICUL , UNIT_COUNT  , PRIHOD_NAKLAD_ID , EXPIRY_DATE , CREATION_DATE , RRL_ARTICULS.NAME , RRL_ARTICULS.CELL , RRL_ARTICULS.UNIT_TYPE  from  RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL and  UID_PALLET='" + h_UID_PALLET + "' ";

            // ==============================================================================

            OracleCommand ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;

            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = MINI_WMS_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {
                    object[] values1 = new object[9];
                    for (int yy = 0; yy < 9; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }

                    string h_articul  = values1[1].ToString();
                    string h_unit_count = values1[2].ToString();
                    string PRIHOD_NAKLAD_ID = values1[3].ToString();
                    DateTime EXPIRY_DATE = Convert.ToDateTime(values1[4]);
                    DateTime CREATION_DATE = Convert.ToDateTime(values1[5]);
                    string h_name = values1[6].ToString();
                    string h_cell = values1[7].ToString();
                    string h_UNIT_TYPE = values1[8].ToString();

                    
                    // ================================================================

                    Image r = Code128Rendering.MakeBarcodeImage(h_UID_PALLET, 2, true);
                    //pictureBox_pallet_label.Image = r;
                    //r.Save("C://g//" + TTT + ".gif", System.Drawing.Imaging.ImageFormat.Gif);

                    ev.Graphics.DrawString("артикул: " + h_articul + " ;    кол-во: " + h_unit_count + " " + h_UNIT_TYPE + "  накл:" + PRIHOD_NAKLAD_ID + "   id паллета:" + h_UID_PALLET , printFont_small , Brushes.Black, 100, 700, new StringFormat());
                    ev.Graphics.DrawString(  "товар принят: "+CREATION_DATE.ToString()  , printFont_small , Brushes.Black, 100, 730, new StringFormat());

                    if (h_name.Length > 40)
                    {
                        ev.Graphics.DrawString(h_name.Substring(0, 40), printFont, Brushes.Black, 100, 100, new StringFormat());
                        ev.Graphics.DrawString(h_name.Substring(40, h_name.Length - 40), printFont, Brushes.Black, 100, 150, new StringFormat());
                    }
                    else {
                        ev.Graphics.DrawString(h_name , printFont, Brushes.Black, 100, 100, new StringFormat());
                    }

                    ev.Graphics.DrawString( h_cell, printFont_BIG, Brushes.Black, 150, 200, new StringFormat());
                    ev.Graphics.DrawString( "" + EXPIRY_DATE.Day + "." + EXPIRY_DATE.Month + "." + EXPIRY_DATE.Year  , printFont_BIG, Brushes.Black, 
                        250, 500, new StringFormat());
                   // ev.Graphics.DrawString(CREATION_DATE, printFont, Brushes.Black, 100, 100, new StringFormat());
                   // ev.Graphics.DrawString(PRIHOD_NAKLAD_ID, printFont, Brushes.Black, 100, 100, new StringFormat());
                   // ev.Graphics.DrawString(h_unit_count, printFont, Brushes.Black, 100, 100, new StringFormat());

                    ev.Graphics.DrawImage(r,200,330);


                }

                ora_reader.Close();
                ora_conn.Close();
            }
            catch (Exception Ex)
            {
                MessageBox.Show(" f39 " + Ex.Message);
            }

            // ==============================================================================


           //
        }


        private PPage get_prihod_pallet_print_page(string h_UID_PALLET , string option )
        {


            #region САМА_ПЕЧАТЬ

            PPage _page = new PPage();


            string strSQL = " select UID_PALLET  , RRL_PALLETS.ARTICUL , UNIT_COUNT  , PRIHOD_NAKLAD_ID , "+
                " EXPIRY_DATE , CREATION_DATE , RRL_ARTICULS.NAME , "+
                " RRL_ARTICULS.CELL , RRL_ARTICULS.UNIT_TYPE , RRL_ARTICULS.BARCODE_SHT , RABAEV.RRL_DAY_DISTRIBUTE_ENDS( RRL_PALLETS.ARTICUL , EXPIRY_DATE )  De , RRL_PALLETS.KLADOVSHIK  , RRL_ARTICULS.BESTBEFOREDAYS " +
                " from  RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL and  UID_PALLET='" + h_UID_PALLET + "' ";

            // ==============================================================================

            OracleCommand ora_com = new OracleCommand();
            ora_com.CommandText = strSQL;

            try
            {
                OracleConnection ora_conn = new OracleConnection();
                ora_conn.ConnectionString = MINI_WMS_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                OracleDataReader ora_reader = ora_com.ExecuteReader();

                OracleCommand ora_com2 =  new OracleCommand();
                ora_com2.Connection = ora_conn;
                ora_com2.CommandText = " select  WRITE_BOTH_EXPIRYANDBEST  from rrl_wares where ID=" + this.wms_user.ware_id + " ";
                long WRITE_BOTH_EXPIRYANDBEST = obj2int( ora_com2.ExecuteOracleScalar());



                while (ora_reader.Read())
                {
                    object[] values1 = new object[13];
                    for (int yy = 0; yy < 13; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }

                    string h_articul = values1[1].ToString();
                    string h_unit_count = values1[2].ToString();
                    string PRIHOD_NAKLAD_ID = values1[3].ToString();
                    DateTime EXPIRY_DATE = Convert.ToDateTime(values1[4]);
                    DateTime CREATION_DATE = Convert.ToDateTime(values1[5]);
                    DateTime Distr_ends_DATE = Convert.ToDateTime(values1[10]);
                    string KLADOVSHIK = values1[11].ToString();
                    long BESTBEFORE  =  obj2int( values1[12] ) ;
                    string h_name = values1[6].ToString();
                    string h_cell = values1[7].ToString();
                    string h_UNIT_TYPE = values1[8].ToString();
                    string h_BARCODE_SHT = values1[9].ToString();

                    // ================================================================

                    //Image r = Code128Rendering.MakeBarcodeImage(h_UID_PALLET, 2, true);

                    _page.labels.Add(new PPage.PLabel("Версия: " + this.version  , new Point(700, 100), 12));

                    _page.labels.Add(new PPage.PLabel(h_UID_PALLET, new Point(200, 400), 12, "EAN2", 700, 150));

                    _page.labels.Add(new PPage.PLabel(h_UID_PALLET, new Point(200, 0), 12, "EAN2", 700, 50));
                    _page.labels.Add(new PPage.PLabel(h_UID_PALLET, new Point(200, 790), 12, "EAN2", 700, 50));

                    if ((h_BARCODE_SHT != "none"  ) && (h_BARCODE_SHT!=""))
                    {
                        _page.labels.Add(new PPage.PLabel(h_BARCODE_SHT, new Point(830, 670), 12, "EAN", 700, 160));
                    }
                    

                    #region РИСОВАНИЕ

                    _page.labels.Add(new PPage.PLabel("артикул: " + h_articul + " ;    кол-во: " + h_unit_count + " " + h_UNIT_TYPE,
                        new Point(100, 670), 30));
                    _page.labels.Add(new PPage.PLabel("накл:" + PRIHOD_NAKLAD_ID + "   id паллета:" + h_UID_PALLET,
                        new Point(100, 700), 30));
                    _page.labels.Add(new PPage.PLabel("товар принят: " + CREATION_DATE.ToString() + "; принял: " + KLADOVSHIK,
                        new Point(100, 730), 30));

                    if (h_name.Length > 40)
                    {

                        _page.labels.Add(new PPage.PLabel(h_name.Substring(0, 40), new Point(100, 100), 40));
                        _page.labels.Add(new PPage.PLabel(h_name.Substring(40, h_name.Length - 40), new Point(100, 150), 40));
                    }
                    else
                    {
                        _page.labels.Add(new PPage.PLabel(h_name, new Point(100, 100), 40));

                    }

                    if (Distr_ends_DATE <= DateTime.Today)
                    {
                        if (option != "BRAK")
                        {
                            _page.labels.Add(new PPage.PLabel(h_cell, new Point(100, 170), 80));
                            _page.labels.Add(new PPage.PLabel("товар не размещать!", new Point(100, 245), 80));
                            _page.labels.Add(new PPage.PLabel("короткий срок.", new Point(100, 320), 80));
                        }
                        else {
                            _page.labels.Add(new PPage.PLabel("БРАК", new Point(100, 170), 180));
                         }
                      
                   
                    }
                    else {
                        if (option != "BRAK")
                        {
                            _page.labels.Add(new PPage.PLabel(h_cell, new Point(100, 170), 180));
                        }
                        else {
                            _page.labels.Add(new PPage.PLabel("БРАК", new Point(100, 170), 180));
                        
                        }
                    }
                    
                    
                    if ((WRITE_BOTH_EXPIRYANDBEST == 0) || (Distr_ends_DATE == null) || (Distr_ends_DATE.Year<2000))
                    {
                        _page.labels.Add(new PPage.PLabel("" + EXPIRY_DATE.Day + "." + EXPIRY_DATE.Month + "." + EXPIRY_DATE.Year, new Point(200, 550), 100));
                    }
                    else {
                        DateTime man_date = EXPIRY_DATE.AddDays((-1) * BESTBEFORE);
                        if (option == "BRAK") 
                        {
                            _page.labels.Add(new PPage.PLabel("не отгружать" , new Point(50, 540), 90));
                        }
                        else
                        {
                            _page.labels.Add(new PPage.PLabel("отгрузить до:" + Distr_ends_DATE.Day + "." + Distr_ends_DATE.Month + "." + Distr_ends_DATE.Year, new Point(50, 540), 90));
                        }
                        _page.labels.Add(new PPage.PLabel("годен до:" + EXPIRY_DATE.Day + "." + EXPIRY_DATE.Month + "." + EXPIRY_DATE.Year + "; срок годности=" + BESTBEFORE + " дней. " + "произведен:" + man_date.Day + "." + man_date.Month + "." + man_date.Year, new Point(100, 640), 30));
                    
                    }

                    #endregion

                }

                ora_reader.Close();
                ora_conn.Close();
            }
            catch (Exception Ex)
            {
                MessageBox.Show(" f39 " + Ex.Message);
            }

            // ==============================================================================


            #endregion

            return _page;

        }

        private void print_pallet_label_Click(object sender, EventArgs e)
        {

            PPage _page = new PPage();
            
            string h_UID_PALLET = "";
            if (dataGrid_pallets.CurrentRow != null)
            {
                h_UID_PALLET = dataGrid_pallets.CurrentRow.Cells[0].Value.ToString();
            }

            if (h_UID_PALLET == "")
            {
                MessageBox.Show("нечего печатать");
                return;
            }

            _page = get_prihod_pallet_print_page( h_UID_PALLET ,"" );

            PPages.Add(_page);

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {

                pd.DefaultPageSettings.Landscape = true;
                //if( pd.DefaultPageSettings.PrinterSettings.CanDuplex )
                // pd.DefaultPageSettings.PrinterSettings.Duplex = Duplex.Horizontal;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion


        }

        private void В_ХРАНЕНИЕ_Click(object sender, EventArgs e)
        {
            try
            {

                string pallet_id = dataGrid_pallets.CurrentRow.Cells[0].Value.ToString();


                foreach (DataGridViewRow dr3 in dataGrid_pallets.Rows)
                {

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.RRL_GIVE_DESTINATION_CELL2";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("pallet_uid", OracleType.VarChar).Value = dr3.Cells[0].Value.ToString() ;
                    ora_com.Parameters.Add("ware_id1", OracleType.Int32).Value = 1;
                    ora_com.Parameters.Add("cell_destination", OracleType.VarChar, 50).Direction =
                        ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();
                    dr3.Cells["CELL_TO"].Value =ora_com.Parameters["cell_destination"].Value.ToString();
                }


            }
            catch (Exception ex)
            {
                MessageBox.Show(" f42 " +  ex.Message);
            }

        }


        private void разместить_в_ячейку_Click(object sender, EventArgs e)
        {//  Перемещаем выделенный паллет в указанную ячейку  (m_cell_to)

            DataGridViewRow  dr3 = dataGrid_pallets.CurrentRow;
            if (dr3 == null)
            {
                return;
            }

            try {

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_INTERNAL_MOVE2";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("pallet_id", OracleType.VarChar).Value = dr3.Cells[0].Value.ToString();
                ora_com.Parameters.Add("cell_to", OracleType.VarChar).Value = m_cell_to.Text ;
                ora_com.Parameters.Add("count1", OracleType.Number).Value = Convert.ToInt64( dr3.Cells[2].Value.ToString()) ;
                ora_com.Parameters.Add("user_id1", OracleType.VarChar ).Value = wms_user.user_id ;
                ora_com.Parameters.Add("ok", OracleType.VarChar, 50).Direction =
                    ParameterDirection.ReturnValue;
                ora_com.ExecuteNonQuery();
                string ret = ora_com.Parameters["ok"].Value.ToString();
                if (ret != "ok")
                {
                    MessageBox.Show("ошибка: " + ret );
                }

  
            }
            catch(Exception ex){
                MessageBox.Show(" f56 " + ex.Message);
            }


        }

        private void dataGridView6_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        { // Добавление отгузочной накладной


            OracleCommand ora_com;
            try
            {
                DataGridViewRow dr ;
                string m_NAKLADNAME1;
                string m_MAG_NO1 ;
                DateTime m_NAKLADDATE1 ;
                DateTime m_CREATIONDATE1 ;
                DateTime m_PLANNEDDELIVERYDATE1=DateTime.Today  ;

                try
                {
                     dr = dataGridView6.CurrentRow;
                     m_NAKLADNAME1 = obj2str(dr.Cells[1].Value);
                     m_MAG_NO1 = Convert.ToString(obj2str(dr.Cells[2].Value));
                     m_NAKLADDATE1 = Convert.ToDateTime(obj2str(dr.Cells[3].Value));
                     m_CREATIONDATE1 = DateTime.Today;
                }
                catch { return; }

                try
                {
                    m_PLANNEDDELIVERYDATE1 = Convert.ToDateTime(obj2str(dr.Cells[5].Value));
                }
                catch { }

                if ((dr.Cells[0].Value == null )  && ( m_MAG_NO1!="" )  )
                { // Инсертим
                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("NAKLADNAME1", OracleType.VarChar).Value = m_NAKLADNAME1;
                    ora_com.Parameters.Add("MAG_NO1", OracleType.VarChar).Value = m_MAG_NO1;
                    ora_com.Parameters.Add("NAKLADDATE1", OracleType.DateTime).Value = m_NAKLADDATE1;
                    ora_com.Parameters.Add("CREATIONDATE1", OracleType.DateTime).Value = m_CREATIONDATE1;
                    ora_com.Parameters.Add("PLANNEDDELIVERYDATE1", OracleType.DateTime).Value = m_PLANNEDDELIVERYDATE1;

                    ora_com.Parameters.Add("ware_id1", OracleType.Int32 ).Value = this.wms_user.ware_id ;

                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    dr.Cells[0].Value = ora_com.Parameters["ID"].Value;

                    // инсертим
                }
                else
                { // Апдейтим

                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    DateTime m_PLANNEDDELIVERYDATE12 = Convert.ToDateTime((dr.Cells[4].Value.ToString()));
                    ora_com.CommandText = "update RABAEV.RRL_OTHOD_NAKLAD set   PLANNEDDELIVERYDATE = " + date2sql_ora(m_PLANNEDDELIVERYDATE12) + "    " +
                    " where ID=" + Convert.ToString(dr.Cells[0].Value.ToString()) + "   ";
                    ora_com.ExecuteNonQuery();

                } // Апдейтим

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f51" + ex.Message);
            }

        }

        private void Загрузить_Click(object sender, EventArgs e)
        {
            dataGridView6.Rows.Clear();
            string strSQL = " SELECT ID ,  NAKLADNAME ,  MAG_NO     ,  NAKLADDATE ,  CREATIONDATE ,  PLANNEDDELIVERYDATE  ,  CONDITION   " +
            "  FROM rabaev.RRL_OTHOD_NAKLAD where CREATIONDATE >= " + date2sql_ora(dateTimePicker_ON_FROM.Value) + " and CREATIONDATE<=" + date2sql_ora(dateTimePicker_ON_to.Value)+" and ware_id="+this.wms_user.ware_id.ToString(); ;
            fill_view_MINI_WMS(dataGridView6, strSQL, 7);
            return;

        }

        private void dataGridView7_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {



            OracleCommand ora_com;
            try
            {
                DataGridViewRow dr ;
                long m_ID_NAKLAD;
                long m_ROW_ID=0;
                string m_articul="";
                double m_col;
                long id_row = 0;


                try
                {
                    dr = dataGridView7.CurrentRow;
                    if (dr.Cells[0].Value != null) {
                        id_row = Convert.ToInt64(dr.Cells[0].Value);
                    }

                    if (dr.Cells[3].Value == null)
                    {
                        m_ID_NAKLAD = Convert.ToInt64(dataGridView6.CurrentRow.Cells[0].Value);
                        m_ROW_ID = 0;
                    }
                    else
                    {
                        m_ROW_ID = Convert.ToInt64(obj2str(dr.Cells[0].Value));
                        m_ID_NAKLAD = Convert.ToInt64(dr.Cells[3].Value);
                    }

                    
                    m_articul = Convert.ToString (obj2str(dr.Cells[1].Value));
                    m_col = Convert.ToDouble (obj2str(dr.Cells[2].Value));

                }
                catch { return; }

                
              

                 // Инсертим
                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD_ROWS";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("ID_ROW1", OracleType.Int32 ).Value = id_row ;
                
                    ora_com.Parameters.Add("ID_NAKLAD1", OracleType.Int32 ).Value = m_ID_NAKLAD;
                    ora_com.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = m_articul;
                    ora_com.Parameters.Add("COUNT2", OracleType.Number ).Value = m_col;

                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    if (id_row==0)
                    dr.Cells[0].Value = ora_com.Parameters["ID"].Value;

                    // инсертим
               
               

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f52 " + ex.Message);
            }





        }

        private void dataGridView6_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView6.CurrentRow.Cells[0].Value == null)
                return;

            string id = dataGridView6.CurrentRow.Cells[0].Value.ToString() ; 

            dataGridView7.Rows.Clear();
            string strSQL = " SELECT R.ID  , R.ARTICUL , R.COUNT1 , R.ID_NAKLAD , A.NAME " +
            "  FROM RABAEV.RRL_OTHOD_NAKLAD_ROWS R , RABAEV.RRL_ARTICULS A where A.ACTICUL = R.ARTICUL(+) and ID_NAKLAD = " + id + " ";
            fill_view_MINI_WMS(dataGridView7, strSQL, 5);
            return;
        }

        private void button12_Click(object sender, EventArgs e)
        { // Загрузка данных из EXCEL


            long pos = 2;
            try
            {
                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                string Filename = "C:\\g\\nomenk.xls" ;


                oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);

              
                while (  ((Excel.Range)oExcelApp.Cells[pos,1 ]).Value2.ToString() !="")
                {
                    
                    string articul4 = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
                    string name4 = ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString();
                    string section4 = ((Excel.Range)oExcelApp.Cells[pos,3 ]).Value2.ToString();

                    long Z  = str2int (  ((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString()  );
                    long X3 = str2int(((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString());
                    long Y = str2int(((Excel.Range)oExcelApp.Cells[pos,6 ]).Value2.ToString());
                    long X = str2int(((Excel.Range)oExcelApp.Cells[pos,7 ]).Value2.ToString());
                    long count_in_layer = str2int(((Excel.Range)oExcelApp.Cells[pos,8 ]).Value2.ToString());
                    long layer_in_pall = str2int(((Excel.Range)oExcelApp.Cells[pos,9 ]).Value2.ToString());
                    long count_in_pal = str2int(((Excel.Range)oExcelApp.Cells[pos, 10]).Value2.ToString());
                    string cell4 = ((Excel.Range)oExcelApp.Cells[pos,11 ]).Value2.ToString();
                    double weight_of_kor = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos,12 ]).Value2.ToString());
                    string unit_barkode = ((Excel.Range)oExcelApp.Cells[pos,13 ]).Value2.ToString();
                    string kor_barkode = ((Excel.Range)oExcelApp.Cells[pos,14 ]).Value2.ToString();



                    // ================================================================

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();

                    ora_com.CommandText = "RABAEV.RRL_UPDATE_ARTICUL_EX";
                    ora_com.CommandType = CommandType.StoredProcedure;

                   ora_com.Parameters.Add("articul4", OracleType.VarChar).Value = articul4;
                   ora_com.Parameters.Add("name4", OracleType.VarChar).Value = name4;
                   ora_com.Parameters.Add("section4", OracleType.VarChar).Value = section4;
                   ora_com.Parameters.Add("Z", OracleType.Int32 ).Value = Z;
                   ora_com.Parameters.Add("X3", OracleType.Int32 ).Value = X3;
                   ora_com.Parameters.Add("Y", OracleType.Int32 ).Value = Y;
                   ora_com.Parameters.Add("X", OracleType.Int32 ).Value = X;
 
                  ora_com.Parameters.Add("count_in_layer", OracleType.Int32 ).Value = count_in_layer;
                  ora_com.Parameters.Add("layer_in_pall", OracleType.Int32 ).Value = layer_in_pall;
                  ora_com.Parameters.Add("count_in_pal", OracleType.Int32 ).Value = count_in_pal;
                  ora_com.Parameters.Add("cell4", OracleType.VarChar ).Value = cell4;
                  ora_com.Parameters.Add("weight_of_kor", OracleType.Number  ).Value = weight_of_kor;
                 
                  ora_com.Parameters.Add("unit_barkode", OracleType.VarChar).Value = unit_barkode;
                  ora_com.Parameters.Add("kor_barkode", OracleType.VarChar).Value = kor_barkode;

                  ora_com.Parameters.Add("tmpVar", OracleType.VarChar , 25).Direction = ParameterDirection.ReturnValue;
                  int rowsAffected = ora_com.ExecuteNonQuery();
                  string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                    // ================================================================
 

                    pos++;
                }
                MessageBox.Show("Данные выгружены в Excel");
            }
            catch (Exception ex)
            {
                MessageBox.Show( Convert.ToString(pos) +" _ "+  ex.Message);
            }
            // ================================


        }

        private void button13_Click(object sender, EventArgs e)
        { // ЗАГРУЗКА СПРАВОЧНИКА ЯЧЕЕК

            


            long pos = 2;
            try
            {
                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                string Filename = "C:\\WMS\\cells.xls";


                oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);


                while (oExcelApp.Cells[1, pos] != "")
                {

                    string articul4 = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
                    string name4 = ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString();
                    string section4 = ((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString();

                    long Z = str2int(((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString());
                    long X3 = str2int(((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString());
                    long Y = str2int(((Excel.Range)oExcelApp.Cells[pos, 6]).Value2.ToString());
                    long X = str2int(((Excel.Range)oExcelApp.Cells[pos, 7]).Value2.ToString());
                    long count_in_layer = str2int(((Excel.Range)oExcelApp.Cells[pos, 8]).Value2.ToString());
                    long layer_in_pall = str2int(((Excel.Range)oExcelApp.Cells[pos, 9]).Value2.ToString());
                    long count_in_pal = str2int(((Excel.Range)oExcelApp.Cells[pos, 10]).Value2.ToString());
                    string cell4 = ((Excel.Range)oExcelApp.Cells[pos, 11]).Value2.ToString();
                    double weight_of_kor = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 12]).Value2.ToString());
                    string unit_barkode = ((Excel.Range)oExcelApp.Cells[pos, 13]).Value2.ToString();
                    string kor_barkode = ((Excel.Range)oExcelApp.Cells[pos, 14]).Value2.ToString();


                    // ================================================================

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();

                    ora_com.CommandText = "RABAEV.RRL_UPDATE_ARTICUL_EX";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("articul4", OracleType.VarChar).Value = articul4;
                    ora_com.Parameters.Add("name4", OracleType.VarChar).Value = name4;
                    ora_com.Parameters.Add("section4", OracleType.VarChar).Value = section4;
                    ora_com.Parameters.Add("Z", OracleType.Int32).Value = Z;
                    ora_com.Parameters.Add("X3", OracleType.Int32).Value = X3;
                    ora_com.Parameters.Add("Y", OracleType.Int32).Value = Y;
                    ora_com.Parameters.Add("X", OracleType.Int32).Value = X;

                    ora_com.Parameters.Add("count_in_layer", OracleType.Int32).Value = count_in_layer;
                    ora_com.Parameters.Add("layer_in_pall", OracleType.Int32).Value = layer_in_pall;
                    ora_com.Parameters.Add("count_in_pal", OracleType.Int32).Value = count_in_pal;
                    ora_com.Parameters.Add("cell4", OracleType.VarChar).Value = cell4;
                    ora_com.Parameters.Add("weight_of_kor", OracleType.Number).Value = weight_of_kor;

                    ora_com.Parameters.Add("unit_barkode", OracleType.VarChar).Value = unit_barkode;
                    ora_com.Parameters.Add("kor_barkode", OracleType.VarChar).Value = kor_barkode;

                    ora_com.Parameters.Add("tmpVar", OracleType.VarChar, 25).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                    // ================================================================
                    pos++;
                }
                MessageBox.Show("Данные выгружены в Excel");
            }
            catch (Exception ex)
            {
                MessageBox.Show(Convert.ToString(pos) + " _ " + ex.Message);
            }
            // ================================

            

        }

        private void Загрузить_инвентаризацию_Click(object sender, EventArgs e)
        {





long pos = 2;
try
{
    //Excel Application Object
    Excel.Application oExcelApp = new Excel.Application();
    oExcelApp.Visible = true;

    object obj = new object();
    string Filename = "C:\\g\\invent.xls";


    oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);


    while ( oExcelApp.Cells[pos, 1] != null )
    {

        string cell5 = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
        string articul5 = ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString();
        double count5 = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString());
        DateTime  date5 = Convert.ToDateTime(((Excel.Range)oExcelApp.Cells[pos, 4]).Text.ToString());
        double PRICE5 = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString());
        
        

        // ================================================================

        OracleCommand ora_com = new OracleCommand();
        ora_com.Connection = get_wms_connection();

        ora_com.CommandText = "RABAEV.RRL_ADD_INV_LINE";
        ora_com.CommandType = CommandType.StoredProcedure;


        ora_com.Parameters.Add("CELL5", OracleType.VarChar).Value = cell5;
        ora_com.Parameters.Add("articul5", OracleType.VarChar).Value = articul5;
        ora_com.Parameters.Add("COUNT15", OracleType.Number ).Value = count5;
        ora_com.Parameters.Add("date_of_expire5", OracleType.DateTime).Value = date5;
        ora_com.Parameters.Add("PRICE5", OracleType.Number).Value = PRICE5;
        ora_com.Parameters.Add("inventory_id", OracleType.Int32 ).Value = 1;
        ora_com.Parameters.Add("iser_id5", OracleType.VarChar).Value = wms_user.user_id;

        
        

        ora_com.Parameters.Add("tmpVar", OracleType.VarChar, 25).Direction = ParameterDirection.ReturnValue;
        int rowsAffected = ora_com.ExecuteNonQuery();
        string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
        // ================================================================
        pos++;
    }

    MessageBox.Show("Данные загружены из Excel");
}
catch (Exception ex)
{
    MessageBox.Show(Convert.ToString(pos) + " _ " + ex.Message);
}
// ================================





        }

        private void button11_Click(object sender, EventArgs e)
        {

            string strSQL = " SELECT UID_PALLET " +
           "  FROM rabaev.RRL_PALLETS where PRIHOD_NAKLAD_ID= -1   ";
            fill_view_MINI_WMS(dataGridView8, strSQL, 1);
            return;


//            m_pallets_to_print


        }

        private void dataGridView5_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void СоздатьизEXCEL_Click(object sender, EventArgs e)
        { // СОЗДАНИЕ ОТГРУЗОЧНОЙ НАКЛАДНОЙ



            long pos = 1;
            try
            {
                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                string Filename = "C:\\MINI WMS\\отгрузки.xls";


                oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);


                long УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ =0;
                DateTime ДатаНакладной=DateTime.Today ;
 OracleCommand ora_com; 

                while ( ((Excel.Range)oExcelApp.Cells[pos, 4]).Value2 != null)
                {

                   
                    if (((Excel.Range)oExcelApp.Cells[pos, 1]).Value2 != null)
                    { // НОВАЯ НАКЛАДНАЯ
                        string НомерНакладной1 = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
                        DateTime date1 = Convert.ToDateTime(((Excel.Range)oExcelApp.Cells[pos, 2]).Text.ToString());
                        string Адрес1 = ((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString();


                        // СОЗДАНИЕ НАКЛАДНОЙ  ==============================
                       
                        ora_com = new OracleCommand();
                        ora_com.Connection = get_wms_connection();
                        ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD";
                        ora_com.CommandType = CommandType.StoredProcedure;

                        ora_com.Parameters.Add("NAKLADNAME1", OracleType.VarChar).Value = НомерНакладной1;
                        ora_com.Parameters.Add("MAG_NO1", OracleType.VarChar).Value = Адрес1;
                        ora_com.Parameters.Add("NAKLADDATE1", OracleType.DateTime).Value = date1;
                        ora_com.Parameters.Add("CREATIONDATE1", OracleType.DateTime).Value = DateTime.Today ;
                        ora_com.Parameters.Add("PLANNEDDELIVERYDATE1", OracleType.DateTime).Value = DateTime.Today;

                        ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected = ora_com.ExecuteNonQuery();
                        УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ = Convert.ToInt64(  ora_com.Parameters["ID"].Value ) ;

                        // СОЗДАНИЕ НАКЛАДНОЙ  ==============================
                    }
                    

                    double count5 = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 6]).Value2.ToString());
                    string АРТИКУЛ = Convert.ToString (((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString());


                     ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD_ROWS";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("ID_ROW1", OracleType.Int32).Value = 0;

                    ora_com.Parameters.Add("ID_NAKLAD1", OracleType.Int32).Value = УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ;
                    ora_com.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = АРТИКУЛ;
                    ora_com.Parameters.Add("COUNT2", OracleType.Number).Value = count5;

                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();
                    
                    long УИД_НОВОЙ_СТРОКИ = Convert.ToInt64( ora_com.Parameters["ID"].Value );



                    // ================================================================





                    // ================================================================
                    pos++;
                }

                MessageBox.Show("Данные загружены из Excel");





            }catch(Exception ex)
                {

                    MessageBox.Show(" f53 " + ex.Message);

                }   


        }



        private void Close_Othod_Naklad(long order_id)
        {
            string rrr = " " + order_id+" = ";
            try
            {
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RRL_CLOSE_OTHOD_NAKLAD";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("naklad_num", OracleType.Int32).Value = order_id;
                ora_com.Parameters.Add("iser_id21", OracleType.VarChar).Value = wms_user.user_id;
                ora_com.Parameters.Add("ret", OracleType.VarChar , 50).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
                rrr = rrr + ora_com.Parameters["ret"].Value.ToString();


            }
            catch (Exception ex)
            {
                MessageBox.Show(" f90: ORDER_ID= " + order_id.ToString() + " ;  " + ex.Message);
            }

            m_spisok_otg_nakl.Text +=  rrr+"  \n";
        }


        private void Закрыть_Текущую_Накладную_Click(object sender, EventArgs e)
        {

            if ( Convert.ToInt64(dataGridView6.CurrentRow.Cells[6].Value) == 2)
            {
                MessageBox.Show("накладная закрыта");
                return;
            }

            try
            {
               int order_id = Convert.ToInt32(dataGridView6.CurrentRow.Cells[0].Value.ToString());
               Close_Othod_Naklad( order_id);
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f89 " + ex.Message);
            }

          dataGridView6.CurrentRow.Cells[6].Value = 2;
        }

        private void button14_Click(object sender, EventArgs e)
        {



            string h_articul = ЯЧЕЙКА_ОТКУДА.Text;
            int selected_ware = 0;
            try
            {
                selected_ware = Convert.ToInt32(ware_id_cell.Text);
            }
            catch { }



            string strSQL = "select UID_POLETA ,  REMAIN ,  RRL_ARTICULS.NAME  from RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where   RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and " +
            " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL   " +
            " and RRL_REMAINS.CELL='" + ЯЧЕЙКА_ОТКУДА.Text + "' and REMAIN<>0 ";

            if (selected_ware > 0)
            {
                strSQL = "select UID_POLETA ,  REMAIN ,  RRL_ARTICULS.NAME from RABAEV.RRL_REMAINS , " +
               " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS ,   RABAEV.RRL_CELLS   " +
               " where ( RABAEV.RRL_ARTICULS.CELL= RABAEV.RRL_CELLS.CELL ) and (RABAEV.RRL_CELLS.ware_id in ( " + selected_ware.ToString()+
               " )  ) and ( RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET ) and " +
               " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL   " +
               " and RRL_REMAINS.CELL='" + ЯЧЕЙКА_ОТКУДА.Text + "' and REMAIN<>0 ";
            }


            fill_view_MINI_WMS(dataGrid_ПАЛЛЕТЫ_ОТКУДА, strSQL, 3);


        }

        private void ПЕРЕМЕСТИТЬ_Click(object sender, EventArgs e)
        {
            
            DataGridViewRow dr3 = dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow;
                if (dr3 == null) { return;}

                if (ЯЧЕЙКА_КУДА.Text == "BRAK")
                {
                    if (!has_right("MOVE_TO_BRAK"))
                    {
                        MessageBox.Show("Нет прав на MOVE_TO_BRAK");
                        return;
                    }
                }

                try
                {
                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.RRL_INTERNAL_MOVE2";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("pallet_id", OracleType.VarChar).Value = dr3.Cells[0].Value.ToString();
                    ora_com.Parameters.Add("cell_to", OracleType.VarChar).Value = ЯЧЕЙКА_КУДА.Text;
                    
                    long iiii=0;
                    try
                    {
                        iiii = Convert.ToInt64(СКОЛЬКО_ПЕРЕМЕЩАЕМ.Text);
                    }catch{}
                    ora_com.Parameters.Add("count1", OracleType.Number).Value = iiii;
                    ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = wms_user.user_id;
                    ora_com.Parameters.Add("ok", OracleType.VarChar, 50).Direction = ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();
                    string ret = ora_com.Parameters["ok"].Value.ToString();
                    if (ret.Substring(0, 2) != "ok")
                    {
                        MessageBox.Show("ошибка: " + ret);
                    }
                    else {
                        dataGrid_ПАЛЛЕТЫ_ОТКУДА.Rows.Remove(dr3);
                    }

                }
                catch (Exception ex)
                {
                    MessageBox.Show(" f56 " + ex.Message);
                }

        }

        private void button15_Click(object sender, EventArgs e)
        {




          
            string strSQL = "select RRL_REMAINS.CELL  ,  REMAIN ,  RRL_ARTICULS.NAME from RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where   RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and " +
            " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL   " +
            " and RRL_REMAINS.UID_POLETA='" + m_pallet_name.Text + "' and REMAIN<>0 ";


            fill_view_MINI_WMS(dataGridView9, strSQL, 2);
        }

        private void button16_Click(object sender, EventArgs e)
        {


            string strSQL = "select RRL_REMAINS.CELL  ,  REMAIN , RRL_REMAINS.UID_POLETA , RRL_ARTICULS.NAME , RRL_REMAINS.TIME_OF_LAST_UPDATE , RRL_CELLS.OTBOR " +
            " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where   RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and " +
            " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL and  RRL_REMAINS.CELL = RRL_CELLS.CELL(+) and  not ( RRL_REMAINS.CELL like  'EX_%' ) " +
            "  and  RABAEV.RRL_CELLS.ware_id in ( 0 , "+this.wms_user.ware_id.ToString() + " )  ";

            if(checkBox1.Checked )
            {
                strSQL = "select RRL_CELLS.CELL  ,  0 , '' , '' , '' , RRL_CELLS.OTBOR " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where   " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+)  and ( RRL_REMAINS.CELL is null) " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString() + 
                " order by Z , Y , X  ";
            }

            fill_view_MINI_WMS(dataGridView10 , strSQL, 6);


        }

        private void button17_Click(object sender, EventArgs e)
        {

            grid_2_excel(dataGridView10 );

        }

        private void button18_Click(object sender, EventArgs e)
        {

            foreach (DataGridViewRow dr in dataGrid_pallets.Rows )
            {
                try
                {
                    if (Convert.ToBoolean(dr.Cells[7].Value) == false)
                    {
                        PPage _page = new PPage();
                        string h_UID_PALLET = "";
                        if (dr != null)
                        {
                            h_UID_PALLET = dr.Cells[0].Value.ToString();
                        }
                        _page = get_prihod_pallet_print_page(h_UID_PALLET , "" );
                        PPages.Add(_page);
                        string strSQL = " update RABAEV.RRL_PALLETS set PRINTED=1 where UID_PALLET='" + h_UID_PALLET + "' ";
                        OracleCommand ora_com = new OracleCommand();
                        ora_com.Connection = get_wms_connection();
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();
                        dr.Cells[7].Value = true;
                    }
                }catch(Exception ex)
                {
                
                }
            }

            if (PPages.Count < 1)
            {
                MessageBox.Show("Нет паллет для печати паспортов, либоо паспорта печетались раннее. \n Для того, чтобы распечатать паспорта второй раз уберите флажки 'печать' с паллет. ");
                return;
            }


            #region НАЧАЛО_ПЕЧАТИ

                PrintDocument pd = new PrintDocument();
                try
                {

                    pd.DefaultPageSettings.Landscape = true;
                    pd.PrintPage += new PrintPageEventHandler
                        (pd_PrintPage_SBOR);
                    pd.Print();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(" f48 " + ex.Message);
                }

            #endregion







        }

        private void button19_Click(object sender, EventArgs e)
        {
            // ===================================================================

            
            OracleCommand ora_com;

            DataGridViewRow parent_dr =  dataGridView_prihod.CurrentRow;
            if ( Convert.ToInt64( parent_dr.Cells[5].Value) > 0)
            {
                MessageBox.Show("Накладная закрыта, изменения не возможны");
                return; }
            DataGridViewRow dr = ( dataGridView5  ).CurrentRow;


            try
            {

                string articul = obj2str(dr.Cells[0].Value);
                double count1 = Convert.ToDouble(dr.Cells[1].Value);
                double price = Convert.ToDouble(dr.Cells[2].Value);
                DateTime expiry_date = Convert.ToDateTime(dr.Cells[3].Value);

                if (dr.Cells[4].Value != null)
                {
                            ora_com = new OracleCommand();
                            ora_com.Connection = get_wms_connection();
                            ora_com.CommandText = "DELETE_RRL_PRIH_NAKLAD_ROW";
                            ora_com.CommandType = CommandType.StoredProcedure;
                            long ROW_ID = Convert.ToInt64(dr.Cells[4].Value.ToString());

                            ora_com.Parameters.Add("ROW_ID1", OracleType.Int32).Value = ROW_ID;
                            
                            ora_com.Parameters.Add("ok", OracleType.VarChar , 50).Direction = ParameterDirection.ReturnValue;
                            int rowsAffected = ora_com.ExecuteNonQuery();
                            dr.Cells[4].Value = ora_com.Parameters["ok"].Value;
                }
                dataGridView5.Rows.Remove(dr);
            }catch( Exception ex  )
            {
                MessageBox.Show(ex.Message );
            }


        


            // ===================================================================

        }

        private void button20_Click(object sender, EventArgs e)
        {
            string add_sql1 = "";
            if (textBox6.Text != "")
            {
                add_sql1 = " and ( ACTICUL like '%" + textBox6.Text + "%' ) ";
            }

            string add_sql2 = "";
            if (textBox5.Text != "")
            {
                add_sql2 = " and ( NAME like '%" + textBox5.Text + "%' ) ";
            }


            string add_sql3 = "";
            /* if (has_right("VIEW_ALL_ARTIKULS"))
            {
                add_sql3 = "  ";
            }
            else { } */
            add_sql3="  and ( (c.cell is null) or  (c.ware_id=" + this.wms_user.ware_id + ") ) ";


            string strSQL = " SELECT ACTICUL , NAME , NORMA_UKLADKI , A.Cell , C.cell  , 'false' ,  BARCODE_SHT  ,  BARCODE_BL , BARCODE_KOR , RRL_SKLADNAME_BY_ID( c.ware_id ) , COUNT_SHT_IN_KOR , COUNT_SHT_IN_BL , "+
                "  CARTON_WEIGHT , etaj_limit , BESTBEFOREDAYS , ABC_GROUP , XYZ_GROUP , SSP " +
            "  FROM RABAEV.RRL_ARTICULS A , RABAEV.RRL_CELLS C where A.Cell = C.cell "+
            " " + add_sql3 + " " + add_sql1 + add_sql2;
            fill_view_MINI_WMS(dataGridView11, strSQL, 18);
            return;


        }

        private void dataGridView11_CellLeave(object sender, DataGridViewCellEventArgs e)
        { // =================================================================================

          
            //===============================================================================

        }

        private void dataGridView11_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            /*
    set 
      ID             = ID1,
              = ARTICUL1,
      NAME           = NAME1,
      SHT_IN_KOR     = SHT_IN_KOR1 ,
      SHT_WEIGHT     = SHT_WEIGHT1 ,
      KARTON_WEIGHT  = KARTON_WEIGHT1,
      DELETED        =DELETED1

            */

            if (dataGridView11.CurrentRow == null)
                return;

            string curr_art="";
            try
            {
                curr_art=dataGridView11.CurrentRow.Cells[0].Value.ToString();
            }
            catch
            {
                return;
            }

            
            string strSQL = " select ID , Name , ARTICUL , SHT_IN_KOR ,  SHT_WEIGHT , KARTON_WEIGHT , int2bool( DELETED ) "+
                "  from RRL_ARTICUL_MODS where ARTICUL='" + curr_art + "' ";
           fill_view_MINI_WMS(dataGridView25, strSQL, 7);


        }

        private void tabPage1_Click(object sender, EventArgs e)
        {

        }

        private string decode_cell(string CELL)
        {
            return CELL.Replace('С', 'C').Replace('М', 'M').Replace('Б', 'B').Replace('Г', 'G').Replace('А', 'A').Replace('Д', 'D').Replace('В', 'V');
        }

        private string decode_cell(string CELL , long ware_id)
        {
            if (CELL == "----")
            {
                if (ware_id==1) {CELL="C----";}
                if (ware_id==2) {CELL="M----";}
                if (ware_id==3) {CELL="A----";}
                if (ware_id==4) {CELL="B----";}
                if (ware_id==5) {CELL="I----";}
                if (ware_id==6) {CELL="O----";}
                if (ware_id==7) {CELL="D----";}
                if (ware_id==8) {CELL="V----";}
            }

            return CELL.Replace('С', 'C').Replace('М', 'M').Replace('Б', 'B').Replace('Г', 'G').Replace('А', 'A').Replace('Д', 'D').Replace('В', 'V');
        }

        private void SyncCELL(string CELL , long ware_id)
        {
            OracleCommand ora_com9 = new OracleCommand();
            ora_com9.Connection = get_wms_connection();
            ora_com9.CommandText = " select ware_id from RABAEV.RRL_CELLS where CELL='" + CELL + "' ";

            long ware2id=Convert.ToInt32(ora_com9.ExecuteScalar());


            if (ware2id == 0)
            { // Создаем  ячейку
                string strSQL = " insert into RABAEV.RRL_CELLS (CELL , OTBOR , WARE_ID ) values ( '" + CELL + "' , 1 , " + ware_id.ToString() + " ) ";
                ora_com9.CommandText = strSQL;
                ora_com9.ExecuteNonQuery();


            }
            else {
                if (ware2id != ware_id)
                {
                    MessageBox.Show(" Ячейка " + CELL + " принадлежит другому складу. \n сейчас принадлежит складу № "+ware2id.ToString() +" \n попытка создать в  "+ware_id.ToString() );
                }
            }

            ora_com9.Dispose();

        }

        private void Alert( string error_text )
        {
            OracleCommand ora_com9 = new OracleCommand();
            ora_com9.Connection = get_wms_connection();
            ora_com9.CommandText = " insert into RABAEV.RRL_ERROR_LOG ( ERROR , DATET , USER_ID ) values ( '" + error_text + "' , "+date2sql_ora(DateTime.Now )+" , '"+this.wms_user.user_id +"' ) ";

            ora_com9.ExecuteNonQuery();
            ora_com9.Dispose();
            //if(box)
           // MessageBox.Show( error_text );
        
        }

        private void SyncArticul(string art , long ware_id )
        {   // Синхронизация артикула =========================================================

            string ACTICUL = art;//   VARCHAR2(15 CHAR),
           long NORMA_UKLADKI=0; // NUMBER                         NOT NULL,
           string CELL=""; //  VARCHAR2(50 CHAR),
           string NAME = ""; // VARCHAR2(255 CHAR),
           string UNIT_TYPE = ""; // VARCHAR2(20 CHAR),
           string BARCODE_SHT = ""; // VARCHAR2(128 CHAR)             DEFAULT 777                   NOT NULL,
           string BARCODE_KOR = ""; // VARCHAR2(128 CHAR),
           string BARCODE_BL = ""; // VARCHAR2(128 CHAR),
           double  WEIGHT_OF_KOR =0 ; // NUMBER,
           long COUNT_IN_ROW=0; //INTEGER,
           long ROWS_IN_PAL=0 ; //INTEGER
           string old_cell = "----";
           bool sync_barcodes = false;

           //try
           //{

               string strSQL;
               OracleCommand ora_com = new OracleCommand();
               ora_com.CommandText = " select  PATH  " +
               " from SUPERMAG.vcardstoreprop_rc b " +
               " where ARTICLE = '" + art + "'";


               OracleConnection ora_conn = new OracleConnection();
               ora_conn.ConnectionString = SM_CONNECTION_STRING();
               ora_conn.Open();
               ora_com.Connection = ora_conn;


               CELL = ora_com.ExecuteOracleScalar().ToString();
               CELL = decode_cell( CELL , ware_id ) ;
               SyncCELL(CELL, ware_id);

               #region СИНХРОНИЗАЦИЯ ДАННЫХ АРТИКУЛА 
               string Количество_мест_в_ряду = "";
               try
               {
                   ora_com.CommandText = " select cp.propval as kmr  from supermag.smcardproperties cp " +
                   "  where cp.propid = '4' and  cp.article='" + art + "' ";
                   Количество_мест_в_ряду = ora_com.ExecuteOracleScalar().ToString();
               }catch(Exception ex)
               {
                   Alert(" артикулу " + art + " не назначено Количество_мест_в_ряду ");
               }

               
               string Количество_рядов_в_паллете = "";
               try
               {
                   ora_com.CommandText = " select cp.propval as kmr  from supermag.smcardproperties cp " +
                   "  where cp.propid = '5' and  cp.article='" + art + "' ";
                   Количество_рядов_в_паллете = ora_com.ExecuteOracleScalar().ToString();
               }
               catch (Exception ex)
               {
                   Alert(" артикулу " + art + " не назначено Количество_рядов_в_паллете ");
               }


               try
               {
                   ora_com.CommandText = " select SHORTNAME  from SUPERMAG.SMCARD cp " +
                   "  where   cp.article='" + art + "' ";
                   NAME = ora_com.ExecuteOracleScalar().ToString();
               }
               catch (Exception ex)
               {
                   Alert(" артикулу " + art + " не назначено SHORTNAME ");
               }

               
                string Количество_штук_в_коробке = "";
               try
               {
                   ora_com.CommandText = " select MAX(QUANTITY) as Q  from SUPERMAG.smStoreUnits cp " +
                   "  where  cp.article='" + art + "' and FLAGS=0 ";
                    Количество_штук_в_коробке = ora_com.ExecuteOracleScalar().ToString();
               }
               catch (Exception ex)
               {
                   Alert(" артикулу " + art + " не назначено Количество_штук_в_коробке ");
               }

               string Вес_коробки = "";
             try
             {
               ora_com.CommandText = " select MAX(WEIGHT) as W  from SUPERMAG.smStoreUnits cp " +
               "  where cp.article='" + art + "' and FLAGS=0 ";
               Вес_коробки = ora_com.ExecuteOracleScalar().ToString();
             }
             catch (Exception ex)
             {
                   Alert(" артикулу " + art + " не назначен Вес_коробки ");
             }


               try
               {
                   ora_com.CommandText = " select BARCODE from (  select BARCODE  from SUPERMAG.smStoreUnits b  " +
                   "  where ARTICLE = '" + art + "' and b.BARCODETYPE = 1 ) where FLAGS=0   ";//and ROWNUM=1
                   BARCODE_KOR = ora_com.ExecuteOracleScalar().ToString();
               }
               catch (Exception ex)
               {
                  Alert(" Не задан ШК коробки у артикула  " + art);
               }
               #endregion

              #region СИНХРОНИЗАЦИЯ ДАННЫХ ДОПОЛНИТЕЛЬНЫХ ШТРИХ-КОДОВ 
              string strSQL3 = " select from  BARCODE  from SUPERMAG.smStoreUnits b  " +
                   "  where ARTICLE = '" + art + "' and b.BARCODETYPE = 1 ";
              #endregion


              try
          {
               ora_com.CommandText = " select BARCODE  from SUPERMAG.smStoreUnits b  " +
               "  where ARTICLE = '" + art + "' and b.BARCODETYPE = 7  ";
               BARCODE_SHT = ora_com.ExecuteOracleScalar().ToString();
           }
           catch (Exception ex)
           {
               Alert(" Не задан ШК штуки у артикула  " + art);
           }


               try
               {

                   WEIGHT_OF_KOR = Convert.ToDouble(Вес_коробки);

                   NORMA_UKLADKI = Convert.ToInt64(Количество_штук_в_коробке) *
                       Convert.ToInt64(Количество_рядов_в_паллете) *
                       Convert.ToInt64(Количество_мест_в_ряду);

                   UNIT_TYPE = "шт";
                   COUNT_IN_ROW = Convert.ToInt64(Количество_мест_в_ряду);
                   ROWS_IN_PAL = Convert.ToInt64(Количество_рядов_в_паллете);
               }
               catch (Exception ex)
               {
                   Alert(" Не корректно заполнена карточка артикула " + art + ". Обратитесь в ОТУ. \n " + ex.Message);
                   NORMA_UKLADKI = 10000;

                   //return;
               }
               ora_conn.Close();


               ora_conn.ConnectionString = MINI_WMS_CONNECTION_STRING();
               ora_conn.Open();
               ora_com.Connection = ora_conn;
               ora_com.CommandText = " select NAME , CELL from RABAEV.RRL_ARTICULS where ACTICUL='" + ACTICUL + "' ";
               OracleDataReader ora_reader = ora_com.ExecuteReader();
               bool need_insert = false;

               if (ora_reader.Read())
               {
                   old_cell = ora_reader.GetValue(1).ToString();
                   need_insert = false;
               }
               else
               {
                   need_insert = true;
               }

               if (BARCODE_SHT == "")
               {
                   BARCODE_SHT = "none";
               }
               if (BARCODE_KOR == "")
               {
                   BARCODE_KOR = "none";
               }

               if (need_insert)
               {
                   strSQL = " insert into RABAEV.RRL_ARTICULS ( " +
                   "  ACTICUL       , " +
                   "  NORMA_UKLADKI  , " +
                   "  CELL   , " +
                   "  NAME   , " +
                   "  UNIT_TYPE    , " +
                   "  BARCODE_SHT   , " +
                   "  BARCODE_KOR   , " +
                   "  BARCODE_BL    , " +
                   "  WEIGHT_OF_KOR , " +
                   "  COUNT_IN_ROW   , " +
                   "  ROWS_IN_PAL , COUNT_SHT_IN_KOR , COUNT_SHT_IN_BL  " +
                   " ) values ( " +
                   " '" + ACTICUL + "' , " +
                   " " + NORMA_UKLADKI + ", " +
                   " '" + CELL + "', " +
                   " '" + NAME.Replace("'", "") + "', " +
                   " '" + UNIT_TYPE + "', " +
                   " '" + BARCODE_SHT + "', " +
                   " '" + BARCODE_KOR + "', " +
                   " '" + BARCODE_BL + "', " +
                   " " + WEIGHT_OF_KOR.ToString().Replace(',', '.') + ", " +
                   " " + COUNT_IN_ROW + ", " +
                   " " + ROWS_IN_PAL + " , " + Количество_штук_в_коробке.ToString().Replace(',', '.') + " , 1 " +
                   " ) ";

               }
               else
               {
                   /*
                    * if (CELL.IndexOf("---") != -1)
                   {
                       CELL = decode_cell(old_cell, ware_id);
                   }
                    */


                   NAME = NAME.Replace("'", "");
                   string NAME3 = NAME.Replace("'", "");
                   strSQL = " update RABAEV.RRL_ARTICULS set  " +
                 "  NORMA_UKLADKI =" + NORMA_UKLADKI + " , " +
                 "  CELL = '" + CELL + "' , " +
                 "  NAME = '" + NAME3.Replace("'", "") + "' , " +
                 "  UNIT_TYPE = '" + UNIT_TYPE + "'  , " +
                 "  BARCODE_SHT = '" + BARCODE_SHT + "' , " +
                 "  BARCODE_KOR= '" + BARCODE_KOR + "'  , " +
                 "  BARCODE_BL=   '" + BARCODE_BL + "'  , " +
                 "  WEIGHT_OF_KOR=" + WEIGHT_OF_KOR.ToString().Replace(',', '.') + " , " +
                 "  COUNT_IN_ROW= " + COUNT_IN_ROW + "  , COUNT_SHT_IN_KOR= " +Количество_штук_в_коробке.ToString().Replace(',','.')+" , "+
                 "  ROWS_IN_PAL= " + ROWS_IN_PAL + "  where ACTICUL  =  '" + ACTICUL + "' ";

                  // MessageBox.Show(NAME3);


               }
               ora_com.CommandText = strSQL;
               ora_com.ExecuteNonQuery();

           //}
           //catch (Exception ex1)
           //{
           //    MessageBox.Show(ex1.Message);
           //}
            

            /*
             ) prop_CountPlacesInRow
           , (
             select cp.propval as krp --кол-во рядов в паллете
                  , cp.article
               from supermag.smcardproperties cp
              where cp.propid = '5'
             ) prop_CountRowsInPallet  
             * 
             * 
             * 
             * 
             * 
             * 
             * Таблице с Штрих-кодами
                select * from 
                SUPERMAG.SMStoreUnits
                where ARTICLE = 'Т0000125914'
             * 
             * select * from 
SUPERMAG.SABarcodes
             */




            // ================================================================================
        }



        private void МенюПриходныхНакладных_Click(object sender, EventArgs e)
        {

          

// ***********************************************************************************************

        }

        private void Load_othod_naklad( string NakladID2 )
        {

            string NakladID = NakladID2;
            if (NakladID == null)
                return;

            if (NakladID == "")
                return;

            NakladID = NakladID.Trim();


            DateTime ДатаНакладной = DateTime.Today ;
            long ИД_НАКЛАДНОЙ = 0;
            string Название_магазина="";
            List<object[]> lines = new List<object[]>();

            #region ЗАГРУЗКА_СОСТОЯНИЯ_НАКЛАДНЫХ_ИЗ_СУПЕР_МАГА
       
            string strSQL = "  select " +
                            "  d.id Номер,  " + 
                            "  d.createdat Дата,  " + 
                            "  s.article Артикул, " + 
                            "  s.quantity Колво, " + 
                            "  s.itemprice Цена_с_НДС, " +
                            "  c.shortname Название , cli.NAME " +
                            "  from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli " + 
                            "  where d.doctype in ( 'WO' )   " + 
                            "  and d.docstate in ( 2 , 3 ) " +
                            "  and d.id = '" + NakladID + "'  " + 
                            "  and d.id = s.docid and d.doctype = s.doctype " +
                            "  and s.article = c.article  and cli.ID = d.CLIENTINDEX  ";

                            OracleCommand ora_com = new OracleCommand();
                            ora_com.CommandText = strSQL;
                            OracleDataReader ora_reader;
                            OracleConnection ora_conn;
                            try
                            {

                                ora_conn = new OracleConnection();
                                ora_conn.ConnectionString = SM_CONNECTION_STRING();
                                ora_conn.Open();
                                ora_com.Connection = ora_conn;
                                ora_reader = ora_com.ExecuteReader();

                                while (ora_reader.Read())
                                {
                                    object[] values1 = new object[7];
                                    for (int yy = 0; yy < 7; yy++)
                                    {
                                        values1[yy] = ora_reader.GetValue(yy).ToString();
                                    }
                                    lines.Add(values1);
                                    ДатаНакладной = Convert.ToDateTime(values1[1].ToString());
                                    Название_магазина =(values1[6].ToString());
                                }

                                ora_reader.Close();
                                ora_conn.Close();

                            }catch(Exception ex)
                            {
                                MessageBox.Show(ex.Message);
                            }
            #endregion


                            #region ПРОВЕРКА
                            // ПОДГРУЖАЕМ СПИСОК АРТИКУЛОВ ИЗ WMS
                            Dictionary<string, string> arts = new Dictionary<string, string>();
                            strSQL = " SELECT ACTICUL  FROM RABAEV.RRL_ARTICULS ";
                            ora_com = new OracleCommand();
                            ora_com.CommandText = strSQL;
                            ora_conn = new OracleConnection();
                            ora_conn.ConnectionString = WMS_CONNECTION_STRING();
                            ora_conn.Open();
                            ora_com.Connection = ora_conn;
                            ora_reader = ora_com.ExecuteReader();
                            while (ora_reader.Read())
                            {
                                string art = ora_reader.GetValue(0).ToString();
                                arts.Add(art, art);
                            }

                            bool error = false;
                            string error_msg = "";
                            List<string> articuls_2_add = new List<string>();

                            foreach (object[] line in lines)
                            {// По всем строкам накладных
                                string ar1 = line[2].ToString();

                                if (!arts.ContainsKey(ar1))
                                {
                                    error = true;
                                    error_msg += " В WMS не загружен артикул " + ar1 + "  " + line[5].ToString() + " \n ";
                                    articuls_2_add.Add(ar1);
                                }
                            }
                            
                            if (error)
                            {
                                MessageBoxButtons buttons = MessageBoxButtons.YesNo;
                                DialogResult result;
                                result = MessageBox.Show(error_msg, "Загружаем артикулы?", buttons);
                                if (result == DialogResult.Yes)
                                {
                                    foreach (string kkk in articuls_2_add)
                                    SyncArticul(kkk , this.wms_user.ware_id );
                                }
                                return;
                            }

                            #endregion


            #region СОЗДАНИЕ_НАКЛАДНОЙ

                  
                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("NAKLADNAME1", OracleType.VarChar).Value = NakladID ;
                    
                    Название_магазина=Название_магазина.Replace("\\","");
                    if (Название_магазина.Length > 49)
                    {
                        Название_магазина = Название_магазина.Substring(0, 49);
                    }

                    ora_com.Parameters.Add("MAG_NO1", OracleType.VarChar).Value = Название_магазина;
                    ora_com.Parameters.Add("NAKLADDATE1", OracleType.DateTime).Value = ДатаНакладной ;
                    ora_com.Parameters.Add("CREATIONDATE1", OracleType.DateTime).Value = DateTime.Today ;
                    ora_com.Parameters.Add("PLANNEDDELIVERYDATE1", OracleType.DateTime).Value = DateTime.Today;
                    ora_com.Parameters.Add("ware_id1", OracleType.Int32 ).Value = this.wms_user.ware_id.ToString();

                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    ИД_НАКЛАДНОЙ = Convert.ToInt64( ora_com.Parameters["ID"].Value.ToString());
                 
                 


            #endregion


                            #region ЗАПИСЬ_СТРОК_НАКЛАДНОЙ_В_WMS
           foreach (object[] line in lines)
            {// По всем строкам накладных
                string articul = line[2].ToString();
                double Количество_тов = Convert.ToDouble(line[3].ToString());
                double Цена_с_ндс = Convert.ToDouble(line[4].ToString());



                
                ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.ADD_RRL_OTHOD_NAKLAD_ROWS";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("ID_ROW1", OracleType.Int32).Value = 0;

                ora_com.Parameters.Add("ID_NAKLAD1", OracleType.Int32).Value = ИД_НАКЛАДНОЙ;
                ora_com.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = articul;
                ora_com.Parameters.Add("COUNT2", OracleType.Number).Value = Количество_тов;

                ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                ora_com.ExecuteNonQuery();

                long УИД_НОВОЙ_СТРОКИ = Convert.ToInt64(ora_com.Parameters["ID"].Value);
              

     

            }
            #endregion



        }

        private void button21_Click(object sender, EventArgs e)
        {
            foreach (string line in m_spisok_otg_nakl.Lines)
            {
                Load_othod_naklad(line);
            }

            dataGridView6_CellEnter(null, null);


            MessageBox.Show("Процедура закончена.");
        }

        private void button22_Click(object sender, EventArgs e)
        {

            if (Convert.ToInt64(dataGridView6.CurrentRow.Cells[6].Value) == 2)
            {
                MessageBox.Show("накладная закрыта");
                return;
            }

            try
            {
                int order_id = Convert.ToInt32(dataGridView6.CurrentRow.Cells[0].Value.ToString());
                // ===========================================================
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_CLEAR_OTHOD_NAKLAD2";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("ID_NAKLAD1", OracleType.Int32).Value = order_id;
                ora_com.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f59 " + ex.Message);
            }

            dataGridView6_CellEnter(null, null);

        }

        private void выделитьВсеToolStripMenuItem_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView6.Rows)
            {
                 (((DataGridViewCheckBoxCell)dr.Cells[7])).Value =1;
                
            }


        }

        private void снятьВыделениеСоВсехToolStripMenuItem_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView6.Rows)
            {
                (((DataGridViewCheckBoxCell)dr.Cells[7])).Value = 0;

            }
        }

        private void провестиВыделенныеНакладныеToolStripMenuItem_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView6.Rows)
            {
               long order_id = Convert.ToInt64( ((dr.Cells[0])).Value );
               if (Convert.ToInt64( (   (DataGridViewCheckBoxCell)dr.Cells[7]).Value)     == 1)
               {
                   if (Convert.ToInt64(dr.Cells[6].Value) < 2)
                   Close_Othod_Naklad(order_id);
               }

            }
            MessageBox.Show("Процедура закончена");
        }

        private void снихронизироватьВыделенныеНакладныеToolStripMenuItem_Click(object sender, EventArgs e)
        {

            foreach (DataGridViewRow dr in dataGridView6.Rows)
            {
                string order_id = Convert.ToString(((dr.Cells[1])).Value);
                if (Convert.ToInt64(((DataGridViewCheckBoxCell)dr.Cells[7]).Value) == 1)
                {
                    if ( Convert.ToInt64( dr.Cells[6].Value )<2)
                    Load_othod_naklad(order_id);

                }

            }
            MessageBox.Show("Процедура закончена");

        }

        private void button23_Click(object sender, EventArgs e)
        {
            /*

                        string strSQL = "select UID_POLETA ,  REMAIN ,  RRL_ARTICULS.NAME from RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS   " +
            " where   RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET and " +
            " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL   " +
            " and RRL_REMAINS.CELL='" + ЯЧЕЙКА_ОТКУДА.Text + "' and REMAIN<>0 ";

            if (selected_ware > 0)
            {
                strSQL = "select UID_POLETA ,  REMAIN ,  RRL_ARTICULS.NAME from RABAEV.RRL_REMAINS , " +
               " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS ,   RABAEV.RRL_CELLS   " +
               " where ( RABAEV.RRL_ARTICULS.CELL= RABAEV.RRL_CELLS.CELL ) and (RABAEV.RRL_CELLS.ware_id in ( " + selected_ware.ToString()+
               " )  ) and ( RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET ) and " +
               " RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL   " +
               " and RRL_REMAINS.CELL='" + ЯЧЕЙКА_ОТКУДА.Text + "' and REMAIN<>0 ";
            }


            */

            int selected_ware=0;
            
            try{
                selected_ware= Convert.ToInt32( ware_id_cell.Text );
            }catch
            {
            
            }

            string sql_add = "";
            string sql_add2 = "";

            if(ЯЧЕЙКА_ОТКУДА.Text!="")
            {
                sql_add= " and ( RRL_REMAINS.CELL='" + ЯЧЕЙКА_ОТКУДА.Text + "'   ) ";
            }



            if( selected_ware >0 )
            {
             sql_add2=" and (RABAEV.RRL_CELLS.ware_id in ( " + selected_ware.ToString()+" ) ) ";
            }

            string strSQL = "select UID_POLETA ,  REMAIN ,  RRL_ARTICULS.NAME , TIME_OF_LAST_UPDATE , RRL_REMAINS.CELL  from RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_PALLETS , RABAEV.RRL_ARTICULS ,  RABAEV.RRL_CELLS   " +
            " where   ( RABAEV.RRL_ARTICULS.CELL= RABAEV.RRL_CELLS.CELL ) and ( RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET ) and " +
            " ( RRL_PALLETS.ARTICUL = RRL_ARTICULS.ACTICUL )  " +
            " and ( (RRL_REMAINS.TIME_OF_LAST_UPDATE <= " + date2sql_ora(dateTimePicker3.Value) + " ) or (RRL_REMAINS.TIME_OF_LAST_UPDATE is null )  )  and REMAIN<>0 " +
            sql_add + sql_add2;


            fill_view_MINI_WMS(dataGrid_ПАЛЛЕТЫ_ОТКУДА, strSQL, 5);


        }

        private void button24_Click(object sender, EventArgs e)
        {

            string strSQL = "select    " +
                 "   EEE.ID_EVENT       , " +
                 "   EEE.CELL_FROM      , " +
                 "   EEE.CELL_TO         , " +
                 "   EEE.DATE_EVENT     , " +
                 "   EEE.DATE_OF_ORDER   , " +
                 "   EEE.COUNT_EVENT    , " +
                 "   EEE.TYPE_EVENT       , " +
                 "   EEE.UID_POLETA      , " +
                 "   EEE.USER_ID        , " +
                 "   EEE.PRIHOD_NAKL_ID , EEE.OTHOD_NAKL_ID  , PPP.EXPIRY_DATE  " +
            " from RABAEV.RRL_EVENTS EEE , RABAEV.RRL_PALLETS PPP " +
            " where PPP.UID_PALLET  = EEE.UID_POLETA  and UID_POLETA ='" + textBox3.Text + "' order by ID_EVENT ";
      

            fill_view_MINI_WMS(dataGridView12, strSQL, 11);


             strSQL = " select    " +
             " R.CELL       , " +
             "   R.UID_POLETA      , " +
             "   R.REMAIN         , " +
             "   R.OTHOD_NAKL_ID     , " +
             "   R.TIME_OF_LAST_UPDATE , RRL_PALLETS.EXPIRY_DATE  " +
             " from RABAEV.RRL_REMAINS R , RRL_PALLETS " +
             " where R.UID_POLETA = RRL_PALLETS.UID_PALLET  and  R.UID_POLETA ='" + textBox3.Text + "'";


            fill_view_MINI_WMS(dataGridView13, strSQL, 5);


        }

        private void button25_Click(object sender, EventArgs e)
        {


            string strSQL = "select    " +
             " r.ORDID    , " +
             " r.ARTICUL  , " +
             " h.DATE_OF_ACCEPT  , " +
             " r.ID       , " +
             " r.COUNT1  ,   " +
             " r.PRICE   , SM_NAKLAD_NUMBER , CONDITION , POSTAVSHIK_NAME    " +
             " from RABAEV.RRL_PRIHOD_NAKLAD_ROWS  r , RRL_PRIHOD_NAKLAD h " +
             " where r.ORDID=h.ID(+) and   ARTICUL ='" + textBox4.Text + "'";


            fill_view_MINI_WMS(dataGridView14, strSQL, 9);



             strSQL = "select    " +
             " h.ID , r.ARTICUL ,  NAKLADDATE , r.COUNT1 , NAKLADNAME , MAG_NO , CONDITION " +
             " from RABAEV.RRL_OTHOD_NAKLAD_ROWS  r , RRL_OTHOD_NAKLAD h " +
             " where r.ID_NAKLAD=h.ID(+) and   r.ARTICUL ='" + textBox4.Text + "'";


            fill_view_MINI_WMS(dataGridView15, strSQL, 7);

        }

        private void button26_Click(object sender, EventArgs e)
        {

            string strSQL_add = "";
            if( Скрыть_движения_в_зоне_отгрузки.Checked == true  )
            {
                strSQL_add = " and not( CELL_FROM like 'EX_%' ) and not (CELL_TO like 'EX_%' ) ";
            }

            string strSQL = "select    " +
          "   EEE.ID_EVENT       , " +
          "   EEE.CELL_FROM      , " +
          "   EEE.CELL_TO         , " +
          "   EEE.DATE_EVENT     , " +
          "   EEE.DATE_OF_ORDER   , " +
          "   EEE.COUNT_EVENT    , " +
          "   EEE.TYPE_EVENT       , " +
          "   EEE.UID_POLETA      , " +
          "   EEE.USER_ID        , " +
          "   EEE.PRIHOD_NAKL_ID  ,  EEE.OTHOD_NAKL_ID  , PPP.EXPIRY_DATE " +
          " from RABAEV.RRL_EVENTS EEE , RABAEV.RRL_PALLETS PPP " +
          " where PPP.UID_PALLET  = EEE.UID_POLETA  and PPP.ARTICUL='" + textBox4.Text + "'  " + strSQL_add + " order by ID_EVENT ";


            fill_view_MINI_WMS(dataGridView12, strSQL, 11);

            if (Скрыть_движения_в_зоне_отгрузки.Checked == true)
            {
                strSQL_add = " and not( CELL like 'EX_%' ) ";
            }
            strSQL = "select    " +
            "   EEE.CELL       , " +
            "   EEE.UID_POLETA      , " +
            "   EEE.REMAIN         , " +
            "   EEE.OTHOD_NAKL_ID     , " +
            "   EEE.TIME_OF_LAST_UPDATE   " +
            " from RABAEV.RRL_REMAINS EEE ,  RABAEV.RRL_PALLETS PPP  " +
            " where  PPP.UID_PALLET  =EEE.UID_POLETA   and PPP.ARTICUL='" + textBox4.Text + "' " + strSQL_add ;


            fill_view_MINI_WMS(dataGridView13, strSQL, 5);


        }

        private void button27_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView12);
        }

        private void button28_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView13);
        }

        private void button29_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView14);
        }

        private void button30_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView15);
        }

        private void button31_Click(object sender, EventArgs e)
        {

            // Для каждого артикула: 
            // Сумма приходных накладных - сумма расходных накладных = сумме остатков по ячейкам, где можно мерять остатки
            // Иначе  - ошибка и выводим такой артикул в отчет


            // =======================================================================

            Dictionary<string, object[]> lines_SM = new Dictionary<string, object[]>();
            Dictionary<string, object[]> lines_WMS = new Dictionary<string, object[]>();
            Dictionary<string, object[]> lines_RESULT = new Dictionary<string, object[]>();
            Dictionary<string, string> Список_Артикулов = new Dictionary<string, string>();

            string sql1 = "";
            string sql2 = "";
            string sql3 = "and ware_id="+this.wms_user.ware_id.ToString();

            if (Фильтр_артикула.Text!="")
           {
               sql2 = " and ( r.ARTICUL =  '" + Фильтр_артикула.Text.Trim() + "'  ) ";
               sql3 = "";

           }

           string strSQL = " select NAKLADNAME, ARTICUL , COUNT1 , DATE_OF_ACCEPT " +
            " from RABAEV.RRL_OTHOD_NAKLAD_ROWS r , RABAEV.RRL_OTHOD_NAKLAD h " +
            " where h.ID= r.ID_NAKLAD " +
            " and condition=2 and ware_id=" + this.wms_user.ware_id.ToString() + sql1;



            long pos4 = 0;
            OracleConnection ora_conn;
            OracleCommand ora_com;
            OracleDataReader ora_reader;
            ora_com = new OracleCommand();

            // Список_Артикулов
            #region ВЫДЕЛЕНИЕ СПИСКА АРТИКУЛОВ
            strSQL = " select A.ACTICUL from RABAEV.RRL_ARTICULS A , RABAEV.RRL_CELLS C where A.CELL = C.CELL and C.ware_id=" + this.wms_user.ware_id.ToString() + " ";
            string SQL_IN = "";
            string SQL_IN2 = "";
            if (Фильтр_артикула.Text == "")
            {
                try
                {
                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = WMS_CONNECTION_STRING();
                    ora_conn.Open();
                    ora_com.Connection = ora_conn;
                    ora_com.CommandText = strSQL;
                    ora_reader = ora_com.ExecuteReader();

                    while (ora_reader.Read())
                    {
                        SQL_IN = SQL_IN + " s.article= '" + ora_reader.GetValue(0).ToString() + "' or";
                        SQL_IN2 = SQL_IN2 + " r.ARTICUL= '" + ora_reader.GetValue(0).ToString() + "' or";
                    }
                    SQL_IN = " ( " + SQL_IN.Trim('r').Trim('o') + " ) ";
                    SQL_IN2 = " ( " + SQL_IN2.Trim('r').Trim('o') + " ) ";
                    ora_reader.Close();
                    ora_conn.Close();

                }
                catch (Exception ex)
                {
                    MessageBox.Show("r4 " + ex.Message);
                }
            }
            else
            {
                SQL_IN = "  s.article='" + Фильтр_артикула.Text.Trim() + "'  ";
                SQL_IN2 = "  ( r.ARTICUL ='" + Фильтр_артикула.Text.Trim() + "' ) ";
            }
            #endregion


            strSQL = " select SM_NAKLAD_NUMBER, r.ARTICUL , COUNT1 , a.NAME , DATE_OF_ACCEPT " +
            " from RABAEV.RRL_PRIHOD_NAKLAD_ROWS r , RABAEV.RRL_PRIHOD_NAKLAD h , RABAEV.RRL_ARTICULS a " +
            " where h.ID= r.ORDID " +
            " and condition=2 and a.ACTICUL = r.ARTICUL and DATE_OF_ACCEPT  between " +
            " to_date( " + date2sql_ora(Дата_проверки_движений_от.Value) + " ,'dd.mm.yyyy') and to_date(" + date2sql_ora(Дата_проверки_движений_до.Value) +
            ",'dd.mm.yyyy') and (" + SQL_IN2 + ") " + sql2 + " order by  COUNT1 desc ";// + sql3 
            string key="";


            
            ora_com.CommandText = strSQL;


            long pos1 = 0;


            try
            {
                ora_conn = new OracleConnection();
                ora_conn.ConnectionString = WMS_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = strSQL;
                ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {
                    object[] values1 = new object[7];
                    for (int yy = 0; yy < 5; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }

                    if( Сравнивать_по_датам.Checked ){
                        key = values1[4].ToString() + "_" + values1[1].ToString();
                    }else{
                        key = values1[0].ToString() + "_" + values1[1].ToString();
                    }

                    try
                    {
                        lines_WMS.Add(key, values1);
                    }catch
                    {
                       // lines_WMS[key] = Convert.ToInt32( lines_WMS[key] ) + values1;
                        key = values1[0].ToString() + "_" + values1[1].ToString();
                        lines_WMS.Add(key, values1);
                    }
                    pos4++;
                }

                MessageBox.Show("Сколичество движений по WMS = " + pos4.ToString());
                ora_reader.Close();
                ora_conn.Close();

            }
            catch (Exception ex)
            {
                MessageBox.Show("r4 " + ex.Message);
            }



                // Сверка приходных накладных

            strSQL = "   select  Номер , Артикул , Колво , Название , createdat   from ( select " +
            " d.id Номер,  " +
            " s.article Артикул, " +
            " sum(s.quantity) Колво, " +
            " c.shortname Название , d.createdat " +
           
            " from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli " +
            " where d.doctype in ( 'WO' ,  'WI' , 'IW' )  " +
            " and d.docstate in ( 2 , 3 )  " +
            " and d.createdat between " +
            " to_date( " + date2sql_ora(Дата_проверки_движений_от.Value) + " ,'dd.mm.yyyy') and to_date(" + date2sql_ora(Дата_проверки_движений_до.Value) + ",'dd.mm.yyyy')  " +
            " and s.article in ( " +
            "     SELECT DISTINCT ARTICLE " +
            "     FROM supermag.smcardassort , supermag.sacardassort " +
            "     where idassort=supermag.sacardassort.ID " +
            //  s.article in 
            "      and (  "+ SQL_IN  +"  )    " +
            " ) " +
            " and d.id = s.docid and d.doctype = s.doctype  " +
            " and s.article = c.article " +
            " and  ( d.locationto=2  ) " +
            " and cli.ID = d.CLIENTINDEX "+        
            " group by d.id ,   s.article ,  d.createdat ,  " +
            " c.shortname ) order by Колво desc ";

            //( tree  like '82.5%' ) or ( tree like '1.5.1.5%' )  or 
            ora_com.CommandText = strSQL;

            try
            {

                ora_conn = new OracleConnection();
                ora_conn.ConnectionString = SM_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_reader = ora_com.ExecuteReader();

                while (ora_reader.Read())
                {

                    object[] values1 = new object[5];
                    for (int yy = 0; yy < 5; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }

                    if (Сравнивать_по_датам.Checked)
                    {
                        key = values1[4].ToString() + "_" + values1[1].ToString();
                    }
                    else {
                        key = values1[0].ToString() + "_" + values1[1].ToString();
                    }
                    try
                    {
                        lines_SM.Add(key, values1);
                    }
                    catch
                    {
                        key = values1[0].ToString() + "_" + values1[1].ToString();
                        lines_SM.Add(key, values1);
                    }
                    pos1++;
                }

                ora_reader.Close();
                ora_conn.Close();

                MessageBox.Show("Сколичество движений по СМ = " + pos1.ToString());
            }
            catch (Exception ex)
            {
                MessageBox.Show( ex.Message + " "+ key );
            }







            foreach (string kk in lines_SM.Keys)
            { // ЦИКЛ ===============================================
                object[] arr_2_res = new object[7];
                object[] vvv;
                if (lines_WMS.TryGetValue(kk, out vvv))
                {
                    arr_2_res[0] = vvv[0];// номер накладной
                    arr_2_res[1] = vvv[1];// артикул
                    arr_2_res[2] = vvv[2];// количество
                    arr_2_res[3] = lines_SM[kk][2]; // количество 
                    arr_2_res[4] = lines_SM[kk][3]; //  имя 
                    arr_2_res[6] = lines_SM[kk][4]; //  дата 

                    if ((Выводить_только_разницу.Checked == false) || (arr_2_res[2].ToString() != arr_2_res[3].ToString() ))
                    {
                        lines_RESULT.Add(kk, arr_2_res);
                    }

                    lines_WMS.Remove(kk);
                }
                else
                {
                    arr_2_res[0] = lines_SM[kk][0];// номер накладной
                    arr_2_res[1] = lines_SM[kk][1];// артикул
                    arr_2_res[2] = 0;// количество
                    arr_2_res[3] = lines_SM[kk][2]; // количество 
                    arr_2_res[4] = lines_SM[kk][3];// 
                    arr_2_res[5] = "нет в WMS";
                    arr_2_res[6] = lines_SM[kk][4]; //  дата 

                    string keyrr = "";
                    if (Сравнивать_по_датам.Checked)
                    {
                        keyrr = lines_SM[kk][4].ToString() + "_" + lines_SM[kk][1].ToString();
                    }
                    else
                    {
                        keyrr = lines_SM[kk][0].ToString() + "_" + lines_SM[kk][1].ToString();
                    }

                    try
                    {
                        lines_RESULT.Add(keyrr, arr_2_res);
                    }
                    catch {
                        keyrr = lines_SM[kk][0].ToString() + "_" + lines_SM[kk][1].ToString();
                        lines_RESULT.Add(keyrr, arr_2_res);
                    }
                }
            } // ЦИКЛ ===============================================


            foreach (string kkk in lines_WMS.Keys)
            {
                object[] arr_2_res = new object[7];
                arr_2_res[0] = lines_WMS[kkk][0];// номер накладной
                arr_2_res[1] = lines_WMS[kkk][1];// артикул
                arr_2_res[2] = lines_WMS[kkk][2];// количество
                arr_2_res[3] = 0; // количество 

                arr_2_res[4] = lines_WMS[kkk][3];// количество
                arr_2_res[5] = "нет в СМ";
                arr_2_res[6] = lines_WMS[kkk][4];// дата

                string keyuuu = "";
                if (Сравнивать_по_датам.Checked)
                {
                    keyuuu = lines_WMS[kkk][4].ToString() + "_" + lines_WMS[kkk][1].ToString();
                }
                else
                {
                    keyuuu = lines_WMS[kkk][0].ToString() + "_" + lines_WMS[kkk][1].ToString() ;
                }

                try
                {
                    lines_RESULT.Add(keyuuu, arr_2_res);
                }
                catch {
                    keyuuu = lines_WMS[kkk][0].ToString() + "_" + lines_WMS[kkk][1].ToString();
                    lines_RESULT.Add(keyuuu, arr_2_res);
                }

            }


            // =======================================================================

            dataGridView16.Rows.Clear();
            foreach (string k1 in lines_RESULT.Keys)
            { // ============================================

               int yyyyy= dataGridView16.Rows.Add(lines_RESULT[k1]);
               dataGridView16.Rows[yyyyy].Cells[7].Value = k1;

            } // =============================================
            MessageBox.Show("процедура сравнения закончена");
        }

        private void button32_Click(object sender, EventArgs e)
        {
            grid_2_excel( dataGridView16  );
        }

        public string wms_get_spfunction_value(string spf , string param_name , string value )
        { 
         
            // ================================


            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = spf;
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add(param_name, OracleType.VarChar).Value = value;
            ora_com.Parameters.Add("ret", OracleType.VarChar,255).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com.ExecuteNonQuery();
            string ret= ora_com.Parameters["ret"].Value.ToString();

            // ================================

        return ret;
        }

        public string wms_get_spfunction_n2c_value(string spf, string param_name, string value)
        {

            // ================================


            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = spf;
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add(param_name, OracleType.Int32).Value = value;
            ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();

            // ================================

            return ret;
        }

        public string wms_get_spfunction_n2n_value(string spf, string param_name, string value)
        {

            // ================================

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = spf;
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add(param_name, OracleType.Int32).Value = value;
            ora_com.Parameters.Add("ret", OracleType.Number).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com.ExecuteNonQuery();
            string ret = ora_com.Parameters["ret"].Value.ToString();

            // ================================

            return ret;
        }

        private void load_st_from_sm(string lll, int is_faked, string faked_articul, string faked_articul_name)
        {
            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ
            long current_ware_id = 0;


            long position_in_line = 0;
            long КрасивыйНомерПаллета = 0;
            long КоличествоНеПерегруженныхСТ = 0;

            long local_ware_id = 0;


            #endregion 

            
                #region ЗАГРУЗКА НАКЛАДНОЙ
                OracleCommand ora_com2 = new OracleCommand();
                OracleConnection ora_con2 = new OracleConnection();
                ora_con2.ConnectionString = SM_CONNECTION_STRING();
                ora_con2.Open();
                ora_com2.Connection = ora_con2;
                // СНАЧАЛА ПОЛУЧИМ ВСЕ ПАРАМЕТРЫ ЗАКАЗА
                string strSQL = "  select d.id   " +
                "  , d.createdat " +
                "  , decode(d.docstate, 1, 'Черновик', 2, 'Принят к исполнению', 3, 'Выполнен') dstate " +
                "  , l.name fromname " +
                "  , (select distinct name from supermag.smstorelocations i  " +
                "   where i.id in (select parentloc from supermag.smstorelocations where id=d.location)) toname " +
                " from supermag.smdocuments d " +
                " , supermag.smstorelocations l  " +
                " where d.doctype='SO' " +
                " and d.id='" + lll + "' " +
                " and d.location=l.id ";

                ora_com2.CommandText = strSQL;

                OracleDataReader ora_reader = ora_com2.ExecuteReader();
            

            if (ora_reader.Read())
            {
                object[] values1 = new object[5];
                for (int yy = 0; yy < 5; yy++)
                {
                    values1[yy] = ora_reader.GetValue(yy).ToString();
                }

                DateTime Create_DATE = Convert.ToDateTime(values1[1]);
                string DSSTATE = values1[2].ToString();
                string ADDR = values1[3].ToString();


                if (is_faked == 0)
                {
                    #region ЕСЛИ_СКЛАД_НЕ_ФЕЙКОВЫЙ

                    #region РАЗБИВАЕМ СТ НА ПАЛЛЕТЫ

                    int rowsAffected2 = 0;
                    OracleCommand ora_com3 = new OracleCommand();
                    ora_com3.Connection = ora_con2;
                    ora_com3.CommandType = CommandType.Text;
                    ora_com3.CommandText = "DECLARE cntPos number;   begin   cntPos:=SUPERMAG.fill_mon_wms_stbypall( '" + lll + "' ); end ;";
                    ora_com3.ExecuteNonQuery();

                    #endregion





                    #region ЗАПРОС СТРОК ПАЛЛЕТ ПО ДАННОМУ СТ

                    ora_com3.CommandText = "  select  DOCID ,   article, shortname, replace(bc,';',';'||CHR(10)) bc, abbrev,  " +
                    "  tareweight, path, round(order_weight,4), taresize, quantity,  " +
                    "  round(sum (dd),4) ddd, dd1 as паллет ,  sortfield, auction , round(AQ , 0 ) as количество_коробок  " +
                    "  from (select   *  " +
                    "       from supermag.mon_wms_stbypall t  " +
                    "   order by t.sortfield) where DOCID='" + lll + "' " +
                    "  group by  " +
                    "  DOCID ,  section,  " +
                    "  pass,  pp, specitem, article,  " +
                    "  shortname, bc, abbrev, tareweight,  " +
                    "  ap, aq,  path, order_weight,  " +
                    "  taresize,  quantity, dd1,  " +
                    "  dd2, sortfield, pr, auction  " +
                    "  order by DOCID , dd1 , sortfield  ";

                    OracleDataReader ora_reader4 = ora_com3.ExecuteReader();
                    long last_pall_number = 0;
                    long curr_pall_number = 0;

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    string PALLET_UID1 = "";

                    while (ora_reader4.Read())
                    {
                        
                        object[] values6 = new object[15];
                        for (int yy = 0; yy < 15; yy++)
                        {
                            values6[yy] = ora_reader4.GetValue(yy).ToString();
                        }

                        current_ware_id = WARE_ID_BY_ADDR(values6[6].ToString());

                        string curr_articul = values6[1].ToString();
                        curr_pall_number = Convert.ToInt32(values6[11].ToString());
                        if (last_pall_number != curr_pall_number)
                        { // новый паллет
                            КрасивыйНомерПаллета++;

                            #region СОЗДАНИЕ_ПАЛЛЕТЫ
                            PALLET_UID1 = "OP_" + lll + "_" + КрасивыйНомерПаллета.ToString();
                            // Alert(PALLET_UID1);
                            local_ware_id = current_ware_id;
                            OracleCommand ora_com9 = new OracleCommand();
                            ora_com9.Connection = get_wms_connection();
                            try
                            {

                                ora_com9.CommandText = "select ware_id from RABAEV.RRL_ARTICULS A , RABAEV.RRL_CELLS C where A.CELL = C.CELL and A.ACTICUL = '" + curr_articul + "'  ";
                                local_ware_id = Convert.ToInt32(ora_com9.ExecuteScalar());
                                if (local_ware_id == 0)
                                {
                                    SyncArticul(curr_articul, current_ware_id);
                                }
                            }
                            catch (Exception ex1)
                            { // Надо подгрузить артикул
                                SyncArticul(curr_articul, current_ware_id);
                            }

                            string[] NAPR1 = ADDR.Split('-');
                            string NAPR = "неизв";
                            if (NAPR1.Length >= 1)
                                NAPR = NAPR1[0];

                            if (NAPR == "")
                            {
                                NAPR = "НЕИЗВ";
                            }


                            if (!наследовать_склад_от_товара.Checked)
                            {
                                            
                                    try{
                                         current_ware_id = Convert.ToInt32( comboBox1.Text[0].ToString());
                                         long current_ware_id2 = 0;
                                         try
                                         {
                                            current_ware_id2= Convert.ToInt32(comboBox1.Text[0].ToString() + comboBox1.Text[1].ToString());
                                         }
                                         catch { }
                                         if (current_ware_id2 > current_ware_id)
                                         {
                                             current_ware_id = current_ware_id2;
                                         }

                                    }catch(Exception ex)
                                    {
                                        MessageBox.Show("Не определен склад");
                                        return;
                                    }

                            }

                            ora_com9.CommandText = "RABAEV.RRL_SBORKA_PALLETS_ADD2";
                            ora_com9.CommandType = CommandType.StoredProcedure;
                            ora_com9.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = lll;
                            ora_com9.Parameters.Add("ADDR1", OracleType.VarChar).Value = ADDR;
                            ora_com9.Parameters.Add("PALLET_NUMBER1", OracleType.Int32).Value = КрасивыйНомерПаллета;
                            ora_com9.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                            ora_com9.Parameters.Add("STATE1", OracleType.VarChar).Value = DSSTATE;
                            ora_com9.Parameters.Add("STDATE1", OracleType.DateTime).Value = Create_DATE;
                            ora_com9.Parameters.Add("NAPR1", OracleType.VarChar).Value = NAPR;
                            ora_com9.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                            ora_com9.Parameters.Add("USER_ID1", OracleType.VarChar).Value = this.wms_user.user_id;
                            ora_com9.Parameters.Add("id", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                            int rowsAffected = ora_com9.ExecuteNonQuery();
                            long ret_id = Convert.ToInt32(ora_com9.Parameters["id"].Value.ToString());
                            ora_com9.Dispose();
                            #endregion
                            last_pall_number = curr_pall_number;
                        }
                        #region СОЗДАНИЕ СТРОКИ ПАЛЛЕТЫ

                        //	1	DOCID	Номер накладной
                        //	2	ARTICLE	Артикул
                        //	3	SHORTNAME	Имя товара
                        //	4	BC	Штрих-код
                        //	5	ABBREV	шт
                        //	6	TAREWEIGHT	вес 
                        //	7	PATH	ячейка отбора 
                        //	8	ORDER_WEIGHT	вес 
                        //	9	TARESIZE	объем
                        //	10	QUANTITY	количество
                        //	11	DDD	
                        //	12	ПАЛЛЕТ	паллет
                        //	13	SORTFIELD	сортировка
                        //	14	AUCTION	акция
                        OracleCommand ora_com7 = new OracleCommand();
                        ora_com7.Connection = get_wms_connection();

                        try
                        {

                            ora_com7.CommandText = "select ware_id from RABAEV.RRL_ARTICULS A , RABAEV.RRL_CELLS C where A.CELL = C.CELL and A.ACTICUL = '" + values6[1].ToString() + "'  ";


                            long sdgf_ware_id = Convert.ToInt32(ora_com7.ExecuteScalar());
                            if ((sdgf_ware_id == null) || (sdgf_ware_id == 0))
                                SyncArticul(values6[1].ToString(), current_ware_id);

                        }
                        catch (Exception ex1)
                        { // Надо подгрузить артикул
                            SyncArticul(values6[1].ToString(), current_ware_id);
                        }


                        ora_com7.CommandText = "RABAEV.RRL_SBORKA_PALLET_ROWS_ADD4";
                        ora_com7.CommandType = CommandType.StoredProcedure;
                        ora_com7.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                        ora_com7.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = values6[1].ToString();
                        ora_com7.Parameters.Add("SHORTNAME1", OracleType.VarChar).Value = values6[2].ToString();
                        ora_com7.Parameters.Add("SHTRIHKOD1", OracleType.VarChar).Value = values6[3].ToString();
                        ora_com7.Parameters.Add("EI1", OracleType.VarChar).Value = values6[4].ToString();
                        ora_com7.Parameters.Add("TAREWEIGHT1", OracleType.Number).Value = Convert.ToDouble(values6[5]);
                        ora_com7.Parameters.Add("PATH1", OracleType.VarChar).Value = (values6[6].ToString());
                        ora_com7.Parameters.Add("ORDER_WEIGHT1", OracleType.Number).Value = Convert.ToDouble(values6[7]);
                        ora_com7.Parameters.Add("TARESIZE1", OracleType.Number).Value = Convert.ToDouble(values6[8]);
                        ora_com7.Parameters.Add("QUANTITY1", OracleType.Number).Value = Convert.ToDouble(values6[9]);
                        ora_com7.Parameters.Add("SORTFIELD1", OracleType.Int32).Value = Convert.ToInt32(values6[12]);
                        ora_com7.Parameters.Add("AUCTION1", OracleType.VarChar).Value = values6[13].ToString();
                        ora_com7.Parameters.Add("DOCID1", OracleType.VarChar).Value = values6[0].ToString();
                        ora_com7.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                        ora_com7.Parameters.Add("PACK_COUNT1", OracleType.Int32).Value = Convert.ToDouble(values6[14]);
                        ora_com7.Parameters.Add("id1", OracleType.Int32).Direction = ParameterDirection.ReturnValue;

                        int rowsAffected7 = ora_com7.ExecuteNonQuery();
                        long ret_id7 = Convert.ToInt32(ora_com7.Parameters["id1"].Value.ToString());
                        ora_com7.Dispose();



                        #endregion

                    }





                    #endregion

                    #endregion
                }
                else
                {
                    #region ЕСЛИ СКЛАД ФЕЙКОВЫЙ

                    //СМОТРИМ СТ СБОРКА ТАКИМ НОМЕРОМ В БАЗЕ ВМС. ЕСЛИ УЖЕ ЕСТЬ = ВЫХОДИМ
                    string strSQL5 = " select count(ID) from RABAEV.RRL_SBORKA_PALLETS where ST_NUMBER='" + lll + "' ";
                    OracleCommand ora_com9 = new OracleCommand();
                    ora_com9.CommandText = strSQL5;
                    ora_com9.Connection = get_wms_connection();
                    long l_count_of_such_st = Convert.ToUInt32(ora_com9.ExecuteScalar());
                    if (l_count_of_such_st == 0)
                    { //ИНАЧЕ СОЗДАЕМ ПАЛЛЕТ С 1 СТРОКОЙ.
                        КрасивыйНомерПаллета = 1;
                        string PALLET_UID1 = "OP_" + lll + "_" + КрасивыйНомерПаллета.ToString();
                        #region СОЗДАЕМ_ПАЛЛЕТ
                        string[] NAPR1 = ADDR.Split('-');
                        string NAPR = "неизв";
                        if (NAPR1.Length >= 1)
                            NAPR = NAPR1[0];

                        if (NAPR == "")
                        {
                            NAPR = "НЕИЗВ";
                        }

                        ora_com9.CommandText = "RABAEV.RRL_SBORKA_PALLETS_ADD2";
                        ora_com9.CommandType = CommandType.StoredProcedure;
                        ora_com9.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = lll;
                        ora_com9.Parameters.Add("ADDR1", OracleType.VarChar).Value = ADDR;
                        ora_com9.Parameters.Add("PALLET_NUMBER1", OracleType.Int32).Value = КрасивыйНомерПаллета;
                        ora_com9.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                        ora_com9.Parameters.Add("STATE1", OracleType.VarChar).Value = DSSTATE;
                        ora_com9.Parameters.Add("STDATE1", OracleType.DateTime).Value = Create_DATE;
                        ora_com9.Parameters.Add("NAPR1", OracleType.VarChar).Value = NAPR;
                        ora_com9.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                        ora_com9.Parameters.Add("USER_ID1", OracleType.VarChar).Value = this.wms_user.user_id;
                        ora_com9.Parameters.Add("id", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected = ora_com9.ExecuteNonQuery();
                        long ret_id = Convert.ToInt32(ora_com9.Parameters["id"].Value.ToString());
                        ora_com9.Dispose();

                        #endregion

                        #region СОЗДАЕМ СТРОЧКУ ПАЛЛЕТА
                        OracleCommand ora_com10 = new OracleCommand();
                        ora_com10.CommandText = "RABAEV.RRL_SBORKA_PALLETS_ADD2";
                        ora_com10.CommandType = CommandType.StoredProcedure;
                        ora_com10.Connection = get_wms_connection();

                        ora_com10.CommandText = "RABAEV.RRL_SBORKA_PALLET_ROWS_ADD4";
                        ora_com10.CommandType = CommandType.StoredProcedure;
                        ora_com10.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                        ora_com10.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = faked_articul;
                        ora_com10.Parameters.Add("SHORTNAME1", OracleType.VarChar).Value = faked_articul_name;
                        ora_com10.Parameters.Add("SHTRIHKOD1", OracleType.VarChar).Value = "";
                        ora_com10.Parameters.Add("EI1", OracleType.VarChar).Value = "кг";
                        ora_com10.Parameters.Add("TAREWEIGHT1", OracleType.Number).Value = 1;
                        ora_com10.Parameters.Add("PATH1", OracleType.VarChar).Value = "";
                        ora_com10.Parameters.Add("ORDER_WEIGHT1", OracleType.Number).Value = 1;
                        ora_com10.Parameters.Add("TARESIZE1", OracleType.Number).Value = 1;
                        ora_com10.Parameters.Add("QUANTITY1", OracleType.Number).Value = 1;
                        ora_com10.Parameters.Add("SORTFIELD1", OracleType.Int32).Value = 1;
                        ora_com10.Parameters.Add("AUCTION1", OracleType.VarChar).Value = "";
                        ora_com10.Parameters.Add("DOCID1", OracleType.VarChar).Value = "";
                        ora_com10.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                        ora_com10.Parameters.Add("PACK_COUNT1", OracleType.Int32).Value = 1;
                        ora_com10.Parameters.Add("id1", OracleType.Int32).Direction = ParameterDirection.ReturnValue;

                        int rowsAffected7 = ora_com10.ExecuteNonQuery();
                        long ret_id7 = Convert.ToInt32(ora_com10.Parameters["id1"].Value.ToString());
                        ora_com10.Dispose();



                        #endregion

                    }


                    #endregion
                }





            }


            #endregion


        
        }

        private void ЗАГРУЗИТЬ_СТ_ИЗ_СМ_Click(object sender, EventArgs e)
        {
            long current_ware_id = 1;
            try
            {
                 current_ware_id = Convert.ToInt32( comboBox1.Text[0].ToString());

                 long current_ware_id2 = 0;
                 try
                 {
                     current_ware_id2 = Convert.ToInt32(comboBox1.Text[0].ToString() + comboBox1.Text[1].ToString());
                 }
                 catch { }

                 if (current_ware_id < current_ware_id2) 
                 {
                     current_ware_id = current_ware_id2;
                 }

            }catch(Exception ex)
            {
                MessageBox.Show("Выберите склад");
                return;
            }

            if (!has_right("LOAD_ST"))
            {
                MessageBox.Show(" Нет прав на подгрузку заявок в WMS. ");
                return;
            }


            OracleCommand ora_com6 = new OracleCommand();
            ora_com6.CommandText = " select FAKE_ROWS  from RRL_WARES where ID="+current_ware_id.ToString()+" ";
            ora_com6.Connection = get_wms_connection();
            object ooo = ora_com6.ExecuteScalar();
            long is_faked = Convert.ToInt32 ( ooo );
            ora_com6.CommandText = " select FAKE_ART  from RRL_WARES where ID=" + current_ware_id.ToString() + " ";
            string faked_articul = Convert.ToString (ora_com6.ExecuteScalar());

            ora_com6.CommandText = " select NAME    from RRL_ARTICULS where ACTICUL='" + faked_articul + "' ";
            string faked_articul_name = Convert.ToString(ora_com6.ExecuteScalar());

            long position_in_line=0;
            long КрасивыйНомерПаллета = 0;
            long КоличествоНеПерегруженныхСТ = 0;
           List<string> Список_не_корректно_загруженных_ст=  new List<string>();
           string Список_не_удаленных_ст = "";
            foreach (string lll2 in СТ_ИЗ_СУПЕРМАГА.Lines)
            {


                КрасивыйНомерПаллета = 0;
                position_in_line++;
               // statusBar2.Text=" обработка СТ "+position_in_line.ToString()+" из "+СТ_ИЗ_СУПЕРМАГА.Lines.Length.ToString() ;
                long local_ware_id = 0;
                string lll = lll2.Trim();


                if (wms_get_spfunction_value("RRL_MAY_DELETE", "ST_N", lll) == "yes")
                { // ЕСЛИ ДАННОЕ СТ МОЖНО ТРОГАТЬ

                    if (lll != "")
                    {
                        #region УДАЛЕНИЕ НАКЛАДНЫХ

                        if (УдалятьСТПередЗагрузкой.Checked)
                        {
                            if (has_right("DELETE_ST"))
                            {
                                wms_get_spfunction_value("RRL_DELETE_ST", "ST_NUMBER1", lll.Trim());
                                

                            }
                            else {
                                MessageBox.Show("Нет прав на удаление накладных");
                            }
                        }



                        #endregion

                        bool transfer_suceeded=false;
                        bool exit_ = false;
                        int количество_попыток_загрузить_ст = 0;
                        while ((transfer_suceeded == false) && (exit_ == false))
                        {
                            load_st_from_sm(lll, (int)is_faked, faked_articul, faked_articul_name);
                            List<Dictionary<string, object>> res123 = new List<Dictionary<string, object>>();
                            res123 = СравнитьЗаказСМСЗаказомWMS(lll);
                            if (res123 == null) { transfer_suceeded = true; }
                            else { if (res123.Count == 0) { transfer_suceeded = true; } }
                            количество_попыток_загрузить_ст++;
                            if (количество_попыток_загрузить_ст >= 4)
                            {
                                exit_ = true;
                                Список_не_корректно_загруженных_ст.Add(lll);
                                load_st_from_sm(lll, (int)is_faked, faked_articul, faked_articul_name);
                            }
                            else
                            {
                                if (transfer_suceeded == false)
                                {
                                    wms_get_spfunction_value("RRL_DELETE_ST", "ST_NUMBER1", lll.Trim());
                                }
                            }
                        }


                    }

                }
                else
                {
                    Список_не_удаленных_ст = Список_не_удаленных_ст + " " + lll;
                    КоличествоНеПерегруженныхСТ++;
                }


            }

            string add_2="";
            if( Список_не_корректно_загруженных_ст.Count>0 )
            {
                add_2 = "\n Список не корректно загруженных ст: \n ";
                foreach( string a2 in Список_не_корректно_загруженных_ст  )
                {
                    add_2 = add_2 + " " + a2;
                }
            }

            string add_3 = "";
            if (Список_не_удаленных_ст.Length > 0)
            {
                add_3 = "\n " +Список_не_удаленных_ст;
            }

            MessageBox.Show("Процедура загрузки складских требований закончена. \n Количесвто СТ=" + position_in_line.ToString() 
                + ". \n Количество СТ, которые были уже подгружены = " + КоличествоНеПерегруженныхСТ.ToString() + add_2+
                add_3);


        }

        private void button33_Click(object sender, EventArgs e)
        {
            if (КудаПеремещетьПополнение.Text!="")
            { 
                // =======================

                    OracleCommand ora_com = new OracleCommand();

                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.RRL_GIVE_POPOLNENIE2";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("PIKING_CELL", OracleType.VarChar).Value = КудаПеремещетьПополнение.Text;
                    ora_com.Parameters.Add("ware_id1", OracleType.Int32).Value =  this.wms_user.ware_id ;                     
                    ora_com.Parameters.Add("row_uid", OracleType.VarChar,50).Direction = ParameterDirection.ReturnValue;

                    int rowsAffected = ora_com.ExecuteNonQuery();
                    ЯчейкаОткуда.Text  = ora_com.Parameters["row_uid"].Value.ToString();

                // =======================
            }


        }

        private void toolStripMenuItem1_Click(object sender, EventArgs e)
        {


            List<object[]> lines = new List<object[]>();
            long УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ = 0;

            if ( true )
            {
                if (dataGridView_prihod.CurrentRow != null)
                {
                    string NakladID = dataGridView_prihod.CurrentRow.Cells[0].Value.ToString();
                    long sost = Convert.ToInt64(dataGridView_prihod.CurrentRow.Cells[5].Value);
                    УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ = Convert.ToInt64(dataGridView_prihod.CurrentRow.Cells[6].Value);


                    #region ЧИСТИМ 

                        OracleCommand ura_com8 = new OracleCommand();
                        ura_com8.Connection = get_wms_connection();
                        ura_com8.CommandText = "RABAEV.RRL_CLEAR_PRIH_NAKLAD_ROWS";
                        ura_com8.CommandType = CommandType.StoredProcedure;
                        ura_com8.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ;
                        ura_com8.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected = ura_com8.ExecuteNonQuery();
                        string tmpVar = ura_com8.Parameters["tmpVar"].Value.ToString();

                    #endregion



                    #region  Интеграция_с_супермагом_ЗАГРУЗИЛИ_СТРОКИ_НАКЛАДНОЙ
                    if (sost == 0)
                    {
                        // Интеграция с супермагом 
                        // ЗАГРУЗИЛИ СТРОКИ НАКЛАДНОЙ

                        string strSQL = "  select " +
                        "  d.id Номер,  " +
                        "  d.createdat Дата,  " +
                        "  s.article Артикул, " +
                        "  s.quantity Колво, " +
                        "  s.itemprice Цена_с_НДС, " +
                        "  c.shortname Название , cli.NAME " +
                        "  from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli " +
                        "  where d.doctype in ( 'WI' )   " +
                        "  and d.docstate in ( 1 , 2 , 3 ) " +
                        "  and d.id = '" + NakladID + "'  " +
                        "  and d.id = s.docid and d.doctype = s.doctype " +
                        "  and s.article = c.article  and cli.ID = d.CLIENTINDEX  ";

                        OracleCommand ora_com = new OracleCommand();
                        ora_com.CommandText = strSQL;

                        try
                        {

                            OracleConnection ora_conn = new OracleConnection();
                            ora_conn.ConnectionString = SM_CONNECTION_STRING();
                            ora_conn.Open();
                            ora_com.Connection = ora_conn;
                            OracleDataReader ora_reader = ora_com.ExecuteReader();

                            while (ora_reader.Read())
                            {
                                object[] values1 = new object[7];
                                for (int yy = 0; yy < 7; yy++)
                                {
                                    values1[yy] = ora_reader.GetValue(yy).ToString();
                                }
                                dataGridView_prihod.CurrentRow.Cells[3].Value = values1[6].ToString();
                                lines.Add(values1);
                            }

                            ora_reader.Close();
                            ora_conn.Close();

                            #region ПРОВЕРКА
                            // ПОДГРУЖАЕМ СПИСОК АРТИКУЛОВ ИЗ WMS
                            Dictionary<string, string> arts = new Dictionary<string, string>();
                            strSQL = " SELECT A.ACTICUL  FROM RABAEV.RRL_ARTICULS A ,  RABAEV.RRL_CELLS C where A.cell=C.cell "; // and c.ware_id = " + this.wms_user.ware_id.ToString();
                            ora_com = new OracleCommand();
                            ora_com.CommandText = strSQL;
                            ora_conn = new OracleConnection();
                            ora_conn.ConnectionString = WMS_CONNECTION_STRING();
                            ora_conn.Open();
                            ora_com.Connection = ora_conn;
                            ora_reader = ora_com.ExecuteReader();
                            while (ora_reader.Read())
                            {
                                string art = ora_reader.GetValue(0).ToString();
                                arts.Add(art, art);
                            }

                            bool error = false;
                            string error_msg = "";
                            List<string> articuls_2_add = new List<string>();

                            foreach (object[] line in lines)
                            {// По всем строкам накладных
                                string ar1 = line[2].ToString();

                                if (!arts.ContainsKey(ar1))
                                {
                                    error = true;
                                    error_msg = " В WMS не загружен артикул " + ar1 + "  " + line[5].ToString() + " \n ";
                                    MessageBoxButtons buttons = MessageBoxButtons.YesNo;
                                    DialogResult result;
                                    result = MessageBox.Show(error_msg, "Загружаем артикулы?", buttons);
                                    if (result == DialogResult.Yes)
                                    {
                                        SyncArticul(ar1, this.wms_user.ware_id);
                                    }
                                }
                            }
                            #endregion

                            if (error)
                            {
                                MessageBox.Show(" При загрузке заказа обнаружены ошибки. Повторите загрузку. ");
                            }
                            else
                            {
                                // ЗАГРУЗКА СТРОК  ИЗ СУПЕР-МАГА
                                // *********************************************************************************
                                foreach (object[] line in lines)
                                {// По всем строкам накладных
                                    string articul = line[2].ToString();
                                    double Количество_тов = Convert.ToDouble(line[3].ToString());
                                    double Цена_с_ндс = Convert.ToDouble(line[4].ToString());

                                    ora_com = new OracleCommand();
                                    ora_com.Connection = get_wms_connection();
                                    ora_com.CommandText = "ADD_RRL_PRIH_NAKLAD_ROW";
                                    ora_com.CommandType = CommandType.StoredProcedure;

                                    ora_com.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = УИД_ТЕКУЩЕЙ_НАКЛАДНОЙ;
                                    ora_com.Parameters.Add("articul", OracleType.VarChar).Value = articul;
                                    ora_com.Parameters.Add("expiury_date", OracleType.DateTime).Value = DateTime.Now;
                                    ora_com.Parameters.Add("count1", OracleType.Number).Value = Количество_тов;
                                    ora_com.Parameters.Add("price", OracleType.Number).Value = Цена_с_ндс;

                                    ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                                    int rowsAffected44 = ora_com.ExecuteNonQuery();

                                }

                                dataGridView_prihod_CellEnter(null, null);

                                // *********************************************************************************
                            }

                        }
                        catch (Exception Ex)
                        {
                            MessageBox.Show(" f36 " + Ex.Message);
                        }

                        // ПРОВЕРИЛИ, ЧТО ВСЕ АРТИКУЛЫ ЕСТЬ В БАЗЕ ДАННЫХ

                        // СОЗДАЛИ СТРОКИ В WMS

                    }
                    else
                    {

                        MessageBox.Show(" Накладная закрыта. ");

                    }

                    // Интеграция с супермагом 
                    #endregion







                }
            }
            else
            {

                MessageBox.Show("Накладная проведена, подгрузка не возможна.");
            }




        }

        private void СТ_ИЗ_СУПЕРМАГА_TextChanged(object sender, EventArgs e)
        {

        }

        private void button34_Click(object sender, EventArgs e)
        {


            dataGridView21.Rows.Clear();
            dataGridView22.Rows.Clear();
            dataGridView23.Rows.Clear();
   
            string strSQL;

            strSQL = " select  " + 
            " P.ST_NUMBER , " + 
            " P.NAPR ,  " + 
            "  count ( DISTINCT P.PALLET_UID )  as КОЛИЧЕСТВО ,  " + 
            "  count( R.ID ) as КОЛИЧЕСТВО_СТРОК, " + 
            " P.ADDR " + 
            " from RABAEV.RRL_SBORKA_PALLETS P , RABAEV.RRL_SBORKA_PALLET_ROWS R where " +
            " P.PALLET_UID=R.PALLET_UID and P.ST_NUMBER = '" + НомерСТКПодгрузке.Text.Trim() + "' " + 
            " group by    P.ST_NUMBER ,   P.NAPR ,   P.ADDR " ;

             fill_view_MINI_WMS( dataGridView21 , strSQL   , 5);




        }

        private void dataGridView21_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            object o = dataGridView21.CurrentRow.Cells[0].Value;

            string strSQL = "select  P.PALLET_NUMBER , " +
            "   P.PALLET_UID  , 'false' , int2bool( PROOVED ) , int2bool( PROOVED_BY_SCAN ) , condition  " + 
            " from RABAEV.RRL_SBORKA_PALLETS P " + 
            " where ST_NUMBER='"+o.ToString()+"' ";
            fill_view_MINI_WMS(dataGridView22, strSQL, 6);

        }

        private void dataGridView22_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            СБОРЩИК_1.Tag = "";
            ПРОВЕРЯЮЩИЙ_1.Text="";
            СБОРЩИК_1.Text = "";
            ПРОВЕРЯЮЩИЙ_1.Tag = "";
            ВесДеревянногоПаллета.Enabled = true;

            try
            {

                object o = dataGridView22.CurrentRow.Cells[1].Value;

                string strSQL = "select  ARTICUL , " +
                "   SHORTNAME  , QUANTITY  ,  ID , AUCTION , PALLET_UID , SORTFIELD , CURRENT_MOD_ID , 'false' , SOBRANO  " +
                " from RABAEV.RRL_SBORKA_PALLET_ROWS R " +
                " where PALLET_UID='" + o.ToString() + "' order by SORTFIELD ";
                fill_view_MINI_WMS(dataGridView23, strSQL, 10);

                // заполняем TRIAL_WEIGHT  
                OracleCommand ora_comm = new OracleCommand();
                ora_comm.Connection = get_wms_connection();
                ora_comm.CommandText = " select TRIAL_WEIGHT from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID='" + o.ToString() + "' "; ;
                m_trial_weight.Text = ora_comm.ExecuteScalar().ToString();

                ora_comm.CommandText = " select WOOD_WEIGHT from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID='" + o.ToString() + "' "; ;
                ВесДеревянногоПаллета.Text = ora_comm.ExecuteScalar().ToString();

                ora_comm.CommandText = " select RRL_TT_POGRESHNOST2(PALLET_UID) from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID='" + o.ToString() + "' "; ;
                m_pogr.Text = ora_comm.ExecuteScalar().ToString();


                #region РАБОТА С ВЕСОМ ДЕРЕВА

                if(( ВесДеревянногоПаллета.Text.Trim()!="" ) && ( ВесДеревянногоПаллета.Text!="0" ) )
                {
                    if (has_right("SECOND_CH_WOOD"))
                    {
                        ВесДеревянногоПаллета.Enabled = true;
                    }
                    else 
                    {
                        ВесДеревянногоПаллета.Enabled = false;
                    } 
                
                }
                    
                    
                #endregion


                // =================

                ora_comm.CommandText = " select  U1.ID , U1.NAME , U2.ID , U2.NAME , U1.WMSUSER_ID  from RABAEV.RRL_SBORKA_PALLETS P , RUSERS U1 , RUSERS U2 " +
                    " where  P.PALLET_UID='" + o.ToString() + "' and P.SBORSHIK=U1.ID(+)  and P.KLADOVSHIK=U2.ID(+)  "; ;
                //СБОРЩИК_1.Text = ora_comm.ExecuteScalar().ToString();
                OracleDataReader ora_read10= ora_comm.ExecuteReader();
                if(ora_read10.Read())
                {
                    СБОРЩИК_1.Tag = obj2str( ora_read10.GetValue(0) );
                    СБОРЩИК_1.Text = "[" + obj2str(ora_read10.GetValue(4)) + "]" + obj2str(ora_read10.GetValue(1));
                    ПРОВЕРЯЮЩИЙ_1.Tag = obj2str(ora_read10.GetValue(2));
                    ПРОВЕРЯЮЩИЙ_1.Text = obj2str(ora_read10.GetValue(3));

                }

                //ПРОВЕРЯЮЩИЙ_1.Text;
                // =================


                bool fake = false;
                foreach (DataGridViewRow dr in dataGridView23.Rows)
                {
                    if (dr.Cells[0] != null)
                    {
                        if (dr.Cells[0].Value.ToString().Length > 0)
                            if (dr.Cells[0].Value.ToString()[0] == 'Z') fake=true ;
                    }

                }
                button46.Visible = fake;



                #region РАБОТА_С_МОДами

                // Определяем - есть ли МОДы в данном паллете ( ХП RRL_PALLET_HAS_MODS )

                //OracleCommand ora_comm = new OracleCommand();
                //ora_comm.Connection = get_wms_connection();
                /* ВЕРНУТЬСЯ СЮДА!!!
                 * ora_comm.CommandText = " select RRL_PALLET_HAS_MODS(PALLET_UID) from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID='" + o.ToString() + "' "; ;
                int has_mod = Convert.ToInt32( ora_comm.ExecuteScalar().ToString());
                if (has_mod == 0)
                {
                    panel_mods.Visible = false;
                }
                else 
                {
                    panel_mods.Visible = true;
                }
                */
                #endregion



            }
            catch( Exception ex )
            {
                MessageBox.Show( ex.Message );
            }

        }

        private void dataGridView23_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {


            string articul = "";
            string pallet_uid = "";
            double count = 0;


            articul=dataGridView23.CurrentRow.Cells[0].Value.ToString();
            pallet_uid = dataGridView23.CurrentRow.Cells[5].Value.ToString();
            count = Convert.ToDouble( dataGridView23.CurrentRow.Cells[2].Value.ToString().Replace('.',','));
            int row_id = Convert.ToInt32( dataGridView23.CurrentRow.Cells[3].Value.ToString());

            bool vycherk_ = false;
            
            OracleCommand ora_com7 = new OracleCommand();
            ora_com7.Connection = get_wms_connection();
            ora_com7.CommandText = "  select COUNT_SHT_IN_KOR from  RABAEV.RRL_ARTICULS  where ACTICUL='" + articul.ToString()+"'";
            double COUNT_SHT_IN_KOR = Convert.ToDouble(ora_com7.ExecuteScalar().ToString());
                  

            OracleCommand ora_com9 = new OracleCommand();
            ora_com9.Connection = get_wms_connection();
            ora_com9.CommandText = //"  select ALLOW_HALF_VYCHERK from  RABAEV.RRL_WARES  where ID='" + this.wms_user.ware_id.ToString()+"'";
            "  select WAR.ALLOW_HALF_VYCHERK from RRL_WARES WAR , RRL_SBORKA_PALLETS PAL " +
                   " where PAL.PALLET_UID='" + pallet_uid + "' and PAL.WARE_ID=WAR.ID ";

            int ALLOW_HALF_VYCHERK = Convert.ToInt32 (ora_com9.ExecuteScalar().ToString());

            OracleCommand ora_com4 = new OracleCommand();
            ora_com4.Connection = get_wms_connection();
            ora_com4.CommandText = "  select QUANTITY from RABAEV.RRL_SBORKA_PALLET_ROWS where ID="+row_id.ToString();
            double QUANTITY = Convert.ToDouble( ora_com4.ExecuteScalar().ToString() );

            
            if (ALLOW_HALF_VYCHERK == 0)
            {
                double kolkor= Math.Abs( count ) / COUNT_SHT_IN_KOR;

                if ( (kolkor-Math.Round(kolkor))!=0 )
                {
                    MessageBox.Show("Количество должно быть кратно " + COUNT_SHT_IN_KOR.ToString()+" согласно данных системы. " );
                    return;
                }
            }

            if(count!=0)
            {
               

                if (QUANTITY > 0 && (QUANTITY != count))
                {
                      if ( (QUANTITY - count) >= COUNT_SHT_IN_KOR)
                    {
                        vycherk_ = true;
                    }
                }
                


            }

            // COUNT_SHT_IN_KOR 

            #region РАБОТА С ВЫЧЕРКАМИ
            if (count == 0 || (vycherk_)) // Если делается вычерк и для склада введено правило проверки вычерков, то 
            {   // проверяем количество товара в хранении. если не равно 0 , но выдаем все адреса, где хранится товар.
                // Вычерк не проводим и выходим.

                #region РАБОТА С ВЫЧЕРКАМИ
                OracleCommand ora_com3 = new OracleCommand();
                ora_com3.Connection = get_wms_connection();
                ora_com3.CommandText = "  select WAR.VERIFY_VYCHERK from RRL_WARES WAR , RRL_SBORKA_PALLETS PAL "+
                    " where PAL.PALLET_UID='" + pallet_uid + "' and PAL.WARE_ID=WAR.ID ";

                string VERIFY_VYCHERK = ora_com3.ExecuteScalar().ToString();
                if (VERIFY_VYCHERK == "1")
                {

                    #region ПРОВЕРЯЕМ РЕГИОНЫ С ОСОБЫМИ ТРЕБОВАНИЯМИ К СРОКАМ ГОДНОСТИ
                    int LEAD_TIME = 0;
                    try
                    {
                        OracleCommand ora_com11 = new OracleCommand();
                        ora_com11.Connection = get_wms_connection();
                        ora_com11.CommandText = "  select RRL_ADDR.LEAD_TIME from RABAEV.RRL_ADDR  , RRL_SBORKA_PALLETS PAL " +
                        " where PAL.PALLET_UID='" + pallet_uid + "' and RRL_ADDR.ADDR =PAL.ADDR ";
                        LEAD_TIME = Convert.ToInt32(ora_com11.ExecuteScalar().ToString());
                    }
                    catch { }


                    #endregion

                    DateTime curr_date = DateTime.Today.AddDays(-1*LEAD_TIME);
                    string strSQL= "select sum( RRL_REMAINS.REMAIN ) "+ // + , RRL_REMAINS.UID_POLETA 
                    " from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , "+
                    " RABAEV.RRL_CELLS  " +
                    " where ARTICUL='" + articul.Trim() + "' " +       
                    " and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA " + 
                    " and RRL_CELLS.CELL = RRL_REMAINS.CELL " + 
                    " and RRL_REMAINS.REMAIN>0   " + 
                    " and  RRL_PALLETS.EXPIRY_DATE >= "+ date2sql_ora(curr_date) +" "+
                    " and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1  " + 
                    " and RRL_CELLS.OTBOR =0  " + 
                    " group by ARTICUL " ;

                    ora_com3.CommandText = strSQL;

                    long Количество_в_хранении = Convert.ToInt32(  ora_com3.ExecuteScalar() ) ;
                    if (Количество_в_хранении > 0)
                    {


                        print_vycherk_checking_list(articul);

                        string strSQL2 = "select  ARTICUL АРТИКУЛ , RRL_CELLS.CELL ЯЧЕЙКА ,   RRL_REMAINS.REMAIN ОСТАТОК , EXPIRY_DATE ГОДЕН_ДО , TIME_OF_LAST_UPDATE ДАТА_ПЕРЕМЕЩЕНИЯ  , PRIHOD_NAKLAD_ID , UID_POLETA , CREATION_DATE , KLADOVSHIK " + // + , RRL_REMAINS.UID_POLETA 
                        " from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , " +
                        " RABAEV.RRL_CELLS  " +
                        " where ARTICUL='" + articul + "' " +
                        " and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA " +
                        " and RRL_CELLS.CELL = RRL_REMAINS.CELL " +
                        " and RRL_REMAINS.REMAIN>0   " +
                        " and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1  " +
                        " and RRL_CELLS.OTBOR =0  " +
                        " order by EXPIRY_DATE ";
                        ShowQuery( strSQL2 , "Данный артикул есть в хранении. Вычерк проводить нельзя.");



                        return;
                    }

                }
                #endregion


                #region РАБОТА С ВЫЧЕРКАМИ В ОТБОРЕ
                OracleCommand ora_com5 = new OracleCommand();
                ora_com5.Connection = get_wms_connection();
                ora_com5.CommandText = "  select WAR.VERIFY_VYCHERK_IN_OTBOR  from RRL_WARES WAR , "+
                " RRL_SBORKA_PALLETS PAL " +
                    " where PAL.PALLET_UID='" + pallet_uid + "' and PAL.WARE_ID=WAR.ID ";

                string VERIFY_VYCHERK1 = ora_com5.ExecuteScalar().ToString();

                if (VERIFY_VYCHERK1 == "1")
                {

                    #region ПРОВЕРЯЕМ РЕГИОНЫ С ОСОБЫМИ ТРЕБОВАНИЯМИ К СРОКАМ ГОДНОСТИ
                    int LEAD_TIME = 0;
                    try
                    {
                        OracleCommand ora_com11 = new OracleCommand();
                        ora_com11.Connection = get_wms_connection();
                        ora_com11.CommandText = "  select RRL_ADDR.LEAD_TIME from RABAEV.RRL_ADDR  , RRL_SBORKA_PALLETS PAL " +
                        " where PAL.PALLET_UID='" + pallet_uid + "' and RRL_ADDR.ADDR =PAL.ADDR ";
                        LEAD_TIME = Convert.ToInt32(ora_com11.ExecuteScalar().ToString());
                    }
                    catch { }


                    #endregion

                    DateTime curr_date = DateTime.Today.AddDays(-1 * LEAD_TIME);
                    string strSQL = "select sum( RRL_REMAINS.REMAIN ) " + // + , RRL_REMAINS.UID_POLETA 
                    " from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , " +
                    " RABAEV.RRL_CELLS  " +
                    " where ARTICUL='" + articul.Trim() + "' " +
                    " and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA " +
                    " and RRL_CELLS.CELL = RRL_REMAINS.CELL " +
                    " and RRL_REMAINS.REMAIN>0   " +
                    " and  RRL_PALLETS.EXPIRY_DATE >= " + date2sql_ora(curr_date) + " " +
                    " and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1  " +
                    " and RRL_CELLS.OTBOR =1 and   (BLOCKED_FOR_REMAINS=0) " +
                    " group by ARTICUL ";

                    ora_com3.CommandText = strSQL;

                    long Количество_в_отборе = Convert.ToInt32(ora_com3.ExecuteScalar());
                    if (Количество_в_отборе > 0)
                    {
                        MessageBox.Show("Данный артикул есть в отборе. Вычерк проводить нельзя.");
                        /*
                        print_vycherk_checking_list(articul);
                        string strSQL2 = "select  ARTICUL АРТИКУЛ , RRL_CELLS.CELL ЯЧЕЙКА ,   RRL_REMAINS.REMAIN ОСТАТОК , EXPIRY_DATE ГОДЕН_ДО , TIME_OF_LAST_UPDATE ДАТА_ПЕРЕМЕЩЕНИЯ  , PRIHOD_NAKLAD_ID , UID_POLETA , CREATION_DATE , KLADOVSHIK " + // + , RRL_REMAINS.UID_POLETA 
                        " from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , " +
                        " RABAEV.RRL_CELLS  " +
                        " where ARTICUL='" + articul + "' " +
                        " and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA " +
                        " and RRL_CELLS.CELL = RRL_REMAINS.CELL " +
                        " and RRL_REMAINS.REMAIN>0   " +
                        " and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1  " +
                        " and RRL_CELLS.OTBOR =1 and   (BLOCKED_FOR_REMAINS=0)  " +
                        " order by EXPIRY_DATE ";
                        ShowQuery(strSQL2, "Данный артикул есть в хранении. Вычерк проводить нельзя.");
                        */
                        return;
                    }

                }
                #endregion






            }
            #endregion


            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = "RABAEV.RRL_UPDATE_PALLET_ROW2";
            ora_com.CommandType = CommandType.StoredProcedure;
            ora_com.Parameters.Add("articul1", OracleType.VarChar).Value = articul;
            ora_com.Parameters.Add("pallet_uid1", OracleType.VarChar).Value = pallet_uid;
            ora_com.Parameters.Add("count1", OracleType.Number).Value = count;
            ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;
            ora_com.Parameters.Add("ret", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com.ExecuteNonQuery();
            //ЯчейкаОткуда.Text = ora_com.Parameters["ret"].Value.ToString();

            #region ПРОВЕРКА СОВПАДЕНИЯ СОБРАННОГО СБОРЩИКОМ ТОВАРА И ТЕКУЩЕГО СОСТОЯНИЯ ТАБЛИЦЫ.

            if (ora_com.Parameters["ret"].Value.ToString() == "PROOVED_BY_SCAN")
            {
                dataGridView22.CurrentRow.Cells[4].Value = true;
            }
            #endregion


        }

        // ============================================================================================================
        private void print_vycherk_checking_list(string ID_TT )
        {

       
            
            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ
                int _X = 10, _Y = 30;
            #endregion

            #region ПОДГОТОВКА ПЕЧАТИ
            
            PPage _page = new PPage();
            _page.start_point_4_table.X = 10;
            _page.start_point_4_table.Y = 70;
            _page.font_size_4_table = 11;

            _page.labels.Add(new PPage.PLabel("Лист контроля вычерка", new Point(10, 10), 24));
            _page.labels.Add(new PPage.PLabel("Данный лист передается карщику для проверки наличия товара.", new Point(10, 44), 16));



            string strSQL2 = "select  ARTICUL АРТИКУЛ , RRL_CELLS.CELL ЯЧЕЙКА ,   RRL_REMAINS.REMAIN ОСТАТОК , EXPIRY_DATE ГОДЕН_ДО , TIME_OF_LAST_UPDATE ДАТА_ПЕРЕМЕЩЕНИЯ  , PRIHOD_NAKLAD_ID , UID_POLETA , CREATION_DATE , KLADOVSHIK " + // + , RRL_REMAINS.UID_POLETA 
            " from RABAEV.RRL_PALLETS , RABAEV.RRL_REMAINS , " +
            " RABAEV.RRL_CELLS  " +
            " where ARTICUL='" + ID_TT + "' " +
            " and RRL_PALLETS.UID_PALLET = RRL_REMAINS.UID_POLETA " +
            " and RRL_CELLS.CELL = RRL_REMAINS.CELL " +
            " and RRL_REMAINS.REMAIN>0   " +
            " and RRL_CELLS.BLOCKED_FOR_POPOLNENIE<>1  " +
            " and RRL_CELLS.OTBOR =0  " +
            " order by EXPIRY_DATE ";

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL2;


            _page.add_column("ARTICUL", "string", "АРТИКУЛ", 8); // номер в порядке загрузки авто
            _page.add_column("CELL", "string", "ЯЧЕЙКА", 7);
            _page.add_column("REMAIN", "string", "ОСТАТОК", 7);
            _page.add_column("EXPIRY_DATE", "string", "ГОДЕН_ДО", 10);
            _page.add_column("TIME_OF_LAST_UPDATE", "string", "ДАТА_ПЕРЕМЕЩЕНИЯ", 12);
            _page.add_column("PRIHOD_NAKLAD_ID", "string", "ПРИХОД", 5);
            _page.add_column("UID_POLETA", "string", "НОМЕР ПАЛЛ", 15);
            _page.add_column("CREATION_DATE", "string", "Дата приняти", 10);
      //      _page.add_column("KLADOVSHIK", "string", "принял", 7);



            OracleDataReader ora_read3 = ora_com.ExecuteReader();


            long КОЛИЧЕСТВО_ПАЛЛЕТ1 = 0;
            while (ora_read3.Read())
            {

                Dictionary<string, string> _row = new Dictionary<string, string>();

                _row["ARTICUL"] = obj2str(ora_read3.GetValue(0));
                _row["CELL"] = obj2str(ora_read3.GetValue(1));
                _row["REMAIN"] = obj2str(ora_read3.GetValue(2));
                _row["EXPIRY_DATE"] = obj2str(ora_read3.GetValue(3));
                _row["TIME_OF_LAST_UPDATE"] = obj2str(ora_read3.GetValue(4));
                _row["PRIHOD_NAKLAD_ID"] = obj2str(ora_read3.GetValue(5));
                _row["UID_POLETA"] = obj2str(ora_read3.GetValue(6));
                _row["CREATION_DATE"] = obj2str(ora_read3.GetValue(7));
                _page.add_row(_row);
                КОЛИЧЕСТВО_ПАЛЛЕТ1++;

            }

            PPages.Add(_page);

#endregion

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {
                pd.DefaultPageSettings.Landscape = false;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion



        
        }











        private void button36_Click(object sender, EventArgs e)
        { // ПОДГРУЗКА НЕ РАСПРЕДЕЛЕННЫХ СТ 
            // Добавить Склад Паллеты Адрес СТ ВЕС 
            string add_sql1="";
            string add_sql2="";
            string add_sql3="";
            string add_sql4 = "";
            string add_sql5 = "";
            string add_sql6 = "";
            string add_sql7 = "";
            string add_sql8 = "";

            m_map_V=0 ;
            m_map_WEIGHT=0;
            m_map_P=0;

            if(  Фильтр_по_собранным.Checked )
            {
                add_sql7 = " and (  RRL_ST_VERYFY_PERC(P.ST_NUMBER )>0 ) ";
            
            }


            if (датаСТУч.Checked)
            {
                add_sql5 = " and ( P.STDATE = " + date2sql_ora(dateTimePicker5.Value) + " ) ";
            }

            

            if(МаскаСкладов.Text !="")
            {
                add_sql1 = " and ( RRL_SKLADNAME_BY_ID( P.ware_id ) in ( " + МаскаСкладов.Text + " )) ";
            }

            if(МаскаАдреса.Text !="")
            {
                add_sql2= " and ( P.ADDR like '%"+МаскаАдреса.Text +"%' ) ";
            }

            if (НЕ_РАСПРЕДЕЛЕННЫЕ.Checked )
            {
                add_sql3 = " and ( ( TRANSTASK_ID is null ) or (  TRANSTASK_ID=0 ) ) ";
            }

            if (датаСТУч.Checked)
            {
                add_sql5 = " and ( P.STDATE = " + date2sql_ora( dateTimePicker5.Value ) + " ) ";
            }


            if (ДатаСТДо.Checked)
            {
                 add_sql5 = " and ( P.STDATE >= " + date2sql_ora( dateTimePicker5.Value ) + " ) ";
                add_sql6 = " and ( P.STDATE <= " + date2sql_ora( ДатаСТДо2.Value ) + " ) ";
            }


            
            if(МаскаСТ.Text !="")
            {
                add_sql8 = " and ( P.ST_NUMBER like '%"+МаскаСТ.Text +"%' ) ";
            }


            
                       

            string strSQL = " select 'false', " +
                " RRL_SKLADNAME_BY_ID(P.WARE_ID) ,  " +
                " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , "+
                " round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  " +
                "  RRL_ADDR.REGION , " +
                " P.ADDR ,  " +
                " P.ST_NUMBER ,  " +
                " RRL_GET_TT_INFO(  TRANSTASK_ID ) TTINFO , STDATE , RRL_ST_VERYFY_PERC(P.ST_NUMBER ) , P.USER_ID , "+
                "  RRL_ADDR.RAION ,  RRL_ADDR.ORD , RRL_ADDR.TRANSPORT_TYPE , sum(RRL_SUGAR_HAS(  R.ARTICUL )) " +
                " , 0 , rrl_addr.STOL , min(P.CREATE_DATE) ДатаЗагрузки " + 
                " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R , RRL_ADDR   where " +
                " R.PALLET_UID=P.PALLET_UID  and  ( P.ADDR=RRL_ADDR.ADDR(+) )  " + add_sql1 + add_sql2 + add_sql3 + add_sql4 + add_sql5 +add_sql6+add_sql7+ add_sql8 +
                "group by    RRL_ADDR.TRANSPORT_TYPE ,  rrl_addr.ord ,  RRL_ADDR.REGION  ,  RRL_ADDR.RAION  , "+
                "  P.WARE_ID , P.ADDR ,   P.STDATE , P.USER_ID , P.ST_NUMBER  , "+
                " P.NAPR , RRL_GET_TT_INFO(  TRANSTASK_ID )  , RRL_SHOW_PRICE(TRANSTASK_ID) , rrl_addr.STOL " +
                " order by   RRL_ADDR.ORD  ";

            fill_view_MINI_WMS( dataGridView18 , strSQL , 19 );

        }

        private void ПаллетыВОТдельноеСТ_Click(object sender, EventArgs e)
        {
            string ТекущееСТ = МенюМаршрута.CurrentRow.Cells[2].Value.ToString();
            string[] оригинальный_номер1 =  ТекущееСТ.Split('#');
            string оригинальный_номер = оригинальный_номер1[0];
            
            

            OracleCommand ora_comm = new OracleCommand();
            ora_comm.Connection=get_wms_connection();

            // Сначала определим номер СТ - для этого будем перебирать подномера СТ
            string NewNumber ="";
            for (long ii = 2; ii < 100;ii++ )
            { 
                 NewNumber = оригинальный_номер + "#" + ii.ToString();
                 string strSQL = " select count(ST_NUMBER) from RRL_SBORKA_PALLETS where ST_NUMBER='" + NewNumber + "' group by ST_NUMBER ";
                ora_comm.CommandText = strSQL;
                long naideno = Convert.ToInt32( ora_comm.ExecuteScalar());
                if (naideno == 0)
                {
                    break;
                }
            }
            bool иправления_были = false;
            foreach (DataGridViewRow dr in МенюМаршрута.Rows)
            {
                string PUID = "";
                PUID = dr.Cells[3].Value.ToString();

                if (Convert.ToBoolean(dr.Cells[0].Value) == true)
                {
                    иправления_были = true;
                    string strSQL = " update  RRL_SBORKA_PALLETS  set ST_NUMBER='" + NewNumber + "' where PALLET_UID='" + PUID + "' ";
                    ora_comm.CommandText = strSQL;
                    ora_comm.ExecuteNonQuery();

                }
            }

            if (иправления_были)
            {
                NewNumber = оригинальный_номер + "#1"  ;
                string strSQL = " update  RRL_SBORKA_PALLETS  set ST_NUMBER='" + NewNumber + "' where ST_NUMBER='" + оригинальный_номер + "' ";
                ora_comm.CommandText = strSQL;
                ora_comm.ExecuteNonQuery();
            
            }
            

           dataGridView18_CellEnter(null, null);

        }

        private void dataGridView18_CellEnter(object sender, DataGridViewCellEventArgs e)
        { // Вошли с строчку ст - выдаем список паллет по данному ст
          string PALLET_UID1 = dataGridView18.CurrentRow.Cells[7].Value.ToString();
            // + , Номер паллеты, СТ
          string strSQL = " select 'false' ,PALLET_NUMBER , ST_NUMBER  , PALLET_UID , RRL_PALLET_WEIGHT(PALLET_UID)  " +
              " from RRL_SBORKA_PALLETS where ST_NUMBER = '" + PALLET_UID1 + "' ";

          fill_view_MINI_WMS(МенюМаршрута, strSQL, 5);

        }

        private void label30_Click(object sender, EventArgs e)
        {

        }

        private void button35_Click(object sender, EventArgs e)
        {
           string val="" ;

           if (!has_right("CREATE_ROUTE"))
           {

               MessageBox.Show(" Нет прав на создание маршрута ");
               return;
           }
           try
           {
               OracleCommand ora_com = new OracleCommand();

               ora_com.Connection = get_wms_connection();
               ora_com.CommandText = "RABAEV.RRL_TRASPORT_TASK_ADD";
               ora_com.CommandType = CommandType.StoredProcedure;
               ora_com.Parameters.Add("TRANSTYPE1", OracleType.VarChar).Value = val;
               ora_com.Parameters.Add("SHIPMENT_DATE1", OracleType.DateTime).Value = date2strip_time(dateTimePicker4.Value);
               ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;
               
               ora_com.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;

               int rowsAffected = ora_com.ExecuteNonQuery();

               string TT_ID = ora_com.Parameters["ID1"].Value.ToString();
               object[] ob = new object[9];
               ob[1] = TT_ID;
               ob[5] = val;
               ob[8] = date2strip_time(dateTimePicker4.Value);
               dataGridView17.Rows.Add(ob);



               #region ДОБАВЛЕНИЕ ЗАЯВОК В ТЕКУЩИЙ МАРШРУТ
               m_map_P = 0;
               m_map_V = 0;
               m_map_WEIGHT = 0;

               OracleCommand ora_comm = new OracleCommand();
               ora_comm.Connection = get_wms_connection();


               List<DataGridViewRow> ldr = new List<DataGridViewRow>();
               foreach (DataGridViewRow dr in dataGridView18.Rows)
               {
                   if (Convert.ToBoolean(dr.Cells[0].Value) == true)
                   {
                       OracleCommand ora_com2 = new OracleCommand();
                       ora_com2.Connection = get_wms_connection();

                       string PUID = dr.Cells[7].Value.ToString();
                       //Добавляем СТ в маршрут
                       /*string strSQL = " update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID = " + TT_ID +
                           " where ST_NUMBER='" + PUID + "' ";
                       ora_comm.CommandText = strSQL;
                       ora_comm.ExecuteNonQuery();
                       */
                        #region добавляем (УДАЛЯЕМ) СТ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ

                       ora_com2.CommandText = "RABAEV.RRL_TT_ADD_PALL";
                       ora_com2.CommandType = CommandType.StoredProcedure;
                       ora_com2.Parameters.Add("TT_ID", OracleType.Int32).Value = TT_ID;
                       ora_com2.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = PUID;

                       ora_com2.Parameters.Add("ret", OracleType.VarChar, 1024).Direction = ParameterDirection.ReturnValue;

                       int rowsAffected2 = ora_com2.ExecuteNonQuery();
                       try
                       {
                           dataGridView17.CurrentRow.Cells[12].Value = (ora_com2.Parameters["ret"].Value);
                       }
                       catch
                       { }

                       #endregion

                       ldr.Add(dr);

                      

                   }
               }

               foreach (DataGridViewRow dr2 in ldr)
               {
                   dataGridView18.Rows.Remove(dr2);
               }

               #endregion



                   ora_com = new OracleCommand();
                   ora_com.Connection = get_wms_connection();
                   ora_com.CommandText = "RABAEV.RRL_TT_REORDER_ADR";
                   ora_com.CommandType = CommandType.StoredProcedure;
                   ora_com.Parameters.Add("IDTT", OracleType.Int32).Value = TT_ID.ToString();
                   ora_com.Parameters.Add("ID1", OracleType.Number).Direction = ParameterDirection.ReturnValue;
                   try
                   {
                       int rowsAffected2 = ora_com.ExecuteNonQuery();
                       dataGridView17.CurrentRow.Cells[16].Value = obj2double(ora_com.Parameters["ID1"].Value);
                   }
                   catch 
                   { }

           }
           catch 
           { 
           
           }

       }

        private void SaveST2File( string ST_ID )
        {

            OracleCommand ora_comm = new OracleCommand();
            ora_comm.Connection = get_wms_connection();
            string strSQL = " select " +
            " R.ARTICUL , " +
            " sum(R.QUANTITY) Q  " +
            " from " +
            " RABAEV.RRL_SBORKA_PALLETS P , " +
            " RABAEV.RRL_SBORKA_PALLET_ROWS R " +
            " where (R.QUANTITY>0) and P.PALLET_UID = R.PALLET_UID " +
            " and P.ST_NUMBER='"+ST_ID+"' " +
            " group by R.ARTICUL ";
            ora_comm.CommandText=strSQL;
            OracleDataReader reader = ora_comm.ExecuteReader();

            string path = @"c:\WMS\" + ST_ID + ".txt";
            string ioio = "АРТИКУЛ\n";
                while( reader.Read() )
                        {
                            string art=  reader.GetValue(0).ToString();
                            double q = Convert.ToDouble(reader.GetValue(1));
                            string tr = art + " " + q + "\n";
                            ioio = ioio + tr;
                        }
                File.WriteAllText(path ,ioio , Encoding.GetEncoding("windows-1251")  );
            MessageBox.Show(" Выгружен "+path);

        }

        private void button37_Click(object sender, EventArgs e)
        {// Выгрузить в файл выделенные СТ

            foreach (DataGridViewRow dr in dataGridView18.Rows)
            {
                if (Convert.ToBoolean(dr.Cells[0].Value)==true)
                { // Позиция веделена
                    SaveST2File(dr.Cells[7].Value.ToString() );

                }

            }


        }

        private void dateTimePicker4_ValueChanged(object sender, EventArgs e)
        {

            dataGridView20.Rows.Clear();

            string strSQL2 = "";
            if (m_company_filter.Text != "")
            {
                strSQL2 = strSQL2 + " and  RABAEV.RRL_TT_VODITEL_COMPANY(T.VODITEL_ID)='" + m_company_filter.Text + "' ";
            }


            // Волна  Маршрут  Паллеты  Адреса Вес Объем . Дата отгрукзи
            string strSQL = " select T.WAVE , T.ID , RRL_TT_PALLETS(T.ID), round( RRL_TT_WEIGHT(T.ID) , 0 )  , " +
                " round( RRL_TT_VOLUME(T.ID)/1000000, 1 ), T.TRANSTYPE  , T.TRANSPORT ,  ''  , T.SHIPMENT_DATE  "+
                " ,  RRL_TT_VODITEL_INFO(T.VODITEL_ID) , T.VODITEL_ID   , DOCK , RRL_TT_REGIONS( T.ID) , PRICE , " +
                " RABAEV.RRL_TT_VODITEL_COMPANY(T.VODITEL_ID) комп " + 
                " from RRL_TRANSPORT_TASK  T  where   "+
                " SHIPMENT_DATE = " + date2sql_ora(dateTimePicker4.Value) + " and deleted<>1 " + strSQL2 + " order by T.ID DESC ";


            if (checkBox3.Checked)
            {

                strSQL = " select T.WAVE , T.ID , RRL_TT_PALLETS(T.ID), round( RRL_TT_WEIGHT(T.ID) , 0 )  , " +
                   " round( RRL_TT_VOLUME(T.ID)/1000000, 1 ), T.TRANSTYPE  , T.TRANSPORT ,  ''  , T.SHIPMENT_DATE  " +
                   " ,  RRL_TT_VODITEL_INFO(T.VODITEL_ID) , T.VODITEL_ID   , DOCK , RRL_TT_REGIONS( T.ID) , PRICE , " +
                    " RABAEV.RRL_TT_VODITEL_COMPANY(T.VODITEL_ID) комп " +
                   " from RRL_TRANSPORT_TASK  T  where   " +
                   " SHIPMENT_DATE >= " + date2sql_ora(dateTimePicker4.Value) + " and SHIPMENT_DATE <= " + date2sql_ora(dateTimePicker8.Value) +
                   " and deleted<>1 " + strSQL2 + " order by T.ID DESC ";

            }

            fill_view_MINI_WMS(dataGridView17, strSQL, 15);

            dateTimePicker5.Value = dateTimePicker4.Value.AddDays(-1);
            button36_Click(null, null);

            
        }

        private void button38_Click(object sender, EventArgs e)
        {
           
            dateTimePicker4_ValueChanged(null, null);

         

        }

        private void button39_Click(object sender, EventArgs e)
        { // По всем выделеннвм СТ , добавляем их  в выделенный маршрут

            #region ДОБАВЛЕНИЕ ЗАЯВОК В ТЕКУЩИЙ МАРШРУТ
            m_map_P = 0;
            m_map_V = 0;
            m_map_WEIGHT = 0;




            if (  dataGridView17.CurrentRow == null )
            {
                MessageBox.Show("Не выбран текущий маршрут");
                return;
            }

            string TT_ID= dataGridView17.CurrentRow.Cells[1].Value.ToString();
            if (!(Convert.ToInt64(TT_ID) > 0))
            {
                MessageBox.Show("Не выбран текущий маршрут");
                return;
            }

            List<DataGridViewRow> ldr= new List<DataGridViewRow>();
            bool Задето=false ;
            foreach ( DataGridViewRow dr in dataGridView18.Rows   )
            {
                if (Convert.ToBoolean(dr.Cells[0].Value) == true)
                {  
                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    string PUID =dr.Cells[7].Value.ToString();
                    //Добавляем СТ в маршрут
                    //string strSQL = " update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID = " + TT_ID +
                    //    " where ST_NUMBER='" + PUID + "' ";
                    //ora_comm.CommandText = strSQL;
                    //ora_comm.ExecuteNonQuery();
                    #region добавляем (УДАЛЯЕМ) СТ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ

                        ora_com.CommandText = "RABAEV.RRL_TT_ADD_PALL";
                        ora_com.CommandType = CommandType.StoredProcedure;
                        ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = TT_ID;
                        ora_com.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = PUID;

                        ora_com.Parameters.Add("ret", OracleType.VarChar , 1024).Direction = ParameterDirection.ReturnValue;

                        int rowsAffected = ora_com.ExecuteNonQuery();
                        try
                        {
                            dataGridView17.CurrentRow.Cells[12].Value = (ora_com.Parameters["ret"].Value);
                        }catch
                        { }

                    #endregion

                    ldr.Add(dr);
                    Задето = true;
                }
            }



            if( Задето )
            {
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_TT_REORDER_ADR";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("IDTT", OracleType.Int32).Value = TT_ID.ToString();
                ora_com.Parameters.Add("ID1", OracleType.Number).Direction = ParameterDirection.ReturnValue;

                int rowsAffected = ora_com.ExecuteNonQuery();
                try
                {
                    dataGridView17.CurrentRow.Cells[16].Value = obj2double(ora_com.Parameters["ID1"].Value);
                }catch
                {}
            }



            foreach (DataGridViewRow dr2 in ldr)
            {
                dataGridView18.Rows.Remove(dr2);
            }

            #endregion

            dataGridView17_CellEnter(null, null);

        }

        private void button40_Click(object sender, EventArgs e)
        {


            try
            {

                if( str_is_empty( СБОРЩИК_1.Tag   )   )
                {
                    
                     button67_Click( null , null );
                     if (СБОРЩИК_1.Tag == "")
                     {
                         MessageBox.Show(" Не выбран сборщик. ");
                         return;
                     }
                }


                object o = dataGridView22.CurrentRow.Cells[1].Value;




                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_TRIAL_BY_WEIGHT2";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = o.ToString();
                ora_com.Parameters.Add("TRIAL_WEIGHT1", OracleType.Number).Value = Convert.ToDouble(m_trial_weight.Text);
                ora_com.Parameters.Add("WOOD_WEIGHT1", OracleType.Number).Value = Convert.ToDouble(ВесДеревянногоПаллета.Text);
                ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id ;
                ora_com.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;

                int rowsAffected = ora_com.ExecuteNonQuery();

                long ret2 = Convert.ToInt64(ora_com.Parameters["ID1"].Value.ToString());

                if (ret2 == 1)
                {
                    label43.Text = "Паллет прошел весовой контроль";
                    button41_Click(null, null);
                    MessageBox.Show("Вес корректен");
                }
                else {


                    label43.Text = "Паллет ПЕРЕБРАН Кладовщиком склада __________(" + ПРОВЕРЯЮЩИЙ_1.Text + ")";
                    MessageBox.Show("В сборке ошибка. вес не корректен."); 
                }

            }catch( Exception ex )
            {
                MessageBox.Show( ex.Message );
            }


             dataGridView22_CellEnter(null, null );
        }

        private void ВесДеревянногоПаллета_TextChanged(object sender, EventArgs e)
        {

        }


        #region ДЕКОДИРОВАНИЕ

        string pallet_uid_decode(string puid)
        {
            string f = puid.Replace("OP_", "");
            return "OP_" + Encoding.GetEncoding("windows-1251").GetString((Convert.FromBase64String(f)));
        }

        string pallet_uid_code( string PUID )
        {
            string f = PUID.Replace("OP_", "");
            return "OP_" + Convert.ToBase64String((Encoding.GetEncoding("windows-1251").GetBytes(f)));
        }

        #endregion 


        private void button41_Click(object sender, EventArgs e)
        { // Печать сборочника на паллет.

            bool Печатать_шк_штук_коробок_блоков = true;
            List<Dictionary<string, string>> штрих_коды = new List<Dictionary<string, string>>();
            long Количество_строк=30;

            List<PPage> PPages2 = new List<PPage>();
            string Адрес_магазина = "";
            DateTime ДатаСТ=DateTime.Today;
            DateTime ДатаПечати= DateTime.Today;
            int Номер_Паллета = 0;
            int ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ = 0;
            string НОМЕР_СТ = "";
            string ФАМИЛИЯ_ВЕСОВЩИКА = "";
            string ПРОШЕЛ_ВЕСОВОЙ_КОНТРОЛЬ = " Паллет перебран на РЦ.  ____________ (кладовщик) ";
            string ВЕС_ПОДДОНА_НА_ВЕСАХ = "";
            string ВЕС_ДЕРЕВЯННОГО_ПОДДОНА = "";
            string НОРМАТИВНЫЙ_ВЕС_ПОДДОНА = "";
            string SBORSHIK = "";
            int PROOVED_BY_SCAN = 0;
            int PROOVED = 0;
            long PRINT_EXPIRY_DATE_OP = 0;
            long COUNT_OF_PRINTS = 0;
            long WARES_COUNT_OF_PRINTS = 1;

            int NO = 0;

            if (dataGridView22.CurrentRow == null)
            {
                MessageBox.Show(" Не выбран паллет ");
                return;
            }


            #region ОПРЕДЕЛЯЕМ СБОРЩИКА
            if (str_is_empty(СБОРЩИК_1.Tag))
            {
                button67_Click(null, null);
            }
            if (str_is_empty(СБОРЩИК_1.Tag))
            {
                MessageBox.Show("Выберите сборщика!!!");
                return;
            }
            #endregion



            string pallet_UID=dataGridView22.CurrentRow.Cells[1].Value.ToString();
            // В шапке пишем дату СТ, дату печати, Адрес магазина, номер СТ, номер паллета.
            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = WMS_CONNECTION_STRING();
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = " select PALLET_NUMBER , CREATE_DATE , ST_NUMBER , ADDR , PROOVED ,"+
                " TRIAL_WEIGHT , WOOD_WEIGHT , "+
                " round( RRL_OP_WEIGHT2(PALLET_UID) , 2 ) , RUSERS.NAME , PROOVED_BY_SCAN , "+
                " PRINT_EXPIRY_DATE_OP , RRL_SBORKA_PALLETS.COUNT_OF_PRINTS , RRL_WARES.COUNT_OF_PRINTS " +
                " from RABAEV.RRL_SBORKA_PALLETS , RUSERS , RRL_WARES " +
                " where ( RRL_SBORKA_PALLETS.SBORSHIK=RUSERS.ID(+) ) and  PALLET_UID = '" + pallet_UID + 
                "' and RRL_WARES.ID = RRL_SBORKA_PALLETS.ware_id ";

            OracleDataReader ora_read = ora_com.ExecuteReader();
            if (ora_read.Read())
            {
                Номер_Паллета= Convert.ToInt32( ora_read.GetValue(0).ToString() );
                ДатаСТ = (ora_read.GetDateTime(1) );
                НОМЕР_СТ = (ora_read.GetString(2));
                Адрес_магазина = (ora_read.GetString(3));
                if (Convert.ToInt32(ora_read.GetInt32(4)) == 1)
                {
                    ПРОШЕЛ_ВЕСОВОЙ_КОНТРОЛЬ = "Весовой контроль пройден";
                }
                else {

                    if ( str_is_empty(ПРОВЕРЯЮЩИЙ_1.Tag ))
                    {

                        button68_Click(null, null);
                    }

                    if (str_is_empty(ПРОВЕРЯЮЩИЙ_1.Tag))
                    {
                        MessageBox.Show("Выберите кладовщика проверки !!!");
                        return;
                    }

                    ПРОШЕЛ_ВЕСОВОЙ_КОНТРОЛЬ = "Проверил:____________(" + ПРОВЕРЯЮЩИЙ_1.Text + ")";
                }




                ВЕС_ПОДДОНА_НА_ВЕСАХ = ora_read.GetValue(5).ToString();
                ВЕС_ДЕРЕВЯННОГО_ПОДДОНА = ora_read.GetValue(6).ToString();
                НОРМАТИВНЫЙ_ВЕС_ПОДДОНА = Convert.ToString( (Convert.ToDouble( ora_read.GetValue(7).ToString() ) + Convert.ToDouble(  ВЕС_ДЕРЕВЯННОГО_ПОДДОНА ) ) );
                SBORSHIK = obj2str( ora_read.GetValue(8)) ;
                PROOVED_BY_SCAN = (int) obj2int(ora_read.GetValue(9));
                PROOVED = (int) obj2int(ora_read.GetValue(4));


                if ( str_is_empty( SBORSHIK) )
                {

                    SBORSHIK = "__________________";
                }
            }
            else {
                MessageBox.Show("Нет такого паллета");
                return;
            }



            PRINT_EXPIRY_DATE_OP = obj2int (ora_read.GetValue(10));
            COUNT_OF_PRINTS  =   obj2int( ora_read.GetValue(11) );
            WARES_COUNT_OF_PRINTS = obj2int(ora_read.GetValue(12));

            if (WARES_COUNT_OF_PRINTS != 0)
            {
                if (COUNT_OF_PRINTS >= WARES_COUNT_OF_PRINTS)
                {
                    if (!has_right("PRINT_OP_PASSPORT_UNLIMIT"))
                    {
                        MessageBox.Show("Нет прав на распечатку паллета более 1 раза");
                        return;
                    }
                }
            }


            if (ВЕС_ПОДДОНА_НА_ВЕСАХ == "" || ВЕС_ПОДДОНА_НА_ВЕСАХ == "0")
                ВЕС_ПОДДОНА_НА_ВЕСАХ = "НЕ ВЗВЕШИВАЛСЯ";

            if (ВЕС_ДЕРЕВЯННОГО_ПОДДОНА == "" || ВЕС_ДЕРЕВЯННОГО_ПОДДОНА == "0")
                ВЕС_ДЕРЕВЯННОГО_ПОДДОНА = "НЕ ВЗВЕШИВАЛСЯ";


            ora_com.CommandText = " select count( ST_NUMBER )  from RABAEV.RRL_SBORKA_PALLETS where ST_NUMBER = '" + НОМЕР_СТ + "' ";
            ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ = Convert.ToInt32( ora_com.ExecuteScalar());

            ora_com.CommandText = " select NAME  from RABAEV.RUSERS where ID = '" + this.wms_user.user_id  + "' ";
            ФАМИЛИЯ_ВЕСОВЩИКА = Convert.ToString(ora_com.ExecuteScalar());


            string ARTICUL, SHORTNAME, SHTRIHKOD, EI, PATH, AUCTION;
            double QUANTITY, ORDER_WEIGHT;

            ora_com.CommandText = " select ARTICUL, SHORTNAME  , SHTRIHKOD , EI , "+
                " QUANTITY , PATH , AUCTION , round(ORDER_WEIGHT ,2) , BARCODE_SHT , BARCODE_KOR , "+
                " BARCODE_BL , RRL_COUNT_KOR2( ARTICUL , QUANTITY , CURRENT_MOD_ID ) , "+
                " ( round(ORDER_WEIGHT ,2) +RRL_CARTON_WEIGHT2( ARTICUL , QUANTITY , CURRENT_MOD_ID ) ) " +
                " ,  EXPIRY_DATE   " +
                " from RABAEV.RRL_SBORKA_PALLET_ROWS , RRL_ARTICULS where PALLET_UID = '"
                + pallet_UID + "' and QUANTITY>0 and "+
                " ( RRL_SBORKA_PALLET_ROWS.ARTICUL=RRL_ARTICULS.ACTICUL(+) ) order by SORTFIELD ";

            ora_read = ora_com.ExecuteReader();
            long prows = 0;
            int _X = 20 , _Y = 20;
            int h = 36;




            #region ПЕЧАТЬ ПАСПОРТА
            
            int help_xt = 450;
            if ((PROOVED == 1) || (PROOVED_BY_SCAN == 1))
            {
                PPage _p_sb = new PPage();
                _p_sb.start_point_4_table = new Point(30, 200);
                if (Номер_Паллета > 9)
                {
                    _p_sb.labels.Add(new PPage.PLabel(Номер_Паллета.ToString(), new Point(-50, 100 + _Y), 620, Brushes.Black ));
                    _p_sb.labels.Add(new PPage.PLabel(" из " + ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ.ToString() + " паллет.", new Point(750, 500 + _Y), h, Brushes.Black));

                }
                else
                {
                    _p_sb.labels.Add(new PPage.PLabel(Номер_Паллета.ToString(), new Point(-50, 0 + _Y), 720, Brushes.Black));
                    _p_sb.labels.Add(new PPage.PLabel(" из " + ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ.ToString() + " паллет.", new Point(10 + _X + help_xt, 500 + _Y), h, Brushes.Black));

                }

                
                

              
                _p_sb.labels.Add(new PPage.PLabel(pallet_uid_code(pallet_UID), new Point(0 + _X + help_xt, 00 + 0), 12, "EAN2", 300, 60));
                _p_sb.labels.Add(new PPage.PLabel(pallet_uid_code(pallet_UID), new Point(0 + _X + help_xt, 750 + _Y), 12, "EAN2", 300, 120));
                _p_sb.labels.Add(new PPage.PLabel("Паллет №  " + Номер_Паллета.ToString() + " по СТ: " + НОМЕР_СТ, new Point(10 + _X + help_xt, 1 * h + _Y), h));
                _p_sb.labels.Add(new PPage.PLabel("Паспорт:  " + pallet_UID.ToString(), new Point(10 + _X + help_xt, 2 * h + _Y), h));
                _p_sb.labels.Add(new PPage.PLabel("Адрес: " + Адрес_магазина, new Point(10 + _X + help_xt, 3 * h + _Y), h));
                _p_sb.labels.Add(new PPage.PLabel("Сборщик: " + SBORSHIK.ToString(), new Point(10 + _X , 600 + 3 * h + _Y), h));
                //  _p_sb.labels.Add(new PPage.PLabel("Вес тары (поддона): " + ВЕС_ДЕРЕВЯННОГО_ПОДДОНА, new Point(10 + _X, 800+ 4 * h + _Y), h ));
                _p_sb.labels.Add(new PPage.PLabel("Фактический вес (брутто): " + ВЕС_ПОДДОНА_НА_ВЕСАХ, new Point(10 + _X + help_xt,   4 * h + _Y), h));
                //_p_sb.labels.Add(new PPage.PLabel("Нормативный вес палеты (брутто): " + НОРМАТИВНЫЙ_ВЕС_ПОДДОНА  , new Point(10 + _X, 800 + 6 * h + _Y), h));


                PPages2.Add(_p_sb);
            }
            #endregion


            PPage _p = new PPage();
            _p.start_point_4_table = new Point( 30, 212);


            #region РАЗНЫЕ_ЗАМЕТКИ

            _p.labels.Add(new PPage.PLabel(Номер_Паллета.ToString(), new Point(_X + 600, _Y + 1000), 120, Brushes.Black));
            if ((PROOVED == 1) || (PROOVED_BY_SCAN == 1))
            {
                _p.labels.Add(new PPage.PLabel("Сборочный лист по СТ: " + НОМЕР_СТ + "     ПАЛЛ №: " + Номер_Паллета.ToString(), new Point(10 + _X, 10 + _Y), 24));
                _p.labels.Add(new PPage.PLabel(" (  из  " + ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ + " ) ", new Point(625 + _X, 16 + _Y), 12));

            }
            else {
                _p.labels.Add(new PPage.PLabel("Задание на проверку по СТ: " + НОМЕР_СТ + "ПАЛЛ №: " + Номер_Паллета.ToString(), new Point(10 + _X, 10 + _Y), 24));
                _p.labels.Add(new PPage.PLabel(" (  из  " + ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ + " ) ", new Point(645 + _X, 16 + _Y), 12));

            }
           


             h = 12;
            _p.labels.Add(new PPage.PLabel("Адрес магазина: " + Адрес_магазина, new Point(10 + _X, 40 + _Y), 12));
            _p.labels.Add(new PPage.PLabel("ДатаСТ: " + ДатаСТ.ToLongDateString(), new Point(10 + _X, 40+h + _Y), 12));
            _p.labels.Add(new PPage.PLabel("ДатаПечати: " + ДатаПечати.ToLongDateString(), new Point(10 + _X, 40 + 2*h + _Y), 12));
            _p.labels.Add(new PPage.PLabel("Идентификатор паллета: " + pallet_UID, new Point(10 + _X, 40 + 3*h + _Y), 12));
            _p.labels.Add(new PPage.PLabel("Весовой контролер: " + ФАМИЛИЯ_ВЕСОВЩИКА, new Point(10 + _X, 40 + 4 * h + _Y), 12));
           
             _p.labels.Add(new PPage.PLabel("Вес тары (поддона): " + ВЕС_ДЕРЕВЯННОГО_ПОДДОНА, new Point(10 + _X, 40 + 5 * h + _Y), 12));
             _p.labels.Add(new PPage.PLabel("Фактический вес паллета: " + ВЕС_ПОДДОНА_НА_ВЕСАХ, new Point(10 + _X, 40 + 6 * h + _Y), 12));
             _p.labels.Add(new PPage.PLabel("Вес паллета по нормативу: " + НОРМАТИВНЫЙ_ВЕС_ПОДДОНА , new Point(10 + _X, 40 + 7 * h + _Y), 12));

             _p.labels.Add(new PPage.PLabel("Сборщик: " + SBORSHIK, new Point(10 + _X, 40 + 8 * h + _Y), 12));
             _p.labels.Add(new PPage.PLabel(ПРОШЕЛ_ВЕСОВОЙ_КОНТРОЛЬ, new Point(10 + _X, 40 + 9 * h + _Y), 22));


             if ((PROOVED == 1) || (PROOVED_BY_SCAN == 1))
             {
                 _p.labels.Add(new PPage.PLabel("ПРАВИЛА ВЕСОВОЙ ПЕРЕДАЧИ ГРУЗА В МАГАЗИН:", new Point(10 + _X, 986 + _Y), 10));
                 _p.labels.Add(new PPage.PLabel("а) Водитель принимает паллеты на РЦ по весу. При этом он может потребовать проверку работы весов на стандартном грузе.", new Point(10 + _X, 1000 + _Y), 10));
                 _p.labels.Add(new PPage.PLabel("б) Перед приемкой товара, магазин обязан проверить корректную работу весов совместно с водителем.", new Point(10 + _X, 1012 + _Y), 10));
                 _p.labels.Add(new PPage.PLabel("в) Магазин принимает паллет по весам. в случае отклонения веса паллета от нормативного,", new Point(10 + _X, 1024 + _Y), 10));
                 _p.labels.Add(new PPage.PLabel("палет принимается согласно сборочного листа,  вложенного в паллет. ", new Point(10 + _X, 1036 + _Y), 10));
                 _p.labels.Add(new PPage.PLabel("В случае обнаружения пересорта и недостач, формируется акт по форме, приложенной к сборочному листу.", new Point(10 + _X, 1048 + _Y), 10));
             }

            //string gfds = pallet_uid_decode(pallet_uid_code(pallet_UID));
            _p.labels.Add(new PPage.PLabel( pallet_uid_code( pallet_UID ) , new Point(400 + _X, 40 + _Y), 12, "EAN" , 300 , 80 )  );

            #endregion

            _p.add_column("NO", "string", "№" , 2);
            _p.add_column("ARTICUL", "string" , "АРТИКУЛ" );
            _p.add_column("SHORTNAME", "string" , "НАИМЕНОВАНИЕ" , 30 );
            //_p.add_column("SHTRIHKOD", "EAN" , "ШТРИХ-КОД" , 8 );
            _p.add_column("EI", "string" , "ЕИ" , 2 );
            _p.add_column("QUANTITY", "double" , "КОЛ" , 3 );
            _p.add_column("KOR", "double", "КОР", 3);

            _p.add_column("PATH", "string" , "ЯЧЕЙКА" , 6 );
            _p.add_column("AUCTION", "string" , "АКЦИЯ" , 4 );
            _p.add_column("ORDER_WEIGHT", "string", "ВЕС", 4);
            _p.add_column("ORDER_WEIGHT_BRUTTO", "string", "БРУТТО", 5);

            if (PRINT_EXPIRY_DATE_OP==1)
            {
                _p.add_column("EXPIRY_DATE", "string", "СРОК ГОДНОСТИ", 6);
            }


            PPages.Add(_p);
            #region ФОРМИРУЕМ_СТРАНИЦЫ_ДЛЯ_ПЕЧАТИ
            int x33 = 10, y33 = 10 , y44=-330;
            int inc = 40;

            while (ora_read.Read())
            {
               // ==========================
                Dictionary<string, string> _row = new Dictionary<string, string>();
                NO++;
                ARTICUL = (ora_read.GetValue(0).ToString());
                SHORTNAME = (ora_read.GetValue(1).ToString());
                SHTRIHKOD = (ora_read.GetValue(2).ToString());
                EI = (ora_read.GetValue(3).ToString());
                QUANTITY = (ora_read.GetFloat(4));
                PATH = (ora_read.GetValue(5).ToString());
                AUCTION = (ora_read.GetValue(6).ToString());
                ORDER_WEIGHT = ora_read.GetDouble(7);



                string ШтрихКодШтуки = ora_read.GetValue(8).ToString();
                string ШтрихКодБлока = ora_read.GetValue(9).ToString();
                string ШтрихКодКоробки = ora_read.GetValue(10).ToString();
                string EXPIRY_DATE1 = ora_read.GetValue(13).ToString();
                int количество_коробок = 0;
                try
                {
                    количество_коробок = ora_read.GetInt32(11);
                }catch{}
                double ORDER_WEIGHT_BRUTTO = 0;
                try
                {
                    ORDER_WEIGHT_BRUTTO = ora_read.GetDouble(12);
                }
                catch { }



                _row["NO"] = NO.ToString();
                _row["ARTICUL"] = ARTICUL;
                _row["SHORTNAME"]=SHORTNAME.Replace("\t" , " ");
                //_row["SHTRIHKOD"] = ШтрихКодШтуки;
                _row["EI"]=EI;
                string ff = "        ";
                _row["QUANTITY"] = QUANTITY.ToString();// +ff.Substring(0, 8 - QUANTITY.ToString().Length) + " [" + количество_коробок.ToString() + "к]";
                _row["KOR"] = количество_коробок.ToString()+"к";
                if (количество_коробок == 0)
                {
                    _row["KOR"] = "";
                }


                _row["ORDER_WEIGHT_BRUTTO"] = ORDER_WEIGHT_BRUTTO.ToString();
                _row["EXPIRY_DATE"] = EXPIRY_DATE1.ToString();

                
                _row["PATH"]=PATH;
                _row["AUCTION"]=AUCTION;
                _row["ORDER_WEIGHT"] = ORDER_WEIGHT.ToString();

                PPages[PPages.Count-1].add_row(_row);

                prows++;
                if (prows == Количество_строк)
                {
                    PPage _p2 = new PPage();
                    _p2.columns = _p.columns;


                    _p2.labels.Add(new PPage.PLabel(pallet_uid_code(pallet_UID), new Point(400 + _X, 00 + 20), 12, "EAN", 600, 60));
                    _p2.labels.Add(new PPage.PLabel(pallet_uid_code(pallet_UID), new Point(400 + _X, 800 + _Y), 12, "EAN", 600, 120));
                    _p2.labels.Add(new PPage.PLabel("Паллет №  " + Номер_Паллета.ToString() + " по СТ: " + НОМЕР_СТ, new Point(10 + _X, 1 * h + _Y), h));
                    _p2.labels.Add(new PPage.PLabel("Паспорт:  " + pallet_UID.ToString(), new Point(10 + _X, 2 * h + _Y), h));
                    _p2.labels.Add(new PPage.PLabel("Адрес: " + Адрес_магазина, new Point(10 + _X, 3 * h + _Y), h));
                    _p2.labels.Add(new PPage.PLabel("Сборщик: " + SBORSHIK.ToString(), new Point(10 + _X,   4 * h + _Y), h));
                    


                    _p2.labels.Add(new PPage.PLabel("ПРАВИЛА ВЕСОВОЙ ПЕРЕДАЧИ ГРУЗА В МАГАЗИН:", new Point(10 + _X, 986 + _Y + y44), 10));
                    _p2.labels.Add(new PPage.PLabel("а) Водитель принимает паллеты на РЦ по весу. При этом он может потребовать проверку работы весов на стандартном грузе.", new Point(10 + _X, 1000 + _Y + y44), 10));
                    _p2.labels.Add(new PPage.PLabel("б) Перед приемкой товара, магазин обязан проверить корректную работу весов совместно с водителем.", new Point(10 + _X, 1012 + _Y + y44), 10));
                    _p2.labels.Add(new PPage.PLabel("в) Магазин принимает паллет по весам. в случае отклонения веса паллета от нормативного (3 кг),", new Point(10 + _X, 1024 + _Y + y44), 10));
                    _p2.labels.Add(new PPage.PLabel("палет принимается согласно сборочного листа,  вложенного в паллет. ", new Point(10 + _X, 1036 + _Y + y44), 10));
                    _p2.labels.Add(new PPage.PLabel("В случае обнаружения пересорта и недостач, формируется акт по форме, приложенной к сборочному листу.", new Point(10 + _X, 1048 + _Y + y44), 10));

                    _p2.start_point_4_table = new Point(30, 100);
                    _p2.labels.Add(new PPage.PLabel("Сборочный лист по СТ: " + НОМЕР_СТ + "     ПАЛЛ №: " + Номер_Паллета.ToString(), new Point(10 + _X, 10 + _Y + y44), 24));
                    _p2.labels.Add(new PPage.PLabel(" (  из  " + ЧИСЛО_ПАЛЛЕТ_В_ДАННОМ_СТ + " ) ", new Point(625 + _X, 16 + _Y + y44), 12));

                    PPages.Add(_p2);
                    
                    prows = 1;
                }

               // ===========================
            }


            for (int i = 0; i < PPages.Count; i++)
            {
                PPages[i].labels.Add(new PPage.PLabel("страница: " + (i + 1).ToString() + " из " + PPages.Count.ToString(), new Point( _X+700,   _Y-5 ) , 12 ));
                PPages[i].labels.Add(new PPage.PLabel("страница: " + (i + 1).ToString() + " из " + PPages.Count.ToString(), new Point( _X , _Y + 750 ) , 12 ));
            }

            foreach (PPage ppp in PPages2)
            {
                PPages.Add(ppp);
            }




            #endregion

            #region НАЧАЛО_ПЕЧАТИ

            PrintDocument pd = new PrintDocument();

 /*           try
            {
*/
                
                pd.DefaultPageSettings.Landscape = true ;

                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
   /*         }
            catch (Exception ex)
            {
                MessageBox.Show(" f41 " + ex.Message);

            }
            */
            #endregion




              OracleCommand ora_com7 = new OracleCommand();
              ora_com7.CommandText = " update  RABAEV.RRL_SBORKA_PALLETS set COUNT_OF_PRINTS=(COUNT_OF_PRINTS+1) "+
              " where  PALLET_UID = '" + pallet_UID + "' " ;
              ora_com7.Connection = get_wms_connection();
              ora_com7.ExecuteNonQuery();


              ora_com7 = new OracleCommand();
              ora_com7.CommandText = " insert into RRL_SBORKA_PALLETS_HISTORY ( PALLET_UID ,USER_ID ,  ZONE ,  EVENT ) " +
              " values ('" + pallet_UID + "' , '" + this.wms_user.user_id + "' , 'VESOV' , 'PRINT'   ) ";
              ora_com7.Connection = get_wms_connection();
              ora_com7.ExecuteNonQuery();

        }


        // ===



        private void pd_PrintPage_SBOR(object sender, PrintPageEventArgs ev)
        {
            float leftMargin = ev.MarginBounds.Left;
            float topMargin = ev.MarginBounds.Top;

            
            ev.HasMorePages = false;

            PPage _page_2_print= PPages[PPages.Count - 1];
            _page_2_print.print(ev);

           //Image r = Code128Rendering.MakeBarcodeImage(h_UID_PALLET, 2, true);
           //  ev.Graphics.DrawString("артикул: " + h_articul + " ;    кол-во: " + h_unit_count + " " + h_UNIT_TYPE + "  накл:" + PRIHOD_NAKLAD_ID + "   id паллета:" + h_UID_PALLET, printFont_small, Brushes.Black, 100, 700, new StringFormat());
           //ev.Graphics.DrawImage(r, 200, 330);
           // _page_2_print.
           
           PPages.Remove(_page_2_print);

           if (PPages.Count >= 1)
           {
               ev.HasMorePages = true;
           }

            // ==============================================================================
        }

        private void датаСТУч_CheckedChanged(object sender, EventArgs e)
        {
            dateTimePicker5.Visible = датаСТУч.Checked;
        }

        private void button42_Click(object sender, EventArgs e)
        {

            grid_2_excel(dataGridView18); 
        }

        private void назначитьТранспортToolStripMenuItem_Click(object sender, EventArgs e)
        {
            DataGridViewRow dr = dataGridView17.CurrentRow;
            if(dr==null)
            {
                MessageBox.Show(" Не выбран маршрут ");
            }

            if (!has_right("CHANGE_VODITEL"))
            {

                MessageBox.Show("Нет прав на изменение транспорта");
                return;
            }


            try
            {
                TRANSPORT ftr = new TRANSPORT();
                ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
                ftr.ShowDialog();

                string h = ftr.CHOOSE;
                if (h!=null)
                    if (h!="")
                dr.Cells[6].Value = h;

                dataGridView17_CellEndEdit(null, null);
            }catch(Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {
            СТ_ИЗ_СУПЕРМАГА.Enabled = true;


        }


        
        private bool str_is_empty(string str)
        {
            if (str == null)
                return true;
            if (str.Trim() == "")
                return true;
            return false;
        }

        private bool str_is_empty(object str)
        {

            if (str == null)
                return true;
            if (str.ToString().Trim() == "")
                return true;
            return false;
        }

        private void dataGridView17_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {


            DataGridViewRow dr= dataGridView17.CurrentRow;
           if (dr == null) return;
           string TRANSPORT1 = obj2str(dr.Cells[6].Value);

           if (e != null)
           {

               #region ИЗМЕНЕНИЕ МАШИНЫ
               if ((e.ColumnIndex == 6) && (TRANSPORT1!=""))
               { // Если изменилась машина
                   OracleCommand ora_com2 = new OracleCommand();
                   ora_com2.Connection = get_wms_connection();
                   ora_com2.CommandText = " select NUM from RRL_TR_VEHICLE where NUM like '%" + TRANSPORT1 + "%' ";
                   int count_of_tr = 0;
                   OracleDataReader ora_read2 = ora_com2.ExecuteReader();
                   string TRANSPORT2 = TRANSPORT1;
                   while (ora_read2.Read())
                   {
                       count_of_tr++;
                       TRANSPORT2 = ora_read2.GetValue(0).ToString();
                   }
                   if (count_of_tr != 1)
                   { // открываем форму для выбора транспорта 

                       TRANSPORT ftr = new TRANSPORT();
                       ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
                       ftr.NUM_FILTER = TRANSPORT1;
                       ftr.ShowDialog();

                       string h = ftr.CHOOSE;
                       if (h == null)
                           return;
                       if (h == "")
                           return;
                       dr.Cells[6].Value = h;
                       TRANSPORT1 = h;
                       TRANSPORT2 = TRANSPORT1;
                   }
                   else
                   {
                       TRANSPORT1 = TRANSPORT2;
                   }

               }
                #endregion

               #region ИЗМЕНЕНИЕ ВОДИТЕЛЯ
               if ((e.ColumnIndex == 9) && ( (dr.Cells[9].Value == "") || (dr.Cells[9].Value == null) ) )
               {
                   MessageBox.Show("Поле 'Водитель' не может , быть пустым. Выберите водителя");
                   //dr.Cells[9].Value = null;
                   //dr.Cells[10].Value = null;

                    назначитьВодителяToolStripMenuItem_Click( null , null);
                    return;
               }

               if ((e.ColumnIndex == 9) && (dr.Cells[9].Value != "") && (dr.Cells[9].Value != null ) )
               {
                   string VODITEL_PART_NAME = obj2str(dr.Cells[9].Value);

                    VODITEL ftr = new VODITEL();
                    ftr.Filter_FIO = VODITEL_PART_NAME;
                    ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
                    ftr.ShowDialog();


                    dr.Cells[ 9  ].Value = ftr.CHOOSE ;
                    dr.Cells[ 10 ].Value = ftr.CHOOSE_ID;

                   if(( ftr.CHOOSE_NUM!=null ) && ( ftr.CHOOSE_NUM!= "" ))
                   {
                       if ( str_is_empty(dr.Cells[6].Value ) )
                        {
                            dr.Cells[6].Value = ftr.CHOOSE_NUM;
                            TRANSPORT1 = obj2str(dr.Cells[6].Value);
                        }
                   }
               }

               #endregion

           }
          
           long TT_ID = Convert.ToInt32( dr.Cells[1].Value);
           if (TT_ID == 0) return;
           string WAVE1 = "";
            if(dr.Cells[0].Value!=null)
           WAVE1 = dr.Cells[0].Value.ToString();
           string PRIMECHANIE1 = ПРИМЕЧАНИЕ_ТТ.Text;
          

               long VODITEL_ID1 = obj2int(dr.Cells[10].Value);
               DateTime SHIPMENT_DATE1 = DateTime.Now ;
           try
           {
               SHIPMENT_DATE1 = Convert.ToDateTime(dr.Cells[8].Value);
           }catch( Exception ex ){
                
           }
               string TRANSTYPE1 = obj2str(dr.Cells[5].Value);

               string DOCK = obj2str(dr.Cells[11].Value);

               string ROUTETYPE1 = obj2str(dr.Cells[11].Value);

               if ((TRANSTYPE1 == null) || (TRANSTYPE1 == ""))
               {
                   if (TRANSPORT1 != "")
                   {
                       try
                       {
                           OracleCommand ora_com2 = new OracleCommand();
                           ora_com2.Connection = get_wms_connection();
                           ora_com2.CommandText = " select TR_TYPE from RRL_TR_VEHICLE where NUM = '" + TRANSPORT1 + "' ";
                           int count_of_tr = 0;
                           TRANSTYPE1 = ora_com2.ExecuteScalar().ToString();
                           dr.Cells[5].Value = TRANSTYPE1;
                       }catch(Exception ex)
                       {
                       
                       }
                   }
               }

               if (!has_right("CHANGE_ROUTE"))
               {
                   MessageBox.Show(" Нет прав на CHANGE_ROUTE ");
                   return;
               }

               #region ПРОВЕРКА НАЛИЧИЯ ЛОПАТЫ И ГИДРОБОРТА

 
               OracleCommand ora_com = new OracleCommand();
               ora_com.Connection = get_wms_connection();
               ora_com.CommandText = "RABAEV.RRL_TT_SET_TRANSCOMMENT";
               ora_com.CommandType = CommandType.StoredProcedure;
               ora_com.Parameters.Add("TRANS", OracleType.VarChar).Value = TRANSPORT1;
               ora_com.Parameters.Add("TTID1", OracleType.Int32).Value = TT_ID;
               
               ora_com.Parameters.Add("ret", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
               int rowsAffected = ora_com.ExecuteNonQuery();
               string ret = ora_com.Parameters["ret"].Value.ToString();
               if (ret != "OK")
               {
                   MessageBox.Show(ret);
               }

               #endregion

               ora_com = new OracleCommand();
               ora_com.Connection = get_wms_connection();
               ora_com.CommandText = "RABAEV.RRL_TRASPORT_TASK_UPDATE";
               ora_com.CommandType = CommandType.StoredProcedure;

               ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = TT_ID;
               ora_com.Parameters.Add("TRANSTYPE1", OracleType.VarChar).Value = TRANSTYPE1;
               ora_com.Parameters.Add("TRANSPORT1", OracleType.VarChar).Value = TRANSPORT1;      
               ora_com.Parameters.Add("ROUTETYPE1", OracleType.VarChar).Value = ROUTETYPE1;
               ora_com.Parameters.Add("WAVE1", OracleType.VarChar).Value = WAVE1;
               ora_com.Parameters.Add("SHIPMENT_DATE1", OracleType.DateTime).Value = SHIPMENT_DATE1;
               ora_com.Parameters.Add("VODITEL_ID1", OracleType.Int32).Value = VODITEL_ID1;


               ora_com.Parameters.Add("PRIMECHANIE1", OracleType.VarChar ).Value = PRIMECHANIE1;

               ora_com.Parameters.Add("DOCK1", OracleType.VarChar).Value = DOCK;
               ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;

               // DOCK
               ora_com.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;

                rowsAffected = ora_com.ExecuteNonQuery();

               string ID2 = ora_com.Parameters["ID1"].Value.ToString();



        }

        private void dataGridView17_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            long TT_ID = 0;
            try
            {
                DataGridViewRow dr = dataGridView17.CurrentRow;
                if (dr == null)
                {
                    ПРИМЕЧАНИЕ_ТТ.Text = "";
                    return;
                }
                TT_ID= Convert.ToInt32(dr.Cells[1].Value);
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = " select PRIMECHANIE from RRL_TRANSPORT_TASK where ID=" + TT_ID.ToString() + " ";
                ПРИМЕЧАНИЕ_ТТ.Text = ora_com.ExecuteScalar().ToString();

                // ТЕПЕРЬ ПОДГРУЖАЕМ СТ
                // =======================================================================================
            }
            finally { }


            string strSQL = " select 'false', " +
    " RRL_SKLADNAME_BY_ID( P.WARE_ID ) ,  " +
    " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  " +
     " P.ORD,   P.ADDR , " +
    " P.ST_NUMBER ,  " +
    "  RRL_ST_VERYFY_PERC(P.ST_NUMBER )  " +
    " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R where " +
    " R.PALLET_UID=P.PALLET_UID  and  TRANSTASK_ID = "+  TT_ID.ToString() +
    " group by P.WARE_ID , P.ADDR ,  P.ORD  ,  P.STDATE , P.USER_ID , P.ST_NUMBER  , P.NAPR , RRL_GET_TT_INFO(  TRANSTASK_ID ) " +
    " order by   P.NAPR ";

            fill_view_MINI_WMS(dataGridView20, strSQL, 9);




        }

        private void ПРИМЕЧАНИЕ_ТТ_TextChanged(object sender, EventArgs e)
        {

        }

        private void ПРИМЕЧАНИЕ_ТТ_Leave(object sender, EventArgs e)
        {
           
        }

        private void button43_Click(object sender, EventArgs e)
        {
            dataGridView17_CellEndEdit(null,null);
        }

        private void dataGridView18_CellClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void dataGridView18_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {
            if(e.ColumnIndex==0)
            {
                m_map_V = 0;
                m_map_WEIGHT = 0;
                m_map_P = 0;

                Dictionary<string, double> vals = new Dictionary<string, double>();

                foreach (DataGridViewRow dr in dataGridView18.Rows)
                {
                    if (Convert.ToBoolean(dr.Cells[0].Value))
                    {
                        m_map_V += obj2double(dr.Cells[4].Value);
                        m_map_WEIGHT += obj2double(dr.Cells[3].Value);
                        m_map_P += obj2double(dr.Cells[2].Value);
                    }
                }
                label33.Text = "";
                foreach (string key in vals.Keys)
                {
                    label33.Text = label33.Text + key + " = " + vals[key].ToString() + ";";
                }

                label33.Text = "P=" + Convert.ToInt32(m_map_P).ToString() + "  M=" + Convert.ToInt32(m_map_WEIGHT).ToString() + "  V=" + Convert.ToInt32(m_map_V).ToString() + "";
         
            }
            /*
            if ((e.ColumnIndex == 0) && (e.RowIndex>=0))
            {

                if (Convert.ToBoolean(dataGridView18.Rows[e.RowIndex].Cells[0].Value))
                {
                    m_map_V += obj2double(dataGridView18.Rows[e.RowIndex].Cells[4].Value);
                    m_map_WEIGHT += obj2double(dataGridView18.Rows[e.RowIndex].Cells[3].Value);
                    m_map_P += obj2double(dataGridView18.Rows[e.RowIndex].Cells[2].Value);
                }
                else {
                    m_map_V -= obj2double(dataGridView18.Rows[e.RowIndex].Cells[4].Value);
                    m_map_WEIGHT -= obj2double(dataGridView18.Rows[e.RowIndex].Cells[3].Value);
                    m_map_P -= obj2double(dataGridView18.Rows[e.RowIndex].Cells[2].Value);
            
                }
                label33.Text = "P=" + Convert.ToInt32(m_map_P).ToString() + "  M=" + Convert.ToInt32(m_map_WEIGHT).ToString() + "  V=" + Convert.ToInt32(m_map_V).ToString() + "";
            }

            */

            
        }

        private void dataGridView20_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {

            if ((e.ColumnIndex == 0) && (e.RowIndex >= 0))
            {

                if (Convert.ToBoolean(dataGridView20.Rows[e.RowIndex].Cells[0].Value))
                {
                    m_map2_V += obj2double(dataGridView20.Rows[e.RowIndex].Cells[4].Value);
                    m_map2_WEIGHT += obj2double(dataGridView20.Rows[e.RowIndex].Cells[3].Value);
                    m_map2_P += obj2double(dataGridView20.Rows[e.RowIndex].Cells[2].Value);
                }
                else
                {
                    m_map2_V -= obj2double(dataGridView20.Rows[e.RowIndex].Cells[4].Value);
                    m_map2_WEIGHT -= obj2double(dataGridView20.Rows[e.RowIndex].Cells[3].Value);
                    m_map2_P -= obj2double(dataGridView20.Rows[e.RowIndex].Cells[2].Value);

                }
                label50.Text = "P=" + Convert.ToInt32(m_map2_P).ToString() + "  M=" + Convert.ToInt32(m_map2_WEIGHT).ToString() + "  V=" + Convert.ToInt32(m_map2_V).ToString() + "";
            }

        }

        private void button44_Click(object sender, EventArgs e)
        {
            // 6
            try
            {
                
                DataGridViewRow dr = dataGridView20.CurrentRow;
                if ( (dr != null ) && ( dr.Cells[7].Value!=null ) )
                {
                    string stn = dr.Cells[7].Value.ToString();
                    // string strSQL = " update RRL_SBORKA_PALLETS set TRANSTASK_ID=NULL where ST_NUMBER='" + stn + "' ";

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    /*
                     *ora_com.CommandText = strSQL;
                    ora_com.ExecuteNonQuery();
                    */

                    #region добавляем (УДАЛЯЕМ) СТ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ

                    ora_com.CommandText = "RABAEV.RRL_TT_ADD_PALL";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = 0;
                    ora_com.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = stn;

                    ora_com.Parameters.Add("ret", OracleType.VarChar,1024).Direction = ParameterDirection.ReturnValue;

                    int rowsAffected = ora_com.ExecuteNonQuery();
                    


                    #endregion



                    dataGridView20.Rows.Remove(dr);
                }

            }catch( Exception ex )
            {
                MessageBox.Show(ex.Message);
            }


        }



        private string WARE_BY_ID(long id)
        {
            switch(id)
            {
                case 1 :
                    return "АЛКО";
                case 2:
                    return "МЕЗ";
                case 3:
                    return "СУХОЙ";
                case 4:
                    return "ПРОМ";
                case 5:
                    return "ЯЙЦО";
                case 6:
                    return "ОВОЩИ";
                case 7:
                    return "КОЛБАСА";
                case 8:
                    return "ХОЛОД";
                case 9:
                    return "ПИВО";

                case 10:
                    return "АРБУЗ";

            }

            return "НЕ ИЗВЕСТНЫЙ СКЛАД";
        }

        int WARE_ID_BY_ADDR(string path)
        {
            string ch = path.Substring(0,1) ;
            switch( ch )
            {
                case "B": return 4;
                case "I": return 5;
                case "O": return 6;
                case "D": return 7;
                case "V": return 8;
                case "C": return 1;
                case "M": return 2;
                case "A": return 3;
                case "Г": return 8;
                case "В": return 8;
                case "Д": return 7;
                case "Б": return 4;
                case "М": return 2;
                case "А": return 3;
                case "С": return 1;
                case "R": return 10;

            }

            try
            {
                string h = comboBox1.Text.Substring(0, 1);
                int i = Convert.ToInt32(h);
                return i;
            }
            catch { }

            return 0;

        }


        private void button45_Click(object sender, EventArgs e)
        {// Выгрузка в Excel Распила.

            long РЕЙС_КОЛИЧЕСТВО_ПАЛЛЕТ = 0;
            double РЕЙС_ВЕС = 0;
            double РЕЙС_ОБЪЕМ = 0;
            long ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ = 0;

            long pos = 1;
            Excel.Application oExcelApp = new Excel.Application();
            oExcelApp.Visible = true;

            object obj = new object();
            oExcelApp.Workbooks.Add("");

            oExcelApp.Cells[pos, 1] = "План отгрузок";

            //oExcelApp.get_Range("a1", "a1").Borders.Weight = Excel.XlBorderWeight.xlThin;
            oExcelApp.get_Range("a1", "a1").Font.Size = 16;
           

                foreach (DataGridViewRow dr in dataGridView17.Rows)
                {


                    string TT_ID = dr.Cells[1].Value.ToString();
                    string strSQL = " select WAVE , TRANSPORT , TRANSTYPE  , SHIPMENT_DATE  , PRIMECHANIE , RRL_TT_PALLETS(ID), round( RRL_TT_WEIGHT(ID) , 0 )  , round( RRL_TT_VOLUME(ID)/1000000, 1 ) , ID , PRICE " +
                       " from RRL_TRANSPORT_TASK where ID = " + TT_ID + " ";

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.CommandText = strSQL;


                    try
                    {
                        ora_com.Connection = get_wms_connection();
                        OracleDataReader ora_reader = ora_com.ExecuteReader();

                        if (ora_reader.Read())
                        {
                            pos++; pos++;
                             РЕЙС_КОЛИЧЕСТВО_ПАЛЛЕТ=0;
                             РЕЙС_ВЕС=0;
                             РЕЙС_ОБЪЕМ=0;
                             ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ = pos;


                            object[] values1 = new object[9];
                            for (int yy = 0; yy < 9; yy++)
                            {
                                values1[yy] = ora_reader.GetValue(yy).ToString();
                            }

                            oExcelApp.Cells[pos, 1] = "№ МАШИНЫ = " + values1[1].ToString() + " ТИП=" + values1[2].ToString();
                            oExcelApp.Cells[pos, 2] = "Время=" + values1[0].ToString();
                            oExcelApp.Cells[pos, 3] = "ID рейса = " + values1[8].ToString();
                            oExcelApp.Cells[pos, 4] = "Дата отгрузки= " + Convert.ToDateTime(values1[3]).ToLongDateString();
                            oExcelApp.Cells[pos, 5] = values1[4].ToString();
                            oExcelApp.get_Range("a" + pos.ToString(), "e" + pos.ToString()).Interior.ColorIndex = 37;


                            pos++;
                        }

                        ora_reader.Close();
                        #region  ТЕПЕРЬ ЧИТАЕМ ПАЛЛЕТЫ ДАННОГО МАРШРУТА

                        strSQL = " select  " +
                       " P.WARE_ID ,  " +
                       " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  " +
                       " P.ADDR ,  " +
                       " P.ST_NUMBER ,  " +
                       "  RRL_ST_VERYFY_PERC(P.ST_NUMBER )  " +
                       " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R where " +
                       " R.PALLET_UID=P.PALLET_UID  and  TRANSTASK_ID = " + TT_ID.ToString() +
                       " group by P.WARE_ID , P.ADDR ,   P.STDATE , P.USER_ID , P.ST_NUMBER  , P.NAPR , RRL_GET_TT_INFO(  TRANSTASK_ID ) " +
                       " order by   P.NAPR ";

                        ora_com.CommandText = strSQL;
                        ora_reader = ora_com.ExecuteReader();
                        while (ora_reader.Read())
                        {

                            //pos++;

                            oExcelApp.Cells[pos, 1] = " СТ = " + obj2str(ora_reader.GetValue(5)) + " СКЛАД= " + WARE_BY_ID(obj2int(ora_reader.GetValue(0)));
                            oExcelApp.Cells[pos, 2] = " К-во палл= " + obj2str(ora_reader.GetValue(1));
                            oExcelApp.Cells[pos, 3] = " Вес= " + obj2str(ora_reader.GetValue(2));
                            oExcelApp.Cells[pos, 4] = " Объем= " + obj2str(ora_reader.GetValue(3));
                            oExcelApp.Cells[pos, 5] = " Адрес= " + obj2str(ora_reader.GetValue(4));
                            oExcelApp.get_Range("a" + pos.ToString(), "e" + pos.ToString()).Interior.ColorIndex = 43;
                            pos++;

                            РЕЙС_КОЛИЧЕСТВО_ПАЛЛЕТ+= Convert.ToInt32( ora_reader.GetValue(1) ) ;
                            РЕЙС_ВЕС+= Convert.ToDouble ( ora_reader.GetValue(2) ) ;
                            РЕЙС_ОБЪЕМ= Convert.ToDouble ( ora_reader.GetValue(3) );

                            #region РИСУЕМ_САМИ_ПАЛЛЕТЫ
                            if (!checkBox2.Checked)
                            {
                                string ST_UID = obj2str(ora_reader.GetValue(5));
                                string strSQL2 = " select P.PALLET_UID , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , " +
                                    " round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем   " +
                                    " from RRL_SBORKA_PALLETS P  , " +
                                    " RRL_SBORKA_PALLET_ROWS R where  R.PALLET_UID=P.PALLET_UID  and P.ST_NUMBER='" + ST_UID + "' group by  P.PALLET_UID  ";
                                OracleCommand ora_com8 = new OracleCommand();
                                ora_com8.CommandText = strSQL2;
                                ora_com8.Connection = get_wms_connection();
                                OracleDataReader ora_read8 = ora_com8.ExecuteReader();
                                oExcelApp.Cells[pos, 2] = "№ палл";
                                oExcelApp.Cells[pos, 3] = "вес";
                                oExcelApp.Cells[pos, 4] = "объем";
                                long mini_tab = pos;
                                oExcelApp.get_Range("b" + pos.ToString(), "d" + pos.ToString()).Interior.ColorIndex = 36;

                                while (ora_read8.Read())
                                {
                                    pos++;
                                    oExcelApp.Cells[pos, 2] = obj2str(ora_read8.GetValue(0));
                                    oExcelApp.Cells[pos, 3] = obj2str(ora_read8.GetValue(1));
                                    oExcelApp.Cells[pos, 4] = obj2str(ora_read8.GetValue(2));
                                }
                                oExcelApp.get_Range("b" + mini_tab.ToString(), "d" + pos.ToString()).Borders.Weight = Excel.XlBorderWeight.xlHairline;

                                pos++;
                            }
                            #endregion
                            //===========

                        }

                        #endregion


                    }
                    catch (Exception Ex)
                    {
                        MessageBox.Show(" f312 " + Ex.Message);
                    }

                    oExcelApp.get_Range("a" + ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ.ToString(), "e" + pos.ToString()).Borders[Excel.XlBordersIndex.xlEdgeTop].Weight = Excel.XlBorderWeight.xlMedium;
                    oExcelApp.get_Range("a" + ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ.ToString(), "e" + pos.ToString()).Borders[Excel.XlBordersIndex.xlEdgeBottom].Weight = Excel.XlBorderWeight.xlMedium;
                    oExcelApp.get_Range("a" + ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ.ToString(), "e" + pos.ToString()).Borders[Excel.XlBordersIndex.xlEdgeLeft].Weight = Excel.XlBorderWeight.xlMedium;
                    oExcelApp.get_Range("a" + ПОЗИЦИЯ_ДАННОГО_МАРШРУТА_В_ЛИСТЕ.ToString(), "e" + pos.ToString()).Borders[Excel.XlBordersIndex.xlEdgeRight].Weight = Excel.XlBorderWeight.xlMedium;


                    oExcelApp.Cells[pos, 2] = "ПАЛЛ=" + РЕЙС_КОЛИЧЕСТВО_ПАЛЛЕТ.ToString();
                    oExcelApp.Cells[pos, 3] = "РЕЙС_ВЕС = " + РЕЙС_ВЕС.ToString();
                    oExcelApp.Cells[pos, 4] = "РЕЙС_ОБЪЕМ = " + РЕЙС_ОБЪЕМ.ToString();
                    oExcelApp.get_Range("a" + pos.ToString(), "e" + pos.ToString()).Interior.ColorIndex = 48;
                    pos++;



                }
                    oExcelApp.Cells.Select();
                    oExcelApp.Cells.EntireColumn.AutoFit();
        }

        private void печатьСопроводительногоЛистаToolStripMenuItem_Click(object sender, EventArgs e)
        { // Перчать сопроводительно листа отгузки

            DataGridViewRow dr = dataGridView17.CurrentRow;
            if (dr == null)
            {
                MessageBox.Show(" Не выбран рейс ");
                return;
            }

            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ

                string ID_TT = dr.Cells[1].Value.ToString();
                int _X = 10, _Y = 30;

            #endregion



                #region ПРОВЕРКА ТОГО, ЧТО ВСЕ ПАЛЛЕТЫ ПРОВЕРЕНЫ.
                OracleCommand oracle_com5 = new OracleCommand();
                oracle_com5.Connection = get_wms_connection();

                oracle_com5.CommandText = " select P.PALLET_UID   from RRL_SBORKA_PALLETS P , RRL_WARES W where P.TRANSTASK_ID=" + ID_TT
                + " and ( P.ware_id=W.id ) and ( W.block_if_no_proove=1 ) and ( P.PROOVED=0 ) and (P.PROOVED_BY_SCAN=0)    ";

                OracleDataReader ora_read5 = oracle_com5.ExecuteReader();
                string kosyak_pallets = ""; ;
                bool erros=false;
                while( ora_read5.Read() )
                {
                    erros = true;
                    kosyak_pallets = kosyak_pallets + " " + ora_read5.GetValue(0).ToString();
                }

                if (erros)
                {
                    MessageBox.Show(" Не проверены паллеты "+kosyak_pallets+". \n Сопроводительный лист будет напечатан только после проверки паллет. ");
                    return;
                }
                    
                
                #endregion

                #region ВЫТАСКИВАЕМ ИЗ БАЗЫ ИНФОРМАЦИЮ По ШАПКЕ

                string DOCK = "";
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "select TRANSPORT, TRANSTYPE, ROUTETYPE,  CONDITION , TRANSP_ZONE , "+
                    " WAVE , SHIPMENT_DATE , PRIMECHANIE , VODITEL_ID , DOCK , tr.doverennost_ot , concat( concat( concat( tr.F , ' ' ) , concat( tr.I , ' ' )) , tr.O  )  " +
                    " from RABAEV.RRL_TRANSPORT_TASK ,  rrl_tr_voditel tr "+
                    " where RRL_TRANSPORT_TASK.voditel_id = tr.ID and RRL_TRANSPORT_TASK.ID=" + ID_TT;

                OracleDataReader ora_reader = ora_com.ExecuteReader();
                object[] values1 = new object[12];
                if (ora_reader.Read())
                {

                    for (int yy = 0; yy < 12; yy++)
                    {
                        values1[yy] = ora_reader.GetValue(yy).ToString();
                    }
                }
                else {
                    MessageBox.Show("Нет ID"); return;
                }
                string TRANSPORT = values1[0].ToString();
                string TRANSTYPE = values1[1].ToString();
                string ROUTETYPE = values1[2].ToString();
                string CONDITION = values1[3].ToString();
                string TRANSP_ZONE = values1[4].ToString();
                DOCK = values1[9].ToString();
                string KOMPANY = values1[10].ToString();
                string FIO = values1[11].ToString(); 
            

                string WAVE = values1[5].ToString();
                DateTime SHIPMENT_DATE = Convert.ToDateTime( values1[6] ) ;
                string PRIMECHANIE = values1[7].ToString();
                string VODITEL_ID = values1[8].ToString();

            #endregion



            PPage _page = new PPage();
            _page.start_point_4_table.X = 10;
            _page.start_point_4_table.Y = 170;
            _page.font_size_4_table = 11;

            _page.labels.Add(new PPage.PLabel("Сопроводительный лист отгрузки", new Point(10, 10), 24));
            _page.labels.Add(new PPage.PLabel("Прикрепляется к маршрутному листу с каждой отгрузкой. Возвращается на РЦ.", new Point(10, 44), 16));
            _page.labels.Add(new PPage.PLabel(PRIMECHANIE , new Point(10, 60), 16));

            _page.labels.Add(new PPage.PLabel("TZONE_SLO_" + ID_TT, new Point(680, 1020), 24, "EAN", 100, 100));
            _page.labels.Add(new PPage.PLabel("ФИО ВОДИТЕЛЯ=" + FIO + "; ТРАНСПОРТНАЯ КОМПАНИЯ=" + KOMPANY, new Point(10, 72), 12));




            _page.labels.Add(new PPage.PLabel(" Роспись водителя: __________________________(" + FIO + ")", new Point(10 + _X, 898 + _Y), 12));
            _page.labels.Add(new PPage.PLabel(" (Претензий к погрузке не имею, с правилами приема и передачи товара ознакомлен и согласен.) ", new Point(10 + _X, 910 + _Y), 12));
            

            _page.labels.Add(new PPage.PLabel("Правила приема товара на РЦ и передачи его в магазин:", new Point(10 + _X, 934 + _Y), 12));
            _page.labels.Add(new PPage.PLabel("1) НА РЦ Товар принимается водителем по-паллетно, по весам. Водитель сверяет вес,", new Point(10 + _X, 948 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("указанный в сопроводительном листе с показаниями весов на отгрузке.", new Point(10 + _X, 960 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("При несоответствии веса в «сопроводительном листе» показаниям весов более чем на 3 кг., потребуйте от приемосдатчика", new Point(10 + _X, 972 + _Y), 10));
            _page.labels.Add(new PPage.PLabel(" устранить несоответствие : паллет должен быть перебран силами работников склада до устранения причин несоответствия.", new Point(10 + _X, 984 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("2) После сверки на весах, распишитель в приеке товара в колонке 'Подпись1'", new Point(10 + _X, 996 + _Y), 10));

            _page.labels.Add(new PPage.PLabel("3) В МАГАЗИНЕ: Водитель обязан присутствовать при выгрузке и приемке товара в магазине.", new Point(10 + _X, 1008 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("Магазин принимает паллет по весам, фиксирует вес в колонке 'ВесВМаг' , В случае отклонения  веса ", new Point(10 + _X, 1020 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("паллета от нормативного на 3 кг и выше, паллет принимается согласно сборочного листа, вложенного в паллет.", new Point(10 + _X, 1032 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("В случае выявления излишков, недостач, пересорта  в паллете, магазин формирует акт.", new Point(10 + _X, 1044 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("После приемки товара, магазин ставит подпись и печать магазина о приемке груза.", new Point(10 + _X, 1056 + _Y), 10));
            _page.labels.Add(new PPage.PLabel("4) После взвешивания на весах магазина, распишитель о передаче товара в колонке 'Подпись2'", new Point(10 + _X, 1068 + _Y), 10));



            
            //====================================
            _page.add_column("NUMB", "string", "№", 2); // номер в порядке загрузки авто
            _page.add_column("ST_NUMB", "string", "НОМЕР СТ", 9);
            _page.add_column("N_NUMB", "string", "ЗОНА ОТГР", 7);
            _page.add_column("ADR", "string", "АДРЕС", 15);
            _page.add_column("PALL_NUMB", "string", "№ ПАЛЛ", 11);
            _page.add_column("WARE", "string", "СКЛАД", 5);
            _page.add_column("WPALL", "string", "ВЕС ПАЛЛ", 5);
            _page.add_column("PRIM", "string", "Подпись", 5);
            _page.add_column("W2", "string", "ВесВМаг", 5);
            _page.add_column("P2", "string", "Подпись", 5);

            //_page.column_groups.Add(new PPage.PColumnGroup("вес на РЦ", 6, 8, 12));
            
            _page.column_groups.Add(new PPage.PColumnGroup("    вес в магазине", 8, 10, 12));
            _page.height_of_column = 36;


            

            ora_com.CommandText = " select ORD , ST_NUMBER ,NAKLAD_NUMBER , CREATE_DATE , "+
                " RRL_SKLADNAME_BY_ID( WARE_ID ) , " +
                " PALLET_UID ,ADDR , 1 ,   round( TRIAL_WEIGHT , 2 ) , ZONE "+
                " from RRL_SBORKA_PALLETS where TRANSTASK_ID=" + ID_TT
                + " order by ORD , PALLET_UID ";
            // round( RRL_OP_WEIGHT(PALLET_UID) ,2) TRIAL_WEIGHT
            OracleDataReader ora_read3 = ora_com.ExecuteReader();


            long КОЛИЧЕСТВО_ПАЛЛЕТ1 = 0;
            while (ora_read3.Read())
            {

                Dictionary<string, string> _row = new Dictionary<string, string>();

                _row["NUMB"] = obj2str(ora_read3.GetValue(0));
                _row["ST_NUMB"] = obj2str( ora_read3.GetValue(1) ) ;
                _row["N_NUMB"] = obj2str(ora_read3.GetValue(9));
                _row["ADR"] = obj2str(ora_read3.GetValue(6)).Replace("СМ ","");
                _row["PALL_NUMB"] = obj2str(ora_read3.GetValue(5));
                _row["WARE"] = obj2str(ora_read3.GetValue(4));
                _row["WPALL"] = obj2str(    ora_read3.GetValue(8)    )   ;
                _row["PRIM"] = "";
                _row["W2"] = "";
                _row["P2"] = "";

                _page.add_row(_row);
                КОЛИЧЕСТВО_ПАЛЛЕТ1++ ;

            }


            #region ШАПКА_СОПРОВОДИТЕЛЬНОГО_ЛИСТА

                PPage.PTable _tble = new PPage.PTable();
                _tble.start_point_4_table.X = 10;
                _tble.start_point_4_table.Y = 100;

                _tble.add_column("AUTO", "string", "№ АВТО", 7); // номер в порядке загрузки авто
                _tble.add_column("GATE", "string", "ДОК", 5);
                _tble.add_column("DATE", "string", "ДАТА", 7);

                _tble.add_column("TIME", "string", "ВРЕМЯ", 5);
                _tble.add_column("ID", "string", "ID рейса", 5);
                _tble.add_column("PR", "string", "ФИО ПРИЕМОСДАТЧИКА", 30);

                Dictionary<string, string> _row2 = new Dictionary<string, string>();
                _row2["AUTO"] = TRANSPORT;
                _row2["GATE"] = DOCK;
                _row2["DATE"] = DateTime.Now.ToLongDateString() ;
                _row2["TIME"] = DateTime.Now.ToLongTimeString();
                _row2["ID"] = ID_TT;
                _row2["PR"] = "";

                _tble.add_row(_row2);
                _page.tables.Add(_tble);

            #endregion

            #region ТАБЛИЦА_С_КОЛИЧЕСТВОМ ОТГРУЖЕННЫХ ПАЛЛЕТ

                PPage.PTable _tble2 = new PPage.PTable();
                _tble2.start_point_4_table.X = 650;
                _tble2.start_point_4_table.Y = 930;

                _tble2.add_column("GRUZ", "string", "ГРУЗЧИК", 7); // номер в порядке загрузки авто
                _tble2.add_column("OTG_PALL", "string", "К-ВО ПАЛЛ", 7);


                Dictionary<string, string> _row3 = new Dictionary<string, string>();
                _row3["GRUZ"] = "";
                _row3["OTG_PALL"] = "";
                _tble2.add_row(_row3);

                Dictionary<string, string> _row4 = new Dictionary<string, string>();
                _row4["GRUZ"] = "";
                _row4["OTG_PALL"] = "";
                _tble2.add_row(_row4);

            
                Dictionary<string, string> _row5 = new Dictionary<string, string>();
                _row5["GRUZ"] = "Итого";
                _row5["OTG_PALL"] = КОЛИЧЕСТВО_ПАЛЛЕТ1.ToString();
                _tble2.add_row(_row5);



                _page.tables.Add(_tble2);

            #endregion

            PPages.Add(_page);

            #region НАЧАЛО_ПЕЧАТИ
                PrintDocument pd = new PrintDocument();
                try
                {
                    pd.DefaultPageSettings.Landscape = false;
                    pd.PrintPage += new PrintPageEventHandler
                        (pd_PrintPage_SBOR);
                    pd.Print();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(" f48 " + ex.Message);
                }
            #endregion



        }

        private void dataGridView20_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

            /* from  P  , RRL_SBORKA_PALLET_ROWS R where " +
    " R.PALLET_UID
                */
            if (e.ColumnIndex == 6)
            {
                string STN = obj2str(dataGridView20.CurrentRow.Cells[7].Value);
                long ORD = obj2int(dataGridView20.CurrentRow.Cells[5].Value);
                string strSQL = " update RRL_SBORKA_PALLETS set ORD=" + ORD.ToString() + " where ST_NUMBER ='" + STN + "' ";
                OracleCommand ora_com = new OracleCommand();
                ora_com.CommandText = strSQL;
                ora_com.Connection = get_wms_connection();
                ora_com.ExecuteNonQuery();

            }
        }

        private void button46_Click(object sender, EventArgs e)
        { // Добавляем фейковый паллет по аналогии с текущим выбранным паллетом

            string lll = "";
            DataGridViewRow dr = dataGridView22.CurrentRow;
            if (dr == null) { return; }
            string pall_uid = dr.Cells[1].Value.ToString();

            #region ЕСЛИ СКЛАД ФЕЙКОВЫЙ

            // ПО ДАННОМУ УИДУ ПАЛЛЕТА НУЖНО ПОЛУЧИТЬ НОМЕР НОВОГО ПАЛЛЕТА, НОМЕР СТ
            string strSQL5 = " select ST_NUMBER from RABAEV.RRL_SBORKA_PALLETS where PALLET_UID='" + pall_uid + "' ";
            OracleCommand ora_com9 = new OracleCommand();
            ora_com9.CommandText = strSQL5;
            ora_com9.Connection = get_wms_connection();
            lll = ora_com9.ExecuteScalar().ToString();


            strSQL5 = " select ADDR , max(PALLET_NUMBER) , WARE_ID  from  RRL_SBORKA_PALLETS where "+
                " ST_NUMBER='" + lll + "' group by   ADDR  , WARE_ID  ";

            OracleCommand ora_com11 = new OracleCommand();
            ora_com11.Connection = get_wms_connection();
            ora_com11.CommandText = strSQL5;
            OracleDataReader ora_read11 = ora_com11.ExecuteReader();
            long КрасивыйНомерПаллета = 1;
            long current_ware_id = 1;
            string ADDR = "";
            if (ora_read11.Read())
            {
                ADDR = ora_read11.GetValue(0).ToString();
                КрасивыйНомерПаллета = Convert.ToInt32(  ora_read11.GetValue(1) ) ;
                current_ware_id = Convert.ToInt32(ora_read11.GetValue(2));

            }
            else {
                MessageBox.Show("Не могу найти паллет");
                return;
            }

            OracleCommand ora_com6 = new OracleCommand();
            ora_com6.Connection = get_wms_connection();
            ora_com6.CommandText = " select FAKE_ART  from RRL_WARES where ID=" + current_ware_id.ToString() + " ";
            string faked_articul = Convert.ToString(ora_com6.ExecuteScalar());

            ora_com6.CommandText = " select NAME    from RRL_ARTICULS where ACTICUL='" + faked_articul + "' ";
            string faked_articul_name = Convert.ToString(ora_com6.ExecuteScalar());

            КрасивыйНомерПаллета++;

            if (lll != "")
            { //ИНАЧЕ СОЗДАЕМ ПАЛЛЕТ С 1 СТРОКОЙ.
                
                string PALLET_UID1 = "OP_" + lll + "_" + КрасивыйНомерПаллета.ToString();
                #region СОЗДАЕМ_ПАЛЛЕТ
                string[] NAPR1 = ADDR.Split('-');
                string NAPR = "неизв";
                if (NAPR1.Length >= 1)
                    NAPR = NAPR1[0];

                if (NAPR == ""){ NAPR = "НЕИЗВ";}

                ora_com9.CommandText = "RABAEV.RRL_SBORKA_PALLETS_ADD2";
                ora_com9.CommandType = CommandType.StoredProcedure;
                ora_com9.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = lll;
                ora_com9.Parameters.Add("ADDR1", OracleType.VarChar).Value = ADDR;
                ora_com9.Parameters.Add("PALLET_NUMBER1", OracleType.Int32).Value = КрасивыйНомерПаллета;
                ora_com9.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                ora_com9.Parameters.Add("STATE1", OracleType.VarChar).Value = "Выдан в сборку";
                ora_com9.Parameters.Add("STDATE1", OracleType.DateTime).Value = DateTime.Today;
                ora_com9.Parameters.Add("NAPR1", OracleType.VarChar).Value = NAPR;
                ora_com9.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                ora_com9.Parameters.Add("USER_ID1", OracleType.VarChar).Value = this.wms_user.user_id;
                ora_com9.Parameters.Add("id", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com9.ExecuteNonQuery();
                long ret_id = Convert.ToInt32(ora_com9.Parameters["id"].Value.ToString());
                ora_com9.Dispose();

                #endregion

                #region СОЗДАЕМ СТРОЧКУ ПАЛЛЕТА
                OracleCommand ora_com10 = new OracleCommand();
                ora_com10.CommandText = "RABAEV.RRL_SBORKA_PALLETS_ADD2";
                ora_com10.CommandType = CommandType.StoredProcedure;
                ora_com10.Connection = get_wms_connection();

                ora_com10.CommandText = "RABAEV.RRL_SBORKA_PALLET_ROWS_ADD4";
                ora_com10.CommandType = CommandType.StoredProcedure;
                ora_com10.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = PALLET_UID1;
                ora_com10.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = faked_articul;
                ora_com10.Parameters.Add("SHORTNAME1", OracleType.VarChar).Value = faked_articul_name;
                ora_com10.Parameters.Add("SHTRIHKOD1", OracleType.VarChar).Value = "";
                ora_com10.Parameters.Add("EI1", OracleType.VarChar).Value = "кг";
                ora_com10.Parameters.Add("TAREWEIGHT1", OracleType.Number).Value = 1;
                ora_com10.Parameters.Add("PATH1", OracleType.VarChar).Value = "";
                ora_com10.Parameters.Add("ORDER_WEIGHT1", OracleType.Number).Value = 1;
                ora_com10.Parameters.Add("TARESIZE1", OracleType.Number).Value = 1;
                ora_com10.Parameters.Add("QUANTITY1", OracleType.Number).Value = 1;
                ora_com10.Parameters.Add("SORTFIELD1", OracleType.Int32).Value = 1;
                ora_com10.Parameters.Add("AUCTION1", OracleType.VarChar).Value = "";
                ora_com10.Parameters.Add("DOCID1", OracleType.VarChar).Value = "";
                ora_com10.Parameters.Add("ware_id1", OracleType.Int32).Value = current_ware_id;
                ora_com10.Parameters.Add("PACK_COUNT1", OracleType.Int32).Value = 1;
                ora_com10.Parameters.Add("id1", OracleType.Int32).Direction = ParameterDirection.ReturnValue;

                int rowsAffected7 = ora_com10.ExecuteNonQuery();
                long ret_id7 = Convert.ToInt32(ora_com10.Parameters["id1"].Value.ToString());
                ora_com10.Dispose();



                #endregion

            }


            #endregion


            dataGridView21_CellEnter(null, null);

        }








        private void пеToolStripMenuItem_Click(object sender, EventArgs e)
        {   // Печать маршрутного листа ===================================================

            Dictionary<string, string> Возвраты= new Dictionary<string,string>();
            DataGridViewRow dr = dataGridView17.CurrentRow;
            if (dr == null)
            {
                MessageBox.Show(" Не выбран рейс ");
                return;
            }

           string tt_id = (dataGridView17.CurrentRow.Cells[1].Value.ToString());
            try{
                if (obj2int(dataGridView17.CurrentRow.Cells[13].Value) == 0)
                {
                    string ret = wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
                    double price = obj2double(ret);
                    dataGridView17.CurrentRow.Cells[13].Value = price;
                    if (price == 0)
                    {
                        MessageBox.Show( "Прайс для данного рейса не рассчитан автоматически.\n"+
                            "Регионы рейса не внесены в разряд допустимых.\n"+
                            "Возможно вы ошиблись в составлении рейса." );
                    }
                }
            }catch{}

            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ

            string ID_TT = dr.Cells[1].Value.ToString();
            int _X = 10, _Y = 30;

            #endregion

            #region ВЫТАСКИВАЕМ ИЗ БАЗЫ ИНФОРМАЦИЮ По ШАПКЕ

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = "select RRL_TRANSPORT_TASK.TRANSPORT, RRL_TRANSPORT_TASK.TRANSTYPE, "+
                " RRL_TRANSPORT_TASK.ROUTETYPE,  RRL_TRANSPORT_TASK.CONDITION , RRL_TRANSPORT_TASK.TRANSP_ZONE ,  " +
                " RRL_TRANSPORT_TASK.WAVE , RRL_TRANSPORT_TASK.SHIPMENT_DATE , RRL_TRANSPORT_TASK.PRIMECHANIE , "+
                " RRL_TRANSPORT_TASK.VODITEL_ID , RRL_TR_VEHICLE.MARKA , F ,I,O, PASSPORT , DOVERENNOST_OT , ADDR  , TEL ,SOBSTVENNYY , RRL_TRANSPORT_TASK.DOCK " +
                " from RABAEV.RRL_TRANSPORT_TASK , RRL_TR_VEHICLE , RRL_TR_VODITEL where RRL_TRANSPORT_TASK.ID=" + ID_TT +
                " and RRL_TR_VEHICLE.NUM = RRL_TRANSPORT_TASK.TRANSPORT and "+
                " RRL_TR_VODITEL.ID = RRL_TRANSPORT_TASK.VODITEL_ID ";

            OracleDataReader ora_reader = ora_com.ExecuteReader();
            object[] values1 = new object[19];
            if (ora_reader.Read())
            {

                for (int yy = 0; yy < 19; yy++)
                {
                    values1[yy] = ora_reader.GetValue(yy).ToString();
                }
            }
            else
            {
                MessageBox.Show("Не назначена машина или водитель для маршрута."); return;
            }
            string TRANSPORT = values1[0].ToString();
            string TRANSTYPE = values1[1].ToString();
            string ROUTETYPE = values1[2].ToString();
            string CONDITION = values1[3].ToString();
            string TRANSP_ZONE = values1[4].ToString();
            string WAVE = values1[5].ToString();
            DateTime SHIPMENT_DATE = Convert.ToDateTime(values1[6]);
            string PRIMECHANIE = values1[7].ToString();
            string VODITEL_ID = values1[8].ToString();
            string MARKA= values1[9].ToString();
            string DOCK = values1[18].ToString();
            // F ,I,O, PASSPORT , DOVERENNOST_OT , ADDR  , TEL ,SOBSTVENNYY 

            string Фамилия_водителя = values1[10].ToString();
            string Имя_водителя = values1[11].ToString();
            string Отчество_водителя = values1[12].ToString();
            string Паспорт_водителя = values1[13].ToString();
            string Доверенность_водителя = values1[14].ToString();
            string Адрес_водителя = values1[15].ToString();
            string Тел_водителя = values1[16].ToString();
            int Собственный = Convert.ToInt32( values1[17] ) ;

            if (Доверенность_водителя == "")
            {
                MessageBox.Show("Не выбрана компания водителя");
                return;
            }

            if (TRANSTYPE == "нет" || TRANSTYPE == "")
            {
                MessageBox.Show("Не выбран тип транспортного средства");
                return;
                
            }

            #endregion


            int h=10;
            int x1 = 24;
            PPage _page = new PPage();

            _page.font_size_4_table = 11;
            _page.height_of_column = 60;
            _page.start_point_4_table.X = 10;
            _page.start_point_4_table.Y = 140;

            _page.labels.Add(new PPage.PLabel("Маршрутный лист грузового автомобиля: "+ TRANSPORT+" №  "+ ID_TT, new Point(10, 10), 24));
            _page.labels.Add(new PPage.PLabel("от " + DateTime.Today.ToLongDateString() + " " + DateTime.Now.ToLongTimeString(), new Point(10, 44), h));
            _page.labels.Add(new PPage.PLabel(" Организация: ООО 'Элемент-трейд' ", new Point(10, x1+h*3)  , h));
            _page.labels.Add(new PPage.PLabel(" Марка автомобиля: " + MARKA , new Point(10, x1 + h * 4), h));
            _page.labels.Add(new PPage.PLabel(" Государственный номер: " + TRANSPORT, new Point(10, x1 + h * 5), h));
            _page.labels.Add(new PPage.PLabel(" Водитель: " + Фамилия_водителя+" "+Имя_водителя+" "+Отчество_водителя , new Point(10, x1 + h * 6), h));

            if (Тел_водителя != "")
            {
                _page.labels.Add(new PPage.PLabel("тел.водителя: "+Тел_водителя, new Point(400, x1 + h * 3), 24));
            }

            _page.labels.Add(new PPage.PLabel("компания: " + Доверенность_водителя, new Point(400, x1 + h * 7), 24));

            _page.labels.Add(new PPage.PLabel("тип тс: " + TRANSTYPE, new Point(800, x1 + h * 7), 24));


            _page.labels.Add(new PPage.PLabel(" Время постановки на док: " + WAVE , new Point(10, x1 + h * 7), h));
            _page.labels.Add(new PPage.PLabel(" Док погрузки: " + DOCK, new Point(10, x1 + h * 8), h));



            _page.labels.Add(new PPage.PLabel("TZONE_ML_" + ID_TT, new Point(980, 10), 24, "EAN", 100, 100));




            _page.labels.Add(new PPage.PLabel( PRIMECHANIE , new Point(10 + _X, 480 + _Y), 16));

            int sh = 600;



            _page.labels.Add(new PPage.PLabel(" Роспись водителя: ________________________________________________________________________", new Point(10 + _X, sh+h*1-2 + _Y), 12));
            _page.labels.Add(new PPage.PLabel(" (Претензий к погрузке не имею, с правилами приема и передачи товара ознакомлен и согласен.) ", new Point(10 + _X, sh + h * 2  +_Y), h));
            _page.labels.Add(new PPage.PLabel("Правила приема товара на РЦ и передачи его в магазин:", new Point(10 + _X, sh + h * 3 + _Y), h));
            _page.labels.Add(new PPage.PLabel("1) НА РЦ Товар принимается водителем по-паллетно, по весам. Водитель сверяет вес,", new Point(10 + _X, sh + h * 4 + _Y), h));
            _page.labels.Add(new PPage.PLabel("указанный в сопроводительном листе с показаниями весов на отгрузке.", new Point(10 + _X, sh + h * 5 + _Y), h));
            _page.labels.Add(new PPage.PLabel("При несоответствии веса в «сопроводительном листе» показаниям весов более чем на 3 кг., потребуйте от приемосдатчика", new Point(10 + _X, sh + h * 6 + _Y), h));
            _page.labels.Add(new PPage.PLabel(" устранить несоответствие : паллет должен быть перебран силами работников склада до устранения причин несоответствия.", new Point(10 + _X, sh + h * 7 + _Y), h));
            _page.labels.Add(new PPage.PLabel("2) После сверки на весах, распишитеcь в приеке товара в колонке 'Подпись1' сопроводительного листа", new Point(10 + _X, sh + h * 8 + _Y), h));

            _page.labels.Add(new PPage.PLabel("3) В МАГАЗИНЕ: Водитель обязан присутствовать при выгрузке и приемке товара в магазине.", new Point(10 + _X, sh + h * 9 + _Y), h));
            _page.labels.Add(new PPage.PLabel("Магазин принимает паллет по весам, фиксирует вес в колонке 'ВесВМаг' сопроводительного листа , В случае отклонения  веса ", new Point(10 + _X, sh + h * 10 + _Y), h));
            _page.labels.Add(new PPage.PLabel("паллета от нормативного на 3 кг и выше, паллет принимается согласно сборочного листа, вложенного в паллет.", new Point(10 + _X, sh + h * 11 + _Y), h));
            _page.labels.Add(new PPage.PLabel("В случае выявления излишков, недостач, пересорта  в паллете, магазин формирует акт.", new Point(10 + _X, sh + h * 12 + _Y), h));
            _page.labels.Add(new PPage.PLabel("После приемки товара, магазин ставит подпись и печать магазина о приемке груза.", new Point(10 + _X, sh + h * 13 + _Y), h));
            _page.labels.Add(new PPage.PLabel("4) После взвешивания на весах магазина, распишитель о передаче товара в колонке 'Подпись2' сопроводительного листа", new Point(10 + _X, sh + h * 14 + _Y), h));




            //====================================
            _page.add_column("NUMB", "string", "№", 2); // номер в порядке загрузки авто
            _page.add_column("ADR", "string", "АДРЕС", 15);

            _page.add_column("T1", "string", "прибыл", 6);
            _page.add_column("T2", "string", "начало погрузки", 6);
            _page.add_column("T3", "string", "окончание погрузки", 6);
            _page.add_column("T4", "string", "убыл", 6);

            

            _page.add_column("ST_NUMB", "string", "НОМЕР СТ", 8 );
            _page.add_column("N_NUMB", "string", "НОМЕР НАКЛ", 7);

            _page.add_column("PALL_NUMB", "string", "Количество деревянных поддонов, загруженных в машину", 8);
           // _page.add_column("P3", "string","Количество паллет с ТМЦ, принятых к перевозке, доставленных в магазин" , 8);
            _page.add_column("P4", "string", "Количество деревянных поддонов, принятых от магазина", 8);
            _page.add_column("P5", "string", "Подпись и расшифровка приемо-сдатчика)", 11);
            
            _page.add_column("WARE", "string", "СКЛАД", 5);
            _page.add_column("WPALL", "string", "ВЕС ПАЛЛ", 5);
            _page.add_column("PRIM", "string", "Подпись водителя", 7);
            _page.column_groups.Add(new PPage.PColumnGroup("                              время", 2, 5, 12));


            ora_com.CommandText = " select min( RRL_SBORKA_PALLETS.ORD) , ST_NUMBER , NAKLAD_NUMBER , 1 , " +
                " RRL_SKLADNAME_BY_ID( WARE_ID ) , " +
                " count(PALLET_UID) КолВоПаллет , RRL_ADDR.ADDR , 1 , round( sum( RRL_OP_WEIGHT(PALLET_UID) ) , 1) Вес , RRL_ADDR.PRIM1  from RRL_SBORKA_PALLETS , RRL_ADDR  where TRANSTASK_ID=" + ID_TT
                + " and RRL_SBORKA_PALLETS.ADDR=RRL_ADDR.ADDR(+) group by      ST_NUMBER ,NAKLAD_NUMBER  ,RRL_SKLADNAME_BY_ID( WARE_ID ) , RRL_ADDR.ADDR , RRL_ADDR.PRIM1     order by min(  RRL_SBORKA_PALLETS.ORD ) , ST_NUMBER ";

            OracleDataReader ora_read3 = ora_com.ExecuteReader();
            int pos_1 = 1;
            Dictionary<string, string> _row = new Dictionary<string, string>();

            #region ДОБАВЛЯЕМ_ПЕРВУЮ_СТРОКУ
            
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "РЦ ТС 'Монетка' ";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";

            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            //_row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);

            #endregion



            while (ora_read3.Read())
            {
                pos_1++;
                 _row = new Dictionary<string, string>();

                _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
                _row["ST_NUMB"] = obj2str(ora_read3.GetValue(1));
                _row["N_NUMB"] = obj2str(ora_read3.GetValue(2));
                _row["ADR"] = obj2str(ora_read3.GetValue(6)).Replace("СМ ", "");
                _row["PALL_NUMB"] = obj2str(ora_read3.GetValue(5));
                _row["WARE"] = obj2str(ora_read3.GetValue(4));
                _row["WPALL"] = obj2str( ora_read3.GetValue(8) );

                if ( (  obj2str( ora_read3.GetValue(9) )!="" ) && (  obj2str( ora_read3.GetValue(9) )!=null ) ){
                Возвраты[_row["ADR"]] = obj2str(ora_read3.GetValue(9));
                }

                _row["T1"] = "";
                _row["T2"] = "";
                _row["T3"] = "";
                _row["T4"] = "";
                _row["PRIM"] = "";
                //_row["P3"] = "";
                _row["P4"] = "";
                _row["P5"] = "";
                _page.add_row(_row);

            }

            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);

            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);

            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);
            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);
            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);
            _row = new Dictionary<string, string>();
            pos_1++;
            _row["NUMB"] = pos_1.ToString();// obj2str(ora_read3.GetValue(0));
            _row["ST_NUMB"] = "";
            _row["N_NUMB"] = "";
            _row["ADR"] = "";
            _row["PALL_NUMB"] = "";
            _row["WARE"] = "";
            _row["WPALL"] = "";
            _row["T1"] = "";
            _row["T2"] = "";
            _row["T3"] = "";
            _row["T4"] = "";
            _row["PRIM"] = "";
            _row["P3"] = "";
            _row["P4"] = "";
            _row["P5"] = "";
            _page.add_row(_row);

            #region ВОЗВРАТ С МАГАЗИНОВ И ПОДДОНЫ
           
            PPage.PTable _tble2 = new PPage.PTable();
            _tble2.start_point_4_table.X = 650;
            _tble2.start_point_4_table.Y = 550;
            
            _tble2.add_column("N", "string", "Сдал на РЦ деревянных поддонов: ", 21); // номер в порядке загрузки авто
            _tble2.add_column("P", "string", "Подпись приемо-сдатчика ", 17);
            Dictionary<string, string> _row2 = new Dictionary<string, string>();
            _row2["N"] = "";
            _row2["P"] = "";
            _tble2.add_row(_row2);
            _page.tables.Add(_tble2);


            PPage.PTable _tble = new PPage.PTable();
            _tble.start_point_4_table.X = 10;
            _tble.start_point_4_table.Y = 550;

            _tble.add_column("N", "string", "№", 7); // номер в порядке загрузки авто
            _tble.add_column("ADDR", "string", "Адрес магазина", 11);
            _tble.add_column("ND", "string", "Номер документа", 11);

            _tble.add_column("R", "string", "Подпись приемомоcдатчика", 17);


            _row2 = new Dictionary<string, string>();
            _row2["N"] = "1";
            _row2["ADDR"] = "";
            _row2["ND"] = "";
            _row2["R"] = "";
            _tble.add_row(_row2);
            _row2 = new Dictionary<string, string>();
            _row2["N"] = "2";
            _row2["ADDR"] = "";
            _row2["ND"] = "";
            _row2["R"] = "";
            _tble.add_row(_row2);
            _row2 = new Dictionary<string, string>();
            _row2["N"] = "3";
            _row2["ADDR"] = "";
            _row2["ND"] = "";
            _row2["R"] = "";
            _tble.add_row(_row2);
            _row2 = new Dictionary<string, string>();
            _row2["N"] = "4";
            _row2["ADDR"] = "";
            _row2["ND"] = "";
            _row2["R"] = "";
            _tble.add_row(_row2);

            _page.tables.Add(_tble);


            #endregion

            PPages.Add(_page);

            #region ОБОРОТНАЯ СТОРОНА ЛИСТА

            PPage _page2 = new PPage();
            _page2.font_size_4_table = 16;
            _page2.start_point_4_table.X = 10;
            _page2.start_point_4_table.Y = 10;

            int pos_22 = 0;
            _page2.add_column("N", "string", "№", 2);
            _page2.add_column("TIME", "string", "Дата/Время", 10);
            _page2.add_column("PLOMB1", "string", "Прибыл с пломбой №", 13);
            _page2.add_column("PLOMB2", "string", "Установлена пломба №", 13);
            _page2.add_column("D1", "string", "Должность", 10);
            _page2.add_column("D2", "string", "Подпись", 7);
            _page2.add_column("D3", "string", "Расшифровка подписи", 12);

            for (pos_22 = 1; pos_22 < 12; pos_22++)
            {
                _row = new Dictionary<string, string>();
                _row["N"] = pos_22.ToString();
                _row["TIME"] = "";
                _row["PLOMB1"] = "";
                _row["PLOMB2"] = "";
                _row["D1"] = "";
                _row["D2"] = "";
                _row["D3"] = "";
                _page2.add_row(_row);
            }

            PPage.PTable table24 =  new PPage.PTable();
            table24.font_size_4_table = 16;
            table24.start_point_4_table.X = 10;
            table24.start_point_4_table.Y = 350;

            table24.add_column("DATA", "string", "Дата", 7);
            table24.add_column("PROSTOI", "string", "Причина простоя", 15);
            table24.add_column("MESTO", "string", "Пункт погрузки - выгрузки", 15);
            table24.add_column("MESTO2", "string", "подпись(расшифровка)", 15);
            for (pos_22 = 1; pos_22 < 8; pos_22++)
            {
                _row = new Dictionary<string, string>();
                _row["DATA"] = "";
                _row["PROSTOI"] = "";
                _row["MESTO"] = "";
                _row["MESTO2"] = "";
                table24.add_row(_row);
            }

            _page2.tables.Add(table24);


            #region ТАБЛИЦА ВОЗВРАТОВ


            if (Возвраты.Count > 0)
            {

               
          
                PPage.PTable table25 = new PPage.PTable();
                table25.font_size_4_table = 16;
                table25.start_point_4_table.X = 10;
                table25.start_point_4_table.Y = 590;

                table25.add_column("ADDR", "string", "Адрес", 25);
                table25.add_column("PRIM1", "string", "Задача", 30);
                foreach (string kk in Возвраты.Keys)
                {
                    _row = new Dictionary<string, string>();
                    _row["ADDR"] = kk;
                    _row["PRIM1"] = Возвраты[kk];
                    table25.add_row(_row);
                }

               _page2.tables.Add(table25);
               _page2.labels.Add(new PPage.PLabel("Забрать возвраты " , new Point(10, 550), 24));

            }

            #endregion

            PPages.Add(_page2);
            
            #endregion

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {
                
                pd.DefaultPageSettings.Landscape = true;
                if( pd.DefaultPageSettings.PrinterSettings.CanDuplex )
                pd.DefaultPageSettings.PrinterSettings.Duplex = Duplex.Horizontal;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion






            // Печать маршрутного листа ==================================================
        }

        private void назначитьВодителяToolStripMenuItem_Click(object sender, EventArgs e)
        {

            DataGridViewRow dr = dataGridView17.CurrentRow;
            if (dr == null)
            {
                MessageBox.Show(" Не выбран маршрут ");
            }

            if (!has_right("CHANGE_VODITEL"))
            {

                MessageBox.Show("Нет прав на изменение транспорта");
                return;
            }

            VODITEL ftr = new VODITEL();
            ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            ftr.Filter_FIO = dr.Cells[9].Value.ToString();
            ftr.ShowDialog();

            if (ftr.CHOOSE_ID > 0)
            {
                if (ftr.CHOOSE != null)
                    if (ftr.CHOOSE!="")
                {
                    dr.Cells[9].Value = ftr.CHOOSE;
                    dr.Cells[10].Value = ftr.CHOOSE_ID;

                    dataGridView17_CellEndEdit(null, null);
                }
            }

        }

        private void dataGrid_pallets_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            // EXPIRY_DATE
            DateTime o= Convert.ToDateTime( dataGrid_pallets.CurrentRow.Cells[4].Value ) ;
            string PALLET_ID = dataGrid_pallets.CurrentRow.Cells[0].Value.ToString();
            if (o != null)
            {
                
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = " update RABAEV.RRL_PALLETS set EXPIRY_DATE = " + date2sql_ora(o) + " where UID_PALLET='"+PALLET_ID+"' ";
                ora_com.ExecuteNonQuery();

            }

        }

        private void button47_Click(object sender, EventArgs e)
        {
            foreach( DataGridViewRow dr in dataGridView11.Rows )
            {
                dr.Cells[5].Value = true;
            }

        }

        private void button48_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView11.Rows)
            {
                if (dr.Cells[0].Value != null)
                {
                    string art = dr.Cells[0].Value.ToString();
                    if (Convert.ToBoolean(dr.Cells[5].Value))
                    {
                        SyncArticul(art, wms_user.ware_id);
                        dr.Cells[5].Value = false;
                    }
                    
                }

            }

            button20_Click(null,null);
            MessageBox.Show("Процедура окончена");

        }

        private void Наим_Click(object sender, EventArgs e)
        {

        }

        private void button49_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView11);
        }

        private void dataGridView11_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            try
            {
                long vl = Convert.ToInt64(dataGridView11.CurrentRow.Cells[2].Value);
                string artic7 = Convert.ToString(dataGridView11.CurrentRow.Cells[0].Value);

                string bk_sht = Convert.ToString(dataGridView11.CurrentRow.Cells[6].Value);
                string bk_bl = Convert.ToString(dataGridView11.CurrentRow.Cells[7].Value);
                string bk_kor = Convert.ToString(dataGridView11.CurrentRow.Cells[8].Value);
                long Штук_в_коробке = 1;
                try
                {
                    Штук_в_коробке = Convert.ToInt64(dataGridView11.CurrentRow.Cells[10].Value);
                }
                catch { }
                long Штук_в_блоке = Convert.ToInt64(dataGridView11.CurrentRow.Cells[11].Value);

                double вес_картона = 0;
                try
                {
                    вес_картона = Convert.ToDouble(dataGridView11.CurrentRow.Cells[12].Value.ToString().Replace('.', ','));
                }
                catch { }

                int BESTBEFOREDAYS = 360;
                int etaj_limit = 100;
                
                try
                {
                    etaj_limit = Convert.ToInt32(dataGridView11.CurrentRow.Cells[13].Value.ToString() );
                }
                catch { }

                try
                {
                    BESTBEFOREDAYS = Convert.ToInt32(dataGridView11.CurrentRow.Cells[14].Value.ToString());
                }
                catch { }



                try
                {
                    
                     
                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "update  RABAEV.RRL_ARTICULS set   CARTON_WEIGHT  = " + вес_картона.ToString() +
                        " ,  NORMA_UKLADKI=" + Convert.ToString(vl) +
                        " , BARCODE_SHT='" + bk_sht + "' , BARCODE_BL='" + bk_bl + "' , BARCODE_KOR='" + bk_kor +
                        "' ,COUNT_SHT_IN_KOR=" + Штук_в_коробке.ToString() + " , COUNT_SHT_IN_BL=" + Штук_в_блоке.ToString() + " , etaj_limit=" + etaj_limit.ToString() + " , BESTBEFOREDAYS= " + BESTBEFOREDAYS.ToString() +
                        " where ACTICUL='" + artic7 + "' ";

                    ora_com.CommandType = CommandType.Text;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void label37_Click(object sender, EventArgs e)
        {

        }

        public object[] ShowQuery(string strSQL , string ZAGOLOVOK)
        {
            ЗАПРОСЫ ftr = new ЗАПРОСЫ();
            ftr.sSQL = strSQL;
            ftr.Header_Text = ZAGOLOVOK;
            ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            ftr.ShowDialog();
            return ftr.CHOOSE;
        }

        public object[] ShowQuery(string strSQL, string ZAGOLOVOK , Point p)
        {
            ЗАПРОСЫ ftr = new ЗАПРОСЫ();
            ftr.sSQL = strSQL;
            ftr.Header_Text = ZAGOLOVOK;
            ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            ftr.Default_cell = p;
            ftr.ShowDialog();
            return ftr.CHOOSE;
        }

        private void Контроль_Click(object sender, EventArgs e)
        {
         
            DateTime yesterd = DateTime.Today;
            yesterd = yesterd.AddDays(-1);
            object[] o= ShowQuery(" "+
            " select ST_NUMBER СТ , P.PALLET_UID ПАЛЛЕТ , RRL_PAL_VOLUME( P.PALLET_UID ) ОБЪЕМ ,  RRL_PAL_WEIGHT( P.PALLET_UID ) ВЕС , RRL_SKLADNAME_BY_ID(P.WARE_ID) СКЛАД  " +
            " from RRL_SBORKA_PALLETS P where STDATE>to_date( " + date2sql_ora(yesterd) + " , 'dd.mm.yyyy' )  and " +
            " ( RRL_PAL_VOLUME( P.PALLET_UID )<20000) and (RRL_PAL_WEIGHT( P.PALLET_UID )<100) and RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'ПРОМ' , 'АЛКО' ) " , 
            "ПАЛЛЕТЫ С НЕНОРМАЛЬНЫМ ВЕСОМ И ОБЪЕМОМ");

            if (o.Length > 0)
            {
                string st_numb = o[0].ToString();
                НомерСТКПодгрузке.Text = st_numb;
                button34_Click(null, null);

            }
        }

        private void button50_Click(object sender, EventArgs e)
        {

            DateTime yesterd = DateTime.Today;
            yesterd = yesterd.AddDays(-1);
            object[] o = ShowQuery(" select distinct ARTICUL , SHORTNAME from RRL_SBORKA_PALLET_ROWS where PALLET_UID in ( " +
            " select  P.PALLET_UID ПАЛЛЕТ  " +
            " from RRL_SBORKA_PALLETS P where STDATE>to_date( " + date2sql_ora(yesterd) + " , 'dd.mm.yyyy' )  and " +
            " ( RRL_PAL_VOLUME( P.PALLET_UID )<20000) and (RRL_PAL_WEIGHT( P.PALLET_UID )<100) and RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'ПРОМ' , 'АЛКО' ) ) ",
            "ТОВАРЫ В ПАЛЛЕТАХ С НЕНОРМАЛЬНЫМ ВЕСОМ И ОБЪЕМОМ");

        }

        private void button51_Click(object sender, EventArgs e)
        {


            try
            {

                DataGridViewRow dr = dataGridView17.CurrentRow;
                if ((dr != null) && (dr.Cells[1].Value != null))
                {
                    string TT = dr.Cells[1].Value.ToString();
                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RRL_TT_DROP";
                    ora_com.CommandType = CommandType.StoredProcedure;
                    ora_com.Parameters.Add("IDTT", OracleType.Int32).Value =  Convert.ToInt32( TT);
                    ora_com.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();

                    dataGridView17.Rows.Remove(dr);
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            button36_Click(null, null);

            //dateTimePicker4_ValueChanged(null, null);
        }

        private void dataGridView18_DoubleClick(object sender, EventArgs e)
        {
            
            if ( (dataGridView18.CurrentCell!=null) && (dataGridView18.CurrentCell.ColumnIndex==7) )
            {
                string stn = dataGridView18.CurrentCell.Value.ToString();
                НомерСТКПодгрузке.Text = stn;
                button34_Click(null, null);

            }
        }

        private void button52_Click(object sender, EventArgs e)
        {
            int x=10 , y=20;
            int dec=100;
            PPage _page = new PPage();
            foreach (DataGridViewRow dr in dataGridView11.Rows)
            {
                if (dr.Cells[0].Value != null)
                {
                    string art = dr.Cells[0].Value.ToString();
                    string name = dr.Cells[1].Value.ToString();
                    if (Convert.ToBoolean(dr.Cells[5].Value))
                    {

                        _page.labels.Add(new PPage.PLabel("" + name, new Point(x, y-14), 12, "text"));

                        _page.labels.Add(new PPage.PLabel(""+art, new Point(x, y), 12, "text"));
                        _page.labels.Add(new PPage.PLabel("" + dr.Cells[6].Value.ToString(), new Point(x+100, y), 12, "EAN" , 250 ,50 ));
                        if (dr.Cells[7].Value.ToString()!="")
                        _page.labels.Add(new PPage.PLabel("" + dr.Cells[7].Value.ToString(), new Point(x+ 350 , y), 12, "EAN", 250, 50));
                        _page.labels.Add(new PPage.PLabel("" + dr.Cells[8].Value.ToString(), new Point(x+ 600 , y), 12, "EAN", 250, 50));  
                        y=y+dec;
                    }

                }

            }

            PPages.Add(_page);
            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {

                pd.DefaultPageSettings.Landscape = true;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f46 " + ex.Message);
            }
            #endregion


        }

        private void button53_Click(object sender, EventArgs e)
        {



            string str2 = "";
            if (Фильтр_ячеек.Text != "")
            {
                str2 = " and cell like '" + Фильтр_ячеек.Text + "' ";
            }

            string strSQL = " select  " +
           "    'false' , CELL , int2bool( OTBOR ) , X , Y , Z  , int2bool( BLOCKED_FOR_ACCEPT ) "+
           " , int2bool( BLOCKED_FOR_REMAINS ) ,  int2bool( BLOCKED_FOR_POPOLNENIE ) , RRL_SKLADNAME_BY_ID( ware_id ) , RRL_INFO_CELL_RESTS( CELL ) " +
           "  ,  LIMIT_WEIGHT ,  LIMIT_HEIGHT " +
           " from RABAEV.RRL_CELLS    " +
           " where ware_id=" + this.wms_user.ware_id + " " + str2 + " order by z  ,x , y  ";

            fill_view_MINI_WMS(dataGridView8, strSQL, 13 );




        }

        private void button54_Click(object sender, EventArgs e)
        {
            
            grid_2_excel(dataGridView8);

        }

        private void dataGridView8_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {
            if (e == null) return;
            if (e.RowIndex < 0)
                return;
            if (e.ColumnIndex == 0)
                return;
           DataGridViewRow dr= dataGridView8.Rows[e.RowIndex];
           if (dataGridView8.CurrentRow == null)
           {
               return;
           }
           string cell = dr.Cells[1].Value.ToString();
           int otbor = 0;
           int BLOCKED_FOR_ACCEPT = 0;
           int BLOCKED_FOR_REMAINS = 0;
           int BLOCKED_FOR_POPOLNENIE = 0;

           if ( Convert.ToBoolean(dr.Cells[2].Value) )
           {
               otbor = 1;
           }

            int X = Convert.ToInt32( dr.Cells[3].Value );
            int Y = Convert.ToInt32(dr.Cells[4].Value);
            int Z = Convert.ToInt32(dr.Cells[5].Value);


            if ( Convert.ToBoolean (dr.Cells[6].Value))
            { BLOCKED_FOR_ACCEPT = 1; }

            if (Convert.ToBoolean(dr.Cells[7].Value))
            { BLOCKED_FOR_REMAINS = 1; }

            if (Convert.ToBoolean(dr.Cells[8].Value))
            { BLOCKED_FOR_POPOLNENIE = 1; }

            // BLOCKED_FOR_ACCEPT
            // BLOCKED_FOR_REMAINS
            // BLOCKED_FOR_POPOLNENIE
            /*
CREATE TABLE RABAEV.RRL_CELLS
(
CELL                    VARCHAR2(15 CHAR),
OTBOR                   INTEGER               DEFAULT 0,
BLOCKED_FOR_REMAINS     INTEGER               DEFAULT 0,
BLOCKED_FOR_POPOLNENIE  INTEGER               DEFAULT 0,
UID_POLETA_FOR_BLOCK    VARCHAR2(50 CHAR),
TIME_FOR_BLOCK          DATE,
X                       INTEGER               DEFAULT 10000                 NOT NULL,
Y                       INTEGER               DEFAULT 10000                 NOT NULL,
Z                       INTEGER               DEFAULT 10000                 NOT NULL,
BLOCKED_FOR_ACCEPT      INTEGER               DEFAULT 0,
WARE_ID                 INTEGER               DEFAULT 1
)

*/

            string strSQL = " update RRL_CELLS set OTBOR="+otbor.ToString()+" , X="+X.ToString()
                + " , Y=" + Y.ToString() + " , Z=" + Z.ToString() + " , BLOCKED_FOR_REMAINS=" + BLOCKED_FOR_REMAINS.ToString()+
                " , BLOCKED_FOR_POPOLNENIE=" + BLOCKED_FOR_POPOLNENIE.ToString() + " , BLOCKED_FOR_ACCEPT=" + BLOCKED_FOR_ACCEPT.ToString() + "  where CELL='" + cell + "'  ";

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL;
            ora_com.ExecuteNonQuery();


        }

        private void button55_Click(object sender, EventArgs e)
        {
            long pos = 2;
           
           // try
           // {
                //Excel Application Object
                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();
                string Filename = "C:\\wms\\cells.xls";
                MessageBox.Show(" Подгрузка из файла C:\\wms\\cells.xls справочника ячеек. \n Формат: 2 ячейка=CELL , 4=X 5=Y 6=Z ;  ");

                oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);


                while (((Excel.Range)oExcelApp.Cells[pos, 4]).Value2  != null )
                {

                    string cell4 = ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString();
                    
                    long X = str2int(((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString());
                    long Y = str2int(((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString());
                    long Z = str2int(((Excel.Range)oExcelApp.Cells[pos, 6]).Value2.ToString());
                   
                    


                    // ================================================================

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();

                    ora_com.CommandText = "RABAEV.RRL_UPDATE_CELL";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("cell4", OracleType.VarChar).Value = cell4;
                    ora_com.Parameters.Add("Z1", OracleType.Int32).Value = Z;
                    ora_com.Parameters.Add("Y1", OracleType.Int32).Value = Y;
                    ora_com.Parameters.Add("X1", OracleType.Int32).Value = X;
                    ora_com.Parameters.Add("ware_id4", OracleType.Int32).Value = this.wms_user.ware_id;

                    ora_com.Parameters.Add("tmpVar", OracleType.Int32 ).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                    // ================================================================
                    pos++;
                }
                MessageBox.Show("Данные выгружены в Excel");
           // }
           // catch (Exception ex)
           // {
           //     MessageBox.Show(Convert.ToString(pos) + " _ " + ex.Message);
           // }
            // ================================
        }

        private void button56_Click(object sender, EventArgs e)
        {
            if (dataGridView8.CurrentRow == null)
                return;
            try
            {
                string cell4 = dataGridView8.CurrentRow.Cells[1].Value.ToString();


                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();

                ora_com.CommandText = "RABAEV.RRL_DELETE_CELL";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("cell4", OracleType.VarChar).Value = cell4;
                ora_com.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
                string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();

                dataGridView8.Rows.Remove(dataGridView8.CurrentRow);

            }catch( Exception ex )
            {
                MessageBox.Show(ex.Message);
            }


        }

        private void button58_Click(object sender, EventArgs e)
        {

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_SYNC_ADDR";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("dummy", OracleType.Int32 ).Value = 1;
                ora_com.Parameters.Add("ID1", OracleType.Int32).Direction = ParameterDirection.ReturnValue;

                int rowsAffected = ora_com.ExecuteNonQuery();
                long ret2 = Convert.ToInt64(ora_com.Parameters["ID1"].Value.ToString());
            
                if( ret2>0 )
                {
                    MessageBox.Show("Добавлено адресов: "+ret2.ToString());
                }

        }

        private void button59_Click(object sender, EventArgs e)
        {


            string strSQL = " select ADDR , NAPR, RAION, REGION , ORD , TRANSPORT_TYPE , PRIM1 , int2bool( stol ) "+
                " , dolgota , shirota from RABAEV.RRL_ADDR order by ord ";
            fill_view_MINI_WMS(dataGridView19, strSQL, 10 );

        }

        private void dataGridView19_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            try
            {
                DataGridViewRow dr = dataGridView19.CurrentRow;
                if (dr == null) return;
                string raion = dr.Cells[2].Value.ToString();
                string region = dr.Cells[3].Value.ToString();
                string ADDR = dr.Cells[0].Value.ToString();
                string ORD = dr.Cells[4].Value.ToString();
                string TRANSPORT_TYPE = dr.Cells[5].Value.ToString();
                string   PRIM1 = dr.Cells[6].Value.ToString();
                long stol = 0;
                try
                {
                    if (Convert.ToInt32(dr.Cells[7].Value)==1)
                    {
                        stol = 1;
                    }
                }
                catch { }

                double dolgota =  obj2double (dr.Cells[8].Value );
                double shirota = obj2double(dr.Cells[9].Value );

                string strSQL = " update RRL_ADDR set TRANSPORT_TYPE='" + TRANSPORT_TYPE + "' , RAION = '" + raion +
                    "', REGION = '" + region + "' , ORD=" + ORD + " , PRIM1 = '" + PRIM1 +"' "+
                    " , stol=" + stol.ToString() + " , dolgota=" + (dolgota.ToString().Replace(',', '.')) + " , shirota=" + (shirota.ToString().Replace(',', '.')) + " " +
                    " where addr='" + ADDR + "'  ";
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = strSQL;
                ora_com.ExecuteNonQuery();

            }catch( Exception ex )
            {
                MessageBox.Show(ex.Message);
            }

        }

        private void button57_Click(object sender, EventArgs e)
        {
            // БЕЖИМ ПО ВСЕМ ЯЧЕЙКАМ И ПЕЧАТАЕМ ПАСПОРТА НА ПАЛЛЕТЫ

            int pos = 1;

            Point[] points= new Point[11];

            int hjk = 112;
            int pos1 = 1;
            int oy = -95;

            points[pos1].X = 0;
            points[pos1].Y = pos1 * hjk + oy;
            pos1++;

            points[pos1].X = 400;
            points[pos1].Y = (pos1 - 1) * hjk + oy;
            pos1++;


            points[pos1].X = 0;
            points[pos1].Y = pos1 * hjk + oy;
            pos1++;

            points[pos1].X = 400;
            points[pos1].Y = (pos1 - 1) * hjk + oy;
            pos1++;


            points[pos1].X = 0;
            points[pos1].Y = pos1 * hjk + oy;
            pos1++;

            points[pos1].X = 400;
            points[pos1].Y = (pos1 - 1) * hjk + oy;
            pos1++;


            points[pos1].X = 0;
            points[pos1].Y = pos1 * hjk + oy;
            pos1++;

            points[pos1].X = 400;
            points[pos1].Y = (pos1 - 1) * hjk + oy;
            pos1++;



            points[pos1].X = 0;
            points[pos1].Y = pos1 * hjk + oy;
            pos1++;

            points[pos1].X = 400;
            points[pos1].Y = (pos1 - 1) * hjk + oy;
            pos1++;


            PPage _p = new PPage();
            this.PPages.Add(_p);
            
            foreach (DataGridViewRow dr in dataGridView8.Rows)
            {
                if ( Convert.ToBoolean( dr.Cells[0].Value) )
                {
                    string cell = dr.Cells[1].Value.ToString();
                    bool otborr = Convert.ToBoolean(dr.Cells[2].Value);

                    if (!otborr)
                    {
                        PPages[PPages.Count - 1].labels.Add(new PPage.PLabel(cell, points[pos], 12, "EAN2", 600, 150));
                        PPages[PPages.Count - 1].labels.Add(new PPage.PLabel(cell, (new Point(70 + points[pos].X, 155 + points[pos].Y)), 36, "text"));
                    }
                    else { 
                        PPages[PPages.Count - 1].labels.Add(new PPage.PLabel(cell, points[pos], 12, "EAN2", 600, 150));
                        PPages[PPages.Count - 1].labels.Add(new PPage.PLabel(cell, (new Point(20 + points[pos].X, 155 + points[pos].Y)), 36, "text"));
                        PPages[PPages.Count - 1].labels.Add(new PPage.PLabel("   ОТБ", (new Point(170 + points[pos].X, 155 + points[pos].Y)), 36, "text"));
                    
                    }

                    if (pos == 10)
                    {
                        pos = 0;
                        PPage _p1 = new PPage();
                        this.PPages.Add(_p1);
                    }
                    pos++;
                }
            }

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {

                pd.DefaultPageSettings.Landscape = false;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f49 " + ex.Message);
            }
            #endregion


        }

        private void button60_Click(object sender, EventArgs e)
        {
            foreach (DataGridViewRow dr in dataGridView8.Rows)
            {

                dr.Cells[0].Value = true;
            
            }

        }

        private void button61_Click(object sender, EventArgs e)
        {
            grid_2_excel(dataGridView19);
        }

        private void button62_Click(object sender, EventArgs e)
        {

            DateTime yesterd = dateTimePicker6.Value;
            DateTime afterday = dateTimePicker7.Value;

            object[] o = ShowQuery(" " +
            " select ST_NUMBER СТ , P.PALLET_UID ПАЛЛЕТ , RRL_SKLADNAME_BY_ID(P.WARE_ID) СКЛАД , " +
            " PROOVED КОНТРОЛЬ , TRIAL_WEIGHT ВЕС_НА_1_ВЕСАХ , ( RRL_PAL_WEIGHT( P.PALLET_UID )+WOOD_WEIGHT) ПЛАНОВЫЙ_ВЕС , "+
            " round ( TRIAL_WEIGHT - ( RRL_PAL_WEIGHT( P.PALLET_UID )+WOOD_WEIGHT) ,0 ) РАЗНИЦА , WOOD_WEIGHT ВЕС_ПОДДОНА , ADDR Адрес, RRL_GET_PALLET_CHECK_TIMES(P.PALLET_UID) история   " +
            " , prim , VESOVSHIK from RRL_SBORKA_PALLETS P where STDATE>=to_date( " + date2sql_ora(yesterd) + " , 'dd.mm.yyyy' ) and   STDATE<=to_date( " + date2sql_ora(afterday) + " , 'dd.mm.yyyy' )    and " +
            "   RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'ПРОМ' , 'АЛКО' , 'ХОЛОД' , 'ПИВО' ) and ( ( PROOVED=0 )   or ( RRL_is_PALLET_like_fake(P.PALLET_UID)=1 ) )  and WOOD_WEIGHT>0 ",
            " ПАЛЛЕТЫ, НЕ ПРОШЕДШИЕ ВЕСОВОЙ КОНТРОЛЬ ");

        }

        private void своднаяПоСТToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string add_sql1 = "";
            string add_sql2 = "";
            string add_sql3 = "";
            string add_sql4 = "";
            string add_sql5 = "";

            m_map_V = 0;
            m_map_WEIGHT = 0;
            m_map_P = 0;

            if (МаскаСТ.Text != "")
            {
                add_sql4 = " and ( P.ST_NUMBER like '%" + МаскаСТ.Text + "%' ) ";

            }

            if (МаскаСкладов.Text != "")
            {
                add_sql1 = " and ( RRL_SKLADNAME_BY_ID( P.ware_id ) in ( " + МаскаСкладов.Text + " )) ";
            }

            if (МаскаАдреса.Text != "")
            {
                add_sql2 = " and ( P.ADDR like '%" + МаскаАдреса.Text + "%' ) ";
            }

            if (НЕ_РАСПРЕДЕЛЕННЫЕ.Checked)
            {
                add_sql3 = " and ( ( TRANSTASK_ID is null ) or (  TRANSTASK_ID=0 ) ) ";
            }

            if (датаСТУч.Checked)
            {
                add_sql5 = " and ( P.STDATE = " + date2sql_ora(dateTimePicker5.Value) + " ) ";
            }

            string strSQL = " select   " +
                " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , "+
                " round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  count( R.ID ) строки  ,  " +
                "  RRL_ADDR.REGION , " +
                "  RRL_ADDR.RAION , RRL_ADDR.TRANSPORT_TYPE  " +
                " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R  , rrl_addr  where " +
                " R.PALLET_UID=P.PALLET_UID  and  ( P.ADDR=RRL_ADDR.ADDR(+) )  " + add_sql1 + add_sql2 + add_sql3 + add_sql4 + add_sql5 +
                "group by          RRL_ADDR.REGION , RRL_ADDR.TRANSPORT_TYPE ,  RRL_ADDR.RAION  ,  P.STDATE  " +
                " order by RRL_ADDR.REGION  ,  RRL_ADDR.RAION  , RRL_ADDR.TRANSPORT_TYPE  ";
            ShowQuery(strSQL, "СВОДНАЯ ПО СТ ЗА " + dateTimePicker5.Value.ToString());




        }

        private void своднаяПоПаллетамToolStripMenuItem_Click(object sender, EventArgs e)
        {
            //    (sum( RRL_TT_PALLETS(T.ID)) / count( T.ID )) ПАЛЛ_НА_МАРШРУТ   , 
            string strSQL = " select  sum( RRL_TT_PALLETS(T.ID)) ПАЛЛЕТЫ , count( T.ID ) МАРШРУТЫ ,   round(  SUM (rrl_tt_pallets (t.ID))  / COUNT (t.ID) , 2 ) ПАЛЛ_НА_МАРШРУТ ,   round( sum( RRL_TT_WEIGHT(T.ID)) , 0 ) ВЕС  , " +
            " round( sum( RRL_TT_VOLUME(T.ID) ) /1000000, 1 ) ОБЪЕМ  " +
            " from RRL_TRANSPORT_TASK  T  where   " +
            " SHIPMENT_DATE = " + date2sql_ora(dateTimePicker4.Value) + " and deleted<>1 group by SHIPMENT_DATE ";

            ShowQuery(strSQL, "СВОДНАЯ ПО МАРШРУТАМ " + dateTimePicker5.Value.ToString());
        }

        private void отчетОбИспользованииТранспортаToolStripMenuItem_Click(object sender, EventArgs e)
        {

            DateTime td = DateTime.Today;
            DateTime tomorrow = DateTime.Today.AddDays(1);
            DateTime yesterday = DateTime.Today.AddDays(-1);
            DateTime yesterday1 = DateTime.Today.AddDays(-2);

            string strSQL = "select NUM , MARKA , TR_TYPE , REF_REJIM , PALLETS , " +
                " RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(yesterday1) + " ) РЕЙСЫ_Позавчера , " +
                " RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(yesterday) + " ) РЕЙСЫ_Вчера , " +
                "  RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(td) + " ) РЕЙСЫ_Сегодня  , " +
                "  RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(tomorrow) + " ) РЕЙСЫ_Завтра  , " +
                " DOVERENNOST_OT Компания  , TEL Телефон , F Фамилия , I Имя , O  Отчество , SOBSTVENNYY  " +
                " from RABAEV.RRL_TR_VEHICLE , RABAEV.RRL_TR_VODITEL  " +
            " where working_now=1 and RRL_TR_VEHICLE.NUM=RRL_TR_VODITEL.TRANSPORT_NUM(+)  " +
            " order by tr_type";

            ShowQuery(strSQL, "Отчет об использовании транспорта " + dateTimePicker5.Value.ToString());
        }

        private void оТчетToolStripMenuItem_Click(object sender, EventArgs e)
        {
            DateTime td = DateTime.Today;
            DateTime tomorrow = DateTime.Today.AddDays(1);
            DateTime yesterday = DateTime.Today.AddDays(-1);
            DateTime yesterday1 = DateTime.Today.AddDays(-2);

            string strSQL = "select NUM , MARKA , TR_TYPE , REF_REJIM , PALLETS , " +
                " RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(yesterday1) + " ) РЕЙСЫ_Позавчера , " +
                " RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(yesterday) + " ) РЕЙСЫ_Вчера , " +
                "  RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(td) + " ) РЕЙСЫ_Сегодня  , " +
                "  RRL_VEHICLE_REIS_COUNT(NUM, " + date2sql_ora(tomorrow) + " ) РЕЙСЫ_Завтра  , " +
                " DOVERENNOST_OT Компания  , TEL Телефон , F Фамилия , I Имя , O  Отчество , SOBSTVENNYY  " +
                " from RABAEV.RRL_TR_VEHICLE , RABAEV.RRL_TR_VODITEL  " +
            " where working_now=1 and RRL_TR_VEHICLE.NUM=RRL_TR_VODITEL.TRANSPORT_NUM(+) and tr_type like '15%'  " +
            " order by tr_type";

            ShowQuery(strSQL, "Отчет об использовании 15-тонников " + dateTimePicker5.Value.ToString());
        }

        private void button63_Click(object sender, EventArgs e)
        {


            DateTime yesterd = dateTimePicker6.Value;
            DateTime afterday = dateTimePicker7.Value;


            object[] o = ShowQuery(" select Количество , ARTICUL , SHORTNAME from ( " +
            " select count(ID) Количество , ARTICUL , SHORTNAME "+
            " from  RABAEV.RRL_SBORKA_PALLET_ROWS where RRL_SBORKA_PALLET_ROWS.PALLET_UID in  "+
            " ( select  P.PALLET_UID   " +
            " from RRL_SBORKA_PALLETS P where STDATE>=to_date( " + date2sql_ora(yesterd) + " , 'dd.mm.yyyy' )  and STDATE<=to_date( " + date2sql_ora(afterday) + " , 'dd.mm.yyyy' )    and " +
            "   RRL_SKLADNAME_BY_ID(P.WARE_ID) in ( 'МЕЗ' , 'СУХОЙ' , 'ПРОМ' ) and ( ( PROOVED=0 )   or ( RRL_is_PALLET_like_fake(P.PALLET_UID)=1 ) ) "+
            " and WOOD_WEIGHT>0 ) group by  ARTICUL , SHORTNAME ) order by Количество DESC ",
            " ТОВАР В ПАЛЛЕТАХ, НЕ ПРОШЕДШИХ ВЕСОВОЙ КОНТРОЛЬ ");


        }

        private void отчетОбИспользованииТранспортаToolStripMenuItem1_Click(object sender, EventArgs e)
        {

        }

        private void списокМаршрутовВExcelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            
            grid_2_excel( dataGridView17 );

        }

        private void историяСтToolStripMenuItem_Click(object sender, EventArgs e)
        {
            DataGridViewRow dr = dataGridView18.CurrentRow;
            if( dr==null )
            {
                return;
            }

            string st=dr.Cells[7].Value.ToString();

            if (st.Split('#').Length > 1)
            {
                st = st.Split('#').GetValue(0).ToString();
            }

            object[] o = ShowQuery("select  PALLET_UID , USER_ID ,ZONE , EVENT , TIME1 " +
                ",WEIGHT from RABAEV.RRL_SBORKA_PALLETS_HISTORY where PALLET_UID like '%" + st + "%' order by PALLET_UID , TIME1 ", "ИСТОРИЯ ПАЛЛЕТ ПО СТ ");
 
        }

        public bool has_right(string WRIGHT)
        {

            if (this.wms_user.USER_GROUP == "GLOBAL_ADMIN")
            {
                return true;
            }


            try
            {
                if (WRIGHT_CACHE.ContainsKey(WRIGHT))
                    return WRIGHT_CACHE[WRIGHT];

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                // RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )
                ora_com.CommandText = "RABAEV.RRL_HAS_WRIGHT";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("user_id", OracleType.VarChar).Value = this.wms_user.user_id;
                ora_com.Parameters.Add("wright_name", OracleType.VarChar).Value = WRIGHT;

                ora_com.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
                string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                if (tmpVar == "1")
                {
                    WRIGHT_CACHE[WRIGHT] = true;
                    return true;
                }

                WRIGHT_CACHE[WRIGHT] = false;
                return false;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return false;
            }

        }

        private void Маршруты_Click(object sender, EventArgs e)
        {

        }




        private void добавитьВМаршрутЗавтрашнегоДняToolStripMenuItem_Click(object sender, EventArgs e)
        {
            DateTime dt = dateTimePicker5.Value ;
            dt = dt.AddDays(1);

            string strSQL = " select  T.ID , T.TRANSPORT ,  RRL_TT_VODITEL_INFO(T.VODITEL_ID),  RRL_TT_PALLETS(T.ID), round( RRL_TT_WEIGHT(T.ID) , 0 )  , " +
            " round( RRL_TT_VOLUME(T.ID)/1000000, 1 ), T.TRANSTYPE    " +
            " ,   RRL_TT_REGIONS( T.ID)" +
            " from RRL_TRANSPORT_TASK  T  where   " +
            " SHIPMENT_DATE = " + date2sql_ora( dt ) + " and deleted<>1 ";

            object[] o= ShowQuery( strSQL , "Выберите маршрут от "+dt.ToLongDateString() );
            if( o!=null )
                if (o.Length != 0)
                {



                    #region ДОБАВЛЕНИЕ ЗАЯВОК В ТЕКУЩИЙ МАРШРУТ

                        m_map_P = 0;
                        m_map_V = 0;
                        m_map_WEIGHT = 0;

                        OracleCommand ora_comm = new OracleCommand();
                        ora_comm.Connection = get_wms_connection();


                        string TT_ID = o[0].ToString();
                        if (!(Convert.ToInt64(TT_ID) > 0))
                        {
                            MessageBox.Show("Не выбран текущий маршрут");
                            return;
                        }

                        List<DataGridViewRow> ldr = new List<DataGridViewRow>();
                        foreach (DataGridViewRow dr in dataGridView18.Rows)
                        {
                            if (Convert.ToBoolean(dr.Cells[0].Value) == true)
                            {
                                string PUID = dr.Cells[7].Value.ToString();
                                //Добавляем СТ в маршрут
                                string strSQL2 = " update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID = " + TT_ID +
                                    " where ST_NUMBER='" + PUID + "' ";
                                ora_comm.CommandText = strSQL2;
                                ora_comm.ExecuteNonQuery();
                                ldr.Add(dr);
                            }
                        }

                        foreach (DataGridViewRow dr2 in ldr)
                        {
                            dataGridView18.Rows.Remove(dr2);
                        }

                    #endregion



                }


        }

        private void change_selection(Label label1, DataGridView dataGridView1)
        {

            Dictionary<string, double> vals = new Dictionary<string, double>();

            foreach (DataGridViewRow dr in dataGridView1.Rows)
            {
                for (int i = 0; i < dataGridView1.ColumnCount; i++)
                {
                    if (dr.Cells[i].Selected)
                    {
                        try
                        {
                            vals[dr.Cells[i].OwningColumn.HeaderText] = vals[dr.Cells[i].OwningColumn.HeaderText] + Convert.ToDouble(dr.Cells[i].Value);
                        }
                        catch (Exception ex)
                        {
                            try
                            {
                                vals[dr.Cells[i].OwningColumn.HeaderText] = 0 + Convert.ToDouble(dr.Cells[i].Value);
                            }
                            catch (Exception ex2)
                            {
                                vals[dr.Cells[i].OwningColumn.HeaderText] = 0;
                            }
                        }
                    }

                }

            }
            label1.Text = "";
            foreach (string key in vals.Keys)
            {
                label1.Text = label1.Text + key + " = " + vals[key].ToString() + ";";
            }

        
        }

        private void dataGridView18_SelectionChanged(object sender, EventArgs e)
        {
            if( m_stop_selection_event )
            {
                return;
            }

            if (dataGridView18.CurrentCell != null)
            { // ЕСЛИ ВЫДЕЛЕН АДРЕС, ТО ИЩЕМ ВСЕ СТРОКИ С ДАННЫМ АДРЕСОМ И ВЫДЕЛЯЕМ ИХ 
                m_stop_selection_event = true;
                if(dataGridView18.CurrentCell.ColumnIndex == 6)
                {
                    
                    bool is_selected = dataGridView18.CurrentCell.Selected;
                    string adr = dataGridView18.CurrentCell.Value.ToString();
                    foreach (DataGridViewRow dr in dataGridView18.Rows)
                    {
                        if (dr.Cells[6].Value.ToString()== adr )
                        {
                            dr.Cells[2].Selected = is_selected;
                            dr.Cells[3].Selected = is_selected;
                            dr.Cells[4].Selected = is_selected;
                        }
                    }
                }

                if (dataGridView18.CurrentCell.ColumnIndex == 5)
                {

                    bool is_selected = dataGridView18.CurrentCell.Selected;
                    string adr = dataGridView18.CurrentCell.Value.ToString();
                    foreach (DataGridViewRow dr in dataGridView18.Rows)
                    {
                        if (dr.Cells[5].Value.ToString() == adr)
                        {
                            dr.Cells[2].Selected = is_selected;
                            dr.Cells[3].Selected = is_selected;
                            dr.Cells[4].Selected = is_selected;
                        }
                    }
                }

                if (dataGridView18.CurrentCell.ColumnIndex == 8)
                {

                    bool is_selected = dataGridView18.CurrentCell.Selected;
                    string adr = dataGridView18.CurrentCell.Value.ToString();
                    foreach (DataGridViewRow dr in dataGridView18.Rows)
                    {
                        if (dr.Cells[8].Value.ToString() == adr)
                        {
                            dr.Cells[2].Selected = is_selected;
                            dr.Cells[3].Selected = is_selected;
                            dr.Cells[4].Selected = is_selected;
                        }
                    }
                }

                if (dataGridView18.CurrentCell.ColumnIndex == 12)
                {

                    bool is_selected = dataGridView18.CurrentCell.Selected;
                    string adr = dataGridView18.CurrentCell.Value.ToString();
                    foreach (DataGridViewRow dr in dataGridView18.Rows)
                    {
                        if (dr.Cells[12].Value.ToString() == adr)
                        {
                            dr.Cells[2].Selected = is_selected;
                            dr.Cells[3].Selected = is_selected;
                            dr.Cells[4].Selected = is_selected;
                        }
                    }
                }

                m_stop_selection_event = false;
            }

             change_selection( label49 , dataGridView18  );

        }

        private void dataGridView17_SelectionChanged(object sender, EventArgs e)
        {
            change_selection(label49, dataGridView17);
        }



        private void создатьМаршрутВЗавтрашнемДнеToolStripMenuItem_Click(object sender, EventArgs e)
        {
             button35_Click(null, null);
        }

        private void button64_Click(object sender, EventArgs e)
        {

            try
            {
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                DataGridViewRow dr = dataGridView18.CurrentRow;
                if (dr == null)
                    return;
                string PUID = dr.Cells[7].Value.ToString();
                //Добавляем СТ в маршрут
                /*string strSQL2 = " update RABAEV.RRL_SBORKA_PALLETS set  TRANSTASK_ID = NULL " +
                    " where ST_NUMBER='" + PUID + "' ";
                ora_comm.CommandText = strSQL2;
                ora_comm.ExecuteNonQuery();
                dr.Cells[8].Value = "пусто";

                */
                #region добавляем (УДАЛЯЕМ) СТ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ

                ora_com.CommandText = "RABAEV.RRL_TT_ADD_PALL";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("TT_ID", OracleType.Int32).Value = 0;
                ora_com.Parameters.Add("ST_NUMBER1", OracleType.VarChar).Value = PUID;

                ora_com.Parameters.Add("ret", OracleType.VarChar ,1024).Direction = ParameterDirection.ReturnValue;

                int rowsAffected = ora_com.ExecuteNonQuery();
                try
                {
                    dataGridView17.CurrentRow.Cells[12].Value = (ora_com.Parameters["ret"].Value);
                }
                catch
                { }

                #endregion



            }catch(Exception ex7)
            {
                MessageBox.Show( ex7.Message );
            }
        }


        #region ПЕРЕНОС_СТ
        private void вТекущийДеньToolStripMenuItem_Click(object sender, EventArgs e)
        {
            try
            {
                OracleCommand ora_comm = new OracleCommand();
                ora_comm.Connection = get_wms_connection();
                DataGridViewRow dr = dataGridView18.CurrentRow;
                if (dr == null)
                    return;
                string PUID = dr.Cells[7].Value.ToString();
                //Добавляем СТ в маршрут
                DateTime dt = DateTime.Now;

                string strSQL2 = " update RABAEV.RRL_SBORKA_PALLETS set  STDATE ="+date2sql_ora( dt )+"  " +
                    " where ST_NUMBER='" + PUID + "' ";
                ora_comm.CommandText = strSQL2;
                ora_comm.ExecuteNonQuery();
                dr.Cells[8].Value = "пусто";
                dataGridView18.Rows.Remove(dr);
            }
            catch (Exception ex7)
            {
                MessageBox.Show(ex7.Message);
            }
        }

        private void вЗавтрашнийДеньToolStripMenuItem_Click(object sender, EventArgs e)
        {

            try
            {
                OracleCommand ora_comm = new OracleCommand();
                ora_comm.Connection = get_wms_connection();
                DataGridViewRow dr = dataGridView18.CurrentRow;
                if (dr == null)
                    return;
                string PUID = dr.Cells[7].Value.ToString();
                //Добавляем СТ в маршрут
                DateTime dt = DateTime.Now.AddDays(1);

                string strSQL2 = " update RABAEV.RRL_SBORKA_PALLETS set  STDATE =" + date2sql_ora(dt) + "  " +
                    " where ST_NUMBER='" + PUID + "' ";
                ora_comm.CommandText = strSQL2;
                ora_comm.ExecuteNonQuery();
                dr.Cells[8].Value = "пусто";
                dataGridView18.Rows.Remove(dr);
            }
            catch (Exception ex7)
            {
                MessageBox.Show(ex7.Message);
            }

        }

        #endregion

        #region УДОБСТВА_ДЛЯ_РАБОТЫ_СО_СПИСКОМ_СТ

        private void dataGridView18_change_flags()
        {
            foreach (DataGridViewRow dr in dataGridView18.Rows)
            {
                if (dr.Cells[1].Selected)
                {
                    dr.Cells[0].Value = true;
                }
            }
        
        }

        private void dataGridView18_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar == 1)
            { 
                
            }
        }

        #endregion

        private void button65_Click(object sender, EventArgs e)
        {
            DateTime yesterd = dateTimePicker6.Value;
            DateTime afterday = dateTimePicker7.Value;

            string strSQL = "SELECT p.pallet_uid, rrl_skladname_by_id (p.ware_id) СКЛАД,  " + 
            "     decode(  rrl_is_pallet_strictly_fake (p.pallet_uid) , 1  ,  'НЕ ПЕРЕВЕШИВАЛСЯ, И ЗНАЧИТ НЕ ПРОВЕРЯЛСЯ' , 2 , 'ИНТЕРВАЛ ПРОВЕРКИ МЕНЕЕ 5 МИНУТ' ,0  ,'БОЛЕЕ 15'  , 4 , 'ОТ 5 до 15' , ''  )     ПАЛЛЕТ_КРИВОЙ , " +
            "     ADDR , " +
            " TRIAL_WEIGHT ВЕС_НА_1_ВЕСАХ , ( RRL_PAL_WEIGHT( P.PALLET_UID )+WOOD_WEIGHT) ПЛАНОВЫЙ_ВЕС , "+
            " round ( TRIAL_WEIGHT - ( RRL_PAL_WEIGHT( P.PALLET_UID )+WOOD_WEIGHT) ,0 ) РАЗНИЦА , WOOD_WEIGHT ВЕС_ПОДДОНА , ADDR Адрес, RRL_GET_PALLET_CHECK_TIMES(P.PALLET_UID) история , u2.Name СБОРЩИК , u1.Name ПРОВЕРЯЮЩИЙ  "+
            "            FROM rrl_sborka_pallets p , rusers u1 ,  rusers u2 " + 
            " WHERE stdate >= TO_DATE ( " + date2sql_ora( yesterd )  +" , 'dd.mm.yyyy') and  stdate <= TO_DATE ( " + date2sql_ora( afterday )  + " , 'dd.mm.yyyy')   " + 
            "   AND rrl_is_pallet_strictly_fake (p.pallet_uid)>0 " + 
            "   AND wood_weight > 0 " +
            "   AND rrl_skladname_by_id (p.ware_id) IN ('МЕЗ', 'СУХОЙ' , 'АЛКО') "+
            " and p.SBORSHIK = u1.ID(+) and p.KLADOVSHIK=u2.ID(+) order by p.ware_id ,  rrl_is_pallet_strictly_fake (p.pallet_uid) "
            ;

            object[] o = ShowQuery(
            strSQL,
            " ОТЧЕТ ПО НАРУШЕНИЮ ПРОЦЕДУРЫ ВЗВЕШИВАНИЯ: СПИСОК КРИВЫХ ПОДДОНОВ ЗА " + yesterd.ToShortDateString() );

        }



        private string Nomer_naklad_po_nomeru_zakaza(string sm_zakaz)
        {


            string SM_nomer_nakladnoi = "";
            #region ПО НОМЕРУ ЗАКАЗА ПОДГРУЖАЕМ НОМЕР НАКЛАДНОЙ ИЗ СУПЕР_МАГА
            try
            {
                string sql3 = "select ID from  supermag.smcommonbases  where  BASEID='" + sm_zakaz + "' and basedoctype='OR'  and doctype<>'OR' ";
                OracleConnection ora_con4 = new OracleConnection();
                ora_con4.ConnectionString = SM_CONNECTION_STRING();
                ora_con4.Open();

                OracleCommand ora_com4 = new OracleCommand();
                ora_com4.Connection = ora_con4;
                ora_com4.CommandText = sql3;
                OracleDataReader ora_read4 = ora_com4.ExecuteReader();
                int count_of_naklads = 0;
                string str1 = "";
                while (ora_read4.Read())
                {
                    SM_nomer_nakladnoi = obj2str(ora_read4.GetValue(0));
                    str1 = str1 + " " + SM_nomer_nakladnoi;
                    count_of_naklads++;
                }

                if (count_of_naklads > 1)
                {
                    MessageBox.Show("По заказу " + sm_zakaz + " создано несколько накладных. \n Закачайте накладную, указав ее номер. \n Номера накладных: " + str1);
                    return "";
                }

                


            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }


            return SM_nomer_nakladnoi;
            #endregion


        
        
        }



        private void загрузитьЗаказИзТерминалаToolStripMenuItem_Click(object sender, EventArgs e)
        {

            try
            {

                DataGridViewRow dr = dataGridView_prihod.CurrentRow;

                if (dr == null)
                {
                    MessageBox.Show(" Не выбрана строка. ");
                    return;
                }
                string sm_zakaz = obj2str(dr.Cells[2].Value);
                if (sm_zakaz == "")
                {
                    MessageBox.Show(" Не введен номер заказа. ");
                    return;
                }

                if (obj2int(dr.Cells[5].Value) != 0)
                {
                    MessageBox.Show(" Накладная в статусе, не позволяющем подгружать строки. ");
                    return;
                }

                long ID_НАКЛАДНОЙ = obj2int(dr.Cells[6].Value);


                if (obj2int(dr.Cells[6].Value) == 0)
                {
                    MessageBox.Show(" Накладная должна быть создана ");
                    return;
                }

                double time_coeff = 0.6;
                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                // RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )


                ora_com.CommandText = "RABAEV.RRL_CLEAR_PRIH_NAKLAD_ROWS";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = obj2int(dr.Cells[6].Value);
                ora_com.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com.ExecuteNonQuery();
                string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();

                #region Настройки склада - узнаем коэффициент времени

                OracleCommand ora_com9 = new OracleCommand();
                ora_com9.Connection = get_wms_connection();
                ora_com9.CommandText = " select time_coeff from RABAEV.RRL_WARES where ID =" +this.wms_user.ware_id ;
                time_coeff= Convert.ToDouble( ora_com9.ExecuteScalar().ToString().Replace('.',',') );


                #endregion


                string SM_nomer_nakladnoi = "";
                #region ПО НОМЕРУ ЗАКАЗА ПОДГРУЖАЕМ НОМЕР НАКЛАДНОЙ ИЗ СУПЕР_МАГА
                try
                {
                    string sql3 = "select ID from  supermag.smcommonbases  where  BASEID='" + sm_zakaz + "' and basedoctype='OR'  and doctype<>'OR' ";
                    OracleConnection ora_con4 = new OracleConnection();
                    ora_con4.ConnectionString = SM_CONNECTION_STRING();
                    ora_con4.Open();

                    OracleCommand ora_com4 = new OracleCommand();
                    ora_com4.Connection = ora_con4;
                    ora_com4.CommandText = sql3;
                    OracleDataReader ora_read4 = ora_com4.ExecuteReader();
                    int count_of_naklads = 0;
                    string str1 = "";
                    while (ora_read4.Read())
                    {
                        SM_nomer_nakladnoi = obj2str(ora_read4.GetValue(0));
                        str1 = str1 + " " + SM_nomer_nakladnoi;
                        count_of_naklads++;
                    }

                    if (count_of_naklads > 1)
                    {
                        MessageBox.Show("По заказу " + sm_zakaz + " создано несколько накладных. \n Закачайте накладную, указав ее номер. \n Номера накладных: " + str1);
                        return;
                    }

                    dataGridView_prihod.CurrentRow.Cells[0].Value = SM_nomer_nakladnoi;
                    OracleCommand ora_com8 = new OracleCommand();
                    ora_com8.Connection = get_wms_connection();
                    ora_com8.CommandText = " update  RABAEV.RRL_PRIHOD_NAKLAD set NAKLAD_NUMBER='" + SM_nomer_nakladnoi + "' where ID=" + ID_НАКЛАДНОЙ.ToString() + " ";
                    ora_com8.ExecuteNonQuery();

                    if (1==1 /*SM_nomer_nakladnoi != ""*/)
                    {
                        try
                        {
                            string strSQL99 = "  select " +
                               "  cli.NAME " +
                               "  from supermag.smdocuments d, supermag.smspec s, supermag.smcard c, SUPERMAG.SMCLIENTINFO cli " +
                               "  where d.doctype in ( 'WI' )   " +
                               "  and d.id = '" + SM_nomer_nakladnoi + "'  " +
                               "  and d.id = s.docid and d.doctype = s.doctype " +
                               "  and s.article = c.article  and cli.ID = d.CLIENTINDEX  ";

                            OracleCommand ora_com99 = new OracleCommand();
                            ora_com99.Connection = ora_con4;
                            ora_com99.CommandText = strSQL99;
                            string ПОСТАВЩИК2 = ora_com99.ExecuteScalar().ToString();
                            dataGridView_prihod.CurrentRow.Cells[3].Value = ПОСТАВЩИК2;
                        }
                        catch (Exception ex)
                        {
                            MessageBox.Show("  " + ex.Message);
                        }
                    }


                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }

                // ЕСЛИ НАКЛАДНАЯ СУЩЕСТВУЕТ - фиксируем ее номер в строчке накладной.
                if (SM_nomer_nakladnoi != "")
                {
                    dr.Cells[0].Value = SM_nomer_nakladnoi;
                }
                else
                {

                }

                #endregion




                // ПОДКЛЮЧАЕМСЯ К СКЛ СЕРВЕРУ, ЗАПРАШИВАЕМ ПО ДАНОМУ ЗАКАЗУ СТРОКИ
                // Подключаемся к ораклу, запрашиваем по данному заказу номер накладной. и ее строки.
                // Если таковой есть, проверяем соответствие строк накладной паллетам заказа
                // Если соответствия нет - просим устранить несоответствие, выдем список строк с ошибками.
                // Если соответствие есть, создаем строки накладной, 
                // создаем паллеты по накладной, 
                // закрываем накладную в 1- статус

                #region ПОДКЛЮЧАЕМСЯ К СКЛ СЕРВЕРУ, ЗАПРАШИВАЕМ ПО ДАНОМУ ЗАКАЗУ СТРОКИ
                string strSQL1 = "  select * from invoice_dh where pdate >= '04/04/2010'  ";

                strSQL1 = "  select * from invoice_dh where num = @Param1   ";


                SqlParameter myParam1 = new SqlParameter("@Param1", SqlDbType.NVarChar, 55);
                myParam1.Value = sm_zakaz;


                SqlCommand my_com = new SqlCommand();
                my_com.Parameters.Add(myParam1);
                SqlConnection myConnection = new SqlConnection("user id=sa;" +
                                           "password=utyfwdfkt;server=RC-TSD;" +
                                           "Trusted_Connection=no;" +
                                           "database=DKLinkTSD; " +
                                           "connection timeout=30");

                myConnection.Open();

                my_com.Connection = myConnection;
                my_com.CommandText = strSQL1;
                SqlDataReader my_reader = my_com.ExecuteReader();
                int id = 0;
                if (my_reader.Read())
                {
                    id = Convert.ToInt32(my_reader.GetValue(0));
                }
                else
                {
                    MessageBox.Show("Заказа с номером '" + sm_zakaz + "' в базе DKLINK нет ");
                    return;
                }
                my_reader.Close();

                SqlCommand my_com2 = new SqlCommand();
                SqlParameter myParam2 = new SqlParameter("@Param2", SqlDbType.NVarChar, 100);
                myParam2.Value = id;

                string strSQL2 = " select row_id , field , value from PrintingServiceNET.dbo.TaskStrings where row_id in ( " +
                    " select row_id from PrintingServiceNET.dbo.TaskStrings where value = @Param2 " +
                    " ) order by row_id ";
                my_com2.Connection = myConnection;
                my_com2.CommandText = strSQL2;
                my_com2.Parameters.Add(myParam2);
                SqlDataReader ora_read2 = my_com2.ExecuteReader();


                List<Dictionary<string, string>> zakaz_from_dklink = new List<Dictionary<string, string>>();
                #region ПОДГРУЖАЕМ ЗАКАЗ ИЗ DKLINK
                string current_row_id = "";
                Dictionary<string, string> ora_row = new Dictionary<string, string>();

                while (ora_read2.Read())
                {

                    string row_id = obj2str(ora_read2.GetValue(0));
                    string field = obj2str(ora_read2.GetValue(1));
                    string value = obj2str(ora_read2.GetValue(2));
                    if ((current_row_id != row_id) && (current_row_id != ""))
                    {

                        if (!ora_row.ContainsKey("productiondate"))
                        {
                            if (this.wms_user.ware_id == 4)
                            {
                                DateTime yyy = DateTime.Today;
                                ora_row["productiondate"] = yyy.AddDays(365).ToString();
                            }
                        }
                        else if (ora_row["productiondate"] == "")
                        {
                            if (this.wms_user.ware_id == 4)
                            {
                                DateTime yyy = DateTime.Today;
                                ora_row["productiondate"] = yyy.AddDays(365).ToString();
                            }
                        }

                        zakaz_from_dklink.Add(ora_row);
                        ora_row = new Dictionary<string, string>();
                    }
                    


                    current_row_id = row_id;
                    switch (field)
                    {

                        case "ItemID": // Цена .
                            ora_row[field] = value;
                            break;

                        case "name": // Цена .
                            ora_row[field] = value;
                            break;

                        case "fcount": // Фактически пришедшее количество 
                            ora_row[field] = value;
                            break;

                        case "kolpal": // Вложенность в паллет.
                            ora_row[field] = value;
                            break;


                        case "productiondate": // Годен до.
                            ora_row[field] = value;
                            break;

                        case "fprice": // Цена.
                            ora_row[field] = value;
                            break;

                        case "fprice_notax": // Цена .
                            ora_row[field] = value;
                            break;

                        case "expirationdate": // срок годности в днях .
                            ora_row[field] = value;
                            break;

                        default:
                            break;
                    }

                }

                if (ora_row != null)
                {

                    if (!ora_row.ContainsKey("productiondate"))
                    {
                        if (this.wms_user.ware_id == 4)
                        {
                            DateTime yyy = DateTime.Today;
                            ora_row["productiondate"] = yyy.AddDays(365).ToString();
                        }
                    }
                    else if (ora_row["productiondate"]=="")
                    {
                        if (this.wms_user.ware_id == 4)
                        {
                            DateTime yyy = DateTime.Today;
                            ora_row["productiondate"] = yyy.AddDays(365).ToString();
                        }
                    }


                    if (ora_row.ContainsKey("ItemID"))
                        zakaz_from_dklink.Add(ora_row);
                }

                #endregion


                if (zakaz_from_dklink.Count == 0)
                {
                    MessageBox.Show(" заказ не загружен из терминала ");
                    return;
                }

                #endregion



                #region ФОРМИРУЕМ ПРИХОД ИЗ zakaz_from_dklink



                #region ПРОВЕРКА
                // ПОДГРУЖАЕМ СПИСОК АРТИКУЛОВ ИЗ WMS
                Dictionary<string, string> arts = new Dictionary<string, string>();
                string strSQL = " SELECT A.ACTICUL  FROM RABAEV.RRL_ARTICULS A ,  RABAEV.RRL_CELLS C where A.cell=C.cell "; // and c.ware_id = " + this.wms_user.ware_id.ToString();
                OracleCommand ora_com6 = new OracleCommand();
                ora_com6.CommandText = strSQL;
                ora_com6.Connection = get_wms_connection();
                OracleDataReader ora_reader = ora_com6.ExecuteReader();
                while (ora_reader.Read())
                {
                    string art = ora_reader.GetValue(0).ToString();
                    arts.Add(art, art);
                }


                foreach (Dictionary<string, string> seq in zakaz_from_dklink)
                {// По всем строкам накладных
                    string ar1 = seq["ItemID"];

                    if (!arts.ContainsKey(ar1))
                    {
                        SyncArticul(ar1, this.wms_user.ware_id);
                    }
                }


                #endregion




                #region СОЗДАЕМ СТРОЧКИ ЗАКАЗА

                foreach (Dictionary<string, string> df in zakaz_from_dklink)
                {// По всем строкам накладных
                    /*	
                case "ItemID": // Цена .
                case "name": // Цена .
                case "fcount": // Фактически пришедшее количество 
                case "kolpal": // Вложенность в паллет.
                case "productiondate": // Годен до.
                case "fprice": // Цена.
                case "fprice_notax": // Цена .
                case "expirationdate": // срок годности в днях .
*/
                    long срок_годности_в_днях=360;
                    string articul = df["ItemID"];
                    double Количество_тов = obj2double(df["fcount"]);
                    double Цена_с_ндс = obj2double(df["fprice"]);

                    DateTime expirationdate = DateTime.Now;
                    #region СРОКИ ГОДНОСТИ
                    try
                    {
                         expirationdate = Convert.ToDateTime(df["productiondate"]);
                         срок_годности_в_днях = Convert.ToInt32 (df["expirationdate"]);


                        /*
                         if ((this.wms_user.ware_id == 7)  )
                         {
                             expirationdate = expirationdate.AddDays(срок_годности_в_днях * 0.33);
                         }
                         else {
                             expirationdate = expirationdate.AddDays(срок_годности_в_днях * 0.6);
                         }*/

                         expirationdate = expirationdate.AddDays(срок_годности_в_днях * time_coeff);
                        

                         OracleCommand ora_com89 = new OracleCommand();
                        ora_com89.Connection =  get_wms_connection() ;
                        ora_com89.CommandType = CommandType.StoredProcedure;

                        ora_com89.CommandText = "RABAEV.RRL_UPDATE_SG";
                        ora_com89.CommandType = CommandType.StoredProcedure;
                        ora_com89.Parameters.Add("articul1", OracleType.VarChar).Value = articul;
                        ora_com89.Parameters.Add("sg", OracleType.Int32).Value = срок_годности_в_днях;

                        ora_com89.Parameters.Add("ret", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected89 = ora_com89.ExecuteNonQuery();
                        //string tmpVar45 = ora_com45.Parameters["tmpVar"].Value.ToString();



                    }catch(Exception ex)
                    {
                        MessageBox.Show("Не введен срок годности. накладная не будет загружена.  Артикул=" + articul);

                        OracleCommand ora_com45 = new OracleCommand();
                        ora_com45.Connection = get_wms_connection();
                        // RRL_HAS_WRIGHT( user_id varchar2 , wright_name varchar2 )

                        ora_com45.CommandText = "RABAEV.RRL_CLEAR_PRIH_NAKLAD_ROWS";
                        ora_com45.CommandType = CommandType.StoredProcedure;
                        ora_com45.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = obj2int(dr.Cells[6].Value);
                        ora_com45.Parameters.Add("tmpVar", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected45 = ora_com45.ExecuteNonQuery();
                        string tmpVar45 = ora_com45.Parameters["tmpVar"].Value.ToString();
                        dataGridView_prihod_CellEnter(null, null);
                        return;
                    }
                    #endregion
                    
                    double kolpal = obj2double(df["kolpal"]);
                    long srok_godnosti = obj2int(df["expirationdate"]);

                    ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "ADD_RRL_PRIH_NAKLAD_ROW2";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("NAKLAD_ID", OracleType.Int32).Value = ID_НАКЛАДНОЙ; // SM_nomer_nakladnoi;
                    ora_com.Parameters.Add("articul1", OracleType.VarChar).Value = articul;
                    ora_com.Parameters.Add("expiury_date", OracleType.DateTime).Value = expirationdate;
                    ora_com.Parameters.Add("count1", OracleType.Number).Value = Количество_тов;
                    ora_com.Parameters.Add("price", OracleType.Number).Value = Цена_с_ндс;
                    ora_com.Parameters.Add("kolpal1", OracleType.Number).Value = kolpal;
                    ora_com.Parameters.Add("srok_godnosti1", OracleType.Int32).Value = srok_godnosti;

                    ora_com.Parameters.Add("ret", OracleType.Int32).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected3 = ora_com.ExecuteNonQuery();

                }

                dataGridView_prihod_CellEnter(null, null);
                // dataGridView_prihod_CellEnter(null, null);
                dataGridView_prihod_CellEndEdit(null, null);

                #endregion


                #endregion
                MessageBox.Show(" Загрузка завершена. ");
            }catch(Exception ex)
            {
                MessageBox.Show("err 40: "+ex.Message);
            }


             Закрыть_Click(null, null);
             dataGridView_prihod_CellEnter(null, null);
             button18_Click(null,null); // ПЕЧАТЬ

            }

        private void СправочникВодителей_Click(object sender, EventArgs e)
        {
            VODITEL v = new VODITEL();
            v.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            v.ShowDialog();
        }

        private void СправочникМашин_Click(object sender, EventArgs e)
        {
            TRANSPORT t = new TRANSPORT();
            t.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            t.ShowDialog();
        }

        private void ассортиментToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView18.CurrentRow == null)
            {
                MessageBox.Show( " Не выбрана строка " );
            }

            if (dataGridView18.CurrentRow.Cells[7].Value == null)
            {
                MessageBox.Show(" Не выбрана строка ");
            }

            string st = dataGridView18.CurrentRow.Cells[7].Value.ToString();
            
            string strSQL = "select  R.ARTICUL , " +
                "   R.SHORTNAME  , R.QUANTITY  ,  R.AUCTION , R.PALLET_UID , R.SORTFIELD " +
                " from RABAEV.RRL_SBORKA_PALLET_ROWS R ,  RABAEV.RRL_SBORKA_PALLETS P " +
                " where  R.PALLET_UID=P.PALLET_UID and P.ST_NUMBER='" + st.ToString() + "'  "+
                "   order by SORTFIELD ";

            ShowQuery(strSQL, " СОСТАВ СТ " + st);


        }

        private void dataGridView18_KeyDown(object sender, KeyEventArgs e)
        {
            if(e.KeyCode== Keys.F5 )
            {

                    foreach (DataGridViewRow dr in dataGridView18.Rows)
                    {
                        dr.Cells[0].Value = dr.Cells[2].Selected;
                    }
            }
        }

        private void button66_Click(object sender, EventArgs e)
        {
            string add_sql = "";
            string add_sql2 = " and ( user_group <> 'GLOBAL_ADMIN' ) ";
            if (has_right("EDIT_GLOBAL_ADMIN"))
            {
                add_sql2 = "";
            }

            if( Поиск_пользователей.Text!="" )
            {
                add_sql = " and ID like '%" + Поиск_пользователей.Text + "%' or NAME like '%" + Поиск_пользователей.Text + "%' or  USER_GROUP like '%" + Поиск_пользователей.Text + "%'  ";
            }

            string strSQL = " select ID, NAME , ware_id , pass, user_group ,  int2bool( deleted) , "+
                " int2bool( pravo_admin_login ) , ID , WMSUSER_ID , "+
                " int2bool(  PRAVO_KARSHIK ) , int2bool(  PRAVO_CHECK_ORDER ) , int2bool(  PRAVO_RAZVOZ_ZAYAVOK ) , SMENA  from RUSERS where 1=1 " + add_sql + add_sql2;

            fill_view_MINI_WMS(dataGridView24, strSQL , 13 );

        }

        private void dataGridView24_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView24.CurrentRow == null)
            { return; }

            if (dataGridView24.CurrentRow.Cells[0].Value == null)
            { return; }

            string ID = dataGridView24.CurrentRow.Cells[0].Value.ToString();
            string OLD_ID = obj2str( dataGridView24.CurrentRow.Cells[7].Value );
            string NAME = obj2str( dataGridView24.CurrentRow.Cells[1].Value);
            string WARE_ID =  obj2str(  dataGridView24.CurrentRow.Cells[2].Value );
            string ПАРОЛЬ = obj2str(  dataGridView24.CurrentRow.Cells[3].Value );
            string ГРУППА = obj2str(  dataGridView24.CurrentRow.Cells[4].Value );
            string СМЕНА = obj2str(dataGridView24.CurrentRow.Cells[12].Value);

           
                string WMSID = obj2str(dataGridView24.CurrentRow.Cells[8].Value);
            



            int PRAVO_KARSHIK = 0; try { if (Convert.ToBoolean(dataGridView24.CurrentRow.Cells[9].Value)) { PRAVO_KARSHIK = 1; }; }
            catch { }
            int PRAVO_CHECK_ORDER = 0; try { if (Convert.ToBoolean(dataGridView24.CurrentRow.Cells[10].Value)) { PRAVO_CHECK_ORDER = 1; }; }
            catch { }
            int PRAVO_RAZVOZ_ZAYAVOK = 0; try { if (Convert.ToBoolean(dataGridView24.CurrentRow.Cells[11].Value)) { PRAVO_RAZVOZ_ZAYAVOK = 1; }; }
            catch { }

            int УД = 0; try { if (Convert.ToBoolean(dataGridView24.CurrentRow.Cells[5].Value)) { УД = 1; }; }
            catch { }
            int ПРОГ = 0; try { if (Convert.ToBoolean(dataGridView24.CurrentRow.Cells[6].Value)) { ПРОГ = 1; }; }
            catch { }
            string strSQL = "";

            if (WARE_ID == "")
                return;



            if ( (ГРУППА == "GLOBAL_ADMIN") || (ГРУППА == "STOCK_MANAGER") || (ГРУППА == "ST_SMEN") ||
                (ГРУППА == "LOGIST") || (ГРУППА == "LOGIST_BUH")
                || (ГРУППА == "VESOV")|| (ГРУППА == "REVIZOR") || (ГРУППА == "STOPPER")
                || (ГРУППА == "WARE_HEAD") || (ГРУППА == "ST_PRIEMO_SD") )
            { 
                if( !has_right("EDIT_USER_"+ГРУППА) )
                {
                    MessageBox.Show("Нет прав на редактирование EDIT_USER_" + ГРУППА);
                    return;
                }
            }


            


            // PRAVO_KARSHIK PRAVO_CHECK_ORDER PRAVO_RAZVOZ_ZAYAVOK 
            if (OLD_ID != "")
            {
                 strSQL = " update rusers set ID='" + ID + "' , NAME='" + NAME + "' , " +
                    " ware_id=" + WARE_ID + " , PASS='" + ПАРОЛЬ + "' , user_group='" + ГРУППА + "' "+
                    " , PRAVO_KARSHIK="+PRAVO_KARSHIK.ToString()+" , PRAVO_CHECK_ORDER="+ PRAVO_CHECK_ORDER.ToString() +" , PRAVO_RAZVOZ_ZAYAVOK= "+PRAVO_RAZVOZ_ZAYAVOK.ToString()+
                    " , DELETED=" + УД.ToString() + " , PRAVO_ADMIN_LOGIN=" + ПРОГ.ToString() + " , WMSUSER_ID= '" + WMSID.ToString().Trim() + "' , SMENA='" + СМЕНА + "' where  ID='" + OLD_ID + "'  ";


            }
            else {

                strSQL = " insert into rusers (ID ,NAME , ware_id,PASS , user_group, DELETED , PRAVO_ADMIN_LOGIN , PRAVO_KARSHIK , PRAVO_CHECK_ORDER , PRAVO_RAZVOZ_ZAYAVOK , WMSUSER_ID ) values " +
                    " ( '" + ID + "' ,'" + NAME + "' ," + WARE_ID + " ,'" + ПАРОЛЬ + "' ,'" + ГРУППА + "' , " + УД.ToString() + " ," + ПРОГ.ToString() + " , " + PRAVO_KARSHIK + " , " + PRAVO_CHECK_ORDER + " , " + PRAVO_RAZVOZ_ZAYAVOK + " , '" + WMSID.ToString().Trim() + "'  )  " +
                    "  ";

                dataGridView24.CurrentRow.Cells[7].Value = ID;
            }
            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL;
            ora_com.ExecuteNonQuery();

        }

        private void отчетПоПривлечениюКомпанийToolStripMenuItem_Click(object sender, EventArgs e)
        {

            DateTime td = DateTime.Today;
            DateTime yesterday1 = DateTime.Today.AddDays(-7);

            DateTime td_7 = DateTime.Today.AddDays(-7);
            DateTime td_14 = DateTime.Today.AddDays(-14);
            DateTime td_21 = DateTime.Today.AddDays(-21);

            string strSQL = " select  КОЛИЧЕСТВО , Компания , ТИП from ( "+
                " select count(RRL_TRANSPORT_TASK.ID) КОЛИЧЕСТВО , " +
                " DOVERENNOST_OT Компания  , RRL_TR_VEHICLE.TR_TYPE ТИП  " +
                " from  RABAEV.RRL_TRANSPORT_TASK , RABAEV.RRL_TR_VEHICLE , RABAEV.RRL_TR_VODITEL  " +
            " where ( RABAEV.RRL_TRANSPORT_TASK.TRANSPORT=RRL_TR_VEHICLE.NUM ) and ( RRL_TR_VEHICLE.NUM=RRL_TR_VODITEL.TRANSPORT_NUM(+) ) "+
            " and CREATEDATE<=" + date2sql_ora(td) + " and   CREATEDATE>=" + date2sql_ora(yesterday1) + " " +
            "       group by  doverennost_ot, rrl_tr_vehicle.tr_type ) DDD   ";



            strSQL =
              "  SELECT DDD.КОЛИЧЕСТВО ЗА_НЕДЕЛЮ,  DDD2.КОЛИЧЕСТВО ЗА_ПРОШЛУЮ , DDD3.КОЛИЧЕСТВО ЗА_ПОЗАПРОШЛУЮ ,  DDD4.КОЛИЧЕСТВО ЗА_ПОЗАПОЗАПРОШЛУЮ  ,  DDD.Компания, DDD.ТИП  " +
              "  FROM  " +
              "   (SELECT   COUNT (rrl_transport_task.ID) КОЛИЧЕСТВО, " +
              "                 doverennost_ot Компания, rrl_tr_vehicle.tr_type ТИП " +
              "            FROM rabaev.rrl_transport_task, " +
              "                 rabaev.rrl_tr_vehicle, " +
              "                 rabaev.rrl_tr_voditel " +
              "           WHERE (rabaev.rrl_transport_task.transport = rrl_tr_vehicle.num) " +
              "            AND (rrl_tr_vehicle.num = rrl_tr_voditel.transport_num(+)) " +
              "             AND createdate <= " + date2sql_ora(td) + " " +
              "             AND createdate >= " + date2sql_ora(yesterday1) + " " +
              "        GROUP BY doverennost_ot, rrl_tr_vehicle.tr_type) ddd  ,  " +


              "  (SELECT   COUNT (rrl_transport_task.ID) КОЛИЧЕСТВО, " +
              "                doverennost_ot Компания, rrl_tr_vehicle.tr_type ТИП " +
              "           FROM rabaev.rrl_transport_task, " +
              "               rabaev.rrl_tr_vehicle, " +
              "               rabaev.rrl_tr_voditel " +
              "         WHERE (rabaev.rrl_transport_task.transport = rrl_tr_vehicle.num) " +
              "             AND (rrl_tr_vehicle.num = rrl_tr_voditel.transport_num(+)) " +
              "             AND createdate <= " + date2sql_ora(td_7) + " " +
              "             AND createdate >= " + date2sql_ora(td_14) + " " +
              "        GROUP BY doverennost_ot, rrl_tr_vehicle.tr_type) ddd2 ,  " +

                            "  (SELECT   COUNT (rrl_transport_task.ID) КОЛИЧЕСТВО, " +
              "                doverennost_ot Компания, rrl_tr_vehicle.tr_type ТИП " +
              "           FROM rabaev.rrl_transport_task, " +
              "               rabaev.rrl_tr_vehicle, " +
              "               rabaev.rrl_tr_voditel " +
              "         WHERE (rabaev.rrl_transport_task.transport = rrl_tr_vehicle.num) " +
              "             AND (rrl_tr_vehicle.num = rrl_tr_voditel.transport_num(+)) " +
              "             AND createdate <= " + date2sql_ora(td_14) + " " +
              "             AND createdate >= " + date2sql_ora(td_21) + " " +
              "        GROUP BY doverennost_ot, rrl_tr_vehicle.tr_type) ddd3 ,  " +

                                          "  (SELECT   COUNT (rrl_transport_task.ID) КОЛИЧЕСТВО, " +
              "                doverennost_ot Компания, rrl_tr_vehicle.tr_type ТИП " +
              "           FROM rabaev.rrl_transport_task, " +
              "               rabaev.rrl_tr_vehicle, " +
              "               rabaev.rrl_tr_voditel " +
              "         WHERE (rabaev.rrl_transport_task.transport = rrl_tr_vehicle.num) " +
              "             AND (rrl_tr_vehicle.num = rrl_tr_voditel.transport_num(+)) " +
              "             AND createdate <= " + date2sql_ora(td_14) + " " +
              "             AND createdate >= " + date2sql_ora(td_21) + " " +
              "        GROUP BY doverennost_ot, rrl_tr_vehicle.tr_type) ddd4   " +

              "       where  ( ddd.Компания = ddd2.Компания(+) ) and  ( ddd.ТИП = ddd2.ТИП(+) ) "+
              " and ( ddd.Компания = ddd3.Компания(+) ) and  ( ddd.ТИП = ddd3.ТИП(+) )  "+
              " and ( ddd.Компания = ddd4.Компания(+) ) and  ( ddd.ТИП = ddd4.ТИП(+) )  ";


            ShowQuery( strSQL , " Отчет по транспортным компаниям за неделю " );

        }

        private void button67_Click(object sender, EventArgs e)
        {
  //          KLADOVSHIK
//SHTABELER
           if (dataGridView22.CurrentRow == null) return;
 
           object[] o2 = ShowQuery(" select ID  , WMSUSER_ID , NAME  from rusers where  USER_GROUP ='SBORSHIK' and ware_id=" + this.wms_user.ware_id + " order by name ", "Выберите сборщика" ,  new Point( 2,0 ) );
           if ( (o2 != null) && ( o2.Length>1 ) )
           {
               СБОРЩИК_1.Tag  = o2[0].ToString();
               СБОРЩИК_1.Text = "["+ o2[1].ToString() +"] " + o2[2].ToString();

               object o = dataGridView22.CurrentRow.Cells[1].Value;
               OracleCommand ora_com2 = new OracleCommand();
               ora_com2.Connection = get_wms_connection();
               ora_com2.CommandText = "RABAEV.RRL_SET_SBORSHIK";
               ora_com2.CommandType = CommandType.StoredProcedure;
               ora_com2.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = o.ToString();
               ora_com2.Parameters.Add("SBORSHIK1", OracleType.VarChar).Value = СБОРЩИК_1.Tag;
               ora_com2.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
               int rowsAffected = ora_com2.ExecuteNonQuery();
           }

        }

        private void button68_Click(object sender, EventArgs e)
        {

            if (dataGridView22.CurrentRow == null) return;
            //          KLADOVSHIK
            //SHTABELER

            object[] o2 = ShowQuery(" select ID  , WMSUSER_ID , NAME  from rusers where  USER_GROUP ='KLADOVSHIK' and ware_id=" + this.wms_user.ware_id + " order by name ", "Выберите проверяющего", new Point(2, 0));
            if ((o2 != null) && (o2.Length > 1))
            {
                ПРОВЕРЯЮЩИЙ_1.Tag = o2[0].ToString();
                ПРОВЕРЯЮЩИЙ_1.Text =  o2[2].ToString();

                object o = dataGridView22.CurrentRow.Cells[1].Value;
                OracleCommand ora_com2 = new OracleCommand();
                ora_com2.Connection = get_wms_connection();
                ora_com2.CommandText = "RABAEV.RRL_SET_KLADOVSHIK";
                ora_com2.CommandType = CommandType.StoredProcedure;
                ora_com2.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = o.ToString();
                ora_com2.Parameters.Add("KLADOVSHIK1", OracleType.VarChar).Value = ПРОВЕРЯЮЩИЙ_1.Tag;
                ora_com2.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
                int rowsAffected = ora_com2.ExecuteNonQuery();
            }



        }

        private void подтвердитьПереворкуПаллетыToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView22.CurrentRow == null)
            {
                return;
            }

            ОшибкиСборки dial = new ОшибкиСборки();
            dial.ShowDialog();
            
            //dial.type;
            int count_of_errors=dial.count_of_errors;
            string prim = dial.prim ;

            if (prim.Length > 1023)
            {
                prim = dial.prim.Substring(0, 1024);
            }

            if ( ( count_of_errors==0  ) && ( prim=="" ) )
            {
                MessageBox.Show("Не указана причина несоответвия. \n Проверка не подтверждается. ");
                return;
            }

            string pallet_uid = dataGridView22.CurrentRow.Cells[1].Value.ToString();
            
            /*OracleCommand ora_com2 = new OracleCommand();
            ora_com2.Connection = get_wms_connection();
            ora_com2.CommandText = "RABAEV.RRL_SET_SCAN_PROOVE";
            ora_com2.CommandType = CommandType.StoredProcedure;
            ora_com2.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = pallet_uid.ToString();
            ora_com2.Parameters.Add("count_of_errors1", OracleType.Int32).Value = count_of_errors ;
            ora_com2.Parameters.Add("prim1", OracleType.VarChar).Value = prim;
            ora_com2.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
            int rowsAffected = ora_com2.ExecuteNonQuery();
            dataGridView22.CurrentRow.Cells[4].Value = true;
            */
            OracleCommand ora_com3 = new OracleCommand();
            ora_com3.Connection = get_wms_connection();
            ora_com3.CommandText = "RABAEV.RRL_SET_SCAN_PROOVE2";
            ora_com3.CommandType = CommandType.StoredProcedure;
            ora_com3.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = pallet_uid.ToString();
            ora_com3.Parameters.Add("count_of_errors1", OracleType.Int32).Value = 0;
            ora_com3.Parameters.Add("prim1", OracleType.VarChar).Value = prim;
            ora_com3.Parameters.Add("SBORSHIK1", OracleType.VarChar).Value = "";
            ora_com3.Parameters.Add("KLADOVSHIK1", OracleType.VarChar).Value = this.wms_user.user_id;

            ora_com3.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;

            int rowsAffected = ora_com3.ExecuteNonQuery();

        }

        private void checkBox4_CheckedChanged(object sender, EventArgs e)
        {
            БИЛЛИНГ_ДО.Visible = checkBox4.Checked;
        }

        private void button69_Click(object sender, EventArgs e)
        {
            #region ОТЧЕТ ПО СБОРКЕ И ПРОВЕРКЕ

            string sql_add2="";
            if (checkBox4.Checked)
            {
                sql_add2 = " and ( STDATE <=" + date2sql_ora(БИЛЛИНГ_ДО.Value) + " ) and ( STDATE >=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " )  ";
            }
            else {
                sql_add2 = " and ( STDATE =" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " )  ";
            }


            

            string strSQL = " select RRL_SKLADNAME_BY_ID( P.WARE_ID ) СКЛАД , "+
                " PALLET_UID, RRL_PAL_ROW_COUNT(PALLET_UID) СТРОКИ , PROOVED ВЕС , PROOVED_BY_SCAN СКАН  , "+
                " COUNT_OF_ERRORS Ошибки , "+
                " U1.Name Сборщик , U2.Name Проверил , STDATE , PRIM Примечание , "+
                " RRL_is_PALLET_strictly_fake(PALLET_UID) fake ,  RRL_GET_PALLET_CHECK_TIMES(P.PALLET_UID) история , "+
                " round ( TRIAL_WEIGHT - ( RRL_PAL_WEIGHT( P.PALLET_UID )+WOOD_WEIGHT) ,0 ) РАЗНИЦА   " +
                " from RRL_SBORKA_PALLETS P , RUSERS U1 , RUSERS U2  "+
                " where (not (SBORSHIK is null)) and ( P.SBORSHIK = U1.ID(+) )  and ( P.KLADOVSHIK = U2.ID(+) ) " + sql_add2;

            ShowQuery( strSQL , "Отчет по собранным строкам за период" );
            

            #endregion


        }

        private void button70_Click(object sender, EventArgs e)
        {

            #region ОТЧЕТ ПО СБОРКЕ И ПРОВЕРКЕ

            string sql_add2 = "";
            if (checkBox4.Checked)
            {
                sql_add2 = " and ( CREATION_DATE <=" + date2sql_ora(БИЛЛИНГ_ДО.Value) + " ) and ( CREATION_DATE >=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " )  ";
            }
            else
            {
                sql_add2 = " and ( CREATION_DATE <=" + date2sql_ora(БИЛЛИНГ_ДО.Value.AddDays(1)) + " ) and ( CREATION_DATE >=" + date2sql_ora(БИЛЛИНГ_ДО.Value) + " )  ";
            }

// (not (KLADOVSHIK is null)) and
            string strSQL = " select count(P.UID_PALLET) , CREATION_DATE , U1.Name  " +
                " from RRL_PALLETS P , RUSERS U1  where  ( P.KLADOVSHIK = U1.ID(+) )    " + sql_add2 + " group by CREATION_DATE , U1.Name ";
            ShowQuery(strSQL, "Отчет по принятым паллетам за период");


            #endregion


        }

        private List<Dictionary<string, object>> СравнитьНакладнуюСМСЗаказомWMS(string ST2)
        { 
         string ST=ST2;

            try
            {
                // ST = dataGridView18.CurrentRow.Cells[7].Value.ToString();
                if(ST.Split('#').Length>1)
                {
                    ST = ST.Split('#')[0];
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return null;
            }

            string strSQL="   select  " +
            " s.article Артикул, " + 
            " c.shortname Название, " + 
            " sum(s.quantity) Колво " + 
            " from supermag.smdocuments d, supermag.smspec s, supermag.smcard c " + 
            " where d.doctype in ( 'WO' ,  'WI' , 'IW'  )   " + 
            " and d.docstate in (0 , 1 , 2 , 3 )   " + 
            " and d.id = s.docid and d.doctype = s.doctype  " + 
            " and s.article = c.article " +
            " and d.id in ( select id from  supermag.smcommonbases  where  BASEID='" + ST + "'  and basedoctype='SO' ) " +
            " having  sum(s.quantity)>0 " +
            " group by  s.article , c.shortname ";


                OracleCommand ora_com = new OracleCommand();
                OracleConnection ora_conn = new OracleConnection();
                
                Dictionary<string, double> sm_nakl = new Dictionary<string, double>();

            try
            {
                
                ora_conn.ConnectionString = SM_CONNECTION_STRING();
                ora_conn.Open();
                ora_com.Connection = ora_conn;
                ora_com.CommandText = strSQL;
                OracleDataReader ora_reader = ora_com.ExecuteReader();
                while (ora_reader.Read())
                {
                    sm_nakl[ora_reader.GetValue(0).ToString()] = Convert.ToDouble(ora_reader.GetValue(2));
                }
                ora_reader.Close();
                ora_reader.Dispose();
                ora_reader = null;

            }catch(Exception ex)
            {
                MessageBox.Show(ex.Message);
                return null;

            }
           
            if (sm_nakl.Count == 0)
            {
                return null;
            }


            string strSQL2 = " select R.ARTICUL , sum(R.QUANTITY) from  RABAEV.RRL_SBORKA_PALLET_ROWS R ,  RABAEV.RRL_SBORKA_PALLETS P " +
                " where R.PALLET_UID = P.PALLET_UID and P.ST_NUMBER like '" + ST + "%' having sum(R.QUANTITY)>0 group by R.ARTICUL  ";

            OracleCommand ora_com2 = new OracleCommand();
            ora_com2.Connection = get_wms_connection();
            ora_com2.CommandText = strSQL2;
            OracleDataReader ora_read2= ora_com2.ExecuteReader();
            Dictionary<string, double> wms_nakl = new Dictionary<string, double>();
            while (ora_read2.Read())
            {
                wms_nakl[ora_read2.GetValue(0).ToString()] = Convert.ToDouble(ora_read2.GetValue(1));
            }
            ora_read2.Close();
            ora_read2.Dispose();
            ora_read2 = null;
            List<Dictionary<string, object>> res = new List<Dictionary<string, object>>();

            foreach (string art_in_wms in wms_nakl.Keys)
            {
                Dictionary<string, object> result_row = new Dictionary<string, object>();
                if (sm_nakl.ContainsKey(art_in_wms))
                {
                    if (wms_nakl[art_in_wms] != sm_nakl[art_in_wms])
                    { // Фиксируем разницу
                        //
                        result_row["articul"] = art_in_wms;
                        result_row["count_in_wms"] = wms_nakl[art_in_wms];
                        result_row["count_in_sm"] = sm_nakl[art_in_wms];
                        result_row["ST"] = ST;

                       // wms_get_spfunction_value("", "", "");

                        res.Add(result_row);
                    }
                    sm_nakl.Remove(art_in_wms);
                }
                else{ // Фиксируем отсутствие артикула в супермаге
                    
                    result_row["articul"] = art_in_wms;
                    result_row["count_in_wms"] = wms_nakl[art_in_wms];
                    result_row["count_in_sm"] = 0;
                    result_row["ST"] = ST;
                    res.Add(result_row);
                }

            }

            foreach (string kk in sm_nakl.Keys)
            {
                if (kk != "Тар0000000155")
                {
                    Dictionary<string, object> result_row = new Dictionary<string, object>();
                    result_row["articul"] = kk;
                    result_row["count_in_wms"] = 0;
                    result_row["count_in_sm"] = sm_nakl[kk];
                    result_row["ST"] = ST;
                    res.Add(result_row);
                }
            }
            return res;
                  
        }

        private void сравнениеНакладныхСупермагИПаллетWMSToolStripMenuItem_Click(object sender, EventArgs e)
        {

            string ST = "";
            if (dataGridView18.CurrentRow == null)
            {
                MessageBox.Show("Не выбрано ст");
                return;
            }

            try
            {
                 ST = dataGridView18.CurrentRow.Cells[7].Value.ToString();
                if(ST.Split('#').Length>1)
                {
                    ST = ST.Split('#')[0];
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return;
            }
            
            List< Dictionary<string,object> > res= СравнитьНакладнуюСМСЗаказомWMS(ST);

            if (res == null)
            {
                MessageBox.Show(" Накладных в СМ не создано ");
                return;
            }

            if (res.Count == 0)
            {
                MessageBox.Show("накладные совпадают.");
            }
            else {
                ЗАПРОСЫ Z = new ЗАПРОСЫ();
                Z.res= res ;
                Z.ShowDialog();
            }

        }

        private void сравнитьВсеНакладныеToolStripMenuItem_Click(object sender, EventArgs e)
        {
            List<Dictionary<string, object>> res2 = new List<Dictionary<string, object>>();
            foreach (DataGridViewRow dr in dataGridView18.Rows)
            {
                string ST = dr.Cells[7].Value.ToString();
                List<Dictionary<string, object>> res123 = new List<Dictionary<string, object>>();
                res123=СравнитьНакладнуюСМСЗаказомWMS(ST);
                if (res123 != null)
                {
                    foreach (Dictionary<string, object> g in res123)
                    {
                        res2.Add(g);
                    }
                    res123 = null;
                }
            }

            if (res2.Count == 0)
            {
                MessageBox.Show("Все накладные совпадают.");
            }
            else
            {
                ЗАПРОСЫ Z = new ЗАПРОСЫ();
                Z.res = res2;
                Z.ShowDialog();
            }

        }

        private void сравнитьВыделенныеНакладныеToolStripMenuItem_Click(object sender, EventArgs e)
        {


            List<Dictionary<string, object>> res2 = new List<Dictionary<string, object>>();
            foreach (DataGridViewRow dr in dataGridView18.Rows)
            {
                if (Convert.ToBoolean(dr.Cells[0].Value))
                {
                    string ST = dr.Cells[7].Value.ToString();
                    List<Dictionary<string, object>> res123 = new List<Dictionary<string, object>>();
                    res123 = СравнитьНакладнуюСМСЗаказомWMS(ST);
                    if (res123 != null)
                    {
                        foreach (Dictionary<string, object> g in res123)
                        {
                            res2.Add(g);
                        }
                        res123 = null;
                    }
                }
            }

            if (res2.Count == 0)
            {
                MessageBox.Show("Все накладные совпадают.");
            }
            else
            {
                ЗАПРОСЫ Z = new ЗАПРОСЫ();
                Z.res = res2;
                Z.ShowDialog();
            }


        }



        private List<Dictionary<string, object>> СравнитьЗаказСМСЗаказомWMS(string ST2)
        {
            string ST = ST2;

            try
            {
                if (ST.Split('#').Length > 1)
                {
                    ST = ST.Split('#')[0];
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return null;
            }

            string strSQL = "   select  " +
            " s.article Артикул, " +
            " c.shortname Название, " +
            " sum(s.quantity) Колво " +
            " from supermag.smdocuments d, supermag.smspec s, supermag.smcard c " +
            " where d.doctype in ( 'SO'  )   " +
            " and d.docstate in (0 , 1 , 2 , 3 )   " +
            " and d.id = s.docid and d.doctype = s.doctype  " +
            " and s.article = c.article " +
            " and d.id  ='" + ST + "'   " +
            " having  sum(s.quantity)>0 " +
            " group by  s.article , c.shortname ";

            OracleCommand ora_com = new OracleCommand();
            OracleConnection ora_conn = new OracleConnection();
            ora_conn.ConnectionString = SM_CONNECTION_STRING();
            ora_conn.Open();
            ora_com.Connection = ora_conn;
            ora_com.CommandText = strSQL;
            OracleDataReader ora_reader = ora_com.ExecuteReader();
            Dictionary<string, double> sm_nakl = new Dictionary<string, double>();
            while (ora_reader.Read())
            {
                sm_nakl[ora_reader.GetValue(0).ToString()] = Convert.ToDouble(ora_reader.GetValue(2));
            }
            ora_reader.Close();
            ora_reader.Dispose();
            ora_reader = null;
            if (sm_nakl.Count == 0)
            {
                return null;
            }

            string strSQL2 = " select R.ARTICUL , sum( R.ORIGINAL_QUANTITY ) from  RABAEV.RRL_SBORKA_PALLET_ROWS R ,  RABAEV.RRL_SBORKA_PALLETS P " +
                " where R.PALLET_UID = P.PALLET_UID and P.ST_NUMBER like '" + ST + "%' having sum(R.ORIGINAL_QUANTITY)>0 group by R.ARTICUL  ";

            OracleCommand ora_com2 = new OracleCommand();
            ora_com2.Connection = get_wms_connection();
            ora_com2.CommandText = strSQL2;
            OracleDataReader ora_read2 = ora_com2.ExecuteReader();
            Dictionary<string, double> wms_nakl = new Dictionary<string, double>();
            while (ora_read2.Read())
            {
                wms_nakl[ora_read2.GetValue(0).ToString()] = Convert.ToDouble(ora_read2.GetValue(1));
            }
            ora_read2.Close();
            ora_read2.Dispose();
            ora_read2 = null;
            List<Dictionary<string, object>> res = new List<Dictionary<string, object>>();

            foreach (string art_in_wms in wms_nakl.Keys)
            {
                Dictionary<string, object> result_row = new Dictionary<string, object>();
                if (sm_nakl.ContainsKey(art_in_wms))
                {
                    if (wms_nakl[art_in_wms] != sm_nakl[art_in_wms])
                    { // Фиксируем разницу
                        //
                        result_row["articul"] = art_in_wms;
                        result_row["count_in_wms"] = wms_nakl[art_in_wms];
                        result_row["count_in_sm"] = sm_nakl[art_in_wms];
                        result_row["ST"] = ST;
                        res.Add(result_row);
                    }
                    sm_nakl.Remove(art_in_wms);
                }
                else
                { // Фиксируем отсутствие артикула в супермаге

                    result_row["articul"] = art_in_wms;
                    result_row["count_in_wms"] = wms_nakl[art_in_wms];
                    result_row["count_in_sm"] = 0;
                    result_row["ST"] = ST;
                    res.Add(result_row);
                }

            }

            foreach (string kk in sm_nakl.Keys)
            {
                if (kk != "Тар0000000155")
                {
                    Dictionary<string, object> result_row = new Dictionary<string, object>();
                    result_row["articul"] = kk;
                    result_row["count_in_wms"] = 0;
                    result_row["count_in_sm"] = sm_nakl[kk];
                    result_row["ST"] = ST;
                    res.Add(result_row);
                }
            }
            return res;




        }


        private void сравнитьВыделенныйЗаказСЗаказомСМToolStripMenuItem_Click(object sender, EventArgs e)
        {

            string ST = "";
            if (dataGridView18.CurrentRow == null)
            {
                MessageBox.Show("Не выбрано ст");
                return;
            }

            try
            {
                ST = dataGridView18.CurrentRow.Cells[7].Value.ToString();
                if (ST.Split('#').Length > 1)
                {
                    ST = ST.Split('#')[0];
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return;
            }

            List<Dictionary<string, object>> res = СравнитьЗаказСМСЗаказомWMS(ST);

            if (res == null)
            {
                MessageBox.Show(" Накладных в СМ не создано ");
                return;
            }

            if (res.Count == 0)
            {
                MessageBox.Show("накладные совпадают.");
            }
            else
            {
                ЗАПРОСЫ Z = new ЗАПРОСЫ();
                Z.res = res;
                Z.ShowDialog();
            }

        }

        private void сравнитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            List<Dictionary<string, object>> res2 = new List<Dictionary<string, object>>();
            foreach (DataGridViewRow dr in dataGridView18.Rows)
            {
                string ST = dr.Cells[7].Value.ToString();
                List<Dictionary<string, object>> res123 = new List<Dictionary<string, object>>();
                res123 = СравнитьЗаказСМСЗаказомWMS(ST);
                if (res123 != null)
                {
                    foreach (Dictionary<string, object> g in res123)
                    {
                        res2.Add(g);
                    }
                    res123 = null;
                }
            }

            if (res2.Count == 0)
            {
                MessageBox.Show("Все накладные совпадают.");
            }
            else
            {
                ЗАПРОСЫ Z = new ЗАПРОСЫ();
                Z.res = res2;
                Z.ShowDialog();
            }
        }

        private void button71_Click(object sender, EventArgs e)
        {
            string sql_add= " and ( ware_id="+this.wms_user.ware_id.ToString()+" ) ";
            if (has_right("VIEW_ALL_VYCHERK"))
            {
                sql_add = "";
            }

            string strSQL = " select  RRL_SKLADNAME_BY_ID(P.WARE_ID) СКЛАД , P.ST_NUMBER СТ ,R.ARTICUL АРТИКУЛ , SHORTNAME ИМЯ , VYCHERK_USER_ID КТО_ВЫЧЕРКНУЛ , PATH ЯЧЕЙКА  from RABAEV.RRL_SBORKA_PALLET_ROWS R ,  RABAEV.RRL_SBORKA_PALLETS P " +
                " where ( R.PALLET_UID = P.PALLET_UID ) and ( QUANTITY=0 ) and ( CREATE_DATE>=" + date2sql_ora(dateTimePicker6.Value) + " ) and  ( CREATE_DATE<=" + date2sql_ora(dateTimePicker7.Value.AddDays(1)) + " )  " + sql_add ;// 
            object[] o = ShowQuery( strSQL , " Вычерки ");


        }

        private void button72_Click(object sender, EventArgs e)
        {
            long ware_id = 0;
            
            try {
               ware_id= Convert.ToInt32( m_выбранный_склад.Text);
            }catch{}

            if (ware_id == 0) ware_id = this.wms_user.ware_id;

            string strSQL3 = "";
            if (ФильтрПоКарщику.Text != "")
            {
                strSQL3 = " and user_id='" + ФильтрПоКарщику.Text.Trim() + "' ";
            }

            string strSQL = " select  rrl_articuls.Name , e.CELL_FROM ,    e.CELL_TO  , e.DATE_EVENT , e.DATE_OF_ORDER , e.COUNT_EVENT , e.TYPE_EVENT , e.UID_POLETA , e.USER_ID , " +
                " c1.WARE_ID склад_откуда , c2.WARE_ID склад_куда from " +
                " rrl_events e , rrl_cells c1 , rrl_cells c2 , rrl_pallets , rrl_articuls where "+
                " e.UID_POLETA= rrl_pallets.UID_PALLET and rrl_articuls.ACTICUL = rrl_pallets.ARTICUL and  " +
                " ( e.CELL_TO <> 'INVENT' ) and  ( e.CELL_TO <> 'IN_DOCK' )   and " +
                "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
                 " and  ( (  ( c1.OTBOR=1 and c1.CELL<>'INVENT'  )  and ( c2.OTBOR<>1   or c2.CELL='INVENT' )   ) or ( e.CELL_FROM='IN_DOCK'  ) )  " +
                 strSQL3 +
                 "  and " +
                " (  c1.WARE_ID =" + ware_id.ToString() + " or  c2.WARE_ID =" + ware_id.ToString() + " )   " +
                " and ( date_event>=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " ) and  ( date_event<" + date2sql_ora(БИЛЛИНГ_ДО.Value.AddDays(1)) + " ) ";

            object[] o = ShowQuery(strSQL, " работа карщиков: Внутренние перемещения ");


          

            strSQL = " select     e.CELL_TO  , e.TIMEOF , e.UE , e.OPERATION , e.PALLET_UID , e.USER_ID , " +
                            " e.CELL_FROM откуда , e.CELL_TO куда, e.PRIM примечание  from " +
                            "  rrl_billing e , rrl_cells c1 , rrl_cells c2 , rusers  where  (RUSERS.ID= e.USER_ID) and (  RUSERS.USER_GROUP = 'SHTABELER' ) and ( e.CELL_TO <> 'INVENT' )  and " +
                            "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
                            strSQL3+
                         //   "  and (  c1.WARE_ID =" + ware_id.ToString() + " or  c2.WARE_ID =" + ware_id.ToString() + " )   " +
                            " and ( TIMEOF>=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " ) and  ( TIMEOF<" + date2sql_ora(БИЛЛИНГ_ДО.Value.AddDays(1)) + " ) ";

             o = ShowQuery(strSQL, " работа карщиков: Отгрузка ");




             strSQL = " select   e.CELL_FROM,  e.CELL_TO  , e.DATE_EVENT , e.DATE_OF_ORDER , e.COUNT_EVENT , e.TYPE_EVENT , e.UID_POLETA , e.USER_ID , " +
             " c1.WARE_ID склад_откуда , c2.WARE_ID склад_куда from " +
             " rrl_events e , rrl_cells c1 , rrl_cells c2  where  ( e.CELL_TO <> 'INVENT' ) and  ( e.CELL_TO <> 'IN_DOCK' )   and " +
             "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
             " and not ( (  ( c1.OTBOR=1 and c1.CELL<>'INVENT'  )  and ( c2.OTBOR<>1   or c2.CELL='INVENT' )   ) or ( e.CELL_FROM='IN_DOCK'  ) )  " +
             strSQL3 +
             "  and " +
             " (  c1.WARE_ID =" + ware_id.ToString() + " or  c2.WARE_ID =" + ware_id.ToString() + " )   " +
             " and ( date_event>=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " ) and  ( date_event<" + date2sql_ora(БИЛЛИНГ_ДО.Value.AddDays(1)) + " ) ";

             o = ShowQuery(strSQL, " работа карщиков: что не вошло во Внутренние перемещения ");

        }

        private void Сводная_карщики_Click(object sender, EventArgs e)
        {
            long ware_id = 0;

            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1.AddDays(1);
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }

            try
            {
                ware_id = Convert.ToInt32(m_выбранный_склад.Text);
            }
            catch { }


            string str22 = "";
            /*if (ware_id>0)
            {
            str22= " and (  c1.WARE_ID =" + ware_id.ToString() + " or  c2.WARE_ID =" + ware_id.ToString() + " )   "; 
            }*/
            string strSQL = "  select     e.TYPE_EVENT , count( e.UID_POLETA ) , e.USER_ID  " +
                " from rrl_events e , rrl_cells c1 , rrl_cells c2  where  ( e.CELL_TO <> 'INVENT' ) and   ( e.CELL_TO <> 'IN_DOCK' )  and " +
                "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
                " and  ( (  ( c1.OTBOR=1 and c1.CELL<>'INVENT'  )  and ( c2.OTBOR<>1   or c2.CELL='INVENT' )   ) or ( e.CELL_FROM='IN_DOCK'  ) )  " +
                str22  +
                " and ( date_event>=" + date2sql_ora(dt1) + " ) and  ( date_event<=" + date2sql_ora(dt2) + " ) " +
                "  group by    e.TYPE_EVENT ,  e.USER_ID  "; //,   c1.WARE_ID 

            object[] o = ShowQuery(strSQL, "Работа карщиков: Внутренние перемещения ");

            


            /*

             strSQL = "  select     e.TYPE_EVENT , count( e.UID_POLETA ) , e.USER_ID  " +
            " from rrl_events e , rrl_cells c1 , rrl_cells c2  where  ( e.CELL_TO <> 'INVENT' ) and   ( e.CELL_TO <> 'IN_DOCK' )  and " +
            "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
            str22 +
            " and ( date_event>=" + date2sql_ora(dt1) + " ) and  ( date_event<=" + date2sql_ora(dt2) + " ) " +
            "  group by    e.TYPE_EVENT ,  e.USER_ID  "; //,   c1.WARE_ID 

            o = ShowQuery(strSQL, "Работа карщиков: Внутренние перемещения2 ");

            */



            strSQL = " select    sum( e.UE ) , e.OPERATION ,  e.USER_ID " +
                          "   from " +
                          " rrl_billing e , rrl_cells c1 , rrl_cells c2  , rusers  where  (RUSERS.ID= e.USER_ID) and (  RUSERS.USER_GROUP = 'SHTABELER' ) and   ( e.CELL_TO <> 'INVENT' )  and " +
                          "  ( e.CELL_TO= c1.CELL(+) ) and   ( e.CELL_FROM= c2.CELL(+) )  " +
               
                          " and ( TIMEOF>=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " ) and  ( TIMEOF<" + date2sql_ora(БИЛЛИНГ_ДО.Value.AddDays(1)) + " ) "+
                          " group by  e.OPERATION ,  e.USER_ID "  ;

            o = ShowQuery(strSQL, "Работа карщиков: Отгрузка ");

        }

        private void button73_Click(object sender, EventArgs e)
        {


            foreach (DataGridViewRow dr3 in dataGrid_ПАЛЛЕТЫ_ОТКУДА.Rows)
            {
                if (dr3 != null)
                {
                    if (dr3.Cells[0].Selected)
                    {
                        try
                        {
                            OracleCommand ora_com = new OracleCommand();
                            ora_com.Connection = get_wms_connection();
                            ora_com.CommandText = "RABAEV.RRL_INTERNAL_MOVE2";
                            ora_com.CommandType = CommandType.StoredProcedure;
                            ora_com.Parameters.Add("pallet_id", OracleType.VarChar).Value = dr3.Cells[0].Value.ToString();
                            ora_com.Parameters.Add("cell_to", OracleType.VarChar).Value = ЯЧЕЙКА_КУДА.Text;

                            long iiii = 0;
                            try
                            {
                                iiii = Convert.ToInt64(СКОЛЬКО_ПЕРЕМЕЩАЕМ.Text);
                            }
                            catch { }
                            ora_com.Parameters.Add("count1", OracleType.Number).Value = iiii;
                            ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = wms_user.user_id;
                            ora_com.Parameters.Add("ok", OracleType.VarChar, 50).Direction = ParameterDirection.ReturnValue;
                            ora_com.ExecuteNonQuery();
                            string ret = ora_com.Parameters["ok"].Value.ToString();
                            if (ret.Substring(0, 2) != "ok")
                            {
                               // MessageBox.Show("ошибка: " + ret);
                            }
                            else
                            {
                                dataGrid_ПАЛЛЕТЫ_ОТКУДА.Rows.Remove(dr3);
                            }

                        }
                        catch (Exception ex)
                        {
                            MessageBox.Show(" f56 " + ex.Message);
                        }
                    }
                }
            }
        }

        private void button74_Click(object sender, EventArgs e)
        {

            long ware_id = 0;

            try
            {
                ware_id = Convert.ToInt32(m_выбранный_склад.Text);
            }
            catch { }

            if (ware_id == 0) ware_id = this.wms_user.ware_id;

            string strSQL = "  select   *  " +
                " from rrl_prihod_naklad p  where condition=1 and " +
                "   WARE_ID =" + ware_id.ToString() + "  " +
                " and ( date_of_accept>=" + date2sql_ora(БИЛЛИНГ_ОТ.Value) + " ) and  ( date_of_accept<=" + date2sql_ora(БИЛЛИНГ_ОТ.Value.AddDays(1)) + " ) " +
                "  ";

            object[] o = ShowQuery(strSQL, " Не закрытые накладные ");




        }

        private void button75_Click(object sender, EventArgs e)
        {

            long ware_id = 0;
            try  { ware_id = Convert.ToInt32(m_выбранный_склад.Text);}
            catch { }

            if (ware_id == 0) ware_id = this.wms_user.ware_id;

            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1.AddDays(1);
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }

            string strSQL = " select sum( RRL_PAL_ROW_COUNT(PALLET_UID) ) СТРОКИ ,  sum(PROOVED) ВЕС , sum(PROOVED_BY_SCAN ) СКАН , "+
                " sum(COUNT_OF_ERRORS ) Ошибки , "+
                " U1.Name Сборщик , sum( RRL_is_PALLET_strictly_fake(PALLET_UID) ) fake  " +
                " from RRL_SBORKA_PALLETS P , RUSERS U1 , RUSERS U2  "+
                "  where (not (SBORSHIK is null)) and ( P.SBORSHIK = U1.ID(+) )  and ( P.KLADOVSHIK = U2.ID(+) ) " +
                " and ( STDATE>=" + date2sql_ora(dt1) + " ) and  ( STDATE<=" + date2sql_ora(dt2) + " ) "+
                " group by U1.Name  ";

            object[] o = ShowQuery(strSQL, " работа сборщиков ");

        }

        private void выгрузитьВExcelToolStripMenuItem_Click(object sender, EventArgs e)
        {
            grid_2_excel( dataGrid_ПАЛЛЕТЫ_ОТКУДА );
        }

        private void button76_Click(object sender, EventArgs e)
        {

            long ware_id = 0;
            try { ware_id = Convert.ToInt32(m_выбранный_склад.Text); }
            catch { }

            if (ware_id == 0) ware_id = this.wms_user.ware_id;

            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1.AddDays(1);
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }

            string strSQL = " select PALLET_UID ,( RRL_PAL_ROW_COUNT(PALLET_UID) ) СТРОКИ ,  (PROOVED) ВЕС , (PROOVED_BY_SCAN ) СКАН , " +
                " (COUNT_OF_ERRORS ) Ошибки , " +
                " U1.Name Сборщик ,  ( RRL_is_PALLET_strictly_fake(PALLET_UID) ) fake  " +
                " from RRL_SBORKA_PALLETS P , RUSERS U1 , RUSERS U2  " +
                "  where (not (SBORSHIK is null)) and ( P.SBORSHIK = U1.ID(+) )  and ( P.KLADOVSHIK = U2.ID(+) ) " +
                " and ( STDATE>=" + date2sql_ora(dt1) + " ) and  ( STDATE<=" + date2sql_ora(dt2) + " ) " +
                "  ";

            object[] o = ShowQuery(strSQL, " работа сборщиков ");


        }

        private void dataGridView25_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (dataGridView25.CurrentRow == null)
            {
                return;
            }


            if (dataGridView11.CurrentRow == null)
            {
                return;
            }

           long ID= obj2int( dataGridView25.CurrentRow.Cells[0].Value );
           string Name = obj2str (dataGridView25.CurrentRow.Cells[1].Value);

           string articul = obj2str(dataGridView11.CurrentRow.Cells[0].Value);
           double sht_in_kor = obj2double(dataGridView25.CurrentRow.Cells[3].Value);
           double ves_sht = obj2double (dataGridView25.CurrentRow.Cells[4].Value);
           double ves_kart_kor = obj2double(dataGridView25.CurrentRow.Cells[5].Value);
           long deleted = 0;




           try
           {
               if (Convert.ToBoolean(dataGridView25.CurrentRow.Cells[6].Value) == true)
               {
                    deleted = 1;
               }

               OracleCommand ora_com = new OracleCommand();
               ora_com.Connection = get_wms_connection();
               ora_com.CommandText = "RABAEV.UPDATE_RRL_MOD2";
               ora_com.CommandType = CommandType.StoredProcedure;

               ora_com.Parameters.Add("ID1", OracleType.Int32).Value = ID;
               ora_com.Parameters.Add("ARTICUL1", OracleType.VarChar).Value = articul;
               ora_com.Parameters.Add("NAME1", OracleType.VarChar).Value = Name;
               ora_com.Parameters.Add("SHT_IN_KOR1", OracleType.Number).Value = sht_in_kor;
               ora_com.Parameters.Add("SHT_WEIGHT1", OracleType.Number).Value = ves_sht;
               ora_com.Parameters.Add("KARTON_WEIGHT1", OracleType.Number).Value = ves_kart_kor;
               ora_com.Parameters.Add("DELETED1", OracleType.Int32).Value = deleted;

               ora_com.Parameters.Add("ID", OracleType.Int32).Direction = ParameterDirection.ReturnValue;


               ora_com.ExecuteNonQuery();
             if (ID == 0)
               {
                   ID = obj2int(ora_com.Parameters["ID"].Value);
               }
               dataGridView25.CurrentRow.Cells[0].Value = ID;

           }
           catch (Exception ex)
           {
               MessageBox.Show(ex.Message);
               return;
           }

         
        }

        private void dataGridView23_CellEnter(object sender, DataGridViewCellEventArgs e)
        {
            /*
            Если для склада разрешено использовать МОДы
            Если для данного артикула есть  не удаленные МОДы
            Оператор выбирает мод (или пустое место). 
            при проверке весового контроля плановый вес брутто считается с учетом 
            выбранного мода для данной строки паллета.
            */

            if (dataGridView23.CurrentRow == null)
            {
                return;
            }


            string art = dataGridView23.CurrentRow.Cells[0].Value.ToString();
            string mod = "";

            if (dataGridView23.CurrentRow.Cells[7].Value != null)
            {
               mod= dataGridView23.CurrentRow.Cells[7].Value.ToString();
            }
            else 
            {
                mod = "";
            }

            string strSQL = "select ID , NAME from RRL_ARTICUL_MODS  where ARTICUL='" + art + "' and deleted<>1 ";
            fill_view_MINI_WMS(dataGridView26, strSQL, 2);
            if ((mod != "") && (mod != null))
            {
                foreach (DataGridViewRow dr in dataGridView26.Rows)
                {
                    if (dr.Cells[0].Value.ToString() == mod)
                    {
                        dr.Cells[2].Value = true;
                    }
                }
            }



        }

        private void dataGridView26_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            /*
            if (dataGridView26.CurrentRow == null) // Таблица с МОДами
            {
                return;
            }

            if (dataGridView23.CurrentRow == null) // Таблица со строками 
            {
                return;
            }
            // Если щелкнули крыжик - нужно изменить текущий выделенный мод

             long mod_id = Convert.ToInt32( dataGridView26.CurrentRow.Cells[0].Value );
             long row_id = Convert.ToInt32(dataGridView23.CurrentRow.Cells[3].Value );
             string strSQL = " update RRL_SBORKA_PALLET_ROWS set  CURRENT_MOD_ID = " + mod_id.ToString() + " where ID=" + row_id.ToString() + "  ";
             dataGridView23.CurrentRow.Cells[7].Value = mod_id;

             OracleCommand ora_com = new OracleCommand();
             ora_com.Connection = get_wms_connection();
             ora_com.CommandText = strSQL;
             ora_com.CommandType = CommandType.Text;
             ora_com.ExecuteNonQuery();


             // dataGridView23_CellEnter(null,null);
            
             foreach (DataGridViewRow dr in dataGridView26.Rows )
            {
                if (dr.Cells[0].Value.ToString() != mod_id.ToString())
                {
                    dr.Cells[2].Value = false;
                }
            }
            */

        }

        private void dataGridView26_CellValuePushed(object sender, DataGridViewCellValueEventArgs e)
        {

        }

        private void dataGridView26_CellBeginEdit(object sender, DataGridViewCellCancelEventArgs e)
        {

        }

        private void dataGridView26_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void dataGridView26_DoubleClick(object sender, EventArgs e)
        {
            if (dataGridView26.CurrentRow == null) // Таблица с МОДами
            {
                return;
            }

            if (dataGridView23.CurrentRow == null) // Таблица со строками 
            {
                return;
            }
            // Если щелкнули крыжик - нужно изменить текущий выделенный мод

            long mod_id = Convert.ToInt32(dataGridView26.CurrentRow.Cells[0].Value);
            long row_id = Convert.ToInt32(dataGridView23.CurrentRow.Cells[3].Value);
            string strSQL = " update RRL_SBORKA_PALLET_ROWS set  CURRENT_MOD_ID = " + mod_id.ToString() + " where ID=" + row_id.ToString() + "  ";
            dataGridView23.CurrentRow.Cells[7].Value = mod_id;

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL;
            ora_com.CommandType = CommandType.Text;
            ora_com.ExecuteNonQuery();


            foreach (DataGridViewRow dr in dataGridView26.Rows)
            {
                if (dr.Cells[0].Value.ToString() != mod_id.ToString())
                {
                    dr.Cells[2].Value = false;
                }
                else {
                    dr.Cells[2].Value = true;
                
                }
            }
        }

        private void button77_Click(object sender, EventArgs e)
        {
            #region  УБИРАЕМ МОДИФИКАЦИЮ 



            if (dataGridView23.CurrentRow == null) // Таблица со строками 
            {
                return;
            }
            // Если щелкнули крыжик - нужно изменить текущий выделенный мод

            long mod_id = 0;
            long row_id = Convert.ToInt32(dataGridView23.CurrentRow.Cells[3].Value);
            string strSQL = " update RRL_SBORKA_PALLET_ROWS set  CURRENT_MOD_ID = " + mod_id.ToString() + " where ID=" + row_id.ToString() + "  ";
            dataGridView23.CurrentRow.Cells[7].Value = mod_id;

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL;
            ora_com.CommandType = CommandType.Text;
            ora_com.ExecuteNonQuery();


            foreach (DataGridViewRow dr in dataGridView26.Rows)
            {
              
                    dr.Cells[2].Value = false;
               
            }



            #endregion

        }

        private void Сторнировать_приход_Click(object sender, EventArgs e)
        {
            #region СТОРНИРОВАНИЕ ПРИХОДА

            try
            {
                int order_id = Convert.ToInt32(dataGridView_prihod.CurrentRow.Cells[6].Value.ToString());

                OracleCommand ora_com2 = new OracleCommand();
                ora_com2.Connection = get_wms_connection();
                ora_com2.CommandText = "select RRL_PRIHOD_MAY_STORNO( " + order_id.ToString()+ " ) from dual  ";
                int may_storno = Convert.ToInt32(ora_com2.ExecuteScalar());
                if (may_storno != 1) {
                    string strSQL7="   SELECT PP.UID_PALLET, PP.ARTICUL , REMAINS.REMAIN , REMAINS.CELL  " +
                    " FROM RRL_PALLETS PP , RRL_REMAINS REMAINS  where PRIHOD_NAKLAD_ID= " + order_id.ToString() + " " +
                    " and PP.UID_PALLET = REMAINS.UID_POLETA and REMAINS.CELL<>'IN_DOCK'" ;

                    ShowQuery(strSQL7, " Накладную нельзя сторнировать: часть паллет не находятся в IN_DOCK ");
                    return;
                }

                dataGridView_prihod.CurrentRow.Cells[5].Value = 3;

                // ===========================================================

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();

                ora_com.CommandText = "RRL_STORNO_ORDER3";
                ora_com.CommandType = CommandType.StoredProcedure;
                ora_com.Parameters.Add("order_id", OracleType.Int32).Value = order_id;
                ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = "KLAD_RABAEV";

                int rowsAffected = ora_com.ExecuteNonQuery();

            }
            catch (Exception ex)
            {
                MessageBox.Show(" f38 " + ex.Message);
            }
            dataGridView_prihod_CellEnter(null, null);

            #endregion

        }

        private void button78_Click(object sender, EventArgs e)
        {
            string strSQL = "select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK   " + 
                            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART " + 
                            " where R.cell='INVENT' and  " + 
                            " P.UID_PALLET =   R.UID_POLETA  and " + 
                            " P.ARTICUL = ART.ACTICUL ";
            ShowQuery( strSQL , " Паллеты в ячейке недостач " );
            
        }

        private void button79_Click(object sender, EventArgs e)
        {


           
            

            string strSQL = " select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , CEL.WARE_ID  " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , RRL_CELLS CEL " + 
            " where R.cell='IN_DOCK' and  " + 
            " P.UID_PALLET =   R.UID_POLETA  and " + 
            " P.ARTICUL = ART.ACTICUL and " + 
            " ART.CELL = CEL.CELL "+
            " and ( CEL.ware_id="+this.wms_user.ware_id.ToString()+" )  " +
            " and ( P.CREATION_DATE <=  SYSTIMESTAMP - interval '120' minute ) "+
            " and ( P.CREATION_DATE >= '" + dateTimePicker9.Value.Day + "." + dateTimePicker9.Value.Month + "." + dateTimePicker9.Value.Year + "' ) ";

            ShowQuery(strSQL, " приходы, не размещенные более 2 часов начиная с " + dateTimePicker9.Value.Day + "." + dateTimePicker9.Value.Month + "." + dateTimePicker9.Value.Year + " по складу " + this.wms_user.ware_id.ToString() + " ");

        }

        private void button80_Click(object sender, EventArgs e)
        {
            int осталосьДней = 30;
            try
            {
                осталосьДней = Convert.ToInt32( Сроки_годности.Text );
            }
            catch { }


            string strSQL = "  select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK   "+
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , rrl_cells " +
            " where " + // rrl_cells.OTBOR = 0 and  " + 
            " P.UID_PALLET =   R.UID_POLETA  and " + 
            " P.ARTICUL = ART.ACTICUL and " + 
            " R.CELL=RRL_CELLS.CELL and " + 
            " RRL_CELLS.WARE_ID="+ wms_user.ware_id +" and " + 
            " P.EXPIRY_DATE <  SYSTIMESTAMP + "+осталосьДней+" " +
            " and REMAIN>0    order by z  ,x , y   ";
            ShowQuery(strSQL, " Истекающие сроки годности по складу "+ wms_user.ware_id +". Осталось менее "+осталосьДней.ToString()+" дней ");
        }

        private void ДатаСТДо_CheckedChanged(object sender, EventArgs e)
        {
            ДатаСТДо2.Visible=ДатаСТДо.Checked;
        }

        private void вПредыдущийПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (!has_right("OP_CHANGE"))
            {
                MessageBox.Show("Нет прав на операции с паллетами (OP_CHANGE).");
                return;
            }

            #region РАБОТА С ВЫДЕЛЕННЫМИ СТРОКАМИ

               // Сначала смотрим :  есть - ли предыдущий паллет, если нет, то возвращаемся.
                string PREV_PALL = "";
                string CURRENT_PAL="";
                try
                {

                    if (dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) == 0) 
                    {
                        MessageBox.Show("Предыдущего паллета не существует.");
                        return; 
                    }

                    if (dataGridView22.Rows[dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) - 1] == null) return;
                    CURRENT_PAL=dataGridView22.CurrentRow.Cells[1].Value.ToString();
                    PREV_PALL = dataGridView22.Rows[dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) - 1].Cells[1].Value.ToString();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                    return;
                }
                string str_add="";
                foreach (DataGridViewRow dr in dataGridView23.Rows)
                {
                    if ( Convert.ToBoolean( dr.Cells[8].Value ) )
                    {
                        long row_id = Convert.ToInt32(dr.Cells[3].Value);
                        str_add = str_add +  ", "+row_id.ToString();


                        #region ПЕРЕНОС СТРОКИ В СЛЕДУЮЩИЙ ПАЛЛЕТ ПРОИЗВОДИТСЯ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ.

                            OracleCommand ora_com = new OracleCommand();
                            ora_com.Connection = get_wms_connection();
                            ora_com.CommandText = "RABAEV.RRL_UPDATE_SBORKA_PALLET_ROWS2";
                            ora_com.CommandType = CommandType.StoredProcedure;
                            ora_com.Parameters.Add("PALLET_UID_to", OracleType.VarChar).Value = PREV_PALL;
                            ora_com.Parameters.Add("row_id_from", OracleType.Int32).Value = row_id;
                            ora_com.Parameters.Add("ret", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
                            int rowsAffected = ora_com.ExecuteNonQuery();


                        #endregion

                    }
                }

                if (str_add == "")
                {
                    MessageBox.Show( " Не выбрано ни одной позиции. Паллеты должны быть выделены флажком." );
                    return;
                }
               /*
                str_add = str_add.Trim(',');
                string strSQL = " update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = '" + PREV_PALL + "' , selected=1 where ID in ( " + str_add + " ) ";
                

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = strSQL ;
                int rowsAffected = ora_com.ExecuteNonQuery();
            */
                dataGridView22_CellEnter(null, null);

            #endregion
        }

        private void вСледующийПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {

            string PREV_PALL = "";
            string CURRENT_PAL = "";
            try
            {

            if (!has_right("OP_CHANGE"))
            {
                MessageBox.Show("Нет прав на операции с паллетами (OP_CHANGE).");
                return;
            }

            #region РАБОТА С ВЫДЕЛЕННЫМИ СТРОКАМИ

            // Сначала смотрим :  есть - ли предыдущий паллет, если нет, то возвращаемся.



                if (dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) < 0) return;
                if (dataGridView22.Rows.Count <= dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) + 1)
                {
                    MessageBox.Show(" Следующего паллета не существует. ");
                    return;
                }
                CURRENT_PAL = dataGridView22.CurrentRow.Cells[1].Value.ToString();
                PREV_PALL = dataGridView22.Rows[dataGridView22.Rows.IndexOf(dataGridView22.CurrentRow) + 1].Cells[1].Value.ToString();
            }
            catch (Exception ex)
            {
                MessageBox.Show("err6903: "+ex.Message);
                return;
            }



            try
            {
                string str_add = "";
                foreach (DataGridViewRow dr in dataGridView23.Rows)
                {
                    if (Convert.ToBoolean(dr.Cells[8].Value))
                    {
                        long row_id = Convert.ToInt32(dr.Cells[3].Value);
                        str_add = str_add + ", " + row_id.ToString();

                        #region ПЕРЕНОС СТРОКИ В СЛЕДУЮЩИЙ ПАЛЛЕТ ПРОИЗВОДИТСЯ ПРИ ПОМОЩИ ХРАНИМОЙ ПРОЦЕДУРЫ.

                        OracleCommand ora_com = new OracleCommand();
                        ora_com.Connection = get_wms_connection();
                        ora_com.CommandText = "RABAEV.RRL_UPDATE_SBORKA_PALLET_ROWS2";
                        ora_com.CommandType = CommandType.StoredProcedure;
                        ora_com.Parameters.Add("PALLET_UID_to", OracleType.VarChar).Value = PREV_PALL;
                        ora_com.Parameters.Add("row_id_from", OracleType.Int32).Value = row_id;
                        ora_com.Parameters.Add("ret", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected = ora_com.ExecuteNonQuery();


                        #endregion

                    }
                }

                if (str_add == "")
                {
                    MessageBox.Show(" Не выбрано ни одной позиции.");
                    return;
                }
                /*
                str_add = str_add.Trim(',');
                string strSQL = " update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = '" + PREV_PALL + "' , selected=1 where ID in ( " + str_add + " ) ";



                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = strSQL;
                int rowsAffected = ora_com.ExecuteNonQuery();
                */

                dataGridView22_CellEnter(null, null);
            }
            catch (Exception ex)
            {
                MessageBox.Show("err6902: " + ex.Message);
                return;
            }


            #endregion
        }

        private void создатьНовыйПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string NEW_PALL_UID ="";
            string CURRENT_PAL = "";


            if (!has_right("OP_CHANGE"))
            {
                MessageBox.Show("Нет прав на операции с паллетами (OP_CHANGE).");
                return;
            }

            #region СОЗДАЕМ НОВЫЙ ПАЛЛЕТ
           

            try
            {

                CURRENT_PAL = dataGridView22.CurrentRow.Cells[1].Value.ToString();

                OracleCommand ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_GIVE_NEXT_OPALLET_NUMBER";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("PREV_PALLET_ID", OracleType.VarChar).Value = CURRENT_PAL;
                ora_com.Parameters.Add("USER_ID1", OracleType.VarChar).Value = wms_user.user_id;
                ora_com.Parameters.Add("ID", OracleType.VarChar,100).Direction = ParameterDirection.ReturnValue;
                ora_com.ExecuteNonQuery();
                NEW_PALL_UID = ora_com.Parameters["ID"].Value.ToString() ;
              
                if (NEW_PALL_UID == "")
                {
                    MessageBox.Show("Ошибка в определении номера следующего паллета.");
                    return;
                }
                
                

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return;
            }
            
                
            #endregion




            #region Убираем выделенные строки в новый паллет

            // Сначала смотрим :  есть - ли предыдущий паллет, если нет, то возвращаемся.


            string str_add = "";
            foreach (DataGridViewRow dr in dataGridView23.Rows)
            {
                if (Convert.ToBoolean(dr.Cells[8].Value))
                {
                    long row_id = Convert.ToInt32(dr.Cells[3].Value);
                    str_add = str_add + ", " + row_id.ToString();
                }
            }
            str_add = str_add.Trim(',');
            string strSQL = " update RRL_SBORKA_PALLET_ROWS  set  PALLET_UID = '" + NEW_PALL_UID + "' , selected=1 where ID in ( " + str_add + " ) ";



            OracleCommand ora_com2 = new OracleCommand();
            ora_com2.Connection = get_wms_connection();
            ora_com2.CommandText = strSQL;
            int rowsAffected = ora_com2.ExecuteNonQuery();

            dataGridView21_CellEnter(null, null);

            #endregion



        }

        private void убратьФлажкиToolStripMenuItem_Click(object sender, EventArgs e)
        {



        }

        private void dataGridView23_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode == Keys.F5)
            {

                foreach (DataGridViewRow dr in dataGridView23.Rows)
                {
                    dr.Cells[8].Value = dr.Cells[0].Selected;
                }
            }

            if (e.KeyCode == Keys.F6)
            {

                foreach (DataGridViewRow dr in dataGridView23.Rows)
                {
                    dr.Cells[8].Value = false;
                }
            }


        }

        private void удалитьПустойПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView23.Rows.Count != 0)
            {
                MessageBox.Show("Паллет не пустой!");
                return;
            }

            if (!has_right("OP_DELETE"))
            {
                MessageBox.Show("Нет прав на операции с паллетами (OP_DELETE).");
                return;
            }



           string CURRENT_PAL = dataGridView22.CurrentRow.Cells[1].Value.ToString();

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = "RABAEV.RRL_DELETE_OPALLET";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("PALLET_ID1", OracleType.VarChar).Value = CURRENT_PAL;
            ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            //NEW_PALL_UID = ora_com.Parameters["ID"].Value.ToString();


            dataGridView21_CellEnter(null, null);

        }

        private void button81_Click(object sender, EventArgs e)
        {




            string strSQL = "select RRL_CELLS.CELL  , X  ,Y , Z , BLOCKED_FOR_ACCEPT БЛОК_ПРИЕМКИ , BLOCKED_FOR_REMAINS БЛОК_ОСТАТКОВ , BLOCKED_FOR_POPOLNENIE БЛОК_ПОПОЛНЕНИЯ , LAST_TIME_OF_UPDATE " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where   " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+)  and ( RRL_REMAINS.CELL is null) " +
                " and RRL_CELLS.OTBOR=0 and RRL_CELLS.IS_SYSTEM=0 " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString()+
                "  order by Z,Y,X ";
            ShowQuery(strSQL, "Отчет по пустым ячейкам");


        }

        private void button82_Click(object sender, EventArgs e)
        {



            string sql2 = "";
            if (m_выбранный_склад.Text != "")
            {
                sql2 = " and ( CEL.ware_id=" + m_выбранный_склад.Text.ToString() + " )  ";
            }

            string strSQL = " select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , CEL.WARE_ID , R.cell  " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , RRL_CELLS CEL " +
            " where  ( REMAIN>0 ) and R.cell in ( 'IN_DOCK' , 'TRASH' ) and  " +
            " P.UID_PALLET =   R.UID_POLETA  and " +
            " P.ARTICUL = ART.ACTICUL and " +
            " ART.CELL = CEL.CELL " +
            sql2 +
            " and ( P.CREATION_DATE <=  SYSTIMESTAMP - interval '120' minute ) " +
            " and ( P.CREATION_DATE >= '" + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + "' ) ";

            ShowQuery(strSQL, " приходы, не размещенные более 2 часов начиная с " + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + " по складу " + m_выбранный_склад.Text.ToString() + " ");


        }

        private void dataGridView18_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {

            
            //e.CellStyle.Alignment = DataGridViewContentAlignment.MiddleRight;

            if (e.ColumnIndex == 1)
            {
                if (obj2int(dataGridView18[10, e.RowIndex].Value) >= 100)
                {
                    e.CellStyle.BackColor = Color.Green;
                }

                if ((obj2int(dataGridView18[10, e.RowIndex].Value) < 100) && (obj2int(dataGridView18[10, e.RowIndex].Value) > 0))
                {
                    e.CellStyle.BackColor = Color.GreenYellow;
                }

            }

            if (e.ColumnIndex == 6)
            {
                if (obj2int(dataGridView18[17, e.RowIndex].Value) >= 1)
                {
                    e.CellStyle.BackColor = Color.LightCoral;
                }
            }

            if (e.ColumnIndex == 2)
            {
                if (obj2int(dataGridView18[15, e.RowIndex].Value) >= 1)
                {
                    e.CellStyle.BackColor = Color.LightSteelBlue;
                }
            }

            /*  if (DataGridView.Columns[e.ColumnIndex].DataPropertyName == "Table") 
                if (DataGridView["1", e.RowIndex].Value.ToString() == "1") 
                    e.CellStyle.BackColor = Color.Red; 
                else if (DataGridView["1", e.RowIndex].Value.ToString() == "2") 
                    e.CellStyle.BackColor = Color.Green; 
        */

        }

        private void button83_Click(object sender, EventArgs e)
        {

            #region ПОДГРУЗКА ПРАЙСА

            long pos = 2;
            try
            {

                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();



                string Filename = "C:\\WMS\\Цены.xls"; //=ofd.SafeFileName;


                try
                {

                    oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);
                    pos=1;

                    if(
                        ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString()!="РЕГИОН" || 
                        ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString()!="КОМПАНИЯ" || 
                        ((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString() !="РАССТОЯНИЕ" || 
                        ((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString() !="ЦЕНА" ||
                         ((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString() != "ЦЕНА ЗА ТОЧКУ" 
                    ){ 
                        MessageBox.Show(" файл должен иметь структуру: РЕГИОН - КОМПАНИЯ - РАССТОЯНИЕ - ЦЕНА - ЦЕНА ЗА ТОЧКУ ");
                        return;
                    }
                
                
                }
                catch (Exception ex)
                {
                    MessageBox.Show( ex.Message );
                    return;
                }



                    #region ЗАкачка с 1 листа
                    pos = 2;
                    while (obj2str(((Excel.Range)oExcelApp.Cells[pos, 1]).Value2) != "")
                    {

                        string PRICE_NAME1 = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
                        string COMPANY2 = "";
                        COMPANY2 = obj2str(((Excel.Range)oExcelApp.Cells[pos, 2]).Value2);
                        double kilometers1 = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString().Replace('.', ','));
                        double PRICE2 = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 4]).Value2.ToString().Replace('.', ','));
                        double PRICE2_ADDR = Convert.ToDouble(((Excel.Range)oExcelApp.Cells[pos, 5]).Value2.ToString().Replace('.', ','));
                        
                        // ================================================================

                        OracleCommand ora_com = new OracleCommand();
                        ora_com.Connection = get_wms_connection();
                        ora_com.CommandText = "RABAEV.RRL_SET_TRANSPORT_PRICE";
                        ora_com.CommandType = CommandType.StoredProcedure;
                        ora_com.Parameters.Add("PRICE_NAME1", OracleType.VarChar).Value = PRICE_NAME1;
                        string PATH_NAME = PRICE_NAME1.Substring(PRICE_NAME1.IndexOf(']') + 1);
                        ora_com.Parameters.Add("PATH_NAME1", OracleType.VarChar).Value = PATH_NAME;
                        ora_com.Parameters.Add("PRICE2", OracleType.Number).Value = PRICE2;
                        ora_com.Parameters.Add("kilometers1", OracleType.Number).Value = kilometers1;

                        ora_com.Parameters.Add("price_hours1", OracleType.Number).Value = 0;
                        ora_com.Parameters.Add("PRICE2_ADDR", OracleType.Number).Value = PRICE2_ADDR; 
                        ora_com.Parameters.Add("COMPANY2", OracleType.VarChar).Value = COMPANY2;
                        ora_com.Parameters.Add("tmpVar", OracleType.VarChar, 25).Direction = ParameterDirection.ReturnValue;
                        int rowsAffected = ora_com.ExecuteNonQuery();
                        string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                        // ================================================================
                        pos++;
                    }
                    #endregion



                    MessageBox.Show("Данные загружены из Excel. Количество подгруженных строк=" + pos.ToString());
            }
            catch (Exception ex)
            {
                MessageBox.Show(Convert.ToString(pos) + " _ " + ex.Message);
            }
            // ================================

            #endregion


        }

        private void пересчитатьТекущийРейсToolStripMenuItem_Click(object sender, EventArgs e)
        {

            if (!has_right("CALC_TT_PRICE"))
            {
                MessageBox.Show(" У вас нет прав на CALC_TT_PRICE ");
                return;
            }

            DataGridViewRow dr= dataGridView17.CurrentRow;
            if(dr==null) return;
            string tt_id = dr.Cells[1].Value.ToString();
            if (obj2int(tt_id) == 0)
            {
                return;
            }

            string ret = wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
            double price = obj2double(ret);
            
            #region ЕСЛИ ПРАЙС=0, то его просто нет в базе, надо внести
            if (price == 0)
            {
                if (has_right("CREATE_TT_PRICE"))
                {

                    string reg = wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID", "tt_id", tt_id);
                    string rai = wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID2", "tt_id", tt_id);

                    ПРАЙСЫ пр = new ПРАЙСЫ();
                    пр.РАЙОН = rai;
                    пр.РЕГИОН = reg;
                    пр.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
                    пр._pparent = this;
                    пр.ShowDialog();

                }
                else {
                    MessageBox.Show(" У вас нет прав на CREATE_TT_PRICE ");
                    return;
                }

            }
            #endregion

            dataGridView17.CurrentRow.Cells[13].Value = price;
      


        }

        private void пересчитатьВсеВыделенныеРейсыToolStripMenuItem_Click(object sender, EventArgs e)
        {


            if (!has_right("CALC_TT_PRICE"))
            {
                MessageBox.Show(" У вас нет прав на CALC_TT_PRICE ");
                return;
            }

            foreach (DataGridViewRow dr in dataGridView17.Rows)
            {
                
                if (dr == null) return;
                #region По всем  рейсам
                if (1==1 /*dr.Cells[1].Selected*/)
                {
                    string tt_id = dr.Cells[1].Value.ToString();
                    if (obj2int(tt_id) == 0)
                    {
                        return;
                    }
                    string ret = wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
                    double price = obj2double(ret);

                    #region ЕСЛИ ПРАЙС=0, то его просто нет в базе, надо внести
                    
                    #endregion

                    dr.Cells[13].Value = price;
                }
                #endregion
            }



        }




        private void пересчитатьСтавкуToolStripMenuItem_Click(object sender, EventArgs e)
        {



            if (!has_right("CALC_TT_PRICE"))
            {
                MessageBox.Show(" У вас нет прав на CALC_TT_PRICE ");
                return;
            }

            DataGridViewRow dr = dataGridView17.CurrentRow;
            if (dr == null) return;
            string tt_id = dr.Cells[1].Value.ToString();
            string l_company = dr.Cells[14].Value.ToString();

            if (obj2int(tt_id) == 0)
            {
                return;
            }
            string ret = wms_get_spfunction_n2n_value("RRL_UPDATE_PRICE", "tt_id", tt_id);
            double price = obj2double(ret);

            #region ЕСЛИ ПРАЙС=0, то его просто нет в базе, надо внести
            if (1==1)
            {
                if (has_right("CREATE_TT_PRICE"))
                {

                    string reg = wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID", "tt_id", tt_id);
                    string rai = wms_get_spfunction_n2c_value("RRL_GET_TT_PRICE_ID2", "tt_id", tt_id);

                    #region  даем редактировать прайс компании, иначе - редактируем общий прайс
                    // Определяем компанию данного рейса. Если есть прайс на данный регион или район по компании, то 
                    //

                    string strSQL = " select count( PRICE  ) " +
                    " from RRL_TRANSPORT_PRICE where ( PRICE_NAME='" + reg + "' or  PRICE_NAME='" + rai + "' ) " +
                    " and ( COMPANY='" + l_company + "'   ) ";
                    OracleCommand ora_comm2 = new OracleCommand();
                    ora_comm2.CommandText=strSQL;
                    ora_comm2.Connection = get_wms_connection();
                    long l_есть_ли_прайс = obj2int( ora_comm2.ExecuteScalar() );


                    OracleCommand ora_comm3 = new OracleCommand();
                    ora_comm3.CommandText = "   select CC.SPECIAL_PRICE  "+
                        " from RABAEV.RRL_BILL_COMPANY CC where CC.COMPANYNAME =  '" + l_company + "'   ";
                    ora_comm3.Connection = get_wms_connection();
                    long l_специальный_прайс = obj2int(ora_comm3.ExecuteScalar());

                    #endregion

                    ПРАЙСЫ пр = new ПРАЙСЫ();
                    пр.РАЙОН = rai;
                    пр.РЕГИОН = reg;
                    пр.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING_INST;
                    if ((l_есть_ли_прайс > 0) || (l_специальный_прайс > 0))
                    {
                        пр.КОНТОРА = l_company;
                    }
                    пр._pparent = this;
                    пр.ShowDialog();

                }
                else
                {
                    MessageBox.Show(" У вас нет прав на CREATE_TT_PRICE ");
                    return;
                }

            }
            #endregion

            dataGridView17.CurrentRow.Cells[13].Value = price;





        }

        private void поРегионамToolStripMenuItem_Click(object sender, EventArgs e)
        {


            string add_sql1 = "";
            string add_sql2 = "";
            string add_sql3 = "";
            string add_sql4 = "";
            string add_sql5 = "";

            m_map_V = 0;
            m_map_WEIGHT = 0;
            m_map_P = 0;

            if (МаскаСТ.Text != "")
            {
                add_sql4 = " and ( P.ST_NUMBER like '%" + МаскаСТ.Text + "%' ) ";

            }

            if (МаскаСкладов.Text != "")
            {
                add_sql1 = " and ( RRL_SKLADNAME_BY_ID( P.ware_id ) in ( " + МаскаСкладов.Text + " )) ";
            }

            if (МаскаАдреса.Text != "")
            {
                add_sql2 = " and ( P.ADDR like '%" + МаскаАдреса.Text + "%' ) ";
            }

            if (НЕ_РАСПРЕДЕЛЕННЫЕ.Checked)
            {
                add_sql3 = " and ( ( TRANSTASK_ID is null ) or (  TRANSTASK_ID=0 ) ) ";
            }

            if (датаСТУч.Checked)
            {
                add_sql5 = " and ( P.STDATE = " + date2sql_ora(dateTimePicker5.Value) + " ) ";
            }

            string strSQL = " select   " +
                " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , " +
                " round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  count( R.ID ) строки  ,  " +
                "  RRL_ADDR.REGION , " +
                "   RRL_ADDR.TRANSPORT_TYPE  " +
                " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R  , rrl_addr  where " +
                " R.PALLET_UID=P.PALLET_UID  and  ( P.ADDR=RRL_ADDR.ADDR(+) )  " + add_sql1 + add_sql2 + add_sql3 + add_sql4 + add_sql5 +
                "group by          RRL_ADDR.REGION , RRL_ADDR.TRANSPORT_TYPE   ,  P.STDATE  " +
                " order by RRL_ADDR.REGION   , RRL_ADDR.TRANSPORT_TYPE  ";
            ShowQuery(strSQL, "СВОДНАЯ ПО СТ ЗА " + dateTimePicker5.Value.ToString());


        }

        private void поРайонамToolStripMenuItem_Click(object sender, EventArgs e)
        {

            string add_sql1 = "";
            string add_sql2 = "";
            string add_sql3 = "";
            string add_sql4 = "";
            string add_sql5 = "";

            m_map_V = 0;
            m_map_WEIGHT = 0;
            m_map_P = 0;

            if (МаскаСТ.Text != "")
            {
                add_sql4 = " and ( P.ST_NUMBER like '%" + МаскаСТ.Text + "%' ) ";

            }

            if (МаскаСкладов.Text != "")
            {
                add_sql1 = " and ( RRL_SKLADNAME_BY_ID( P.ware_id ) in ( " + МаскаСкладов.Text + " )) ";
            }

            if (МаскаАдреса.Text != "")
            {
                add_sql2 = " and ( P.ADDR like '%" + МаскаАдреса.Text + "%' ) ";
            }

            if (НЕ_РАСПРЕДЕЛЕННЫЕ.Checked)
            {
                add_sql3 = " and ( ( TRANSTASK_ID is null ) or (  TRANSTASK_ID=0 ) ) ";
            }

            if (датаСТУч.Checked)
            {
                add_sql5 = " and ( P.STDATE = " + date2sql_ora(dateTimePicker5.Value) + " ) ";
            }

            string strSQL = " select   " +
                " count( DISTINCT P.PALLET_UID ) колвоПаллет , round( sum(R.ORDER_WEIGHT ) , 0 ) вес  , " +
                " round( sum( R.TARESIZE * ( R.PACK_COUNT ) )/1000000 ,2 ) объем ,  count( R.ID ) строки  ,  " +
                "  RRL_ADDR.REGION , " +
                "  RRL_ADDR.RAION , RRL_ADDR.TRANSPORT_TYPE  " +
                " from RRL_SBORKA_PALLETS P  , RRL_SBORKA_PALLET_ROWS R  , rrl_addr  where " +
                " R.PALLET_UID=P.PALLET_UID  and  ( P.ADDR=RRL_ADDR.ADDR(+) )  " + add_sql1 + add_sql2 + add_sql3 + add_sql4 + add_sql5 +
                "group by          RRL_ADDR.REGION , RRL_ADDR.TRANSPORT_TYPE ,  RRL_ADDR.RAION  ,  P.STDATE  " +
                " order by RRL_ADDR.REGION  ,  RRL_ADDR.RAION  , RRL_ADDR.TRANSPORT_TYPE  ";
            ShowQuery(strSQL, "СВОДНАЯ ПО СТ ЗА " + dateTimePicker5.Value.ToString());


        }

        private void button84_Click(object sender, EventArgs e)
        {
            int осталосьДней = 30;
            try
            {
                осталосьДней = Convert.ToInt32(Сроки_годности.Text);
            }
            catch { }


            string strSQL = "  select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , " +
                " R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , ART.BESTBEFOREDAYS СГ , extract( day from ( P.EXPIRY_DATE - SYSTIMESTAMP ) ) Осталось " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , rrl_cells " +
            " where   " +
            " P.UID_PALLET =   R.UID_POLETA  and " +
            " P.ARTICUL = ART.ACTICUL and " +
            " R.CELL=RRL_CELLS.CELL and " +
            " RRL_CELLS.WARE_ID=" + wms_user.ware_id + " and " +
            " RRL_MAY_DISTRIBUTE(  P.ARTICUL , P.EXPIRY_DATE )=0 " +
            " and REMAIN>0 "; // and rrl_cells.OTBOR=0 ";
            ShowQuery(strSQL, " Истекающие сроки годности по складу " + wms_user.ware_id + ". Осталось менее " + осталосьДней.ToString() + " дней ");
 
        }

        private void button85_Click(object sender, EventArgs e)
        {

            string strSQL = "  select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , " +
                " R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , ART.BESTBEFOREDAYS СГ , extract( day from ( P.EXPIRY_DATE - SYSTIMESTAMP ) ) Осталось ,  RRL_MAY_DISTRIBUTE(  P.ARTICUL , P.EXPIRY_DATE ) РазрешенКОтгрузке " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , rrl_cells " +
            " where   " +
            " P.UID_PALLET =   R.UID_POLETA  and " +
            " P.ARTICUL = ART.ACTICUL and " +
            " R.CELL=RRL_CELLS.CELL and " +
            " RRL_CELLS.WARE_ID=" + wms_user.ware_id + "   " +
            " " +
            " and REMAIN>0 " ;// and rrl_cells.OTBOR=0 ";
            ShowQuery(strSQL, "Отчет по срокам годности по складу " + wms_user.ware_id  );



        }

        private void dataGridView13_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void button86_Click(object sender, EventArgs e)
        {

            BillingTransport bt = new BillingTransport();
            bt.WMS_CONNECTION_STRING_INST = this.WMS_CONNECTION_STRING();
            bt.__parent = this;
            bt.Show();


        }

        private void изменитьЛогопараметрыToolStripMenuItem_Click(object sender, EventArgs e)
        {
            try
            {
                long row_id = obj2int(dataGridView23.CurrentRow.Cells[3].Value);
            
            
            }
            catch 
            {
            
            }
        }

        private void button88_Click(object sender, EventArgs e)
        {



            string strSQL = " select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , CEL.WARE_ID  " +
          " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , RRL_CELLS CEL " +
          " where R.cell<>'IN_DOCK' and  " +
          " P.UID_PALLET =   R.UID_POLETA  and " +
          " P.ARTICUL = ART.ACTICUL and " +
          " ART.CELL = CEL.CELL " +
          " and ( CEL.ware_id=" + this.wms_user.ware_id.ToString() + " )  " +
          " and ( P.CREATION_DATE <=  SYSTIMESTAMP - interval '120' minute ) " +
          " and ( P.CREATION_DATE >= '" + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + "' ) ";

            ShowQuery(strSQL, " приходы, не размещенные более 2 часов начиная с " + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + " по складу " + this.wms_user.ware_id.ToString() + " ");




        }

        private void button89_Click(object sender, EventArgs e)
        {

            string strSQL2 = "";
            string strSQL3 = "";

            int pos = 0;
            foreach (string lll2 in СТ_ИЗ_СУПЕРМАГА.Lines)
            {
                
                if (lll2.Trim() != "")
                {

                    string [] split = lll2.Trim().Split( new Char[]{' ' , '\t'});
                    if (split.Length == 2)
                    {
                        strSQL2 = strSQL2 + " (PAL.pallet_uid like '%" + split.GetValue(0).ToString() + "%'  and ROWSs.ARTICUL='" + split.GetValue(1).ToString() + "' ) or";

                    }else{
                        strSQL2 = strSQL2 + " (PAL.pallet_uid like '%" + lll2 + "%') or";
                    }
                    pos++;
                }
                
            }
            if (pos == 0)
            {
                MessageBox.Show( " Внесите номера ст в окно. " );
                return;
            }
            strSQL2 = strSQL2.Trim('r').Trim('o');
            strSQL2 = "    select PAL.ware_id , PAL.create_date , PAL.pallet_uid , PAL.addr , PAL.user_id Загрузил ,  " + 
                             " PAL.SBORSHIK Сборщик , PAL.KLADOVSHIK Кладовщик , PAL.VESOVSHIK Весовщик , PAL.PROOVED_BY_SCAN Перебран , PAL.PROOVED ВесСовпал   " +
                             " FROM rabaev.rrl_sborka_pallets pal left join  rabaev.rrl_sborka_pallet_rows rowss on pal.pallet_uid = rowss.pallet_uid(+) " +
                             " where   " + strSQL2 + "  "+
                             " group by "+
            "  PAL.ware_id , PAL.create_date , PAL.pallet_uid , PAL.addr , PAL.user_id   ,  " + 
                             " PAL.SBORSHIK   , PAL.KLADOVSHIK   , PAL.VESOVSHIK   , PAL.PROOVED_BY_SCAN   , PAL.PROOVED    ";

            ShowQuery(strSQL2, " Кто собирал, проверял и взвешивал паллеты ");


        }

        private void button90_Click(object sender, EventArgs e)
        {

            ShowQuery( textBox_Запрос.Text , " Запрос ");


        }

        private void гдеНаходитсяТоварВХраненииToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView11.CurrentRow == null)
            {
                MessageBox.Show("Выберите артикул");
                return;
            }

            string art= dataGridView11.CurrentRow.Cells[0].Value.ToString();

            string strSQL = "  select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , " +
                " R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , ART.BESTBEFOREDAYS СГ , extract( day from ( P.EXPIRY_DATE - SYSTIMESTAMP ) ) Осталось ,  RRL_MAY_DISTRIBUTE(  P.ARTICUL , P.EXPIRY_DATE ) РазрешенКОтгрузке " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , rrl_cells " +
            " where   " +
            " P.UID_PALLET =   R.UID_POLETA  and " +
            " P.ARTICUL = ART.ACTICUL and " +
            " P.ARTICUL = '"+art+"' and " + 
            " R.CELL=RRL_CELLS.CELL   " +
            " " +
            " and REMAIN>0 and rrl_cells.OTBOR=0 ";
            ShowQuery(strSQL, "Отчет по срокам годности по артикулу " + art);


        }

        private void button91_Click(object sender, EventArgs e)
        {


            string strSQL =" select ID, USER_ID , ADDR_TO , ADDR_FROM , MESS , PUID , "+
                " COUNT1 , EVENTDATE  from RABAEV.RRL_HISTORY_NOTES where EVENTDATE<="+date2sql_ora( dateTimePicker10.Value.AddDays(1) )+
                " and EVENTDATE>= " + date2sql_ora(dateTimePicker10.Value.AddDays(0)) + " order by EVENTDATE ";
            ShowQuery(  strSQL , "Ошибки карщиков");

        }

        private void button92_Click(object sender, EventArgs e)
        {


            string strSQL = " select  R.UID_POLETA , P.ARTICUL , ART.NAME , RRL_EVENTS.USER_ID , "+
                " RRL_EVENTS.CELL_FROM , "+
                " R.TIME_OF_LAST_UPDATE , " +
                "  REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , R.CELL  , P.CREATION_DATE "+
                " , P.EXPIRY_DATE ,    KLADOVSHIK , CEL.WARE_ID , otbor  " +
           " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , RRL_CELLS CEL , RRL_EVENTS " +
           " where R.cell in ( 'INVENT' , 'TRASH'  )   " +
           " and  RRL_EVENTS.UID_POLETA =  P.UID_PALLET  "+
           " and RRL_EVENTS.CELL_TO='INVENT' " +
           " and P.UID_PALLET =   R.UID_POLETA   " +
           " and P.ARTICUL = ART.ACTICUL  " +
           " and ART.CELL = CEL.CELL " +
           //" and ( CEL.ware_id=" + this.wms_user.ware_id.ToString() + " )  " +
           " and ( P.CREATION_DATE <=  SYSTIMESTAMP - interval '1' minute ) " +
           " and ( P.CREATION_DATE >= '" + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + "' ) ";

            ShowQuery(strSQL, " Паллеты, упавшие в ячейку недостач начиная с " + dateTimePicker10.Value.Day + "." + dateTimePicker10.Value.Month + "." + dateTimePicker10.Value.Year + " по складу " + this.wms_user.ware_id.ToString() + " ");


        }

        private void НеОтправлятьНаСевер_Click(object sender, EventArgs e)
        {


            int осталосьДней = 30;
            try
            {
                осталосьДней = Convert.ToInt32(Сроки_годности.Text);
            }
            catch { }


            string strSQL = "  select  R.UID_POLETA , P.ARTICUL , ART.NAME , R.TIME_OF_LAST_UPDATE ,   REMAIN  КОЛИЧЕСТВО  , round( REMAIN*PRICE , 0 ) СУММА , " +
                " R.CELL  , P.CREATION_DATE  , P.EXPIRY_DATE , KLADOVSHIK , ART.BESTBEFOREDAYS СГ , extract( day from ( P.EXPIRY_DATE - SYSTIMESTAMP ) ) Осталось " +
            " from rrl_remains   R , RRL_PALLETS P , RRL_ARTICULS ART , rrl_cells " +
            " where   " +
            " P.UID_PALLET =   R.UID_POLETA  and " +
            " P.ARTICUL = ART.ACTICUL and " +
            " R.CELL=RRL_CELLS.CELL and " +
            " RRL_CELLS.WARE_ID=" + wms_user.ware_id + " and " +
            " RRL_MAY_DISTRIBUTE(  P.ARTICUL , P.EXPIRY_DATE - interval '5' day )=0 " +
            " and REMAIN>0 " ; // " and rrl_cells.OTBOR=0 ";
            ShowQuery(strSQL, "Нельзя отправлять на север: Истекающие сроки годности по складу " + wms_user.ware_id + ". Осталось менее " + осталосьДней.ToString() + " дней ");
 


        }

        private void button93_Click(object sender, EventArgs e)
        {


            long ware_id = 0;
            try { ware_id = Convert.ToInt32(m_выбранный_склад.Text); }
            catch { }

            if (ware_id == 0) ware_id = this.wms_user.ware_id;

            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1.AddDays(1);
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }





         string strSQL = "    SELECT  sum( (rrl_pal_row_count (p.pallet_uid))  ) СТРОКИ, " + 
            " count( distinct p.sborshik ) СБОРЩИКИ , " + 
            "    to_char(nnn.time1  , 'HH24-DD-MM-YYYY' ) Время ,        " + 
            "       to_char(nnn.time1  , 'HH24' ) ЧАС , " + 
            "       to_char(nnn.time1  , 'DD' ) ДЕНЬ , " + 
            "       to_char(nnn.time1  , 'MM' ) МЕС , " + 
            "       to_char(nnn.time1  , 'YYYY' ) ГОД ,    " +     
            "   round(  sum(   nnn.weight ) / 1000 , 0) ВЕС " + 
            "  FROM rrl_sborka_pallets p, rusers u1, rrl_sborka_pallets_history nnn " + 
            " WHERE (NOT (sborshik IS NULL)) " +
            " and  (p.ware_id=" + ware_id.ToString() +") " +
               "   AND (p.sborshik = u1.ID(+)) " +
               "   AND (p.pallet_uid = nnn.pallet_uid(+)) " +
               "   AND NOT (nnn.pallet_uid IS NULL) " +
               "   AND  ( STDATE>=" + date2sql_ora(dt1) + " ) " +
               "   AND  ( STDATE<=" + date2sql_ora(dt2) + " )  " +
               "   group by  " +
               "          to_char(nnn.time1  , 'HH24' ) , " +
               "       to_char(nnn.time1  , 'DD' ) , " +
               "       to_char(nnn.time1  , 'MM' ) , " +
               "       to_char(nnn.time1  , 'YYYY' ) , " +
               "       to_char(nnn.time1  , 'HH24-DD-MM-YYYY' )  " +
               "   order by  " +
               "        to_char(nnn.time1  , 'YYYY' ) , " +
               "        to_char(nnn.time1  , 'MM' ) , " +
               "        to_char(nnn.time1  , 'DD' ) , " +
               "        to_char(nnn.time1  , 'HH24' )  ";

            object[] o = ShowQuery(strSQL, "Сводная:  производительность сборщиков  ");



        }

        private void убратьЧастьВСледующийПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {

            OracleCommand ora_com;
            string NEW_PALL_UID = "";
            string CURRENT_PAL = "";
            double количество_переноса = 1;


            if (!has_right("OP_CHANGE"))
            {
                MessageBox.Show("Нет прав на операции с паллетами (OP_CHANGE).");
                return;
            }

            #region  р
            try{
            string aa = ask( "Сколько ШТУК убирать в следующий паллет?" );
            количество_переноса = Convert.ToDouble(aa);
            }catch( Exception ex ){
                MessageBox.Show(ex.Message);
                return;
            }
            #endregion


            #region СОЗДАЕМ НОВЫЙ ПАЛЛЕТ


            try
            {

                CURRENT_PAL = dataGridView22.CurrentRow.Cells[1].Value.ToString();

                ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_GIVE_NEXT_OPALLET_NUMBER";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("PREV_PALLET_ID", OracleType.VarChar).Value = CURRENT_PAL;
                ora_com.Parameters.Add("USER_ID1", OracleType.VarChar).Value = wms_user.user_id;
                ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
                ora_com.ExecuteNonQuery();
                NEW_PALL_UID = ora_com.Parameters["ID"].Value.ToString();

                if (NEW_PALL_UID == "")
                {
                    MessageBox.Show("Ошибка в определении номера следующего паллета.");
                    return;
                }



            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return;
            }


            #endregion




            #region Создаем и переносим копию выделенной строки в новый паллет

            // Сначала смотрим :  есть - ли предыдущий паллет, если нет, то возвращаемся.


          
           long row_id = Convert.ToInt32(dataGridView23.CurrentRow.Cells[3].Value);
          
            
                ora_com = new OracleCommand();
                ora_com.Connection = get_wms_connection();
                ora_com.CommandText = "RABAEV.RRL_COPY_PALLET_ROW2";
                ora_com.CommandType = CommandType.StoredProcedure;

                ora_com.Parameters.Add("row_id2", OracleType.Int32).Value = row_id;
                ora_com.Parameters.Add("count1", OracleType.Number).Value = 1;
                ora_com.Parameters.Add("PALLET_UID_NEW", OracleType.VarChar ).Value = NEW_PALL_UID;

            
            

                ora_com.Parameters.Add("ID", OracleType.VarChar, 100).Direction = ParameterDirection.ReturnValue;
                ora_com.ExecuteNonQuery();
                NEW_PALL_UID = ora_com.Parameters["ID"].Value.ToString();







            dataGridView21_CellEnter(null, null);

            #endregion





        }

        private void распечататьПаспортНаПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow == null) { return; }
            string PALL_UID1= dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow.Cells[0].Value.ToString();





            PPage _page = get_prihod_pallet_print_page(PALL_UID1, ЯЧЕЙКА_ОТКУДА.Text);

            PPages.Add(_page);

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {

                pd.DefaultPageSettings.Landscape = true;
                //if( pd.DefaultPageSettings.PrinterSettings.CanDuplex )
                // pd.DefaultPageSettings.PrinterSettings.Duplex = Duplex.Horizontal;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion




        }

        private void button94_Click(object sender, EventArgs e)
        {

            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1 ;
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }

            string fields = "";
            string wheres="";
            string sub_filter = "";
            if (ГР_День.Checked)
            {
                sub_filter = sub_filter + " and shipment_date='[ДАТА]' ";
                fields = fields + " , shipment_date ДАТА ";
                wheres = wheres + " , shipment_date ";
            }

            if (ГР_ТипТР.Checked)
            {
                sub_filter = sub_filter + " and t.transtype='[ТИП_ТР]' ";
                fields = fields + " , t.transtype ТИП_ТР ";
                wheres = wheres + " , t.transtype ";
            }

            if (ГР_Регион.Checked)
            {
                sub_filter = sub_filter + " and rrl_tt_regions (t.ID)='[РЕГИОНЫ]' ";
                fields = fields + " , rrl_tt_regions (t.ID) РЕГИОНЫ ";
                wheres = wheres + " , rrl_tt_regions (t.ID) ";
            }

            if (ГР_Компания.Checked)
            {
                sub_filter = sub_filter + " and  tr.DOVERENNOST_OT ='[КОМПАНИЯ]' ";
                fields = fields + " , tr.DOVERENNOST_OT КОМПАНИЯ ";
                wheres = wheres + " , tr.DOVERENNOST_OT ";
            }


            if (ГР_Машина.Checked)
            {
                sub_filter = sub_filter + " and  t.transport ='[МАШИНА]' ";
                fields = fields + " , t.transport МАШИНА ";
                wheres = wheres + " , t.transport ";
            }

            if (ГР_Логист.Checked)
            {
                sub_filter = sub_filter + " and  t.user_id='[ЛОГИСТ]' ";
                fields = fields + " , t.user_id ЛОГИСТ ";
                wheres = wheres + " , t.user_id ";
            }

            

            if (ГР_Месяц.Checked)
            {
                sub_filter = sub_filter + " and  to_char( shipment_date , 'mm' ) = [МЕСЯЦ] ";
                fields = fields + " , to_char( shipment_date , 'mm' ) МЕСЯЦ ";
                wheres = wheres + " , to_char( shipment_date , 'mm' ) ";
            }

            wheres = wheres.Trim().Trim(',');

            if (wheres.Trim() == "")
            {
                MessageBox.Show( "Выберите группировку" );
                return;
            }
//             shipment_date  , 
//          t.transtype ,  -- , 

            string strSQL = " SELECT   sum( price) Сумма ,  count( price) Количество_рейсов ,  count( distinct t.TRANSPORT  ) Кол_во_единиц_трансп   " + fields +
            "    FROM rrl_transport_task t , rrl_tr_voditel tr " +
            "   WHERE  t.VODITEL_ID=tr.ID and shipment_date >= " + date2sql_ora(dt1) + " and shipment_date <= " + date2sql_ora(dt2) + " AND t.deleted <> 1 " +
            "   group by     " +wheres+
            "    order by sum( price) desc " ;


            ЗАПРОСЫ ftr = new ЗАПРОСЫ();
            ftr.sSQL = strSQL;
            ftr.Header_Text =  "Сводная:  биллинг транспорта  ";

            string strSQL2 = " SELECT  price Сумма , t.user_id ЛОГИСТ , t.transport МАШИНА , "+
            " tr.DOVERENNOST_OT КОМПАНИЯ  ,   rrl_tt_regions (t.ID),  t.transtype ТИП_ТР  , "+
            " shipment_date ДАТА , tr.TEL  " +
            "    FROM rrl_transport_task t , rrl_tr_voditel tr " +
            "   WHERE  t.VODITEL_ID=tr.ID and shipment_date >= " + date2sql_ora(dt1) + " and shipment_date <= " + date2sql_ora(dt2) + " AND t.deleted <> 1 " + sub_filter+
            "    order by   price  desc ";

            ftr.SubQueries.Add(strSQL2);
            ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            ftr.ShowDialog();
 

 



        }

        private void button95_Click(object sender, EventArgs e)
        {

            DateTime dt = new DateTime();
            dt = DateTime.Today.AddDays(-3);

            string strSQL = "select RRL_CELLS.CELL  , X  ,Y , Z , BLOCKED_FOR_ACCEPT БЛОК_ПРИЕМКИ , BLOCKED_FOR_REMAINS БЛОК_ОСТАТКОВ , BLOCKED_FOR_POPOLNENIE БЛОК_ПОПОЛНЕНИЯ , LAST_TIME_OF_UPDATE " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where    " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+)  and ( RRL_REMAINS.CELL is null) " +
                " and RRL_CELLS.OTBOR=0 and RRL_CELLS.IS_SYSTEM=0 " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString() +
                " and ( (LAST_TIME_OF_UPDATE is null) or ( LAST_TIME_OF_UPDATE< " + date2sql_ora(dt) + " )  ) " +
                "  order by Z,Y,X ";
            ShowQuery(strSQL, "Отчет по пустым ячейкам, не пикнутым более 2 дней");

        }

        private void button96_Click(object sender, EventArgs e)
        {
            DateTime dt = new DateTime();
            dt = DateTime.Today.AddDays(-7);

            string strSQL = "select RRL_CELLS.CELL  , X  ,Y , Z , BLOCKED_FOR_ACCEPT БЛОК_ПРИЕМКИ , BLOCKED_FOR_REMAINS БЛОК_ОСТАТКОВ , BLOCKED_FOR_POPOLNENIE БЛОК_ПОПОЛНЕНИЯ , LAST_TIME_OF_UPDATE " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where    " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+) " + //and ( RRL_REMAINS.CELL is null) 
                " and RRL_CELLS.OTBOR=0 and RRL_CELLS.IS_SYSTEM=0 " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString() +
                " and ( (LAST_TIME_OF_UPDATE is null) or ( LAST_TIME_OF_UPDATE< " + date2sql_ora(dt) + " )  ) " +
                "  order by Z,Y,X ";
            ShowQuery(strSQL, "Отчет по ячейкам сухого склада, не пикнутым более 7 дней");


        }

        private void button97_Click(object sender, EventArgs e)
        {
            if(ИНВ_РЯД.Text=="")
            {
                MessageBox.Show("Не выбран Ряд ");
               return;
            }
            

            DateTime dt = dateTimePicker10.Value;

            DateTime dt2  = DateTime.Today.AddDays(1);

            string strSQL = "select RRL_CELLS.CELL  , X  ,Y , Z , BLOCKED_FOR_ACCEPT БЛОК_ПРИЕМКИ , BLOCKED_FOR_REMAINS БЛОК_ОСТАТКОВ , BLOCKED_FOR_POPOLNENIE БЛОК_ПОПОЛНЕНИЯ , LAST_TIME_OF_UPDATE " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where    " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+) " + //and ( RRL_REMAINS.CELL is null) 
                " and RRL_CELLS.OTBOR=0 and RRL_CELLS.IS_SYSTEM=0 " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString() +
                " and Z in ("+ИНВ_РЯД.Text+") "+
                " and ( (LAST_TIME_OF_UPDATE is null) or ( LAST_TIME_OF_UPDATE< " + date2sql_ora(dt) + " )  ) " +
                "  order by Z,Y,X ";
            ShowQuery(strSQL, "Отчет по ячейкам ряда " + ИНВ_РЯД.Text+ ", не пикнутым в течение смены.");

        }
        
        private void dataGridView23_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {


            if (e.ColumnIndex == 1)
            {
                if (( (dataGridView23[2, e.RowIndex].Value.ToString())==  (dataGridView23[9, e.RowIndex].Value.ToString())))
                {
                    e.CellStyle.BackColor = Color.Green;
                }

            }


        }

        private void dataGridView22_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {


            if (e.ColumnIndex == 1)
            {
                if (((dataGridView22[5, e.RowIndex].Value.ToString()) =="2" ))
                {
                    e.CellStyle.BackColor = Color.Green;
                }

                if (((dataGridView22[5, e.RowIndex].Value.ToString()) == "1"))
                {
                    e.CellStyle.BackColor = Color.LightCoral;
                }

            }

        }

        private void чтоНаходитсяВОтбореToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView11.CurrentRow == null) return;
            string art = dataGridView11.CurrentRow.Cells[0].Value.ToString();
            string strSQL = " select  RR.CELL , RR.UID_POLETA ,  RR.REMAIN , RR.TIME_OF_LAST_UPDATE , PP.EXPIRY_DATE , AA.ACTICUL " +
                " from RABAEV.RRL_REMAINS  RR , RABAEV.RRL_ARTICULS AA , RABAEV.RRL_PALLETS PP where AA.ACTICUL='" + art + "' and AA.CELL = RR.CELL and PP.UID_PALLET = RR.UID_POLETA ";


            ShowQuery(strSQL, "Что лежит в отборе артикула " + art);

        }

        private void button2_Click(object sender, EventArgs e)
        {
            string strSQL = "select ID , Name , OVERFLOW_CELL_NAME , PREFIX , FAKE_ART from RABAEV.RRL_WARES order by ID";

            fill_view_MINI_WMS(dataGridView27, strSQL, 5);

        }

        private void ware_change_option(string option1 , bool check1 )
        {
            if (block_change_warehouse_options) return;
            if (dataGridView27.CurrentRow == null) return;
            int val1 = 1;
            if (!check1) val1 = 0;
            string ware1 = dataGridView27.CurrentRow.Cells[0].Value.ToString();
            string strSQL = " update RABAEV.RRL_WARES set " + option1 + "=" + val1.ToString() + " where id=" + ware1 + " ";

            OracleCommand ora_comm = new OracleCommand();
            ora_comm.Connection = get_wms_connection();
            ora_comm.CommandText = strSQL;
            ora_comm.ExecuteNonQuery();
        }


        private void l_FAKE_ROWS_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("FAKE_ROWS", l_FAKE_ROWS.Checked);
        }

        private void l_BLOCK_IF_NO_PROOVE_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("BLOCK_IF_NO_PROOVE", l_BLOCK_IF_NO_PROOVE.Checked);
        }

        private void l_VERIFY_VYCHERK_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("VERIFY_VYCHERK", l_VERIFY_VYCHERK.Checked);
        }

        private void l_ALLOW_HALF_VYCHERK_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("ALLOW_HALF_VYCHERK", l_ALLOW_HALF_VYCHERK.Checked);
        }

        private void l_WRITE_BOTH_EXPIRYANDBEST_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("WRITE_BOTH_EXPIRYANDBEST", l_WRITE_BOTH_EXPIRYANDBEST.Checked);
        }

 

        private void l_SPIS_OTBOR_ON_SCAN_OPALL_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("SPIS_OTBOR_ON_SCAN_OPALL", l_SPIS_OTBOR_ON_SCAN_OPALL.Checked);
        }

        private void l_SPIS_OTBOR_ON_WPROOVE_OPALL_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("SPIS_OTBOR_ON_WPROOVE_OPALL", l_SPIS_OTBOR_ON_WPROOVE_OPALL.Checked);
        }



        #region Параметры склада - ПОДГРУЗКА.
        private void dataGridView27_CellEnter(object sender, DataGridViewCellEventArgs e)
        {

            if (dataGridView27.CurrentRow == null) return;

            string ware1 = dataGridView27.CurrentRow.Cells[0].Value.ToString();
            if (ware1 == "") return;
            string strSQL = " select FAKE_ROWS , " + 
            " BLOCK_IF_NO_PROOVE , " + 
            " VERIFY_VYCHERK , " + 
            " ALLOW_HALF_VYCHERK , " + 
            " WRITE_BOTH_EXPIRYANDBEST , " + 
            " SPIS_IF_HRAN_NO_EMPTY , " + 
            " SPIS_OTBOR_ON_SCAN_OPALL , " +
            " SPIS_OTBOR_ON_WPROOVE_OPALL , time_coeff , VERIFY_VYCHERK_IN_OTBOR from RABAEV.RRL_WARES   where id=" + ware1 + " ";


            OracleCommand ora_comm = new OracleCommand();
            ora_comm.Connection = get_wms_connection();
            ora_comm.CommandText = strSQL;
            OracleDataReader ora_read=  ora_comm.ExecuteReader();
            block_change_warehouse_options = true;
            if( ora_read.Read() )
            {

                l_FAKE_ROWS.Checked = obj2bool(ora_read.GetValue(0));
                l_BLOCK_IF_NO_PROOVE.Checked = obj2bool(ora_read.GetValue(1));
                l_VERIFY_VYCHERK.Checked = obj2bool(ora_read.GetValue(2));
                l_ALLOW_HALF_VYCHERK.Checked = obj2bool(ora_read.GetValue(3));
                l_WRITE_BOTH_EXPIRYANDBEST.Checked = obj2bool(ora_read.GetValue(4));
                
                l_SPIS_OTBOR_ON_SCAN_OPALL.Checked = obj2bool(ora_read.GetValue(6));
                l_SPIS_OTBOR_ON_WPROOVE_OPALL.Checked = obj2bool(ora_read.GetValue(7));
                l_time_coeff.Text = obj2double (ora_read.GetValue(8)).ToString();
                VERIFY_VYCHERK_IN_OTBOR.Checked = obj2bool(ora_read.GetValue(9));
            
            }
            block_change_warehouse_options = false;




        }
        #endregion

        private void l_time_coeff_TextChanged(object sender, EventArgs e)
        {
            try
            {

                Convert.ToDouble( l_time_coeff.Text.Replace('.',',' ));
            }
            catch { return; }

            if (block_change_warehouse_options) return;
            if (dataGridView27.CurrentRow == null) return;
            int val1 = 1;
 
            string ware1 = dataGridView27.CurrentRow.Cells[0].Value.ToString();
            string strSQL = " update RABAEV.RRL_WARES set time_coeff=" + l_time_coeff.Text.Replace(',','.') + " where id=" + ware1 + " ";

            OracleCommand ora_comm = new OracleCommand();
            ora_comm.Connection = get_wms_connection();
            ora_comm.CommandText = strSQL;
            ora_comm.ExecuteNonQuery();
        }

        private void зачиститьЯчейкуОтбораоставимПоследнийПаллетToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView8.CurrentRow == null) return;
             if (( !Convert.ToBoolean(dataGridView8.CurrentRow.Cells[2].Value))) 
             {
                 MessageBox.Show("Ячейка не является ячейкой отбора.");
             }

            string cell1 = dataGridView8.CurrentRow.Cells[1].Value.ToString();

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = "RABAEV.RRL_CLEAR_OTBOR_CELL";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("CELL1", OracleType.VarChar).Value = cell1;
            ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;
            ora_com.Parameters.Add("ID", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
             string mess = ora_com.Parameters["ID"].Value.ToString();
             if (mess != "ok") {
             
                 MessageBox.Show(mess);
             
             }
          

        }

        private void зачиститьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            foreach( DataGridViewRow dr in dataGridView8.Rows )
            {

                //if (dataGridView8.CurrentRow == null) return;
                if ((Convert.ToBoolean(dr.Cells[2].Value)))
                {

                    string cell1 = dr.Cells[1].Value.ToString();

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.RRL_CLEAR_OTBOR_CELL";
                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("CELL1", OracleType.VarChar).Value = cell1;
                    ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = this.wms_user.user_id;
                    ora_com.Parameters.Add("ID", OracleType.VarChar, 255).Direction = ParameterDirection.ReturnValue;
                    ora_com.ExecuteNonQuery();
                    string mess = ora_com.Parameters["ID"].Value.ToString();
                    if (mess != "ok")
                    {

                      //  MessageBox.Show(mess);

                    }
                }
            }


        }

        private void button98_Click(object sender, EventArgs e)
        {


            DateTime dt = dateTimePicker10.Value;
 

            string strSQL = " select * from RABAEV.RRL_ERROR_LOG where DATET>" + date2sql_ora(dt) +
                "  order by DATET ";
            ShowQuery(strSQL, "Отчет по системным ошибкам.");

        }

        private void Печать_задачи_инвентаризации_Click(object sender, EventArgs e)
        {




            #region ОПРЕДЕЛЕНИЕ ПЕРЕМЕННЫХ
            int _X = 10, _Y = 80;
            #endregion

            #region ПОДГОТОВКА ПЕЧАТИ

           


            DateTime dt = dateTimePicker10.Value;
//            dt = DateTime.Today.AddDays();

            string strSQL2 = "select RRL_CELLS.CELL  , X  ,Y , Z  , LAST_TIME_OF_UPDATE " +
                " from RABAEV.RRL_CELLS , RABAEV.RRL_REMAINS  " +
                "   " +
                " where    " +
                "  RRL_CELLS.CELL =   RRL_REMAINS.CELL(+)  and ( RRL_REMAINS.CELL is null) " +
                " and RRL_CELLS.OTBOR=0 and RRL_CELLS.IS_SYSTEM=0 " +
                "  and  RABAEV.RRL_CELLS.ware_id = " + this.wms_user.ware_id.ToString() +
                " and ( (LAST_TIME_OF_UPDATE is null) or ( LAST_TIME_OF_UPDATE< " + date2sql_ora(dt) + " )  ) " +
                "  order by Z,Y,X ";

            
 

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL2;

            #region СОЗДАНИЕ СТРАНИЦЫ
            PPage _page = new PPage();
            _page.start_point_4_table.X = 10;
            _page.start_point_4_table.Y = 70;
            _page.font_size_4_table = 18;
            _page.height_of_column = 24;
            _page.labels.Add(new PPage.PLabel("Лист инвентаризации пустых паллето-мест", new Point(10, 10), 24));
            _page.labels.Add(new PPage.PLabel("Пройдите по ячейкам согласно списка. сканируйте штрих-код ячейки, затем штрих-код паллета, ", new Point(10, 36), 12));
            _page.labels.Add(new PPage.PLabel("Если ячейка пустая, нажмите кнопку 'NO_PALL'. Затем нажмите 'Подтвертить перемещение' на сканнере.", new Point(10, 50), 12));
            _page.labels.Add(new PPage.PLabel("Подпись ответственного лица:  ________________(_______________)", new Point(10, 1110), 22));

            _page.add_column("CELL", "string", "ЯЧЕЙКА", 7);
            _page.add_column("WHAT", "string", "ЧТО НАЙДЕНО?", 10);
            _page.add_column("Y", "string", "ЭТАЖ", 5);
            _page.add_column("Z", "string", "РЯД",4);
            _page.add_column("CELL2", "EAN", "ЯЧЕЙКА", 14);
 
            #endregion


            long in_page = 45;
            
            OracleDataReader ora_read3 = ora_com.ExecuteReader();


            long КОЛИЧЕСТВО_ПАЛЛЕТ1 = 0;
            while (ora_read3.Read())
            {
                Dictionary<string, string> _row = new Dictionary<string, string>();
                _row["CELL"] = obj2str(ora_read3.GetValue(0));
                _row["WHAT"] = "";
                _row["Y"] = obj2str(ora_read3.GetValue(2));
                _row["Z"] = obj2str(ora_read3.GetValue(3));  
                _row["CELL2"] = obj2str(ora_read3.GetValue(0));   
             

                _page.add_row(_row);
                КОЛИЧЕСТВО_ПАЛЛЕТ1++;
                if (КОЛИЧЕСТВО_ПАЛЛЕТ1 >= in_page)
                { 
                    КОЛИЧЕСТВО_ПАЛЛЕТ1=0;
                    PPages.Add(_page);
                    in_page = 47;
                    #region СОЗДАНИЕ СТРАНИЦЫ
                    _page = new PPage();
                    _page.start_point_4_table.X = 10;
                    _page.start_point_4_table.Y = 48;
                    _page.font_size_4_table = 18;

                    _page.labels.Add(new PPage.PLabel("Лист инвентаризации пустых паллето-мест", new Point(10, 10), 24));
                    _page.labels.Add(new PPage.PLabel("Подпись ответственного лица:  ________________(_______________)", new Point(10, 1110), 22));

                    _page.add_column("CELL", "string", "ЯЧЕЙКА", 7);
                    _page.add_column("WHAT", "string", "ЧТО НАЙДЕНО?", 10);
                    _page.add_column("Y", "string", "ЭТАЖ", 5);
                    _page.add_column("Z", "string", "РЯД", 4);
                    _page.add_column("CELL2", "EAN", "ЯЧЕЙКА", 14);
 
                    #endregion
                }

            }

            if (КОЛИЧЕСТВО_ПАЛЛЕТ1 != 0)
            {
                PPages.Add(_page);
            }

            #endregion

            #region НАЧАЛО_ПЕЧАТИ
            PrintDocument pd = new PrintDocument();
            try
            {
                pd.DefaultPageSettings.Landscape = false;
                pd.PrintPage += new PrintPageEventHandler
                    (pd_PrintPage_SBOR);
                pd.Print();
            }
            catch (Exception ex)
            {
                MessageBox.Show(" f48 " + ex.Message);
            }
            #endregion




        }

        private void ABC_calculate_Click(object sender, EventArgs e)
        {
 

            if (dataGridView27.CurrentRow == null) return;
            string ware1 = dataGridView27.CurrentRow.Cells[0].Value.ToString();

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = "RABAEV.RRL_ABC_CALCULATE";
            ora_com.CommandType = CommandType.StoredProcedure;

            ora_com.Parameters.Add("ware_id1", OracleType.Int32).Value =  Convert.ToInt32( ware1 ) ;
               ora_com.Parameters.Add("ID", OracleType.Int32  ).Direction = ParameterDirection.ReturnValue;
            ora_com.ExecuteNonQuery();
            string mess = ora_com.Parameters["ID"].Value.ToString();



        }

        private void Ассортимент_склада_с_отбором_Click(object sender, EventArgs e)
        {
           



            string add_sql3 = "    (c.ware_id=" + this.wms_user.ware_id + ")  ";


            string strSQL = " SELECT ACTICUL , NAME , ROUND( SSP/NORMA_UKLADKI , 1 ) ПАЛЛ_В_ДЕНЬ  , SSP ССП ,NORMA_UKLADKI КОЛВО_НА_ПОДДОНЕ ,ABC_GROUP  , XYZ_GROUP , A.Cell   , " +
                " RRL_SKLADNAME_BY_ID( c.ware_id ) СКЛАД , COUNT_SHT_IN_KOR ШТВКОР , COUNT_SHT_IN_BL ШТВБ , A.WEIGHT_OF_KOR ВЕС_КОРОБКИ , " +
                "     BESTBEFOREDAYS ,   C.X СТЕЛЛАЖ , C.Y ЭТАЖ , C.Z УЛИЦА , round(  ((A.NORMA_UKLADKI  /  (   A.COUNT_SHT_IN_KOR )) *  A.WEIGHT_OF_KOR ) , 0 ) НОРМАТИВНЫЙ_ВЕС_ПОДДОНА " +
            "  FROM RABAEV.RRL_ARTICULS A , RABAEV.RRL_CELLS C where A.Cell = C.cell and C.otbor=1 and " +
            " " + add_sql3 + " order by C.Z  , C.Y  ,C.X   ";


            ShowQuery(strSQL, "Отчет Ассортимент склада с отбором.");
        }

        private void dataGrid_ПАЛЛЕТЫ_ОТКУДА_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {

            if (dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow == null)
            {
                return;
            }

            string pall1 = dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow.Cells[0].Value.ToString();
            string cell1 =  ЯЧЕЙКА_ОТКУДА.Text ;
            string val1 = dataGrid_ПАЛЛЕТЫ_ОТКУДА.CurrentRow.Cells[1].Value.ToString();

            string strSQL = " update RRL_REMAINS set REMAIN=" + val1 +
                " where CELL = '" + cell1 + "' and UID_POLETA='" + pall1 + "'  ";

            OracleCommand ora_com = new OracleCommand();
            ora_com.Connection = get_wms_connection();
            ora_com.CommandText = strSQL;
            ora_com.CommandType = CommandType.Text;
            ora_com.ExecuteNonQuery();

        }

        private void VERIFY_VYCHERK_IN_OTBOR_CheckedChanged(object sender, EventArgs e)
        {
            ware_change_option("VERIFY_VYCHERK_IN_OTBOR", VERIFY_VYCHERK_IN_OTBOR.Checked);

        }

        private void button99_Click(object sender, EventArgs e)
        {

            string add_sql3 = "    (c.ware_id=" + this.wms_user.ware_id + ")  ";


            string strSQL = " SELECT ACTICUL , NAME , ROUND( SSP/NORMA_UKLADKI , 1 ) ПАЛЛ_В_ДЕНЬ  , SSP ССП ,NORMA_UKLADKI КОЛВО_НА_ПОДДОНЕ ,ABC_GROUP  , XYZ_GROUP , A.Cell   , " +
                " RRL_SKLADNAME_BY_ID( c.ware_id ) СКЛАД , COUNT_SHT_IN_KOR ШТВКОР , COUNT_SHT_IN_BL ШТВБ , A.WEIGHT_OF_KOR ВЕС_КОРОБКИ , " +
                "     BESTBEFOREDAYS ,   C.X СТЕЛЛАЖ , C.Y ЭТАЖ , C.Z УЛИЦА , round(  ((A.NORMA_UKLADKI  /  (   A.COUNT_SHT_IN_KOR )) *  A.WEIGHT_OF_KOR ) , 0 ) НОРМАТИВНЫЙ_ВЕС_ПОДДОНА , LIMIT_WEIGHT ДОПУСТИМЫЙ_ВЕС_ЯЧЕЙКИ " +
            "  FROM RABAEV.RRL_ARTICULS A ,   RABAEV.RRL_REMAINS RR , RABAEV.RRL_PALLETS "+
            " where A.Cell = C.cell and RR.PALLET_UID = RRL_PALLETS.PALLET_UID and  RR.otbor=0 and " +
            " " + add_sql3 + " order by C.Z  , C.Y  ,C.X   ";


            ShowQuery(strSQL, "Товар в хранении.");



        }


        #region Групповая работа с ячейками

        private void f_CELL_GROUP_JOB_Click(object sender, EventArgs e)
        {


            int dist = 0;
            
            foreach (DataGridViewRow dr in dataGridView8.Rows)
            {
                if (Convert.ToBoolean(dr.Cells[0].Value))
                {

                    string cell1=dr.Cells[1].Value.ToString();
                    #region ВЫСОТА
                    if (m_limit_height.Text!="")
                    { 
                        if( obj2int( m_limit_height.Text)>0 )
                        {
                            string strSQL = "  update rrl_cells set LIMIT_HEIGHT="+m_limit_height.Text+" where cell='"+cell1+"' ";
                            OracleCommand ora_com = new OracleCommand();
                            ora_com.Connection= get_wms_connection();
                            ora_com.CommandText = strSQL ;
                            ora_com.ExecuteNonQuery();
                            dist++;
                        }
                    }
                    #endregion
                    

                    #region ВЕС
                    if (m_limit_weight.Text!="")
                    {
                        if (obj2int(m_limit_weight.Text) > 0)
                        {
                            string strSQL = "  update rrl_cells set LIMIT_WEIGHT=" + m_limit_weight.Text + " where cell='" + cell1 + "' ";
                            OracleCommand ora_com = new OracleCommand();
                            ora_com.Connection= get_wms_connection();
                            ora_com.CommandText = strSQL ;
                            ora_com.ExecuteNonQuery();
                            dist++;
                        }
                    }
                    #endregion
                    


                }
            }

            MessageBox.Show(" Выполнено " + dist.ToString() + " изменений.");

        }

        #endregion


        private void button100_Click(object sender, EventArgs e)
        {

            /*
            string strSQL = " SELECT ACTICUL , NAME , ROUND( SSP/NORMA_UKLADKI , 1 ) ПАЛЛ_В_ДЕНЬ  , SSP ССП ,NORMA_UKLADKI КОЛВО_НА_ПОДДОНЕ ,ABC_GROUP  , XYZ_GROUP , A.Cell   , " +
            " RRL_SKLADNAME_BY_ID( c.ware_id ) СКЛАД , COUNT_SHT_IN_KOR ШТВКОР , COUNT_SHT_IN_BL ШТВБ , A.WEIGHT_OF_KOR ВЕС_КОРОБКИ , " +
            "     BESTBEFOREDAYS ,   C.X СТЕЛЛАЖ , C.Y ЭТАЖ , C.Z УЛИЦА , round(  ((A.NORMA_UKLADKI  /  (   A.COUNT_SHT_IN_KOR )) *  A.WEIGHT_OF_KOR ) , 0 ) НОРМАТИВНЫЙ_ВЕС_ПОДДОНА , LIMIT_WEIGHT ДОПУСТИМЫЙ_ВЕС_ЯЧЕЙКИ " +
            "  FROM RABAEV.RRL_ARTICULS A ,   RABAEV.RRL_REMAINS RR , RABAEV.RRL_PALLETS , RRL_CELLS C " +
            " where A.Cell = C.cell and RR.PALLET_UID = RRL_PALLETS.PALLET_UID and  C.otbor=0 and    (  LIMIT_WEIGHT <  round(  ((A.NORMA_UKLADKI  /  (   A.COUNT_SHT_IN_KOR )) *  A.WEIGHT_OF_KOR ) , 0 ) ) " +
            "  order by C.Z  , C.Y  ,C.X   ";
            */


            string strSQL = " select  rr.cell ЯЧЕЙКА , sum( rr.REMAIN ) ШТУКИ ,  count( rr.UID_POLETA ) КОЛВО_ПАЛЛЕТ, art.ACTICUL , art.NAME " + 
            " from  rrl_remains rr ,rrl_cells cc , rrl_pallets pall , rrl_articuls art " + 
            " where rr.CELL=cc.CELL " + 
            " and cc.otbor=1  " + 
            " and ware_id in (" + this.wms_user.ware_id.ToString() + ") " + 
            " and pall.UID_PALLET = rr.UID_POLETA  " + 
            " and art.ACTICUL = pall.ARTICUL " +
            " and cc.IS_SYSTEM=0 " +
            " group by rr.cell , " + 
            " art.ACTICUL , " + 
            " art.NAME " + 
            " having count( rr.UID_POLETA )>2 " + 
            " order by  count( rr.UID_POLETA ) desc " ;

            ShowQuery(strSQL, "Товар в хранении (излишки) по складу № " + this.wms_user.ware_id.ToString() + ".");


             strSQL = " select  rr.cell ЯЧЕЙКА , sum( rr.REMAIN ) ШТУКИ ,  count( rr.UID_POLETA ) КОЛВО_ПАЛЛЕТ , art.ACTICUL , art.NAME " +
            " from  rrl_remains rr ,rrl_cells cc , rrl_pallets pall , rrl_articuls art " +
            " where rr.CELL=cc.CELL " +
            " and cc.otbor=1  " +
            " and pall.UID_PALLET = rr.UID_POLETA  " +
            " and art.ACTICUL = pall.ARTICUL " +
            " and cc.IS_SYSTEM=0 " +
            " group by rr.cell , " +
            " art.ACTICUL , " +
            " art.NAME " +
            " having count( rr.UID_POLETA )>2 " +
            " order by  count( rr.UID_POLETA ) desc ";

            ShowQuery(strSQL, "Товар в хранении (излишки) по всем складам.");


        }

        private void button101_Click(object sender, EventArgs e)
        {

            string arts = "";
            foreach (string lin in textBox9.Lines)
            {
                arts = arts + "'" + lin + "',";
            }

            arts = arts.Trim(',').Trim();

            string strSQL1 = "      select " +
            " sum( quantity ) колво , " + 
            " TO_CHAR( pp.CREATE_DATE , 'dd-mm-yyyy'  ) дата ,  " + 
            " rr.ARTICUL " + 
            " from RABAEV.RRL_SBORKA_PALLET_ROWS rr  ,   RABAEV.RRL_SBORKA_PALLETS pp   " + 
            " where  " + 
            " rr.PALLET_UID = pp.PALLET_UID  and  " +
            " rr.ARTICUL in ( " + arts + " )  " + 
            " and ( pp.CREATE_DATE >= " + date2sql_ora( dateTimePicker11.Value.AddDays(-1)  ) + " ) " +
            " and ( pp.CREATE_DATE <= " + date2sql_ora(dateTimePicker12.Value.AddDays(-1)) + " ) " +
            " group by  TO_CHAR( pp.CREATE_DATE , 'dd-mm-yyyy'  ) , " + 
            " rr.ARTICUL " ;

          ShowQuery(strSQL1, "Сколько отгружено на магазины.");
            
            



          string strSQL2 = " select " + 
          "              sum( count_event ) колво ,  " + 
          "              TO_CHAR( ee.date_event , 'dd-mm-yyyy'  ) дата ,  " + 
          "              PP.ARTICUL " + 
          "               from rrl_events EE , rrl_pallets PP , rrl_cells CC  " + 
          "               where  " + 
          "              EE.UID_POLETA = PP.UID_PALLET and  " + 
          "              PP.ARTICUL in ( " + arts + " ) and " + 

          "              ee.date_event >= " + date2sql_ora( dateTimePicker11.Value  ) + "  and " + 
          "              ee.date_event <= " + date2sql_ora( dateTimePicker12.Value  ) + "  and " + 

          "              CC.cell = EE.cell_to and  " + 
          "              CC.otbor=1 and  " + 
          "              CC.is_system =0 " + 
          "              group by TO_CHAR(ee.date_event , 'dd-mm-yyyy'  ) , PP.ARTICUL " ;

          ShowQuery(strSQL2, "Сколько спущено в отбор за период.");

        }

     

        string ask(  string question )
        {
            input form11 = new input();
            form11.ShowDialog();
            return form11.ret;
        }


        private void загрузитьЗоныИзФайлаToolStripMenuItem_Click(object sender, EventArgs e)
        {



            #region ПОДГРУЗКА ПРАЙСА

            long pos = 2;
            try
            {

                Excel.Application oExcelApp = new Excel.Application();
                oExcelApp.Visible = true;

                object obj = new object();



                string Filename = "C:\\WMS\\Цены.xls"; //=ofd.SafeFileName;


                try
                {

                    oExcelApp.Workbooks.Open(Filename, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing, Type.Missing);
                    pos = 1;

                    if (
                    ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString() != "ЗОНА" ||
                    ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString() != "ПОДЗОНА" ||
                    ((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString() != "ДОК" 
                    )
                    {
                        MessageBox.Show(" файл должен иметь структуру: ЗОНА - ПОДЗОНА - ДОК ");
                        return;
                    }


                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                    return;
                }



                #region ЗАкачка с 1 листа
                pos = 2;
                while (obj2str(((Excel.Range)oExcelApp.Cells[pos, 1]).Value2) != "")
                {

                    string ЗОНА = ((Excel.Range)oExcelApp.Cells[pos, 1]).Value2.ToString();
                    string ПОД_ЗОНА = ((Excel.Range)oExcelApp.Cells[pos, 2]).Value2.ToString();
                    string ДОК = ((Excel.Range)oExcelApp.Cells[pos, 3]).Value2.ToString();



                    
                    

                    OracleCommand ora_com = new OracleCommand();
                    ora_com.Connection = get_wms_connection();
                    ora_com.CommandText = "RABAEV.RRL_UPDATE_TT_ZONE";

                    ora_com.CommandType = CommandType.StoredProcedure;

                    ora_com.Parameters.Add("ZONE1", OracleType.VarChar).Value = ЗОНА;
                    ora_com.Parameters.Add("SUB_ZONE1", OracleType.VarChar).Value = ПОД_ЗОНА;
                    ora_com.Parameters.Add("DOCK1", OracleType.VarChar).Value = ДОК;

                        ora_com.Parameters.Add("tmpVar", OracleType.Int32 ).Direction = ParameterDirection.ReturnValue;
                    int rowsAffected = ora_com.ExecuteNonQuery();
                    string tmpVar = ora_com.Parameters["tmpVar"].Value.ToString();
                    // ================================================================
                    pos++;
                }
                #endregion



                MessageBox.Show("Данные загружены из Excel. Количество подгруженных строк=" + pos.ToString());
            }
            catch (Exception ex)
            {
                MessageBox.Show(Convert.ToString(pos) + " _ " + ex.Message);
            }
            // ================================

            #endregion





        }

        private void button102_Click(object sender, EventArgs e)
        {
            string strSQL = " select  ZONE , SUB_ZONE , DOCK   from RRL_TT_ZONES order by SUB_ZONE ";

            fill_view_MINI_WMS(ZONEdataGridView , strSQL , 3 );
        }

        private void СписокСтавок_Click(object sender, EventArgs e)
        {

            Список_прайсов bt = new Список_прайсов();

            bt._pparent = this;
            bt.Show();
        }

        private void dataGridView17_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {

            if (e.ColumnIndex == 0)
            {
                if (dataGridView17[14, e.RowIndex].Value!=null)
                {
                    string comp= dataGridView17[14, e.RowIndex].Value.ToString();
                        string color_string = CachedQuerySingle(" select color from RABAEV.RRL_BILL_COMPANY where COMPANYNAME='"+comp+"' ");
                        if( color_string!="" ){
                            ColorConverter x = new ColorConverter();
                            Color c = (Color)x.ConvertFrom( color_string );                       
                            e.CellStyle.BackColor = c ; //  Green;
                        }
                }
            }


        }

        private void Рейсы_Водителей_за_период_Click(object sender, EventArgs e)
        {
            DateTime dt1 = БИЛЛИНГ_ОТ.Value;
            DateTime dt2 = dt1;
            if (checkBox4.Checked)
            {
                dt2 = БИЛЛИНГ_ДО.Value.AddDays(1);
            }

            string fields = "";
            string wheres = "";
            string sub_filter = "";



            string strSQL = " SELECT t.ID НОМЕР , shipment_date ДАТА ,  t.PAY_REGION РЕГИОН , " +
            "   RRL_TT_ADDR_COUNT(t.ID) КОЛВО_ТОЧЕК , RRL_TT_VODITEL_INFO(VODITEL_ID) ФИО_ВОДИТЕЛЯ  , " +
            "   PRICE СУММА_ЗА_РЕЙС  , t.ADDR_PREMIO ИЗ_НИХ_ПРЕМИЯ , tr. DOVERENNOST_OT " +
            "   FROM rrl_transport_task t , rrl_tr_voditel tr " +
            "   WHERE   t.VODITEL_ID=tr.ID and  shipment_date >= " + date2sql_ora(dt1) +
            "   and shipment_date <= " + date2sql_ora(dt2) + " AND t.deleted <> 1 and tr. DOVERENNOST_OT='МОНЕТКА' ";
        

            ЗАПРОСЫ ftr = new ЗАПРОСЫ();
            ftr.sSQL = strSQL;
            ftr.Header_Text = "Отчеты по рейсам собственных водителей за период";

            ftr.WMS_CONNECTION_STRING_INST = WMS_CONNECTION_STRING();
            ftr.ShowDialog();
 
        }



        // ===

    }

    public class PPage
    {
       public  class PLabel
        {
            public string Label;
            public System.Drawing.Point _point;
            long width_limit = 0;
            long height_limit = 0;
            FontStyle fs = FontStyle.Bold;
            Brush br = Brushes.Black;
            long font_size = 12;
            System.Drawing.Font printFont ; 
            StringFormat sf = new StringFormat();
            string type = "text"; // text , EAN

           public PLabel(string ttext, Point pp, long font_size_ )
           {
               this.Label = ttext;
               this.font_size = font_size_;
               this._point = pp;
           }

           public PLabel(string ttext, Point pp, long font_size_ , Brush br2)
           {
               this.Label = ttext;
               this.font_size = font_size_;
               this._point = pp;
               this.br = br2;
           }

           public PLabel(string ttext, Point pp, long font_size_ , string type_of_label)
           {
               
               this.Label = ttext;
               this.font_size = font_size_;
               this._point = pp;
               this.type = type_of_label;

           }

           public PLabel(string ttext, Point pp, long font_size_, string type_of_label , long wl , long hl)
           {
               this.width_limit = wl;
               this.height_limit = hl;
               this.Label = ttext;
               this.font_size = font_size_;
               this._point = pp;
               this.type = type_of_label;

           }

           public void print(PrintPageEventArgs ev)
            {
                if ((this.type == "text") || (this.type == "string"))
                {
                    printFont = new Font("ARIAL", font_size, fs, GraphicsUnit.Pixel);
                    if (width_limit == 0)
                    {
                        ev.Graphics.DrawString(Label, printFont, br, _point.X, _point.Y, sf);
                    }
                    else
                    {

                        ev.Graphics.DrawString(Label, printFont, br, new RectangleF(_point.X, _point.Y, width_limit, font_size + 2), sf);
                    }
                }

                if (this.type == "EAN")
                {
                    Image r = Code128Rendering.MakeBarcodeImage2(Label , 1, true, (int)width_limit , (int) height_limit  );
                      ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }


                if (this.type == "EAN2")
                {
                    Image r = Code128Rendering.MakeBarcodeImage2(Label, 2, true, (int)width_limit, (int)height_limit);
                    ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }
                if (this.type == "EAN3")
                {
                    Image r = Code128Rendering.MakeBarcodeImage2(Label, 3, true, (int)width_limit, (int)height_limit);
                    ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }

            }
        }
     
       public class PTable
        {

            public List<PColumnGroup> column_groups = new List<PColumnGroup>(); // Группировки колонок
            public Point bottom_point_of_table = new Point();
            long Row_height;
            public List<PColumn> columns = new List<PColumn>();
            List<Dictionary<string, string>> rows = new List<Dictionary<string, string>>();
            public Point start_point_4_table = new Point();
            public int font_size_4_table = 12;
            Pen pen = new Pen(Brushes.Black);
            public void add_row(Dictionary<string, string> _row)
            {
                this.rows.Add(_row);
            }


            public void add_column(string name2, string type2)
            {
                PColumn c = new PColumn(name2, type2);
                columns.Add(c);
            }

            public void add_column(string name2, string type2, string to_pr, long width)
            {
                PColumn c = new PColumn(name2, type2, to_pr, width);
                columns.Add(c);
            }

            public void add_column(string name2, string type2, string to_pr)
            {
                PColumn c = new PColumn(name2, type2, to_pr);
                columns.Add(c);
            }

            public Point print(PrintPageEventArgs ev)
            {
                Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold, GraphicsUnit.Pixel);
                Font printFont2 = new Font("ARIAL", font_size_4_table, FontStyle.Regular, GraphicsUnit.Pixel);

                int _position_x = this.start_point_4_table.X;
                int _position_y = this.start_point_4_table.Y;


                int pos_uio=0;
                foreach (PColumn _col in columns)
                {
                    int start_point_4_table_Y = this.start_point_4_table.Y;
                    // сначала определим - находится - ли данная колонка в группировке. Берем первую группировку по порядку.
                    for (int pcg =0 ; pcg< column_groups.Count ; pcg++ )
                    {
                        if (( pos_uio >= column_groups[pcg].first_column ) && ( pos_uio <= column_groups[pcg].last_column ))
                        { // Понижаем позицию по оси У на высоту объединенной ячейки
                            start_point_4_table_Y=this.start_point_4_table.Y - column_groups[pcg].height_of_column_group ;
                            column_groups[pcg].extend(_position_x , start_point_4_table_Y );
                            column_groups[pcg].extend(_position_x + (int)_col.Width_(font_size_4_table) , this.start_point_4_table.Y  );
                        }
                    }

                    ev.Graphics.DrawRectangle(pen, _position_x,  start_point_4_table_Y, _col.Width_(font_size_4_table), font_size_4_table + 4);
                    ev.Graphics.DrawString(_col.To_print, printFont, Brushes.Black, new RectangleF(_position_x,  start_point_4_table_Y, _col.Width_(font_size_4_table), font_size_4_table + 4));
                    _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                        pos_uio++;
                }

                  for (int pcg =0 ; pcg< column_groups.Count ; pcg++ )
                  {
                       ev.Graphics.DrawRectangle(pen, new Rectangle( column_groups[pcg].left_top ,  column_groups[pcg].size()  ) );
                       ev.Graphics.DrawString(column_groups[pcg].name, printFont, Brushes.Black, new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));

                  }

                foreach (Dictionary<string, string> _row in rows)
                {
                    _position_y = _position_y + font_size_4_table + 4;
                    _position_x = this.start_point_4_table.X;
                    foreach (PColumn _col in columns)
                    {
                        _col.bottom_point.X = _position_x;
                        _col.bottom_point.Y = _position_y;

                        string tp = _row[_col.Name];
                        tp = tp.Replace('\t', ' ');
                        tp = tp.Replace("  ", " ");

                        ev.Graphics.DrawRectangle(pen, _position_x, _position_y, _col.Width_(font_size_4_table), font_size_4_table + 4);
                        ev.Graphics.DrawString(tp, printFont2, Brushes.Black, new RectangleF(_position_x, _position_y, _col.Width_(font_size_4_table), font_size_4_table + 4));
                        _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                    }

                }

                bottom_point_of_table= new Point(_position_x, _position_y);
                return bottom_point_of_table;
            }
        
        }




       public class PColumn
        {
            public string Name;
            public string Type;
            public string To_print;
            long Width=0;
            public Point bottom_point = new Point();
            
            public long Width_(int font_size1)
            {

               // int mul=Convert.ToInt32( System.Math.Ceiling(Convert.ToSingle(font_size1) * .15F));

                if (Width > 0)
                {
                    return Width * font_size1;
                }

                return To_print.Length * font_size1;
            }

            public PColumn( string name1 , string Type1 , string To_print1 , long w )
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = To_print1;
                Width = w;
            }

            public PColumn(string name1, string Type1, string To_print1)
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = To_print1;

            }

            public PColumn()
            {}

            public PColumn(string name1, string Type1 )
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = name1;
            }
            

        }

        public class PColumnGroup
        {
            public PColumn column ;
            public int first_column = 0;
            public int last_column = 0;
            public int height_of_column_group = 0;
            public string name;
            public Point left_top= new Point();
            public Point right_bottom = new Point();

            public void extend(int X, int Y)
            {
                if ( (left_top.X > X  ) ||  (left_top.X==0) ) { left_top.X = X; }
                if ( (left_top.Y > Y)  || (left_top.Y ==0)) { left_top.Y = Y; }

                if ((right_bottom.X < X) || (right_bottom.X==0) ) { right_bottom.X = X; }
                if ((right_bottom.Y < Y) || (right_bottom.Y==0)) { right_bottom.Y = Y; }

            }
            public Size  size()
            {
                return new Size( -left_top.X + right_bottom.X , -left_top.Y + right_bottom.Y);
            }

            public PColumnGroup(string name4, int first1, int last1 , int h)
            {
                first_column = first1;
                last_column = last1;
                name = name4; 
                height_of_column_group = h;
                column = new PColumn(name4, "string");
            }

        }

        public class PArrow
        {
            Point start= new Point();
            Point end = new Point();

            public PArrow(int x1, int y1, int x2, int y2)
            {
                start.X = x1;
                start.Y = y1;
                end.X = x2;
                end.Y = y2;
            }

            public void print(PrintPageEventArgs ev)
            {
                ev.Graphics.DrawLine(Pens.Black, start, end);
            }
        }


       public List<PColumnGroup> column_groups = new List<PColumnGroup>(); // Группировки колонок
       public Point bottom_point_of_table = new Point();  // Сюда заносится информация о нижней точке в таблице
       public List<PLabel> labels= new List<PLabel>();
       public List<PTable> tables = new List<PTable>();
       public string header;
       long Row_height;
       public List<PColumn> columns= new List<PColumn>();
       public List<PArrow> arrows = new List<PArrow>(); 
       List< Dictionary<string,string> > rows= new List<Dictionary<string,string>>();
       
       public Point start_point_4_table = new Point();
       public int font_size_4_table = 12;
        public int height_of_column = 0;
       Pen pen= new Pen(Brushes.Black);

        public void add_row( Dictionary<string,string> _row )
        {
            this.rows.Add(_row);    
        }

        public void print_axes(PrintPageEventArgs ev)
        {
            Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold , GraphicsUnit.Pixel);
            ev.Graphics.DrawLine(Pens.Black, 5, 5, 1000, 5);
            ev.Graphics.DrawString("X", printFont, Brushes.Black, 450, 10);
            ev.Graphics.DrawLine(Pens.Black, 5, 5, 5, 1000);
            ev.Graphics.DrawString("Y", printFont, Brushes.Black, 10, 450);

            for (int i = 100; i < 1000; i = i + 100)
            {
                
                ev.Graphics.DrawString( i.ToString() + "Y" , printFont, Brushes.Black, (float) 7, (float) i);
                ev.Graphics.DrawString( i.ToString() +"X" , printFont, Brushes.Black, (float)i, (float)7);

            }

        }

        public Point print(PrintPageEventArgs ev)
        {
            
//            this.print_axes(ev);

            Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold , GraphicsUnit.Pixel);
            Font printFont2 = new Font("ARIAL", font_size_4_table, FontStyle.Regular , GraphicsUnit.Pixel);

            foreach (PLabel pl in labels)
            {
                pl.print(ev);
            }

            int _position_x = this.start_point_4_table.X;
            int _position_y = this.start_point_4_table.Y;

                int jk ;
                if (height_of_column > 0)
                { jk=height_of_column; }
                else {
                    jk = font_size_4_table;
                }


                int pos_uio = 0;
                foreach (PColumn _col in columns)
                {
                    int jk2 = 0;
                    int start_point_4_table_Y = this.start_point_4_table.Y;
                    // сначала определим - находится - ли данная колонка в группировке. Берем первую группировку по порядку.
                    for (int pcg = 0; pcg < column_groups.Count; pcg++)
                    {
                        if ((pos_uio >= column_groups[pcg].first_column) && (pos_uio <= column_groups[pcg].last_column))
                        { // Понижаем позицию по оси У на высоту объединенной ячейки
                            start_point_4_table_Y = this.start_point_4_table.Y + column_groups[pcg].height_of_column_group;
                            jk2 = column_groups[pcg].height_of_column_group;
                            column_groups[pcg].extend(_position_x, start_point_4_table_Y);
                            column_groups[pcg].extend(_position_x + (int)_col.Width_(font_size_4_table), this.start_point_4_table.Y);
                        }
                    }

                    ev.Graphics.DrawRectangle(pen, _position_x, start_point_4_table_Y, _col.Width_(font_size_4_table), jk - jk2 + 4);
                    ev.Graphics.DrawString(_col.To_print, printFont, Brushes.Black, new RectangleF(_position_x, start_point_4_table_Y, _col.Width_(font_size_4_table), jk - jk2 + 4));
                    _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                    pos_uio++;
                }

                for (int pcg = 0; pcg < column_groups.Count; pcg++)
                {
                    ev.Graphics.DrawRectangle(pen, new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));
                    ev.Graphics.DrawString(column_groups[pcg].name, printFont, Brushes.Black, new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));

                }



            _position_y = _position_y + jk - font_size_4_table;
            foreach (Dictionary<string, string> _row in rows)
            {
                _position_y = _position_y + font_size_4_table + 4;
                _position_x = this.start_point_4_table.X;
                foreach (PColumn _col in columns)
                {
                    string tp=_row[_col.Name];
                    tp= tp.Replace('\t', ' ');
                    tp = tp.Replace("  ", " ");

                    ev.Graphics.DrawRectangle(pen, _position_x, _position_y, _col.Width_(font_size_4_table), font_size_4_table + 4 );
                    if (_col.Type != "EAN")
                    {
                        ev.Graphics.DrawString(tp, printFont2, Brushes.Black, new RectangleF(_position_x, _position_y, _col.Width_(font_size_4_table), font_size_4_table + 4));
                    }
                    else {

                        Image r = Code128Rendering.MakeBarcodeImage2(tp, 1, true, (int)_col.Width_(font_size_4_table) - 4, (int)font_size_4_table-1  );
                        ev.Graphics.DrawImage(r, _position_x + 2, _position_y + 2, (int)_col.Width_(font_size_4_table) - 4, (int)font_size_4_table - 1);

                    }

                    _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                }
                
            }



            foreach (PTable _table in tables)
            {
                _table.print(ev);
            }
            bottom_point_of_table= new Point(_position_x, _position_y);

            foreach (PArrow _arrow in arrows)
            {
                _arrow.print(ev);
            }

            return bottom_point_of_table;
        }

        public void add_column( string name2, string type2 )
        {
            PColumn c = new PColumn(name2, type2);
            columns.Add(c);
        }

        public void add_column(string name2, string type2 , string to_pr , long width )
        {
            PColumn c = new PColumn(name2, type2, to_pr , width );
            columns.Add(c);
        }

        public void add_column(string name2, string type2, string to_pr )
        {
            PColumn c = new PColumn(name2, type2, to_pr);
            columns.Add(c);
        }

       string footer;

       public PPage()
       {
        
       }

    }

    public class MINI_WMS_USER
    {
        public string user_id = "";
        public long ware_id = 0;
        public string USER_GROUP="";
        public MINI_WMS_USER()
        {
            auth();
        }

        int auth()
        {
            user_id = "KLAD_RABAEV";
            return 0;
        }
    }

}