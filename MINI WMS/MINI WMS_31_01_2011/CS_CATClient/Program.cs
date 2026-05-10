using System;
using System.Text;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Collections.Generic;
using System.Windows.Forms;


namespace CS_CATSample
{
    //

    using MapType = Dictionary<string, string>;
    using PairType = KeyValuePair<string, string>;


    class Client
    {
        private TcpClient socket;
        private IPAddress address;
        private int port;
        public funct FUNC_Request;
        public List<funct> FUNC_Response;
        public List<funct> PROGRAM_Request= new  List<funct> ();

        public void alert(string d)
        {
            
        }

        public string Response_to_string()
        {
            string resp="" ;
            foreach (funct f in this.FUNC_Response)
            {
                resp=resp+f.ToString();
            }
            return resp;

        }

        public Client(IPAddress _address, int _port)
        {
            address = _address;
            port = _port;
            SetupClient();
        }

        private void SetupClient()
        {
            IPEndPoint endPoint = new IPEndPoint(address, port);
            socket = new TcpClient();
           // socket.ReceiveTimeout = 100000;
            socket.Connect(endPoint);
        }

        public int Receive()
        {
            try
            {

                FUNC_Response = new List<funct>();
                funct dumm = new funct();
                int numberOfBytesRead;
                int size = 0;

                NetworkStream socketStream = socket.GetStream();
                //--------------------------------------------------------------------

                string message1 = FUNC_Request.encode();
                if (this.PROGRAM_Request != null)
                {
                    foreach (funct ffff in PROGRAM_Request)
                    {
                        message1 =message1+ ffff.encode();  
                    }
                }

                
                // œ»ÿ≈Ã ƒÀ»Õ” «¿√ŒÀŒ¬ ¿ ¬ ’≈ƒ≈–
                int dlina = Encoding.Unicode.GetBytes(message1).GetLength(0);
                string get_len;
                get_len = Convert.ToString(dlina);
                for (int i3 = get_len.Length  ; i3 < 20; i3++)
                { get_len = "0" + get_len; }

                message1 = get_len+message1  ;
                //  œ»ÿ≈Ã ƒÀ»Õ” «¿√ŒÀŒ¬ ¿ ¬ ’≈ƒ≈–

                dlina = Encoding.Unicode.GetBytes(message1).GetLength(0);
                Byte[] data3 = Encoding.Unicode.GetBytes(message1);
                
                socketStream.Write(data3, 0, dlina);

                //--------------------------------------------------------------------
                StringBuilder myCompleteMessage2 = new StringBuilder(); ;
                if (socketStream.CanRead)
                {

                    StringBuilder myCompleteMessage1 = new StringBuilder();

                     myCompleteMessage2 = new StringBuilder();
                     StringBuilder l_header = new StringBuilder();
                    size = 0;
                    numberOfBytesRead = 1;

                    int len2 = 20;
                    byte[] data2 = new byte[len2 * 3];

                    // ◊»“¿≈Ã «¿√ŒÀŒ¬Œ 
                    numberOfBytesRead = socketStream.Read(data2, 0/*size*/, 40);
                    l_header.Append(Encoding.Unicode.GetString(data2, 0, numberOfBytesRead));
                    long len_from_header=Convert.ToInt64( l_header.ToString());
                    // ◊»“¿≈Ã «¿√ŒÀŒ¬Œ 

                    do
                    {
                        int len = 20;
                        byte[] data = new byte[len * 3];
                        numberOfBytesRead = socketStream.Read(data, 0/*size*/, len);
                        size += numberOfBytesRead;
                        myCompleteMessage2.Append(Encoding.Unicode.GetString(data, 0, numberOfBytesRead));
                    } while (size < len_from_header);
                }

                FUNC_Response= dumm.split_program(myCompleteMessage2.ToString());
                socketStream.Close();
                return size ;
            }
            catch (Exception exc)
            {
               MessageBox.Show( "f1: "+ exc.Message);
               throw (exc);
               
            }//*/
            return 0;
        }

        public void Disconnect()
        {
            socket.Close();
        }
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

        public string encode()
        {
            string outp = "FUNC=" + this.function_name + "|";
            foreach (KeyValuePair<string, string> pair in strToIntMap)
            {
                outp = outp + pair.Key + "=" + pair.Value.Replace("|", "!").Replace("=", "#") + "|";
            }
            return outp;
        }

        public List<funct> split_program(string inp)
        {
            List<funct> program_ = new List<funct>();
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
                        program_[(program_.Count - 1)].add_value(pair[0], pair[1]);
                    }
                }
            }
            return program_;
        }

        public void add_value(string vname, string value1)
        {

            vname.Replace("|", "!");
            vname.Replace("=", "#");
            value1.Replace("|", "!");
            value1.Replace("=", "#");
            strToIntMap[vname] = value1;

        }

    }

    static class Program
    {
        
        
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [MTAThread]
        static void Main()
        {
            FormMain fm = new FormMain();
            fm.DoScale();
            Application.Run(fm);
        }
    }
}