

using System;
using System.Text;
using System.Collections.Generic;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.IO;
using System.Data;
using System.Data.OracleClient  ;

using System.Data.OleDb;


namespace Tserver
{

    using MapType = Dictionary<string, string>;
    using PairType = KeyValuePair<string, string>;



    

    class funct
    {
        public string function_name = "dummy";
        public MapType strToIntMap = new MapType();


        public void Console_WriteLine(string str)
        {
            Console.WriteLine(str);
        }


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


        public void add_value(string vname, OracleDateTime value2)
        {
            string value1;
            if (value2.IsNull == true)
            {
                value1 = "##.##.####";
            }
            else
            {
                value1 = "" + value2.Day + "." + value2.Month  + "." + value2.Year  + "";
            }

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





    class Server
    {
        public bool m_trace_overdoze=true;
        private TcpListener hostSocket;
        private IPAddress address;
        private int port;
        public long NumberOfRequests=0;
        public long ware_id = 0;
        public string DBWMSString = "DBWMS";

        #region НАСТРОЙКИ_ФУНКЦИОНАЛА_СЕРВЕРА

       

        #endregion


        private string connection_string_to_wms()
        {
//            return "Server=refstock;Password=refstock;User ID=refstock";
            return "Server=" + DBWMSString + ";Password=RABAEVWMS;User ID=RABAEV";
        }


  

        private string MDB_CONNECTION_STRING()
        {
            return "Provider=Microsoft.Jet.OLEDB.4.0; Data Source=\\\\adserv30\\Files\\_Общие\\Рабаев\\OD\\БД.mdb";
        }




        public Server(IPAddress _address, int _port)
        {
            address = _address;
            port = _port;
        }

        private bool SetupServer()
        {
            try
            {
                IPEndPoint endPoint = new IPEndPoint(address, port);
                hostSocket = new TcpListener(endPoint);
                hostSocket.Start(10);
            }catch(Exception ex)
            {
                Console_WriteLine("Сервер не доступен.");
                Console_WriteLine("error f11"+ex.Message);
                return false;
            }
            return true;
        }

      public  void Console_WriteLine(string str)
        {
            Console.WriteLine(str);
        }


        public void Start()
        {
            if (!SetupServer())
            {
                Console_WriteLine("Выход.");
                //Console.ReadKey();
                return;
            }
            while (true)
            {
                AcceptConnections();
            
            }
        }

        private string to_str(double ddd)
        {
            return Convert.ToString(ddd);
        }



        private string to_str(OracleString value2)
        {

            string value1;
            if (value2.IsNull == true)
            {
                value1 = "";
            }
            else
            {
                value1 = Convert.ToString(value2);
            }

            return value1;
        }

        private string date2sql(DateTime dt)
        {

            return "#" + dt.Month + "/" + dt.Day + "/" + dt.Year + "#";

        }

        private string dateTime2sql(DateTime dt)
        {

            return "#" + dt.Month + "/" + dt.Day + "/" + dt.Year + "  "+dt.Hour +":"+ dt.Minute  +":"+dt.Second +"#";
          //  #11/15/2009  7:41:57#
        }

        private string dateTime2sql_ora(DateTime dt)
        {

            return " '" + dt.Month + "/" + dt.Day + "/" + dt.Year + "  " + dt.Hour + ":" + dt.Minute + ":" + dt.Second + "' ";
            //  #11/15/2009  7:41:57#
        }

        private void AcceptConnections()
        {

            TcpClient handleSocket = hostSocket.AcceptTcpClient();
            ((IPEndPoint)handleSocket.Client.RemoteEndPoint).Port = ++port;
            handleSocket.ReceiveTimeout = 10000;
            StringBuilder myCompleteMessage = new StringBuilder();
            DateTime dt47 = DateTime.Now;
            
            Console_WriteLine("START ************************************************** Time=" + dt47.ToLongTimeString());
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
                    byte[] data1 = new byte[len*3];
                    int size = 0;
                    int numberOfBytesRead = 1;
                    StringBuilder l_header = new StringBuilder();

                    // ПРОЧИТАЛИ ХЕДЕР
                    numberOfBytesRead = socketStream.Read(data1, 0, 40);

                    l_header.Append(Encoding.Unicode.GetString(data1, 0, numberOfBytesRead));
                    long len_from_header = Convert.ToInt64(l_header.ToString());


                    do
                    {
                        numberOfBytesRead = socketStream.Read(data1, 0, len );
                        size += numberOfBytesRead;
                        myCompleteMessage.AppendFormat("{0}", Encoding.Unicode.GetString(data1, 0, numberOfBytesRead));
                    } while (size < len_from_header);
                    //} while ((socketStream.DataAvailable ) );
                    //} while (numberOfBytesRead>0);
                    if(m_trace_overdoze)
                    Console.WriteLine(" Запрос клиента: " +  myCompleteMessage + Convert.ToString(NumberOfRequests));

                }

                //socketStream.Close();

                string f1 = myCompleteMessage.ToString();
                F_Request=F_Request1.split_program(f1);
                if(m_trace_overdoze)
                foreach (funct r9 in F_Request)
                {
                    Console.WriteLine(r9.encode());
                }

                #endregion
            }
            catch (Exception ex)
            {
                  Console_WriteLine("F1:"+ex.Message);
                  Console_WriteLine("FAULT #########################################################");

            }


            string summary = "";
            funct r = new funct();
            string USSCC = "";
            string  strSQL = "";
            string OrderNumber = "";
            string PLACEID = "";
            OracleConnection ora_conn;
            OracleCommand ora_com;
            long lines_count_must_be = 0;

            F_Request1 = F_Request[0];

            OracleDataReader ora_reader;
            long pos;
            

            switch (F_Request1.function_name)
            {

                #region СООБЩЕНИЕ_ОБ_ОКОНЧАНИИ_ПРОВЕРКИ_ПАЛЕТОМЕСТА
                case "PLACE_CHECK_PASSED":
                    // Сборка прошла проверку
                    PLACEID = "";
                    PLACEID = F_Request1.get_value("PALLETID");

                    // Регистритуем событие на сервере.

                    #region РАБОТА_С_ОРАКЛ_РЕГИСТРИРУЕМ_ФАКТ_ПРОВЕРКИ


                    try
                    {
                        strSQL = "delete from  RABAEV.PLACE_AUDIT where PALLETID ='" + PLACEID + "' ";
                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_com = new OracleCommand();
                        ora_conn.Open();

                        ora_com.Connection = ora_conn;
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();

                        strSQL = "delete from  RABAEV.PLACE_AUDIT_ERROR_LINES where PALLETID ='" + PLACEID + "' ";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();



                        strSQL = "delete from  RABAEV.INVENTORY_LINE_PALLET_AUDIT where PALLETID ='" + PLACEID + "' ";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();
                        

                        string cond7 = "СОВПАЛО";

                        foreach (funct f5 in F_Request)
                        {
                            if (f5.function_name == "ERROR_PALLET_CHECK_LINE")
                            {
      
                                string l_UID = f5.strToIntMap["УИД"];
                                string l_KOL = f5.strToIntMap["КОЛ"];
                                string l_TYPE = f5.strToIntMap["ТИП"];
                                string l_EAN = f5.strToIntMap["ШТРИХКОД"];
                                if (l_TYPE == "ИЗЛИШКИ")
                                    cond7 = "ИЗЛИШКИ";
                                strSQL = "insert into RABAEV.PLACE_AUDIT_ERROR_LINES (  PALLETID , CONDITION ,unit_count ,UID1,EAN ) values ('"
                                      + PLACEID + "' , '" + l_TYPE + "' , " + l_KOL + " , '" + l_UID + "' , '" + l_EAN + "'  )";
                                ora_com.CommandText = strSQL;
                                ora_com.ExecuteNonQuery();
                            }


                            if (f5.function_name == "INVENTORY_LINE_PALLET_AUDIT")
                            {
                                string l_UID = f5.strToIntMap["УИД"];
                                string l_KOL = f5.strToIntMap["КОЛ"];
                                string PALLETID = f5.strToIntMap["PALLETID"];
                                string USER_ID = f5.strToIntMap["USER_ID"];
                                DateTime mtd = DateTime.Today;

                                strSQL = "insert into  RABAEV.INVENTORY_LINE_PALLET_AUDIT (  УИД , КОЛ ,PALLETID , USER_ID , ДАТАСОЗДАНИЯ ) "+
                                    " values ('"
                                     + l_UID + "' , " + l_KOL + " , '" + PALLETID + "' , '" + USER_ID + "' , '" + mtd.Day + "." + mtd.Month + "." + mtd.Year + "'  )";
                                ora_com.CommandText = strSQL;
                                ora_com.ExecuteNonQuery();
                            }


                        }


                        strSQL = "insert into  RABAEV.PLACE_AUDIT (  PALLETID , CONDITION ) values ('" + PLACEID + "' , '" + cond7 + "'  )";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();



                    }
                    catch (Exception ex)
                    {

                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("Ошибка F2:" + ex.Message);
                    }
                    #endregion

                    r = new funct();
                    r.function_name = "END_PALLET_CHECK_PASSED";
                    r.add_value("PALLETID", PLACEID);
                    summary = summary + r.encode();



                    break;

                #endregion

                #region СООБЩЕНИЕ_ОБ_ОКОНЧАНИИ_ПРОВЕРКИ_НАКЛАДНОЙ
                case "ORDER_CHECK_PASSED":
                    // Сборка прошла проверку
                    OrderNumber = "";
                    OrderNumber = F_Request1.get_value("ORDER");

                    // Регистритуем событие на сервере.

                    #region РАБОТА_С_ОРАКЛ_ПРОВЕРКА_НАКЛАДНОЙ



                    try
                    {
                        strSQL = "delete from  RABAEV.ORDER_AUDIT where ORDER_NUMBER ='" + OrderNumber + "' ";
                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_com = new OracleCommand();
                        ora_conn.Open();

                        ora_com.Connection = ora_conn;
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();

                        strSQL = "delete from  RABAEV.ORDER_AUDIT_ERROR_LINES where ORDER_NUMBER ='" + OrderNumber + "' ";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();

                        string cond = "ЗОНА_ЭКСПЕДИЦИИ";

                        foreach (funct f5 in F_Request)
                        {
                            if (f5.function_name == "ERROR_LOT_LINE")
                            {
                                string l_USSCC = f5.strToIntMap["USSCC"];
                                string l_UID = f5.strToIntMap["УИД"];
                                string l_KOL = f5.strToIntMap["КОЛ"]; // 
                                string l_ПЛАН_КОЛ = f5.strToIntMap["ПЛАН_КОЛ"]; // 

                                

                                string l_TYPE = f5.strToIntMap["ТИП"];
                                string l_EAN = f5.strToIntMap["ШТРИХКОД"];

                                if (l_TYPE == "НЕДОСТАЧА")
                                {
                                    cond = "ЗОНА_ОШИБОК";
                                }

                                strSQL = "insert into  RABAEV.ORDER_AUDIT_ERROR_LINES (  ORDER_NUMBER , CONDITION ,unit_count ,UID1,EAN ) values ('"
                                      + OrderNumber + "' , '" + l_TYPE + "' , " + l_KOL + " , '" + l_UID + "' , '" + l_EAN + "'  )";

                                ora_com.CommandText = strSQL;
                                ora_com.ExecuteNonQuery();


                                /*
                                    f2.add_value("USSCC", this.Curent_USSCC);
                                    f2.add_value("УИД", dr9["УИД"]);
                                    f2.add_value("КОЛ", dr9["КОЛ"]);
                                    f2.add_value("ТИП", dr9["ТИП"]);
                                    f2.add_value("ШТРИХКОД", dr9["ШТРИХКОД"]);
                                */
                                //Console.WriteLine(" l_USSCC=" + l_USSCC + " l_UID=" + l_UID + " l_KOL=" + l_KOL + " l_TYPE=" + l_TYPE + "  l_EAN=" + l_EAN + " ");

                            }

                        }


                        strSQL = "insert into  RABAEV.ORDER_AUDIT (  ORDER_NUMBER , CONDITION ) values ('" + OrderNumber + "' , '" + cond + "'  )";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();

                        // ЕСЛИ ЗАКАз ПРОВЕРЕН - ОТСТАВЛЯЕМ ЕГО В ЗОНУ ЭКСПЕДИЦИИ. 
                        #region  РАБАТА_СО_СТАТУСОМ_ЗАКАЗА_ACCESS
                        if (cond == "ЗОНА_ЭКСПЕДИЦИИ")
                        {
                            OleDbCommand mdb_comm = new OleDbCommand();
                            OleDbConnection mdb_conn = new OleDbConnection();
                            mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                            mdb_conn.Open();
                            mdb_comm.Connection = mdb_conn;
                            // СТАВИМ СТАТУС У ЗАКАЗА = Собран
                            strSQL = " update ТранспортныеЗаданияСтроки set Статус='Собрана' where УИД = " + OrderNumber + " ";
                            mdb_comm.CommandText = strSQL;
                            mdb_comm.ExecuteNonQuery();

                            // ЕСЛИ ВСЕ ЗАКАЗЫ МАРШРУТА СОБРАНЫ, СТАВИМ СТАТУС МАРШРУТА = СОБРАН ПОЛНОСТЬЮ
                            // ОБНОВЛЯЕМ ПРОЦЕНТ СБОРКИ МАРШРУТА
                            strSQL = " select ИДЕНТИФИКАТОР , ДАТАТЗ from ТранспортныеЗаданияСтроки   where УИД = " + OrderNumber + " ";
                            mdb_comm.CommandText = strSQL;
                            OleDbDataReader m_ole_db_reader1 =  mdb_comm.ExecuteReader  ();
                            if (m_ole_db_reader1.Read())
                            {// ЕСЛИ НАКЛАДНАЯ С ТАКИМ УИДОМ ЕСТЬ В БД ОД 
                                string m_route_number = m_ole_db_reader1[0].ToString();
                                DateTime  m_route_data = Convert.ToDateTime( m_ole_db_reader1[1]) ;
                                m_ole_db_reader1.Close();

                                strSQL = " select  УИД , СТАТУС  from ТранспортныеЗаданияСтроки   where ИДЕНТИФИКАТОР  = '" + m_route_number + "' and ДАТАТЗ=" +  date2sql( m_route_data ) + " ";
                                mdb_comm.CommandText = strSQL;
                                 m_ole_db_reader1 = mdb_comm.ExecuteReader();
                                int всего_накладных = 0;
                                int накладных_собрано = 0;

                                while (m_ole_db_reader1.Read())
                                {
                                    string м_статус_накладной = m_ole_db_reader1[1].ToString();
                                    //string м_статус_накладной = m_ole_db_reader1[0].ToString();
                                    всего_накладных++;
                                    if ((м_статус_накладной == "Собрана") || (м_статус_накладной == "ЧастичноДоставлена") || 
                                        (м_статус_накладной == "Отгружена") || (м_статус_накладной == "Доставлена"))
                                        накладных_собрано++;
                                }

                                m_ole_db_reader1.Close();
                                if (всего_накладных > 0)
                                {
                                    int процент_сборки = ( (накладных_собрано*100) / всего_накладных );
                                    string addsql = "";
                                    if (накладных_собрано == всего_накладных)
                                    {
                                        DateTime dt5 = DateTime.Now;

                                        addsql = "  , Собран=true  , КогдаСобран=" + dateTime2sql (dt5) + " ";
                                    }

                                    strSQL = " update ТранспортныеЗадания set ПроцентЗавершения =" +
                                        Convert.ToString(процент_сборки) + addsql + " where   ИДЕНТИФИКАТОРМАРШРУТА  = '" + 
                                        m_route_number + "' and ДАТАТЗ=" + date2sql( m_route_data ) + " "; 

                                    mdb_comm.CommandText = strSQL;
                                    mdb_comm.ExecuteNonQuery();
                                }


                            }


                        }
                        #endregion



                    }
                    catch (Exception ex)
                    {

                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("Ошибка F3:"+ex.Message);
                    }
                    #endregion

                    r = new funct();
                    r.function_name = "END_ORDER_CHECK_PASSED";
                    r.add_value("ORDER", OrderNumber );
                    summary = summary + r.encode();



                    break;

                #endregion
                
                case "VP":
                   // PALLET_UID = F_Request1.get_value("PALLET_UID");

                   // FUNC=VP|PALLET_UID=OP_СТе8м010522_1|УИД=Т0000093552|TIME='31.10.2010 22:59:22'
                break;


                #region СООБЩЕНИЕ_ОБ_ОКОНЧАНИИ_ПРОВЕРКИ_ЛОТА
                case "LOT_CHECK_PASSED":
                    Console_WriteLine("LOT_CHECK_PASSED!");
                    // Сборка прошла проверку
                    USSCC = "";
                    USSCC = F_Request1.get_value("USSCC");
                    string USER_ID1 = "";
                    USER_ID1 = F_Request1.get_value("USER_ID");
                    long error_count = Convert.ToInt32( F_Request1.get_value("error_count"));
 

                    // Регистритуем событие на сервере.

                    #region РАБОТА_С_ОРАКЛ


                    
                    try
                    {
                        strSQL = "delete from LOT_AUDIT where SSCC='" + USSCC + "' ";
                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_com = new OracleCommand();
                        ora_conn.Open();
                        
                        ora_com.Connection = ora_conn;
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery ();

                        Console_WriteLine("LOT_CHECK_PASSED flag5+" + error_count.ToString());
                        if (error_count == 0)
                        {
                            OracleCommand ora_com2 = new OracleCommand();
                            ora_com2.Connection = ora_conn;
                            ora_com2.CommandText = "RABAEV.RRL_SET_SCAN_PROOVE2";
                            ora_com2.CommandType = CommandType.StoredProcedure;
                            ora_com2.Parameters.Add("PALLET_UID1", OracleType.VarChar).Value = USSCC;
                            ora_com2.Parameters.Add("count_of_errors1", OracleType.Int32).Value = error_count;
                            ora_com2.Parameters.Add("prim1", OracleType.VarChar).Value = "";
                            ora_com2.Parameters.Add("ID1", OracleType.VarChar, 10).Direction = ParameterDirection.ReturnValue;
                            ora_com2.Parameters.Add("SBORSHIK1", OracleType.VarChar).Value = USER_ID1;
                            ora_com2.Parameters.Add("KLADOVSHIK1", OracleType.VarChar).Value = "";
                            int rowsAffected3 = ora_com2.ExecuteNonQuery();
                        }

                        strSQL = "delete from LOT_AUDIT_ERROR_LINES where SSCC='" + USSCC + "' ";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();

                        /*
                        strSQL = " update   RABAEV.RRL_SBORKA_PALLET_ROWS  set SOBRANO = QUANTITY where  ( PALLET_UID='" + USSCC
                                          + "' ) ";
                        Console_WriteLine(strSQL);
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();
                        */

                        string cond = "ЗОНА_ЭКСПЕДИЦИИ";

                        foreach (funct f5 in F_Request)
                        {
                            if (f5.function_name == "ERROR_LOT_LINE")
                            {
                                string l_USSCC = f5.strToIntMap["USSCC"];
                                string l_UID = f5.strToIntMap["УИД"];
                                string l_KOL = f5.strToIntMap["КОЛ"];
                                string l_ПЛАН_КОЛ = f5.strToIntMap["ПЛАН_КОЛ"];
                                string l_TYPE = f5.strToIntMap["ТИП"];
                                string l_EAN = f5.strToIntMap["ШТРИХКОД"];
                                

                                
                                
                                if (l_TYPE == "НЕДОСТАЧА") 
                                {
                                    cond = "ЗОНА_ОШИБОК";
                                }

                                //strSQL = "insert into LOT_AUDIT_ERROR_LINES (SSCC , CONDITION ,unit_count ,UID1,EAN , PLAN_COUNT ) values ('"
                                //    + l_USSCC + "' , '" + l_TYPE + "' , " + l_KOL + " , '" + l_UID + "' , '" + l_EAN + "' , " + l_ПЛАН_КОЛ + " )";
                                strSQL = " update   RABAEV.RRL_SBORKA_PALLET_ROWS  set SOBRANO = " + l_KOL + " where  ( PALLET_UID='" + l_USSCC
                                           + "' ) and ( ARTICUL = '" + l_UID + "' ) ";
                                ora_com.CommandText = strSQL;
                                //Console_WriteLine(strSQL);
                                ora_com.ExecuteNonQuery();

                            }
                            
                            if (f5.function_name == "VP")
                            {
                                string time = f5.strToIntMap["TIME"];
                                if (time != "")
                                {
                                    try
                                    {
                                        OracleCommand ora_com6 = new OracleCommand();
                                        ora_com6.Connection=ora_conn;
                                        string PALLET_UID = f5.strToIntMap["PALLET_UID"];
                                        string l_UID = f5.strToIntMap["УИД"];
                                        strSQL = " update   RABAEV.RRL_SBORKA_PALLET_ROWS  set TIME_OF_CHECKING = to_date( " + time + " ,'dd.mm.yyyy HH24:MI:ss') where  ( PALLET_UID='" + PALLET_UID
                                            + "' ) and ( ARTICUL = '" + l_UID + "' ) ";
                                        ora_com6.CommandText = strSQL;
                                        ora_com6.ExecuteNonQuery();
                                    }catch(Exception exp)
                                    {
                                        Console.WriteLine("VP error: "+exp.Message);
                                    }
                                }
                            }

                        }

                        //Console.WriteLine("ПРИВЕТ");

                        strSQL = "insert into LOT_AUDIT (SSCC , CONDITION ) values ('" + USSCC + "' , '"+cond+"'  )";
                        ora_com.CommandText = strSQL;
                        ora_com.ExecuteNonQuery();



                    }
                    catch (Exception ex)
                    {

                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("Error F477:"+ex.Message);
                    }
                    #endregion

                    r = new funct();
                    r.function_name = "END_LOT_CHECK_PASSED";
                    r.add_value("USSCC", USSCC);
                    summary = summary + r.encode();



                    break;

                #endregion
                

                #region ИНФОРМАЦИЯ_ПО_АРТИКУЛУ
                case  "GET_PRODUCT_INFO":
                    // НУЖНО ВЕРНУТЬ ПАРЕМЕТРЫ КАРТОЧКИ ТОВАРА ИЗ СФЕРЫ
                    string ushk = F_Request1.get_value("ШТРИХКОД");
                    string trim_ushk = ushk.Trim('0');
                    #region РАБОТА_С_ОРАКЛ
                    strSQL = " select " + 
" distinct " + 
" SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-1 ,1  ) as pic_level , " + 
" UL_CPROIN ,  " + 
" UE_ADRUMS ,  " + 
"  TB_ART.AR_LIBPRO as Имя ,  " +
"  TB_ART.AR_PDSUVC  as ВБ_ШТ ,  " +
"  AR_PDSCAR  as ВБ_КОР ,  " +
"  AR_PDSSPC as ВБ_БЛ , " +
"  AR_PDSPAL as ВБ_ПАЛЕТЫ ,  " +
" sfera_ean.EAN_SHT ,  " + 
" sfera_ean.EAN_BL ,  " + 
" sfera_ean.EAN_KOR , " +
"     sfera_ean.SHT_IN_BL , sfera_ean.BL_IN_KOR  " +

" from refstock.TB_LCUMS  " + 
" left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM' " + 
" left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM' " + 
" left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID  " + 
" where ul_donord='RM' " + 
" and not ( sfera_ean.TMC_UID  is null ) " + 
" and not ( UE_ADRUMS is null) " +
" and  ( EAN_SHT='" + ushk + "' or  EAN_BL='" + ushk + "' or  EAN_KOR='" + ushk + "'  or EAN_SHT='" + trim_ushk + "' or  EAN_BL='" + trim_ushk + "' or  EAN_KOR='" + trim_ushk + "'  ) " + 
" and LENGTH(UE_ADRUMS)>=1 " + 
" and SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-1 ,1  ) in ('1','2') ";

                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();
                    ora_com = new OracleCommand();


                    ora_com.CommandText = strSQL;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                         ora_reader = ora_com.ExecuteReader();

                         pos = 0;

                        while (ora_reader.Read())
                        {
                            r = new funct();
                            r.function_name = "END_GET_PRODUCT_INFO";
                            r.add_value("АДРЕС", ora_reader.GetOracleString(2));
                            r.add_value("УИД", ora_reader.GetOracleString(1));
                            r.add_value("ИМЯ", ora_reader.GetOracleString(3));

                            r.add_value("ВБ_ШТ",  ora_reader.GetOracleNumber(4))  ;
                            r.add_value("ВБ_КОР", (  ora_reader.GetOracleNumber(5)));
                            r.add_value("ВБ_БЛ",  ( ora_reader.GetOracleNumber(6)));

                            r.add_value("ШК_ШТ", ora_reader.GetOracleString(8));
                            r.add_value("ШК_БЛ", ora_reader.GetOracleString(9));
                            r.add_value("ШК_КОР", ora_reader.GetOracleString(10));

                             r.add_value("ШВБ", (  ora_reader.GetOracleNumber(11)));
                            r.add_value("БВК",  ( ora_reader.GetOracleNumber(12)));


                            summary = summary + r.encode();

                            pos++;
                        }

                        ora_reader.Close();
                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:"+ex.Message);
                    }

                    #endregion
                    break;
                #endregion



                #region ОБНОВЛЕНИЕ_ИНФОРМАЦИИ_ПО_АРТИКУЛУ
                case "UPDATE_PRODUCT_INFO":
                    // НУЖНО ВЕРНУТЬ ПАРЕМЕТРЫ КАРТОЧКИ ТОВАРА ИЗ СФЕРЫ
                    int ШТВБЛ_7 = 0;
                    int БЛВКОР_7 = 0;

                    try{
                        ШТВБЛ_7 = Convert.ToInt32( F_Request1.get_value("ШТВБЛ") ) ;
                        БЛВКОР_7 = Convert.ToInt32(  F_Request1.get_value("БЛВКОР"));
                    }catch(Exception ex)
                    {
                    
                    }

                    string ШК_ШТУКИ_7 = F_Request1.get_value("ШК_ШТУКИ");
                    string ШК_БЛОКА_7 = F_Request1.get_value("ШК_БЛОКА");
                    string ШК_КОРОБ_7 = F_Request1.get_value("ШК_КОРОБ");
                    string УИД_7 = F_Request1.get_value("УИД");
                    bool штрих_код_изменился = false;
                    // ЕСЛИ ШТРИХ-КОД ШТУКИ НЕ ИЗМЕНИЛСЯ, МЕНЯЕМ ШК БЛОКА И КОРОБКИ В СФЕРЕ И ВМС
                    // ИНАЧЕ ДЕЛАЕМ ДОПОЛНИТЕЛЬНЫЙ МАНУАЛЬНЫЙ ШТРИХ - КОД

                    #region РАБОТА_С_ОРАКЛ
                    string sql1 ="";
                    string sql2 ="";
                    string sql3 ="";
                    string sql4 ="";
                    string sql5 ="";
                    if(ШТВБЛ_7*БЛВКОР_7>0){
                        sql1 = ", COUNT_SHT_IN_KOR=" + Convert.ToString(ШТВБЛ_7 * БЛВКОР_7) + " ";
                    }

                    if(ШТВБЛ_7 >0){
                       sql2 = ", COUNT_SHT_IN_BL=" + Convert.ToString (ШТВБЛ_7 ) + " ";
                    }
                    if(ШК_ШТУКИ_7!="")
                    {
                      sql3 = ", BARCODE_SHT='" + ШК_ШТУКИ_7 + "' ";
                    }
                    
                    if(ШК_БЛОКА_7!="")
                    {
                        sql4 = ", BARCODE_BL='" + ШК_БЛОКА_7 + "' ";
                    }

                    if (ШК_БЛОКА_7 != "")
                    {
                        sql5 = ", BARCODE_KOR='" + ШК_КОРОБ_7 + "' ";
                    }

                    strSQL = " update RABAEV.RRL_ARTICULS   set ACTICUL='" + УИД_7 + "' " + sql1 + sql2 + sql3 + sql4 + sql5 + "  where  ACTICUL='" + УИД_7 + "'     ";

                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();
                    ora_com = new OracleCommand();


                    ora_com.CommandText = strSQL;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();
                        /*
                        while( ora_reader.Read() ){
                        
                            //r = new funct();
                            //r.function_name = "END_GET_PRODUCT_INFO";
                            //r.add_value("АДРЕС", ora_reader.GetOracleString(2));
                            //r.add_value("УИД", );
                            if (ШК_ШТУКИ_7 == ora_reader.GetOracleString(0).ToString())
                            {
                                штрих_код_изменился = false;
                            }
                            else { штрих_код_изменился = true; }

                        }
                        ora_reader.Close();


                        // ЕСЛИ ШТРИХ-КОД ШТУКИ НЕ ИЗМЕНИЛСЯ, МЕНЯЕМ ШК БЛОКА И КОРОБКИ В СФЕРЕ И ВМС
                        if (!штрих_код_изменился)
                        {
                            strSQL = " update RABAEV.SFERA_EAN set EAN_BL='" + ШК_БЛОКА_7 + "' , EAN_KOR='" + ШК_КОРОБ_7 + "' , MANUALENTER='Y'  where  TMC_UID='" + УИД_7 + "'  and  EAN_SHT='" + ШК_ШТУКИ_7 + "'   ";
                            ora_com.CommandText = strSQL;
                            ora_com.ExecuteNonQuery();
                        }
                        else 
                        {
                            strSQL = " insert into RABAEV.SFERA_EAN ( TMC_UID , EAN_SHT , EAN_BL , EAN_KOR , MANUALENTER , ШТВБЛ_7 , БЛВКОР_7 ) values ( '" + УИД_7 + "' , '" + ШК_ШТУКИ_7 + "' , '" + ШК_БЛОКА_7 + "' , ='" + ШК_КОРОБ_7 + "' , 'Y' , SHT_IN_BL , BL_IN_KOR  )  where  TMC_UID='" + УИД_7 + "'     ";
                            ora_com.CommandText = strSQL;
                            ora_com.ExecuteNonQuery();
                        }
                        // ИНАЧЕ ДЕЛАЕМ ДОПОЛНИТЕЛЬНЫЙ МАНУАЛЬНЫЙ ШТРИХ - КОД
                        */

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion
                  


                #region ЗАПРОС_СТРОК_ЛОТА
                case "GET_LOT_ITEMS":
                   
                    // НУЖНО ВЕРНУТЬ ВСЕ ЗАПИСИ ЛОТА ИЗ WMS. : УИД , КОЛИЧЕСТВО ; АДРЕС 
                    // и параметры товара: 
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************
                    USSCC = "";
                    USSCC=F_Request1.get_value("USSCC");
                     
                     ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();

                     ora_com = new OracleCommand();
                    // НОМЕР ЛОТА
                    // НОМЕР АРТИКУЛА
                    // КОЛИЧЕСТВО В ШТУКАХ
                    // Наименование
                    // Адрес отбора
                    // Штук в блоке
                    // блоков в коробке
                    // ШК Штуки
                    // ШК блока
                    // ШК короба

                     strSQL = " select  p.pallet_uid , " +
                         "  R.ARTICUL , " +
                         "  QUANTITY , " +
                         "  SHORTNAME , " +
                         "  PATH , " +
                         "  A.COUNT_SHT_IN_BL , " +
                         "   ROUND(A.COUNT_SHT_IN_KOR/A.COUNT_SHT_IN_BL , 0 ) , " +
                         "  A.BARCODE_SHT , " +
                         "    A.BARCODE_BL , " +
                         "  A.BARCODE_KOR ,  p.ST_NUMBER " +
                         "  from RRL_SBORKA_PALLETS P , RRL_SBORKA_PALLET_ROWS R , RRL_ARTICULS A " +
                         "  where R.PALLET_UID = P.PALLET_UID and P.PALLET_UID = '" + USSCC + 
                         "' and R.ARTICUL = A.ACTICUL(+) order by SORTFIELD "; 




                    ora_com.CommandText = strSQL;
                     lines_count_must_be = 0;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();

                        // Always call Read before accessing data.
                         pos = 0;
                        //string sql_product = "";
                         string order_number="";

                        while (ora_reader.Read())
                        {
                            
                                pos++;
                                lines_count_must_be++;
                                r = new funct();
                                r.function_name = "LOT_LINE";
                                r.add_value("ПП", Convert.ToString(pos));
                                //r.add_value("USSCCD", ora_reader.GetString(0));
                                r.add_value("УИД", ora_reader.GetString(1));
                                r.add_value("КОЛ", Convert.ToString(ora_reader.GetInt64(2)));
                                r.add_value("НАИМ", ora_reader.GetString(3));
                                r.add_value("СЛУЖ_АДР", ora_reader.GetString(4));
                                r.add_value("СЛУЖ_ШТВБЛ", ora_reader.GetInt64(5));

                                long hj = 1;
                            
                                try
                                {
                                    hj =  ora_reader.GetInt64(6);
                                }catch (Exception ex)
                                {
                                    hj = 1;
                                }

                                r.add_value("СЛУЖ_БЛВКОР", hj);
                                r.add_value("СЛУЖ_ШК_ШТУКИ", ora_reader.GetOracleString(7));
                                r.add_value("СЛУЖ_ШК_БЛОКА", ora_reader.GetOracleString(8));
                                r.add_value("СЛУЖ_ШК_КОРОБ", ora_reader.GetOracleString(9));
                                //sfera_ean.EAN_SHT , sfera_ean.EAN_BL , sfera_ean.EAN_KOR 
                                order_number = ora_reader.GetOracleString(10).Value.ToString();

                                summary = summary + r.encode();
                            
                            //sql_product = sql_product + ", " + ora_reader.GetString(1);

                        }
                        //sql_product.TrimStart(',');


                        #region ВЫБОРКА_ДОПОЛНИТЕЛЬНЫХ_ШТРИХ_КОДОВ_ШТРИХКОД_ЯЧЕЙКИ

                            strSQL = " select   " +
                              "  R.ARTICUL , " +
                              "  '' , " +
                              "  '' , " + //A.BARCODE_BL
                              "   A.CELL  , " + //A.BARCODE_KOR
                              "  A.COUNT_SHT_IN_BL , " +
                              "  ROUND(A.COUNT_SHT_IN_KOR/A.COUNT_SHT_IN_BL , 0 )  " +
                              "  from RRL_SBORKA_PALLETS P , RRL_SBORKA_PALLET_ROWS R , RRL_ARTICULS A " +
                              "  where R.PALLET_UID = P.PALLET_UID and P.PALLET_UID = '" + USSCC +
                              "' and R.ARTICUL = A.ACTICUL(+) order by SORTFIELD "; 
                            

                            ora_com.CommandText = strSQL;
                            ora_reader = ora_com.ExecuteReader();

                            while (ora_reader.Read())
                            {
                                r = new funct();
                                r.function_name = "ALT_SHT";
                                r.add_value("УИД", ora_reader.GetOracleString(0));
                                r.add_value("ШКШ", ora_reader.GetOracleString(1));
                                r.add_value("ШКБ", ora_reader.GetOracleString(2));
                                r.add_value("ШКК", ora_reader.GetOracleString(3));
  
                                long ШВБ = Convert.ToInt64(ora_reader.GetOracleNumber(4).Value);
                                r.add_value("ШВБ", ШВБ );
                                long БВК = 1;
                                OracleNumber _БВК = ora_reader.GetOracleNumber(5);
                                if ( ! _БВК.IsNull  )
                                { БВК = Convert.ToInt64(ora_reader.GetOracleNumber(5).Value); }
                                if (БВК == 0) { БВК = 1; }
                                r.add_value("БВК", БВК );
                                summary = summary + r.encode();
                            }
                            ora_reader.Close();

                        #endregion


                            #region ВЫБОРКА_ДОПОЛНИТЕЛЬНЫХ_ШТРИХ_КОДОВ_ШТРИХ_КОД_МОДИФИКАЦИИ

                            strSQL = " select   " +
                              "  R.ARTICUL , " +
                              "  '' , " +
                              "  MOD.SHK_SHT , " + //A.BARCODE_BL
                              "  MOD. SHK_KOR   , " + //A.BARCODE_KOR
                              "  A.COUNT_SHT_IN_BL , " +
                              "  ROUND(A.COUNT_SHT_IN_KOR/A.COUNT_SHT_IN_BL , 0 )  " +
                              "  from RRL_SBORKA_PALLETS P , RRL_SBORKA_PALLET_ROWS R , RRL_ARTICULS A , " +
                              " RRL_ARTICUL_MODS MOD "+
                              "  where R.PALLET_UID = P.PALLET_UID and P.PALLET_UID = '" + USSCC +
                              "' and R.ARTICUL = A.ACTICUL(+) and MOD.ARTICUL=R.ARTICUL order by SORTFIELD ";

                            ora_com = new OracleCommand();
                            ora_com.Connection = ora_conn;
                            ora_com.CommandText = strSQL;
                            ora_reader = ora_com.ExecuteReader();

                            while (ora_reader.Read())
                            {
                                r = new funct();
                                r.function_name = "ALT_SHT";
                                r.add_value("УИД", ora_reader.GetOracleString(0));
                                r.add_value("ШКШ", ora_reader.GetOracleString(1));
                                r.add_value("ШКБ", ora_reader.GetOracleString(2));
                                r.add_value("ШКК", ora_reader.GetOracleString(3));

                                long ШВБ = Convert.ToInt64(ora_reader.GetOracleNumber(4).Value);
                                r.add_value("ШВБ", ШВБ);
                                long БВК = 1;
                                OracleNumber _БВК = ora_reader.GetOracleNumber(5);
                                if (!_БВК.IsNull)
                                { БВК = Convert.ToInt64(ora_reader.GetOracleNumber(5).Value); }
                                if (БВК == 0) { БВК = 1; }
                                r.add_value("БВК", БВК);
                                summary = summary + r.encode();
                            }
                            ora_reader.Close();

                            #endregion



                        r = new funct();
                        r.function_name = "LOT_LINES";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        r.add_value("order_number", order_number);

                        
                        summary =r.encode()+ summary  ;

                        r = new funct();
                        r.function_name = "END";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = summary + r.encode();
                        //r.split_program(summary);

                        // Always call Close when done reading.
                        ora_reader.Close();
                        // Теперь передаем EAN КОДЫ
                        // ДЛЯ ВСЕХ ПРОДУКТОВ ИЗ СБОРКИ, собираем ЕАН коды, с умножителями, передаем клиенту

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message );
                        summary = summary + r.encode();
                        Console_WriteLine("error f6:"+ex.Message);
                    }

                    //F_Response.split("FUNC=LOT_ITEMS|");
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************
                    
                    break;
                #endregion


                #region ЗАПРОС_СТРОК_НАКЛАДНОЙ_ПО_НОМЕРУ_ЛОТА
                case "GET_ORDER_ITEMS":

                    // НУЖНО ВЕРНУТЬ ВСЕ ЗАПИСИ ЛОТА ИЗ WMS. : УИД , КОЛИЧЕСТВО ; АДРЕС 
                    // и параметры товара: 
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************
                    USSCC = "";
                    USSCC = F_Request1.get_value("USSCC");
                     OrderNumber = "";


                    try
                    {


                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();
                    ora_com = new OracleCommand();

                    strSQL = " select  distinct te.CD_NUMCDE " +
                    " from refstock.tb_ecde te   left join refstock.TB_LPREP tlp  " +
                    " on  tlp.LP_NUMORL=te.cd_numorl " +
                    " where   tlp.LP_USSCCD ='" + USSCC + "'  ";

                    ora_com.CommandText = strSQL;
                    ora_conn.Open();
                    ora_com.Connection = ora_conn;
                     ora_reader = ora_com.ExecuteReader();
                     pos = 0;
                    if (ora_reader.Read())
                    {
                        string value2 = to_str(ora_reader.GetOracleString (0));
                        OrderNumber = ( value2 );
                    }





                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();

                    ora_com = new OracleCommand();
                    strSQL = "select distinct " +
                    " te.CD_NUMCDE ,   " +
                    " tl.ld_cproin uid_mat,   " +
                    " sum( LP_UVAPRE  ) kol_sht, " +
                    " ta.ar_libpro nam_mat,   " +
                    " tlp.lp_adrpic adr_pic,   " +
                    " ta.ar_n3uvsp sht_bl ,  " +
                    " ta.AR_N3SPCA bl_v_kor ,   " +
                    " te.cd_numcde,  " +
                    "  RABAEV.RRL_sfera_ean_EAN_SHT( tl.ld_cproin ) ,  " +
                    "  RABAEV.RRL_sfera_ean_EAN_BL( tl.ld_cproin ) ,  " +
                    " RABAEV.RRL_sfera_ean_EAN_KOR( tl.ld_cproin )     " +
                   " from refstock.tb_ecde te " +
                   " left join refstock.TB_LCDE tl on tl.ld_numorl=te.cd_numorl and tl.ld_donord='RM' and tl.ld_depot='01' " +
                   " left join refstock.tb_art ta on ta.ar_cproin=tl.ld_cproin and ta.ar_donord=te.cd_donord  " +
                   " left join refstock.TB_LPREP tlp on tlp.LP_NUMORL=te.cd_numorl and ta.ar_cproin=tlp.lp_cproin " +
                   " left join RABAEV.SFERA_EAN sfera_ean on   ( tl.ld_cproin = sfera_ean.tmc_uid and sfera_ean.manualenter='N' )  " +
                   " where(    te.CD_NUMCDE ='" + OrderNumber + "' )  " +
                    " group by   " +
                    " te.CD_NUMCDE ,  " +
                    " tl.ld_cproin ,    " +
                    " ta.ar_libpro ,    " +
                    " tlp.lp_adrpic ,    " +
                    " ta.ar_n3uvsp  ,   " +
                    " ta.AR_N3SPCA  ,    " +
                    " sfera_ean.EAN_SHT ,   " +
                    " sfera_ean.EAN_BL ,   " +
                    " sfera_ean.EAN_KOR     having  not(  SUM (lp_uvapre)  is null )  " +
                   " order by adr_pic ";



                    ora_com.CommandText = strSQL;
                    lines_count_must_be = 0;
                    
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                         ora_reader = ora_com.ExecuteReader();

                        // Always call Read before accessing data.
                         pos = 0;
                        string sql_product = "";

                        while (ora_reader.Read())
                        {
                            pos++;
                            lines_count_must_be++;
                            r = new funct();
                            r.function_name = "LOT_LINE";
                            r.add_value("ПП", Convert.ToString(pos));
                            //r.add_value("USSCCD", ora_reader.GetString(0));
                            r.add_value("УИД", ora_reader.GetString(1));
                            r.add_value("КОЛ", Convert.ToString(ora_reader.GetInt64(2)));
                            r.add_value("НАИМ", ora_reader.GetString(3));
                            r.add_value("СЛУЖ_АДР", ora_reader.GetString(4));

                            r.add_value("СЛУЖ_ШТВБЛ", ora_reader.GetInt64(5));
                            r.add_value("СЛУЖ_БЛВКОР", ora_reader.GetInt64(6));

                            r.add_value("СЛУЖ_ШК_ШТУКИ", ora_reader.GetOracleString(8));
                            r.add_value("СЛУЖ_ШК_БЛОКА", ora_reader.GetOracleString(9));
                            r.add_value("СЛУЖ_ШК_КОРОБ", ora_reader.GetOracleString(10));
                            //sfera_ean.EAN_SHT , sfera_ean.EAN_BL , sfera_ean.EAN_KOR 
                            summary = summary + r.encode();
                            sql_product = sql_product + ", " + ora_reader.GetString(1);
                        }
                        sql_product=sql_product.TrimStart(',');

                        r = new funct();
                        r.function_name = "LOT_LINES";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        r.add_value("order_number", OrderNumber);
                        summary = r.encode() + summary;

                        r = new funct();
                        r.function_name = "END";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = summary + r.encode();
                        //r.split_program(summary);

                        // Always call Close when done reading.
                        ora_reader.Close();
                        // Теперь передаем EAN КОДЫ
                        // ДЛЯ ВСЕХ ПРОДУКТОВ ИЗ СБОРКИ, собираем ЕАН коды, с умножителями, передаем клиенту

                        #region ВЫБОРКА_ДОПОЛНИТЕЛЬНЫХ_ШТРИХ_КОДОВ




                        strSQL = " select TMC_UID ,EAN_SHT , EAN_BL  , EAN_KOR   , SHT_IN_BL  , " +
                            "  BL_IN_KOR  , MANUALENTER  from RABAEV.SFERA_EAN where TMC_UID in ( " + sql_product +
                            " ) and (not ( SHT_IN_BL is null ))   and (not ( BL_IN_KOR is null )) order by MANUALENTER desc ";
                        ora_com.CommandText = strSQL;
                        ora_reader = ora_com.ExecuteReader();

                        while (ora_reader.Read())
                        {
                            r = new funct();
                            r.function_name = "ALT_SHT";
                            r.add_value("УИД", ora_reader.GetOracleString(0));
                            r.add_value("ШКШ", ora_reader.GetOracleString(1));
                            r.add_value("ШКБ", ora_reader.GetOracleString(2));
                            r.add_value("ШКК", ora_reader.GetOracleString(3));
                            r.add_value("ШВБ", ora_reader.GetInt64(4));
                            r.add_value("БВК", ora_reader.GetInt64(5));
                            summary = summary + r.encode();
                        }

                        #endregion
                        
                        ora_reader.Close();




                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f7:"+ex.Message);
                    }

                    //F_Response.split("FUNC=LOT_ITEMS|");
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************

                    break;
                #endregion


                #region ЗАПРОС_СТРОК_ПАЛЛЕТО_МЕСТА
                case "GET_PLACE_ITEMS":

                    // НУЖНО ВЕРНУТЬ ВСЕ ЗАПИСИ ЛОТА ИЗ WMS. : УИД , КОЛИЧЕСТВО ; АДРЕС 
                    // и параметры товара: 
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************
                    PLACEID = "";
                    PLACEID = F_Request1.get_value("PLACEID");

                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();

                    ora_com = new OracleCommand();

                    strSQL = "  select  " +
   "  UL_CPROIN УИД, " +
   "  sum(UL_NQTUVC) КОЛИЧ , " +
   "  AR_LIBPRO НАИМ ,   " +
   "  UE_ADRUMS АДРЕС, " +
   "     sfera_ean.SHT_IN_BL , sfera_ean.BL_IN_KOR , " +
   "  sfera_ean.EAN_SHT , sfera_ean.EAN_BL , sfera_ean.EAN_KOR , " +
   "  max(to_date(UT_VALIND,'YYYY.MM.DD')) МАКСДАТА , " +
   "  min(to_date(UT_VALIND,'YYYY.MM.DD')) МИНДАТА " +
   " from refstock.TB_LCUMS  " +
   " left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM' " +
   " left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM' " +
   " left join refstock.tb_traums on ue_usscc=ut_usscc and ul_numlig=ut_numlig " +
   " left join refstock.TB_RACK on rk_depot='01' and ue_zone=rk_zone and ue_allee=rk_allee and ue_travee=rk_travee and rk_niveau=ue_niveau " +
   " left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID and manualenter='N' " +
   " where ul_donord='RM' " +
   " and ul_numorl is null    " +
   " and UE_ADRUMS = '" + PLACEID + "' " +
   " and ul_nqtuvc<>0 " +
   " group by  " +
   "  UL_CPROIN, AR_LIBPRO, UE_ADRUMS, AR_NRSFOU , " +
   "  sfera_ean.EAN_SHT , sfera_ean.EAN_BL , sfera_ean.EAN_KOR , sfera_ean.SHT_IN_BL , sfera_ean.BL_IN_KOR ";


                    ora_com.CommandText = strSQL;
                    lines_count_must_be = 0;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();

                        // Always call Read before accessing data.
                        pos = 0;
                        string sql_product = "";

                        while (ora_reader.Read())
                        {
                            pos++;
                            lines_count_must_be++;
                            r = new funct();
                            r.function_name = "PL";
                            r.add_value("ПП", Convert.ToString(pos));
                            r.add_value("УИД", ora_reader.GetString(0));
                            r.add_value("КОЛ", Convert.ToString(ora_reader.GetInt64(1)));
                            r.add_value("НАИМ", ora_reader.GetOracleString(2));
                            r.add_value("СЛУЖ_АДР", ora_reader.GetOracleString(3));

                            r.add_value("СЛУЖ_ШТВБЛ", ora_reader.GetOracleNumber(4));
                            r.add_value("СЛУЖ_БЛВКОР", ora_reader.GetOracleNumber(5));

                            r.add_value("СЛУЖ_ШК_ШТУКИ", ora_reader.GetOracleString(6));
                            r.add_value("СЛУЖ_ШК_БЛОКА", ora_reader.GetOracleString(7));
                            r.add_value("СЛУЖ_ШК_КОРОБ", ora_reader.GetOracleString(8));

                            summary = summary + r.encode();
                            sql_product = sql_product + ", '" + ora_reader.GetString(0)+"'";

                        }
                        sql_product=sql_product.TrimStart(',');

                        r = new funct();
                        r.function_name = "PLACE_LINES";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = r.encode() + summary;

                        r = new funct();
                        r.function_name = "END";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = summary + r.encode();
                        //r.split_program(summary);

                        ora_reader.Close();
                        #region ВЫБОРКА_ДОПОЛНИТЕЛЬНЫХ_ШТРИХ_КОДОВ



                        strSQL = " select TMC_UID ,EAN_SHT , EAN_BL  , EAN_KOR   , SHT_IN_BL  , " +
                                               "  BL_IN_KOR  , MANUALENTER  from RABAEV.SFERA_EAN where TMC_UID in ( " + sql_product +
                                               " ) and (not ( SHT_IN_BL is null ))   and (not ( BL_IN_KOR is null )) order by MANUALENTER desc ";
                 

                        ora_com.CommandText = strSQL;
                        ora_reader = ora_com.ExecuteReader();

                        while (ora_reader.Read())
                        {
                            r = new funct();
                            r.function_name = "ALT_SHT";
                            r.add_value("УИД", ora_reader.GetOracleString(0));
                            r.add_value("ШКШ", ora_reader.GetOracleString(1));
                            r.add_value("ШКБ", ora_reader.GetOracleString(2));
                            r.add_value("ШКК", ora_reader.GetOracleString(3));
                            r.add_value("ШВБ", ora_reader.GetOracleNumber(4));
                            r.add_value("БВК", ora_reader.GetOracleNumber(5));
                            summary = summary + r.encode();
                        }



                        #endregion


                        // Always call Close when done reading.
                        ora_reader.Close();
                        // Теперь передаем EAN КОДЫ
                        // ДЛЯ ВСЕХ ПРОДУКТОВ ИЗ СБОРКИ, собираем ЕАН коды, с умножителями, передаем клиенту

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f8"+ex.Message);
                    }

                    //F_Response.split("FUNC=LOT_ITEMS|");
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************

                    break;
                #endregion


                #region ЗАПРОС_СТРОК_ПРОЛЕТА_СТЕЛЛАЖА
                case "GET_PROLET_ITEMS":

 
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************
                    string пролет = "";
                    string стеллаж = "";

                    пролет = F_Request1.get_value("PROLET");
                    стеллаж = F_Request1.get_value("STELLAJ");


                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();

                    ora_com = new OracleCommand();
                    
                    strSQL = 
                    " select  " + 
                    " SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS) ,1  ) as секция,  " + 
                    " SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-2 ,2  ) as этаж,  " + 
                    " SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-5 ,3  ) as раздел,  " + 
                    " SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-7 ,2  ) as стеллаж,  " + 
                    " sum(UL_NQTUVC) КОЛИЧ ,  " + 
                    " trunc(sum(UL_NQTUVC)/(TB_ART.ar_n3uvsp*TB_ART.ar_n3spca),0) kor,  " + 
                    " trunc((sum(UL_NQTUVC) -(trunc(sum(UL_NQTUVC)/(TB_ART.ar_n3uvsp*TB_ART.ar_n3spca),0)*(TB_ART.ar_n3uvsp*TB_ART.ar_n3spca)))/TB_ART.ar_n3uvsp,0) bl, " + 
                    "   UL_CPROIN,  " + 
                    "   AR_LIBPRO,   " + 
                    "   UE_ADRUMS,  " + 
                    "   max(to_date(UT_VALIND,'YYYY.MM.DD')) ЛучшийСрок,  " + 
                    "   min(to_date(UT_VALIND,'YYYY.MM.DD')) ХудшийСрок  " + 
                    " from refstock.TB_LCUMS  " + 
                    " left join refstock.TB_EUMS on ue_usscc=ul_usscc AND UE_DEPOT=01 AND UE_PROPRI='RM' " + 
                    " left join refstock.TB_ART ON AR_CPROIN=UL_CPROIN AND AR_donord='RM' " + 
                    " left join refstock.tb_traums on ue_usscc=ut_usscc and ul_numlig=ut_numlig " + 
                    " left join refstock.TB_RACK on rk_depot='01' and ue_zone=rk_zone and ue_allee=rk_allee and ue_travee=rk_travee and rk_niveau=ue_niveau " + 
                    " left join RABAEV.SFERA_EAN sfera_ean on  UL_CPROIN=sfera_ean.TMC_UID " + 
                    " where ul_donord='RM' " + 
                    " and (ul_numorl is null)  " + 
                    " and ul_nqtuvc<>0 " + 
                    " and  SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-5 ,3  ) = '"+пролет+"' " +
                    " and  SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-7 ,2  ) = '" + стеллаж + "' " + 
                    " group by  " + 
                    "   UL_CPROIN, " + 
                    "   AR_LIBPRO, " + 
                    "   AR_NRSFOU ,    " + 
                    "   UE_ADRUMS ,   " + 
                    "   TB_ART.ar_n3uvsp ,  " + 
                    "   TB_ART.ar_n3spca " + 
                    "   order by  " + 
                    "   SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-7 ,2  ) , " + 
                    "   SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-5 ,2  ) , " + 
                    "   SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS)-2 ,2  ) ,  " +   
                    "   SUBSTR(UE_ADRUMS,  LENGTH(UE_ADRUMS) ,1  ) ";





                    ora_com.CommandText = strSQL;
                    lines_count_must_be = 0;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();

                        // Always call Read before accessing data.
                        pos = 0;


                        while (ora_reader.Read())
                        {
                            pos++;
                            lines_count_must_be++;
                            r = new funct();
                            r.function_name = "PRLL";  //  СЕК 0 ЭТ 1 КОЛ 4 КОР 5 БЛ 6 УИД 7 НАИМ 8 АДР 9 сркл 10 сркх 11

                            r.add_value("СЕК", ora_reader.GetOracleString(0));
                            r.add_value("ЭТ", ora_reader.GetOracleString(1));
                            r.add_value("КОЛ", ora_reader.GetOracleNumber(4));
                            r.add_value("КОР", ora_reader.GetOracleNumber(5));
                            r.add_value("БЛ", ora_reader.GetOracleNumber(6));
                            r.add_value("УИД", ora_reader.GetOracleString(7));
                            r.add_value("НАИМ", ora_reader.GetOracleString(8));
                            r.add_value("АДР", ora_reader.GetOracleString(9));
                            r.add_value("сркл", ora_reader.GetOracleDateTime(10));
                            r.add_value("сркх", ora_reader.GetOracleDateTime(11));

                            summary = summary + r.encode();

                        }


                        r = new funct();
                        r.function_name = "PROLET_LINES";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = r.encode() + summary;

                        r = new funct();
                        r.function_name = "END";
                        r.add_value("lines_count_must_be", lines_count_must_be);
                        summary = summary + r.encode();
                        //r.split_program(summary);

                        ora_reader.Close();

                        // Always call Close when done reading.
                        ora_reader.Close();
                        // Теперь передаем EAN КОДЫ
                        // ДЛЯ ВСЕХ ПРОДУКТОВ ИЗ СБОРКИ, собираем ЕАН коды, с умножителями, передаем клиенту

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f12" + ex.Message);
                    }

                    
                    // ****************************************************************************
                    // ****************************************************************************
                    // ****************************************************************************

                    break;
                #endregion


                #region ИНФОРМАЦИЯ_ПО_ЗАКАЗУ_НА_ОСНОВАНИИ_НОМЕРА_USSCC

                case "GET_ORDER_INFO2":
                    #region РАБОТА_С_ОРАКЛ
                    OrderNumber = "000000";
                    USSCC =F_Request1.get_value("USSCC");
                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();
                    ora_com = new OracleCommand();

                    strSQL = " select  distinct te.CD_NUMCDE " +
                    " from refstock.tb_ecde te   left join refstock.TB_LPREP tlp  " +
                    " on  tlp.LP_NUMORL=te.cd_numorl " +
                    " where   tlp.LP_USSCCD ='" + USSCC + "'  ";

                    ora_com.CommandText = strSQL;
                    ora_conn.Open();
                    ora_com.Connection = ora_conn;
                    ora_reader = ora_com.ExecuteReader();
                    pos = 0;
                    if (ora_reader.Read())
                    {
                        string value2 = to_str(ora_reader.GetOracleString(0));
                        OrderNumber = (value2);
                    }

                    #endregion
  
                    #region РАБОТА_С_ACCESS

                    // ==================================================
                    try
                    {
                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;


                        strSQL = " SELECT ТранспортныеЗаданияСтроки.НОМЕР, ТранспортныеЗадания.ЗонаОтгрузочной, " +
                        " ТранспортныеЗаданияСтроки.ЗОНА_ФАКТИЧЕСКАЯ, ТранспортныеЗаданияСтроки.ДатаТЗ, " +
                        " ТранспортныеЗаданияСтроки.ИДЕНТИФИКАТОР, ТранспортныеЗадания.ВОЛНА,  " +
                        " ТранспортныеЗаданияСтроки.Статус, ТранспортныеЗаданияСтроки.УИД , ТранспортныеЗадания.Водитель,  " +
                        " ТранспортныеЗадания.Экспедитор, ТранспортныеЗаданияСтроки.ПричинаНеРазвоза,  " +
                        " ТранспортныеЗаданияСтроки.ОБЪЕМ, ТранспортныеЗаданияСтроки.ВЕС, Контрагенты.ЮрЛицо,  " +
                        " Контрагенты.Телефон, ТранспортныеЗаданияСтроки.АДРЕС, ТранспортныеЗаданияСтроки.Примечание " +
                        " FROM (ТранспортныеЗадания INNER JOIN ТранспортныеЗаданияСтроки  " +
                        "    ON (ТранспортныеЗадания.ДатаТЗ=ТранспортныеЗаданияСтроки.ДатаТЗ)  " +
                        "    AND (ТранспортныеЗадания.ИдентификаторМаршрута=ТранспортныеЗаданияСтроки.ИДЕНТИФИКАТОР))  " +
                        "    LEFT JOIN Контрагенты ON ТранспортныеЗадания.Экспедитор=Контрагенты.Код " +
                        " WHERE (  ТранспортныеЗаданияСтроки.УИД=" + OrderNumber + "   ) " +
                        " ORDER BY ТранспортныеЗаданияСтроки.ДатаТЗ, ТранспортныеЗадания.Экспедитор; ";

                        mdb_comm.CommandText = strSQL;
                        OleDbDataReader m_ole_db_reader1 = mdb_comm.ExecuteReader();

                        if (m_ole_db_reader1.Read())
                        {// ЕСЛИ НАКЛАДНАЯ С ТАКИМ УИДОМ ЕСТЬ В БД ОД 
                            r = new funct();
                            r.function_name = "ORDER_POSITION_INFO";
                            r.add_value("NUMBER", m_ole_db_reader1[0].ToString());
                            r.add_value("PLANNED_ZONE", m_ole_db_reader1[1].ToString());
                            r.add_value("CURRENT_ZONE", m_ole_db_reader1[2].ToString());
                            r.add_value("DATE", m_ole_db_reader1[3].ToString());
                            r.add_value("ROUTE_NUMBER", m_ole_db_reader1[4].ToString());
                            r.add_value("VOLNA", m_ole_db_reader1[5].ToString());
                            r.add_value("CONDITION", m_ole_db_reader1[6].ToString());
                            r.add_value("UID", m_ole_db_reader1[7].ToString());

                            m_ole_db_reader1.Close();
                            summary = summary + r.encode();
                        }

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion


                #region УСТАНАВЛИВАЕМ_СБОРЩИКА

                case "SET_RUSER":

                    try
                    {
                        #region РАБОТА_С_ОРАКЛ
                        OrderNumber = "000000";
                        USSCC = F_Request1.get_value("USSCC");
                        string USERID = F_Request1.get_value("USERID");
                        string ORDER_UID1 = F_Request1.get_value("ORDER_UID");
                        string WMS_USER_ID = "";

                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_com = new OracleCommand();

                        strSQL = "select   WMSUSER_ID  from RABAEV.RUSERS where ID='" + USERID + "' ";

                        ora_com.CommandText = strSQL;
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();
                        pos = 0;
                        if (ora_reader.Read())
                        {
                            string value2 = (ora_reader.GetValue(0).ToString());
                            WMS_USER_ID = (value2);
                        }

                        if (ORDER_UID1 != "")
                        {// ЕСЛИ ДАН НОМЕР ЗАКАЗА - ОБНОВЛЯЕМ ПО НОМЕРУ ЗАКАЗА
                            strSQL = " update REFSTOCK.TB_LPREP  set LP_CODPRE='" + WMS_USER_ID + "'  where LP_NUMORL=" + ORDER_UID1 + " ";
                            ora_com.CommandText = strSQL;
                            ora_com.ExecuteNonQuery();
                        }
                        else
                        {
                            strSQL = " update REFSTOCK.TB_LPREP  set LP_CODPRE='" + WMS_USER_ID + "'  where LP_USSCCD=" + USSCC + " ";
                            ora_com.CommandText = strSQL;
                            ora_com.ExecuteNonQuery();
                        }
                    
                    #endregion

                    #region РАБОТА_С_ACCESS

                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;

                        if (ORDER_UID1 != "")
                        {
                            DateTime dt = DateTime.Now ;
                            strSQL = " Update ТранспортныеЗаданияСтроки set Сборщик='" + WMS_USER_ID + "' , ВРЕМЯ_СБОРКИ_ФАКТИЧЕСКОЕ="+ dateTime2sql(dt) +"   where УИД="+ORDER_UID1+" ";
                            mdb_comm.CommandText = strSQL;
                            mdb_comm.ExecuteNonQuery();
                        }

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion


                #region УСТАНАВЛИВАЕМ_ЗОНУ_НАКЛАДНОЙ

                case "SET_TZONE":

                    try
                    {
                        #region РАБОТА_С_ОРАКЛ
                        OrderNumber = "000000";
                        USSCC = F_Request1.get_value("USSCC");
                        string USERID = F_Request1.get_value("USERID");
                        string ORDER_UID1 = F_Request1.get_value("ORDER_UID");
                        string TZONE = F_Request1.get_value("TZONE");

                        string WMS_USER_ID = "";

                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_com = new OracleCommand();

                        strSQL = "select   WMSUSER_ID  from RABAEV.RUSERS where ID='" + USERID + "' ";

                        ora_com.CommandText = strSQL;
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();
                        pos = 0;
                        if (ora_reader.Read())
                        {
                            string value2 = (ora_reader.GetValue(0).ToString());
                            WMS_USER_ID = (value2);
                        }

                        /*
  LAST_FLAG  
  USSCC      
                         */
                        
                            DateTime dt6 = DateTime.Now;
                            string sdt6 = "" + dt6.Day + dt6.Month + dt6.Year +" "+ dt6.Hour + ":" + dt6.Minute + ":" + dt6.Second; // 010202 22:01:01
                            strSQL = " insert into RABAEV.ORDER_MOV_HIST  (ORDER_UID ,ZONE,RUSER, USSCC ,TIME_STAMP ) values ( " + ORDER_UID1 + " , '" + TZONE + "' , '" + USERID + "' , '" + USSCC + "' , to_date ('010202 22:01:01', 'ddmmyy HH24:MI:SS')   ) ";
                            ora_com.CommandText = strSQL;
                            ora_com.ExecuteNonQuery();
                       

                        #endregion

                        #region РАБОТА_С_ACCESS

                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;

                        if (ORDER_UID1 != "")
                        {
                            DateTime dt = DateTime.Now;
                            strSQL = " Update ТранспортныеЗаданияСтроки set КтоРазвезНаПятаке='" + WMS_USER_ID + "' , ЗОНА_ФАКТИЧЕСКАЯ ='" + TZONE + "'   where УИД=" + ORDER_UID1 + " ";
                            mdb_comm.CommandText = strSQL;
                            mdb_comm.ExecuteNonQuery();
                        }

                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f59:" + ex.Message);
                    }

                        #endregion
                    break;
                #endregion


                #region ИНФОРМАЦИЯ_ПО_ЗАКАЗУ
                case "GET_ORDER_INFO1":
                    // НУЖНО ВЕРНУТЬ ИНФОРМАЦИЮ ПО ЮЗЕРУ В СОБСТВЕННОЙ ТАБЛИЦЕ ЮЗЕРОВ
                    string ORDER_UID = F_Request1.get_value("ORDER_UID");

                    #region РАБОТА_С_ACCESS
                   
                    // ==================================================
                    try
                    {
                        OleDbCommand mdb_comm = new OleDbCommand();
                        OleDbConnection mdb_conn = new OleDbConnection();
                        mdb_conn.ConnectionString = MDB_CONNECTION_STRING();
                        mdb_conn.Open();
                        mdb_comm.Connection = mdb_conn;


strSQL = " SELECT ТранспортныеЗаданияСтроки.НОМЕР, ТранспортныеЗадания.ЗонаОтгрузочной, " + 
" ТранспортныеЗаданияСтроки.ЗОНА_ФАКТИЧЕСКАЯ, ТранспортныеЗаданияСтроки.ДатаТЗ, " + 
" ТранспортныеЗаданияСтроки.ИДЕНТИФИКАТОР, ТранспортныеЗадания.ВОЛНА,  " + 
" ТранспортныеЗаданияСтроки.Статус, ТранспортныеЗадания.Водитель,  " + 
" ТранспортныеЗадания.Экспедитор, ТранспортныеЗаданияСтроки.ПричинаНеРазвоза,  " + 
" ТранспортныеЗаданияСтроки.ОБЪЕМ, ТранспортныеЗаданияСтроки.ВЕС, Контрагенты.ЮрЛицо,  " + 
" Контрагенты.Телефон, ТранспортныеЗаданияСтроки.АДРЕС, ТранспортныеЗаданияСтроки.Примечание " + 
" FROM (ТранспортныеЗадания INNER JOIN ТранспортныеЗаданияСтроки  " + 
"    ON (ТранспортныеЗадания.ДатаТЗ=ТранспортныеЗаданияСтроки.ДатаТЗ)  " + 
"    AND (ТранспортныеЗадания.ИдентификаторМаршрута=ТранспортныеЗаданияСтроки.ИДЕНТИФИКАТОР))  " + 
"    LEFT JOIN Контрагенты ON ТранспортныеЗадания.Экспедитор=Контрагенты.Код " +
" WHERE (  ТранспортныеЗаданияСтроки.УИД=" + ORDER_UID + "   ) " + 
" ORDER BY ТранспортныеЗаданияСтроки.ДатаТЗ, ТранспортныеЗадания.Экспедитор; ";

                        mdb_comm.CommandText = strSQL;
                        OleDbDataReader m_ole_db_reader1 =  mdb_comm.ExecuteReader  ();
                            
                        if (m_ole_db_reader1.Read())
                        {// ЕСЛИ НАКЛАДНАЯ С ТАКИМ УИДОМ ЕСТЬ В БД ОД 
                                r = new funct();
                                r.function_name = "ORDER_POSITION_INFO";
                                r.add_value("NUMBER", m_ole_db_reader1[0].ToString()  );
                                r.add_value("PLANNED_ZONE", m_ole_db_reader1[1].ToString() );
                                r.add_value("CURRENT_ZONE", m_ole_db_reader1[2].ToString() );
                                r.add_value("DATE", m_ole_db_reader1[3].ToString() );
                                r.add_value("ROUTE_NUMBER", m_ole_db_reader1[4].ToString() );
                                r.add_value("VOLNA", m_ole_db_reader1[5].ToString() );
                                r.add_value("CONDITION", m_ole_db_reader1[6].ToString() );
                                m_ole_db_reader1.Close();
                                summary = summary + r.encode();
                        }
                         
                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion


                #region ИНФОРМАЦИЯ_ПО_ЮЗЕРУ_RUSER
                case "GET_RUSER":
                    // НУЖНО ВЕРНУТЬ ИНФОРМАЦИЮ ПО ЮЗЕРУ В СОБСТВЕННОЙ ТАБЛИЦЕ ЮЗЕРОВ
                    string RUSER_ID = F_Request1.get_value("USERID");

                    #region РАБОТА_С_ОРАКЛ
                    strSQL = " select  ID , NAME , PRAVO_INVENTORY_EDIT ,   PRAVO_CHECK_ORDER  ,  PRAVO_LIGHT_INVENTORY_CHECK , PRAVO_RAZVOZ_ZAYAVOK , PRAVO_EAN_PRODUCT_CHANGE , PRAVO_KARSHIK , ware_id , to_char( systimestamp , 'dd.mm.yyyy HH24:MI:ss' ) " +
                    " from RABAEV.RUSERS  where ID='" + RUSER_ID + "' and DELETED=0 ";

                    ora_conn = new OracleConnection();
                    ora_conn.ConnectionString = connection_string_to_wms();
                    ora_com = new OracleCommand();

                    ora_com.CommandText = strSQL;
                    try
                    {
                        ora_conn.Open();
                        ora_com.Connection = ora_conn;
                        ora_reader = ora_com.ExecuteReader();

                        pos = 0;

                        while (ora_reader.Read())
                        {
                            r = new funct();
                            r.function_name = "USER_INFO";
                            r.add_value("ID", ora_reader.GetOracleString(0));
                            r.add_value("NAME", ora_reader.GetOracleString(1));
                            r.add_value("PRAVO_INVENTORY_EDIT", ora_reader.GetOracleNumber(2));
                            r.add_value("PRAVO_CHECK_ORDER", ora_reader.GetOracleNumber(3));
                            r.add_value("PRAVO_LIGHT_INVENTORY_CHECK", (ora_reader.GetOracleNumber(4)));
                            r.add_value("PRAVO_RAZVOZ_ZAYAVOK", (ora_reader.GetOracleNumber(5)));
                            r.add_value("PRAVO_EAN_PRODUCT_CHANGE", (ora_reader.GetOracleNumber(6)));


                            r.add_value("PRAVO_KARSHIK", (ora_reader.GetOracleNumber(7)));
                            r.add_value("ware_id", (ora_reader.GetOracleNumber(8)));
                            r.add_value("systimestamp", (ora_reader.GetOracleString(9)));
                            
                            summary = summary + r.encode();
                            pos++;
                        }
                        ora_reader.Close();
                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5:" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion


                #region ВЫЗОВ_ХРАНИМОЙ_ФУНКЦИИ
                case "CALL_SPF":
                    // НУЖНО ВЕРНУТЬ ИНФОРМАЦИЮ ПО ЮЗЕРУ В СОБСТВЕННОЙ ТАБЛИЦЕ ЮЗЕРОВ
                    string m_spf_name = F_Request1.get_value("SPF_NAME");

                    #region РАБОТА_С_ОРАКЛ
                    try
                    {

                        ora_conn = new OracleConnection();
                        ora_conn.ConnectionString = connection_string_to_wms();
                        ora_conn.Open();
                        ora_com = new OracleCommand();
                        ora_com.Connection = ora_conn;
                        ora_com.CommandText = m_spf_name;
                        ora_com.CommandType = CommandType.StoredProcedure;
                        Console.WriteLine("CALL SP : "+m_spf_name);
                        foreach (KeyValuePair<string, string> kkey in F_Request1.strToIntMap)
                        {
                            if (kkey.Key != "SPF_NAME") {
                                Console.Write(""+kkey.Key + " = " + kkey.Value);
                                ora_com.Parameters.Add(kkey.Key, OracleType.VarChar).Value = kkey.Value  ;
                            }
                        }

                        /*
                        ora_com.Parameters.Add("pallet_id", OracleType.VarChar).Value = dr3.Cells[0].Value.ToString();
                        ora_com.Parameters.Add("cell_to", OracleType.VarChar).Value = m_cell_to.Text;
                        ora_com.Parameters.Add("count1", OracleType.Number).Value = Convert.ToInt64(dr3.Cells[2].Value.ToString());
                        ora_com.Parameters.Add("user_id1", OracleType.VarChar).Value = wms_user.user_id;
                        */

                        ora_com.Parameters.Add("ok", OracleType.VarChar, 50).Direction =
                            ParameterDirection.ReturnValue;
                        ora_com.ExecuteNonQuery();
                        string ret = ora_com.Parameters["ok"].Value.ToString();
                        Console.WriteLine( " ret = " + ret ) ;

                        summary = "FUNC=CALL_SP_INFO|ok=" + ret+"|";
                       // if(ora_com.Transaction != null)
                       // ora_com.Transaction.Commit();

                        //Console.WriteLine(" ret = " + ret);
                        ora_conn.Close();
                      
                        ora_conn.Dispose();
                      
                        ora_com.Dispose();


                      
                    }
                    catch (Exception ex)
                    {
                        r = new funct();
                        r.function_name = "FAULT";
                        r.add_value("REASON", ex.Message);
                        summary = summary + r.encode();
                        Console.WriteLine("error f5 :" + ex.Message);
                    }

                    #endregion
                    break;
                #endregion



                default :
                    //F_Response.split("FUNC=ZERO|");
                    Console_WriteLine( "не указано реакции для"+F_Request1.function_name );
                    summary = "FUNC=ZERO|";
                    break;
            }

            if (summary == "") { summary = "FUNC=ZERO|"; }

            Console_WriteLine(summary);

            //string message = "получи результаты : " + myCompleteMessage + " // " + Convert.ToString(NumberOfRequests);
            string message = summary;// F_Response.encode();
            int dlina = Encoding.Unicode.GetBytes(message).GetLength(0);

            // ПИШЕМ ХЕДЕР
            string get_len;
            get_len = Convert.ToString(dlina);
            for (int i3 = get_len.Length ; i3 < 20; i3++)
                get_len = "0" + get_len;

            message = get_len + message;
            dlina = Encoding.Unicode.GetBytes(message).GetLength(0);
            Byte[] data = Encoding.Unicode.GetBytes(message);

            socketStream.Write(data, 0, dlina);

            Console_WriteLine("STOP dlina=" + Convert.ToString(dlina) + "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ");

        }

    }

    class Program
    {

        static void Console_WriteLine(string str)
        {
            Console.WriteLine(str);
        }

        static void Main(string[] args)
        {

            int PORT_p = 20005;
            long ware_id = 3;
            string VERSION1 = " от 03.04.2010";
            string IP_listen = "192.168.30.41";
            string DBWMSString = "DBWMS";
            if(ware_id==1)
            IP_listen = "192.168.193.14";

        if (ware_id == 2)
        {
            IP_listen = "192.168.208.205";
        }

        if (ware_id == 3)
        {
            IP_listen = "192.168.208.205";
            IP_listen = "192.168.208.200"; PORT_p = 20007;
           // IP_listen = "192.168.208.205";

        }

        try
        {
            string[] str4 = File.ReadAllLines("adr.txt", Encoding.GetEncoding("windows-1251"));
            IP_listen = str4[0];
            PORT_p = Convert.ToInt32( str4[1] );

            DBWMSString = str4[3];
        }
        catch(Exception ex)
        {
            Console_WriteLine(ex.Message);
        }


        if (args.Length > 0)
        {
            try {
                PORT_p = Convert.ToInt32( args[1].ToString() );

            }catch
            {
            
            }
        }


            Console.Title = "WMS Сервер. Адрес:" + IP_listen + " ПОРТ:" + PORT_p.ToString() + " Склад:" + ware_id.ToString() + " Версия:" + VERSION1;

            Console_WriteLine("Сервер приложений стартовал. БАЗА=" + DBWMSString + ". Адрес прослушивания = " + IP_listen + " ПОРТ = " + PORT_p.ToString() + " Склад=  " + ware_id.ToString() + "  \n Версия= " + VERSION1);
            while (true)
            {
                try
                {
                    Server server = new Server(IPAddress.Parse(IP_listen), PORT_p);
                    server.DBWMSString = DBWMSString;
                    server.ware_id = ware_id;
                    server.Start();

                }
                catch (Exception ext)
                {
                    Console_WriteLine("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$");
                    Console_WriteLine("Ошибка:" + ext.Message);
                    Console_WriteLine("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$");
                    Console_WriteLine("Перезагрузка");
                }
            }

        }
    }
}


/* ПРОЦЕДУРА ПРОВЕРКИ ЛОТА:
 * 1) РЕВИЗОР сканирует номер лота. Если такого лота нет, система ругается.
 * 2) Система подгружает лот в терминал.
 * 3) Ревизор сканирует товар и групповые упаковки: для каждого скана
 *      ) терминал определяет вид упаковки - штука \ блок \ коробка , на соотв. количество увеличивает 
 *      ) фактический лот. если скан не распознается, система предлагает отложить товар в сторону.
 * 
 * 4) сигналом для проверки является нажатие кнопки.
 *  по нему сверяется сканированный факт и план, помечается лишнее количество
 *  дефицитные позиции.
*/