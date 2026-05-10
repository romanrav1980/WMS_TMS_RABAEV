//--------------------------------------------------------------------
// FILENAME: FromMain.vb
//
// Copyright(c) 2006 Symbol Technologies Inc. All rights reserved.
//
// DESCRIPTION:
// Demonstrates the usage of scanning, SQLCE and sockets.  The data scanned is stored in a SQLCE database on the device. 
// The data queued in the database is then tranfered to the PC via socket communication.  The VB_CATHost application
// must must be running on the PC for the data transfer to occur. VB_CATHost will repsond to the data recevied from the 
// device by sending the date and time of the receipt.  The databse on the device is then updated with the response 
// received from the host
//
//NOTES:
//
// 
//--------------------------------------------------------------------
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Reflection;
using System.IO;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using CS_CATClient;
using System.Globalization;

namespace CS_CATSample
{


    public partial class FormMain : Form
    {
        string version= "symbol/13.12.2012";
        DBComponent dbComponent = null;
        //Communication comm = null;
        DateTime server_time;
        DateTime start_time;
        //public string Curent_USSCC="" ;
        public ASSEMBLE_UNION Curent_Assemble= new ASSEMBLE_UNION ();
        public RUSER current_USER = new RUSER();
        List<string> m_cell_history = new List<string>();
        public string Curent_UID = "";
        public string manual_input_option = "";
        
        private Symbol.Barcode.Reader MyReader = null;
        private Symbol.Barcode.ReaderData MyReaderData = null;
        private Symbol.Audio.Controller MyAudioController = null;

        private System.EventHandler BarEventHandler = null;

        private static bool bPortrait = true;   // The default dispaly orientation 
        // has been set to Portrait.

        private bool bSkipMaxLen = false;    // The restriction on the maximum 
        // physical length is considered by default.

        private bool bInitialScale = true;   // The flag to track whether the 
        // scaling logic is applied for
        // the first time (from scatch) or not.
        // Based on that, the (outer) width/height values
        // of the form will be set or not.
        // Initially set to true.

        private int resWidthReference = 240;   // The (cached) width of the form. 
        // INITIALLY HAS TO BE SET TO THE WIDTH OF THE FORM AT DESIGN TIME (IN PIXELS).
        // This setting is also obtained from the platform only on
        // Windows CE devices before running the application on the device, as a verification.
        // For PocketPC (& Windows Mobile) devices, the failure to set this properly may result in the distortion of GUI/viewability.

        private int resHeightReference = 294;  // The (cached) height of the form.
        // INITIALLY HAS TO BE SET TO THE HEIGHT OF THE FORM AT DESIGN TIME (IN PIXELS).
        // This setting is also obtained from the platform only on
        // Windows CE devices before running the application on the device, as a verification.
        // For PocketPC (& Windows Mobile) devices, the failure to set this properly may result in the distortion of GUI/viewability.

        private const double maxLength = 5.5;  // The maximum physical width/height of the sample (in inches).
        // The actual value on the device may slightly deviate from this
        // since the calculations based on the (received) DPI & resolution values 
        // would provide only an approximation, so not 100% accurate.


        // notification events and data
        private NotifyEvents notifyCommEvent;
        Object notifyCommData = null;

        public FormMain()
        {
            InitializeComponent();


        }

        /// <summary>
        /// This function does the (initial) scaling of the form
        /// by re-setting the related parameters (if required) &
        /// then calling the Scale(...) internally. 
        /// </summary>
        /// 
        public void DoScale()
        {
            if (Screen.PrimaryScreen.Bounds.Width > Screen.PrimaryScreen.Bounds.Height)
            {
                bPortrait = false; // If the display orientation is not portrait (so it's landscape), set the flag to false.
            }

            if (this.WindowState == FormWindowState.Maximized)    // If the form is maximized by default.
            {
                this.bSkipMaxLen = true; // we need to skip the max. length restriction
            }

            if ((Symbol.Win32.PlatformType.IndexOf("WinCE") != -1) || (Symbol.Win32.PlatformType.IndexOf("WindowsCE") != -1) || (Symbol.Win32.PlatformType.IndexOf("Windows CE") != -1)) // Only on Windows CE devices
            {
                this.resWidthReference = this.Width;   // The width of the form at design time (in pixels) is obtained from the platorm.
                this.resHeightReference = this.Height; // The height of the form at design time (in pixels) is obtained from the platform.
            }

            Scale(this); // Initial scaling of the GUI
        }

        /// <summary>
        /// This function scales the given Form & its child controls in order to
        /// make them completely viewable, based on the screen width & height.
        /// </summary>
        private static void Scale(FormMain frm)
        {
            int PSWAW = System.Windows.Forms.Screen.PrimaryScreen.WorkingArea.Width;    // The width of the working area (in pixels).
            int PSWAH = System.Windows.Forms.Screen.PrimaryScreen.WorkingArea.Height;   // The height of the working area (in pixels).

            // The entire screen has been taken in to account below 
            // in order to decide the half (S)VGA settings etc.
            if (!((Screen.PrimaryScreen.Bounds.Width <= (1.5) * (Screen.PrimaryScreen.Bounds.Height))
            && (Screen.PrimaryScreen.Bounds.Height <= (1.5) * (Screen.PrimaryScreen.Bounds.Width))))
            {
                if ((Screen.PrimaryScreen.Bounds.Width) > (Screen.PrimaryScreen.Bounds.Height))
                {
                    PSWAW = (int)((1.33) * PSWAH);  // If the width/height ratio goes beyond 1.5,
                    // the (longer) effective width is made shorter.
                }

            }

            System.Drawing.Graphics graphics = frm.CreateGraphics();

            float dpiX = graphics.DpiX; // Get the horizontal DPI value.

            if (frm.bInitialScale == true) // If an initial scale (from scratch)
            {
                if (Symbol.Win32.PlatformType.IndexOf("PocketPC") != -1) // If the platform is either Pocket PC or Windows Mobile
                {
                    frm.Width = PSWAW;  // Set the form width. However this setting
                    // would be the ultimate one for Pocket PC (& Windows Mobile)devices.
                    // Just for the sake of consistency, it's explicitely specified here.
                }
                else
                {
                    frm.Width = (int)((frm.Width) * (PSWAW)) / (frm.resWidthReference); // Set the form width for others (Windows CE devices).

                }
            }
            if ((frm.Width <= maxLength * dpiX) || frm.bSkipMaxLen == true) // The calculation of the width & left values for each control
            // without taking the maximum length restriction into consideration.
            {
                foreach (System.Windows.Forms.Control cntrl in frm.Controls)
                {
                    cntrl.Width = ((cntrl.Width) * (frm.Width)) / (frm.resWidthReference);
                    cntrl.Left = ((cntrl.Left) * (frm.Width)) / (frm.resWidthReference);

                    if (cntrl is System.Windows.Forms.TabControl)
                    {
                        foreach (System.Windows.Forms.TabPage tabPg in cntrl.Controls)
                        {
                            foreach (System.Windows.Forms.Control cntrl2 in tabPg.Controls)
                            {
                                cntrl2.Width = (((cntrl2.Width) * (frm.Width)) / (frm.resWidthReference));
                                cntrl2.Left = (((cntrl2.Left) * (frm.Width)) / (frm.resWidthReference));
                            }
                        }
                    }
                }

            }
            else
            {   // The calculation of the width & left values for each control
                // with the maximum length restriction taken into consideration.
                foreach (System.Windows.Forms.Control cntrl in frm.Controls)
                {
                    cntrl.Width = (int)(((cntrl.Width) * (PSWAW) * (maxLength * dpiX)) / (frm.resWidthReference * (frm.Width)));
                    cntrl.Left = (int)(((cntrl.Left) * (PSWAW) * (maxLength * dpiX)) / (frm.resWidthReference * (frm.Width)));

                    if (cntrl is System.Windows.Forms.TabControl)
                    {
                        foreach (System.Windows.Forms.TabPage tabPg in cntrl.Controls)
                        {
                            foreach (System.Windows.Forms.Control cntrl2 in tabPg.Controls)
                            {
                                cntrl2.Width = (int)(((cntrl2.Width) * (PSWAW) * (maxLength * dpiX)) / (frm.resWidthReference * (frm.Width)));
                                cntrl2.Left = (int)(((cntrl2.Left) * (PSWAW) * (maxLength * dpiX)) / (frm.resWidthReference * (frm.Width)));
                            }
                        }
                    }
                }

                frm.Width = (int)((frm.Width) * (maxLength * dpiX)) / (frm.Width);

            }

            frm.resWidthReference = frm.Width; // Set the reference width to the new value.


            // A similar calculation is performed below for the height & top values for each control ...

            if (!((Screen.PrimaryScreen.Bounds.Width <= (1.5) * (Screen.PrimaryScreen.Bounds.Height))
            && (Screen.PrimaryScreen.Bounds.Height <= (1.5) * (Screen.PrimaryScreen.Bounds.Width))))
            {
                if ((Screen.PrimaryScreen.Bounds.Height) > (Screen.PrimaryScreen.Bounds.Width))
                {
                    PSWAH = (int)((1.33) * PSWAW);
                }

            }

            float dpiY = graphics.DpiY;

            if (frm.bInitialScale == true)
            {
                if (Symbol.Win32.PlatformType.IndexOf("PocketPC") != -1)
                {
                    frm.Height = PSWAH;
                }
                else
                {
                    frm.Height = (int)((frm.Height) * (PSWAH)) / (frm.resHeightReference);

                }
            }

            if ((frm.Height <= maxLength * dpiY) || frm.bSkipMaxLen == true)
            {
                foreach (System.Windows.Forms.Control cntrl in frm.Controls)
                {

                    cntrl.Height = ((cntrl.Height) * (frm.Height)) / (frm.resHeightReference);
                    cntrl.Top = ((cntrl.Top) * (frm.Height)) / (frm.resHeightReference);


                    if (cntrl is System.Windows.Forms.TabControl)
                    {
                        foreach (System.Windows.Forms.TabPage tabPg in cntrl.Controls)
                        {
                            foreach (System.Windows.Forms.Control cntrl2 in tabPg.Controls)
                            {
                                cntrl2.Height = ((cntrl2.Height) * (frm.Height)) / (frm.resHeightReference);
                                cntrl2.Top = ((cntrl2.Top) * (frm.Height)) / (frm.resHeightReference);
                            }
                        }
                    }

                }

            }
            else
            {
                foreach (System.Windows.Forms.Control cntrl in frm.Controls)
                {

                    cntrl.Height = (int)(((cntrl.Height) * (PSWAH) * (maxLength * dpiY)) / (frm.resHeightReference * (frm.Height)));
                    cntrl.Top = (int)(((cntrl.Top) * (PSWAH) * (maxLength * dpiY)) / (frm.resHeightReference * (frm.Height)));


                    if (cntrl is System.Windows.Forms.TabControl)
                    {
                        foreach (System.Windows.Forms.TabPage tabPg in cntrl.Controls)
                        {
                            foreach (System.Windows.Forms.Control cntrl2 in tabPg.Controls)
                            {
                                cntrl2.Height = (int)(((cntrl2.Height) * (PSWAH) * (maxLength * dpiY)) / (frm.resHeightReference * (frm.Height)));
                                cntrl2.Top = (int)(((cntrl2.Top) * (PSWAH) * (maxLength * dpiY)) / (frm.resHeightReference * (frm.Height)));
                            }
                        }
                    }

                }

                frm.Height = (int)((frm.Height) * (maxLength * dpiY)) / (frm.Height);

            }

            frm.resHeightReference = frm.Height;

            if (frm.bInitialScale == true)
            {
                frm.bInitialScale = false; // If this was the initial scaling (from scratch), it's now complete.
            }
            if (frm.bSkipMaxLen == true)
            {
                frm.bSkipMaxLen = false; // No need to consider the maximum length restriction now.
            }


        }

        // The database is created for queuing the data and the communication module is initiated
        private void FormMain_Load(object sender, EventArgs e)
        {
            Application.DoEvents();

            //MessageBox.Show("This sample is provided for demonstration purpose only. You are welcome to modify the code to suit your requirement. \r\n" +
            //"Please refer to the MSDN help files for description of all SQLCE and socket related calls.", "CATClient");
            
            Symbol.Audio.Device MyDevice=(Symbol.Audio.Device)Symbol.StandardForms.SelectDevice.Select(
			Symbol.Audio.Controller.Title,
			Symbol.Audio.Device.AvailableDevices);
            version_label.Text = version;
            try
            {
                MyAudioController = new Symbol.Audio.StandardAudio(MyDevice);
                MyAudioController.BeeperVolume = 1;
            }
            catch { }

            // If we can initialize the Reader
            if (this.InitReader())
            {
                // Start a read on the reader
                this.StartRead();
            }



            // Create the DB
            dbComponent = new DBComponent();
            dbComponent.DBDelete = true;
            dbComponent.DBEncrypt = true;


            dbComponent.DBCreate();
         
            // Attach the grid to the data source
            dbComponent.DBOpen();


            dataGrid1.DataSource = dbComponent.myDataSet.Tables["PALLET_AS_IS"];
            PLANdataGrid2.DataSource = dbComponent.myDataSet.Tables["PALLET_PLAN"];


            this.tabControl1.Visible = false;
            //Control f = this.tabControl1.TabPages[4];
            //this.tabControl1.TabPages.
            //f.Visible = false;
        }

        // Dispose all the objects before exiting
        private void FormMain_Closing(object sender, CancelEventArgs e)
        {
            dbComponent.DBClose();
            //comm.Close();

            // Terminate reader
            this.TermReader();
        }

        // Update the data grid with the latest data from SQLCE
        private void DataGrid_Refresh()
        {
            try
            {
                dataGrid1.DataSource = dbComponent.myDataSet.Tables["PALLET_AS_IS"];
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        // If the data is manually entered instead of scanning, accept it and queue it in SQLCE


        // Insert the data into the queue
        private void DataInsert(string dataSent, string dataRcvd)
        {
           // dbComponent.add_row_to_pallet_as_is(dataSent, Curent_Assemble );


            // ====================================================================
            
            funct f = new funct();
            f.function_name = "GET_PRODUCT_INFO";
            //f.add_value("USSCC", Curent_USSCC);
            f.add_value("itf", dataSent);
            
            //f.split("FUNC=get_tovar_info|itf=1|usscc=0332222202");

            Client client = new Client(IPAddress.Parse( this.ServerIP.Text ), 20021);
            client.FUNC_Request = f;
            client.Receive();
            client.Disconnect();


            // ====================================================================

            
            DataGrid_Refresh();
        }

        // Establishes the socket connection between the device and PC
        private void buttonConnect_Click(object sender, EventArgs e)
        {
  /*          if (buttonConnect.Text == "Connect")
                comm.Open(textBoxHostIP.Text, Convert.ToInt32(textBoxPort.Text));
            else
                comm.Close();
*/
        }

        private void buttonConnect_KeyDown(object sender, KeyEventArgs e)
        {
            // Checks if the key pressed was an enter button (character code 13)
            if (e.KeyValue == (char)13)
                buttonConnect_Click(this, e);
        }

        private void buttonExit_Click(object sender, EventArgs e)
        {
            this.Close();
        }
        private void buttonExit_KeyDown(object sender, KeyEventArgs e)
        {
            // Checks if the key pressed was an enter button (character code 13)
            if (e.KeyValue == (char)13)
                buttonExit_Click(this, e);
        }

        // Catch socket notification events
        private void Comm_Notify(NotifyEvents nEvent, object data)
        {
            try
            {
                lock (this)
                {
                    notifyCommEvent = nEvent;
                    notifyCommData = data;
                    this.Invoke(new EventHandler(ProcessCommNotifications));
                }
            }
            catch
            {
            }
        }


        private void ProcessCommNotifications(object sender, EventArgs e)
        {
            switch (notifyCommEvent)
            {
                case NotifyEvents.Connected:
                    statusBar1.Text = "Connected to the host";
                    break;

                case NotifyEvents.DataReceived:
                    DataGrid_Refresh();
                    break;

                case NotifyEvents.Disconnected:
                    statusBar1.Text = "Disconnected from the host";
                    break;

                default:
                    statusBar1.Text = notifyCommEvent.ToString() + "-" + notifyCommData.ToString();
                    break;
            }
        }
        
        // Initialize the barcode reader.
        private bool InitReader()
        {
            // If reader is already present then fail initialize
            if (this.MyReader != null)
            {
                return false;
            }

            // Create new reader, first available reader will be used.
            this.MyReader = new Symbol.Barcode.Reader();

            // Create reader data
            this.MyReaderData = new Symbol.Barcode.ReaderData(
                Symbol.Barcode.ReaderDataTypes.Text,
                Symbol.Barcode.ReaderDataLengths.MaximumLabel);

            // Create event handler delegate
            this.BarEventHandler = new EventHandler(BarReader_ReadNotify);

            // Enable reader, with wait cursor
            this.MyReader.Actions.Enable();
            try
            {
                this.MyReader.Parameters.Feedback.Success.BeepTime = 0;
                this.MyReader.Parameters.Feedback.Success.WaveFile = "\\windows\\alarm3.wav";
            }
            catch { }

            return true;
        }

        
        // Stop reading and disable/close barcode reader
        private void TermReader()
        {
            try
            {
                if (MyAudioController != null)
                {
                    MyAudioController.Dispose();
                    MyAudioController = null;
                }
            }
            catch { }

            // If we have a reader
            if (this.MyReader != null)
            {
                // Disable the reader
                this.MyReader.Actions.Disable();

                // Free it up
                this.MyReader.Dispose();

                // Indicate we no longer have one
                this.MyReader = null;
            }

            // If we have a reader data
            if (this.MyReaderData != null)
            {
                // Free it up
                this.MyReaderData.Dispose();

                // Indicate we no longer have one
                this.MyReaderData = null;
            }
        }

        
        // Start a read on the barcode reader
        private void StartRead()
        {
            // If we have both a reader and a reader data
            if ((this.MyReader != null) &&
                 (this.MyReaderData != null))
            {
                // Submit a read
                this.MyReader.ReadNotify += this.BarEventHandler;
                this.MyReader.Actions.Read(this.MyReaderData);
            }
        }

        
        // Stop all reads on the barcode reader
        private void StopRead()
        {
            // If we have a reader
            if (this.MyReader != null)
            {
                // Flush (Cancel all pending reads)
                this.MyReader.ReadNotify -= this.BarEventHandler;
                this.MyReader.Actions.Flush();
            }
        }

        
        // Read complete or failure notification
        private void BarReader_ReadNotify(object sender, EventArgs e)
        {
            Symbol.Barcode.ReaderData TheReaderData = this.MyReader.GetNextReaderData();

            // If it is a successful read (as opposed to a failed one)
            if (TheReaderData.Result == Symbol.Results.SUCCESS)
            {
                // Handle the data from this read
                this.HandleData(TheReaderData);

                // Start the next read
                this.StartRead();
            }
        }

        #region ЦВЕТОМУЗЫКА
        private void Beep_ok()
        {
            
            int Duration = 300;//millisec
            int Frequency = 1500;//hz
            //statusBar1.Text = "";
            try
            {
                this.MyAudioController.PlayAudio(Duration, Frequency);//play Default beep
            }
            catch
            { }
        }

        private void Beep_fault()
        {
            try
            {
                this.MyAudioController.PlayAudio(1500, 4200);//play Default beep
               
            }
            catch
            { }
        }

        private void Beep_win()
        {
            try
            {
                this.MyAudioController.PlayAudio(2000, 1670);//play Default beep

            }
            catch
            { }
        }


        private void Beep_wrong_count_of_product()
        {

            try
            {
                this.MyAudioController.PlayAudio(1000, 4000);//play Default beep

            }
            catch
            { }

        }

        private void Beep_wrong_product()
        {

            try
            {
                this.MyAudioController.PlayAudio(1000, 4000);//play Default beep
              
            }
            catch
            { }

        }

       
        private void Beep_new_audit_started()
        {
            try
            {
                this.MyAudioController.PlayAudio(2000, 1670);//play Default beep

            }
            catch
            { }
        }

        //Сброс Ручного ввода
        private void default_manual_input_option()
        {
            manual_input_option = "";
        
        }        
#endregion

        #region ДЕКОДИРОВАНИЕ

        string pallet_uid_decode(string puid)
        {
            try
            {
                string f = puid.Replace("OP_", "");
                byte[] bbb ;
                bbb=Convert.FromBase64String(f);
                return "OP_" + Encoding.GetEncoding("windows-1251").GetString(bbb, 0, bbb.Length );
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            return "";
        }

        string pallet_uid_code(string PUID)
        {
            string f = PUID.Replace("OP_", "");
            return Convert.ToBase64String((Encoding.GetEncoding("windows-1251").GetBytes(f)));
        }

        #endregion 




        #region СЕТЬ


        private Client nettt2(funct f , int port11)
        {

            Client client;
            string Fault_mess = "NET ERROR";
            try
            {
                client = new Client(IPAddress.Parse(this.ServerIP.Text), port11 );
                client.FUNC_Request = f;
                int rsize = client.Receive();
                trace("Получен пакет длиной=" + Convert.ToString(rsize));
                client.Disconnect();
                return client;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);

                List<string> variant_ip = new List<string>();
 

                variant_ip.Add(this.ServerIP2.Text);
 
                variant_ip.Add(this.ServerIP3.Text);
 
                variant_ip.Add(this.ServerIP4.Text);
 

                bool _exit = false;
                int pos = 0;
                while (!_exit)
                {
                    try
                    {
                        this.ServerIP.Text = variant_ip[pos];
 
                        client = new Client(IPAddress.Parse(this.ServerIP.Text), port11);
                        client.FUNC_Request = f;
                        int rsize = client.Receive();
                        trace("Получен пакет длиной=" + Convert.ToString(rsize));
                        client.Disconnect();
                        _exit = true;
                        return client;
                    }
                    catch (Exception ex2)
                    {
                        Fault_mess = ex2.Message;
                    }

                    pos++;
                    if (pos > 2) { _exit = true; }
                }
                MessageBox.Show("nett!" + Fault_mess);
                return null;
            }
            return null;
        }


        private Client nettt(funct f)
        {

            Client client;
            string Fault_mess = "NET ERROR";
            try
            {
                client = new Client(IPAddress.Parse(this.ServerIP.Text), Convert.ToInt32(this._port.Text));
                client.FUNC_Request = f;
                int rsize = client.Receive();
                trace("Получен пакет длиной=" + Convert.ToString(rsize));
                client.Disconnect();
                return client;
            }
            catch (Exception ex)
            {


                List<string> variant_ip = new List<string>();
                List<long> variant_port = new List<long>();

                variant_ip.Add(this.ServerIP2.Text);
                variant_port.Add(Convert.ToInt32(this._port2.Text));
                variant_ip.Add(this.ServerIP3.Text);
                variant_port.Add(Convert.ToInt32(this._port3.Text));
                variant_ip.Add(this.ServerIP4.Text);
                variant_port.Add(Convert.ToInt32(this._port4.Text));

                bool _exit = false;
                int pos = 0;
                while (!_exit)
                {
                    try
                    {
                        this.ServerIP.Text = variant_ip[pos];
                        this._port.Text = variant_port[pos].ToString();
                        client = new Client(IPAddress.Parse(this.ServerIP.Text), Convert.ToInt32(this._port.Text));
                        client.FUNC_Request = f;
                        int rsize = client.Receive();
                        trace("Получен пакет длиной=" + Convert.ToString(rsize));
                        client.Disconnect();
                        _exit = true;
                        return client;
                    }
                    catch ( Exception ex2 )
                    {
                        Fault_mess = ex2.Message;
                    }

                    pos++;
                    if (pos > 2) { _exit = true; }
                }
                MessageBox.Show("nett!"+Fault_mess);
                return null;
            }
            return null;
        }


        #endregion

        private int get_ware_by_cell(string cell)
        {
            int ret = -1;


            string ch = cell.Substring(0, 2);
            switch (ch)
            {
                case "B-": return 4;
               // case "E-": return 5;
                case "I-": return 5;
                case "O-": return 6;
                case "D-": return 7;
                case "V-": return 8;
                case "C-": return 1;
                case "M-": return 2;
                case "A-": return 3;
                case "Г-": return 8;
                case "В-": return 8;
                case "Д-": return 7;
                case "Б-": return 4;
                case "М-": return 2;
                case "А-": return 3;
                case "С-": return 1;
                case "R-": return 10;
                case "L-": return 11;
                case "E-": return 11;

                case "Y-": return 20;
                case "U-": return 18;
               // case "O-": return 17;

            }

            return ret;
        }


        // НАЖАЛИ НОВЫЙ СКАНЕР
        // ГЛАВНЫЙ ЦИКЛ
        private void HandleData(Symbol.Barcode.ReaderData TheReaderData)
        {

          string TheReaderData_Text= TheReaderData.Text.Replace("?000", "Т000");
           TheReaderData_Text = TheReaderData_Text.Replace("?-", "A-");


           #region 
           if (this.tabControl1.TabPages[this.tabControl1.SelectedIndex].Name == "FULL_PALL")
           {
               if ((TheReaderData_Text.IndexOf("P_") != -1))
               {
                   //TheReaderData_Text = pallet_uid_decode(TheReaderData_Text);
                   fp_PRIHOD.Text = TheReaderData_Text;
                   return;
               }

               if ((TheReaderData_Text.IndexOf("W") != -1))
               {
                   fp_sborka.Text = TheReaderData_Text;
                   return;
               }
               fp_cell.Text = TheReaderData_Text;
               return;
           }
           #endregion


           if ((TheReaderData_Text.IndexOf("OP_") != -1 )  )
          {
              TheReaderData_Text = pallet_uid_decode(TheReaderData_Text);

              if (tabControl1.TabPages[tabControl1.SelectedIndex].Text != "ОТГ")
              { // Если не выбрана вкладка отгрузки, выбираем ее.

                  foreach (TabPage tp in tabControl1.TabPages)
                  { 
                    if( tp.Text=="ОТГ" )
                    {
                        tabControl1.SelectedIndex = tabControl1.TabPages.IndexOf(tp);
                    }

                  }
              }

          }

            #region ИНВЕНТАРИЗАЦИЯ ЯЧЕЕК ОТБОРА
          if (this.tabControl1.TabPages[this.tabControl1.SelectedIndex].Name == "prov")
          {
              
              if (get_ware_by_cell(TheReaderData_Text) > 0)
              {
                  m_inv_otbor_cell.Text = TheReaderData_Text;
              }
              

          }
            #endregion


            #region ИДЕНТИФИКАЦИЯ_И_ПРАВА_НАЗНАЧЕНИЕ_СБОРЩИКА

            if (  TheReaderData_Text.IndexOf("KLAD") == 0)
            {
                
                if (current_USER.ID == "")
                {
                    #region ЛОГИНИМСЯ_В_СИСТЕМУ_И_ПОЛУЧАЕМ_ПРАВА
                    // ДЕЛАЕМ ЗАПРОС НА ПОЛЬЗОВАТЕЛЯ
                    // =====================================================================================
                    funct f = new funct();
                    f.function_name = "GET_RUSER";
                    f.add_value("USERID", TheReaderData_Text);
                    Client client=nettt(f);
 
                    try
                    {
                        if(client!=null)
                        if (client.FUNC_Response != null)
                            if (client.FUNC_Response.Count > 0)
                            {
                                

                                foreach (funct f5 in client.FUNC_Response)
                                {
                                    if (f5.function_name == "USER_INFO")
                                    {
                                        current_USER.ID = f5.strToIntMap["ID"];
                                        current_USER.Name = f5.strToIntMap["NAME"];
                                        current_USER.PRAVO_CHECK_ORDER = (int)str2int(f5.strToIntMap["PRAVO_CHECK_ORDER"]);
                                        current_USER.PRAVO_INVENTORY_EDIT = (int)str2int(f5.strToIntMap["PRAVO_INVENTORY_EDIT"]);
                                        current_USER.PRAVO_LIGHT_INVENTORY_CHECK = (int)str2int(f5.strToIntMap["PRAVO_LIGHT_INVENTORY_CHECK"]);
                                        current_USER.PRAVO_RAZVOZ_ZAYAVOK = (int)str2int(f5.strToIntMap["PRAVO_RAZVOZ_ZAYAVOK"]);
                                        current_USER.PRAVO_EAN_PRODUCT_CHANGE = (int)str2int(f5.strToIntMap["PRAVO_EAN_PRODUCT_CHANGE"]);

                                        current_USER.PRAVO_KARSHIK = (int)str2int(f5.strToIntMap["PRAVO_KARSHIK"]);
                                        current_USER.ware_id = (int)str2int(f5.strToIntMap["ware_id"]);

                                        string systimestamp = f5.strToIntMap["systimestamp"].ToString();


                                        try
                                        {
                                            IFormatProvider culture = new CultureInfo("ru-RU", true);

                                            this.server_time = DateTime.Parse(systimestamp, culture, DateTimeStyles.NoCurrentDateDefault);
                                            this.start_time = DateTime.Now;
                                        }catch
                                        {
                                            IFormatProvider culture = new CultureInfo("de-DE", true);
                                            this.server_time = DateTime.Parse(systimestamp, culture, DateTimeStyles.NoCurrentDateDefault);
                                            this.start_time = DateTime.Now;
                                        }

                                    }
                                }
                                // ТЕПЕРЬ ПОКАЗЫВАЕМ ВКЛАДКИ ПРОГРАММЫ
                                this.tabControl1.Visible = true;

                                И2_СГ.Value = server_time.AddDays(7);

                                // if (current_USER.PRAVO_KARSHIK == 0)
                                //     this.tabControl1.TabPages.RemoveAt(7);


                                if ( (current_USER.PRAVO_INVENTORY_EDIT == 0) && (current_USER.PRAVO_CHECK_ORDER == 0)  )
                                    this.tabControl1.TabPages.RemoveAt(8);


                                if (current_USER.PRAVO_KARSHIK == 0)
                                    this.tabControl1.TabPages.RemoveAt(7);

                                if (current_USER.PRAVO_KARSHIK == 0)
                                    this.tabControl1.TabPages.RemoveAt(6);


                                if (current_USER.PRAVO_EAN_PRODUCT_CHANGE == 0)
                                    this.tabControl1.TabPages.RemoveAt(5);


                                if (current_USER.PRAVO_RAZVOZ_ZAYAVOK == 0)
                                    this.tabControl1.TabPages.RemoveAt(4);


                                if (current_USER.PRAVO_CHECK_ORDER == 0)
                                    this.tabControl1.TabPages.RemoveAt(3);

                                if ((current_USER.PRAVO_INVENTORY_EDIT == 0) && (current_USER.PRAVO_CHECK_ORDER == 0))
                                {
                                    this.tabControl1.TabPages.RemoveAt(1);
                                    this.tabControl1.TabPages.RemoveAt(0);

                                }
                                this.Text = current_USER.ID;
                            }
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message);
                    }

                    // =====================================================================================
               
                #endregion
                }
                else
                {


                }

                return;
            }

            #endregion 

          
            //
            #region ПАРАМЕТРЫ_ПРОДУКТА: ШТРИХ-КОДЫ
            if (tabControl1.TabPages[tabControl1.SelectedIndex].Text == "П")
            {
                if (radioButton3.Checked)
                {
                    prod_ean13_3.Text = TheReaderData_Text;
                }
                else if (radioButton2.Checked ) {
                    prod_ean13_2.Text = TheReaderData_Text;
                }
                else 
                {
                    prod_ean13_1.Text = TheReaderData_Text;
                }


            }
            #endregion


            #region АРМ ПЕРВОНАЧАЛЬНОЙ ИНВЕНТАРИЗАЦИИ
            if( tabControl1.TabPages[tabControl1.SelectedIndex].Text == "И2" )
            {
                if ( get_ware_by_cell(TheReaderData_Text) != -1)
                {
                    И_Ячейка.Text = TheReaderData_Text;
                }
                else
                {
                    И2_Штрихкод.Text = TheReaderData_Text;
                }
                return;
            }
            #endregion


            #region АРМ_КАРЩИКА
            if (tabControl1.TabPages[tabControl1.SelectedIndex].Text == "КАРЩ")
            {
                if (TheReaderData_Text.IndexOf("P_") != -1)
                {
                    m_pallet_uid.Text = TheReaderData_Text;
                    // Теперь надо выяснить, куда нужно поставить данный паллет, либо он уже где-то стоит?

                    funct f = new funct();
                    f.function_name = "CALL_SPF";
                    f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_DESTINATION_CELL2");
                    f.add_value("pallet_uid", m_pallet_uid.Text);
                    f.add_value("ware_id1",  current_USER.ware_id.ToString()  );
                    kar_info.Text = call_spf(f);
                    Beep_ok();
                    label19.Visible = true;
                    label20.Visible = false;

                }
                else {
                    if (get_ware_by_cell(TheReaderData_Text) !=-1  ) 
                    {
                        try
                        {
                            m_cell.Text = TheReaderData_Text;
                            
                            m_cell_history.Add(TheReaderData_Text);
                            // Что поставить в данную ячейку???
                            funct f = new funct();
                            f.function_name = "CALL_SPF";
                            f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_POPOLNENIE2");
                            f.add_value("PIKING_CELL", m_cell.Text);
                            f.add_value("ware_id1", current_USER.ware_id.ToString());
                            kar_info.Text = call_spf(f);
                            label20.Visible = true;
                            label19.Visible = false;
                            Beep_ok();
                        }
                        catch (Exception ex3)
                        {
                            MessageBox.Show("EX4: "+ex3.Message);
                        }
                    }
                }
                return;
            }
            #endregion 

            if (tabControl1.TabPages[tabControl1.SelectedIndex].Text == "ОТГ")
            {
             // ======================================================================
               // if (m_ordNumb.Text!="999999")
              if (TheReaderData_Text.Length>0)
                if (TheReaderData_Text.Substring(0, 3) == "OP_")
                {
                    // вернуться сюда
                     #region ЗАПРОС_ДАННЫХ_О_НАКЛАДНОЙ_ДЛЯ_РАЗВОЗА_ПО_ОТГРУЗОЧНОЙ
                     

                        try
                        {
                            m_otg_pallet.Text = TheReaderData_Text;
                            // Что поставить в данную ячейку???
                            funct f = new funct();
                            f.function_name = "CALL_SPF";
                            f.add_value("SPF_NAME", "RABAEV.RRL_GET_PAL_INFOTEXT");
                            f.add_value("PALLET_UID1", m_otg_pallet.Text);
                           
                            m_otg_label.Text = call_spf(f);
                            
                            Beep_ok();
                        }
                        catch (Exception ex)
                        {
                            MessageBox.Show(ex.Message);
                        }
                        // ======================================================================
                    #endregion
                   
                    return;
                }
                else
                {

                    m_otg_place.Text = TheReaderData_Text;
                }

                return;
                
            }
            


            #region ПРИЕМКА_ШТРИХКОДА_ПАЛЛЕТЫ
            if (this.Curent_Assemble.Is_Empty1() )
            {
                // Очищаем ошибки
                dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Clear();
                Curent_UID = "";
                
                TextBox_USSCC.Text = TheReaderData_Text;
                // Загружаем плановую накладную =================================================
                long lines_count = 0;
                long lines_count_must_be = 0;

                if ((TheReaderData_Text.IndexOf("OP_") != -1 )  )
                {
                    



                    this.Curent_Assemble.Curent_USSCC = TheReaderData_Text;
                    
                    #region ПРОВЕРКА_НАКЛАДНОЙ_ИЛИ_ЛОТА

                    funct f = new funct();
                    if (this.Curent_Assemble.by_order())
                    {
                        f.function_name = "GET_ORDER_ITEMS";
                    }
                    else
                    {
                        f.function_name = "GET_LOT_ITEMS";
                    }

                    f.add_value("USSCC", this.Curent_Assemble.Curent_USSCC);

                    Client client = nettt(f);
 

                    try
                    {
                        if (client.FUNC_Response != null)
                            if (client.FUNC_Response.Count > 0)
                            {
                                foreach (funct g in client.FUNC_Response)
                                {

                                    if (g.function_name == "LOT_LINES")
                                    {
                                        lines_count_must_be = (long)Convert.ToInt64(g.strToIntMap["lines_count_must_be"]);
                                        //this.Curent_Assemble.Curent_Order = (g.strToIntMap["order_number"]);
                                    }

                                    if (g.function_name == "ALT_SHT")
                                    { // УИД ШКШ ШКБ ШКК ШВБ ШВК
                                        DataRow dr = dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].NewRow();
                                        foreach (KeyValuePair<string, string> pair in g.strToIntMap)
                                        { dr[pair.Key] = pair.Value; }
                                        dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].Rows.Add(dr);
                                    }

                                    if (g.function_name == "LOT_LINE")
                                    {
                                        DataRow dr = dbComponent.myDataSet.Tables["PALLET_PLAN"].NewRow();
                                        DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].NewRow();
                                        lines_count++;
                                        foreach (KeyValuePair<string, string> pair in g.strToIntMap)
                                        {
                                            string k1 = pair.Key;
                                            if (k1.IndexOf("СЛУЖ_") < 0)
                                            {
                                                dr[pair.Key] = pair.Value;
                                                if (k1 == "УИД")
                                                    dr2[pair.Key] = pair.Value;
                                            }
                                            else
                                            {
                                                k1 = k1.Replace("СЛУЖ_", "");
                                                dr2[k1] = pair.Value;
                                            }
                                        }

                                        dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Add(dr);
                                        dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Add(dr2);

                                    }
                                }
                            }

                    }catch(Exception ex)
                    {
                        MessageBox.Show(ex.Message );
                    }

                    if (lines_count == 0)
                    {

                        dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Clear();
                        dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Clear();

                        if (lines_count_must_be == 0)
                        {  // ТАКОГО ЛОТА НЕТ
                            m_error_log.Text = m_error_log.Text + client.Response_to_string();
                            MessageBox.Show(" Лота с таки штрих-кодом (" + this.Curent_Assemble.Curent_USSCC + ") нет. ");
                            this.Curent_Assemble.Make_Empty();
                        }
                        else
                        {
                            this.Curent_Assemble.Make_Empty();
                            m_error_log.Text = m_error_log.Text + client.Response_to_string();
                            MessageBox.Show(" Строк не загружено. client.FUNC_Response.Count= " + Convert.ToString(client.FUNC_Response.Count) + " ШК= " + TheReaderData_Text);
                        }
                        return;
                    }

                    if (lines_count != lines_count_must_be)
                    {
                        dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Clear();
                        this.Curent_Assemble.Make_Empty();
                        MessageBox.Show(" проблема связи. Загружено " + Convert.ToString(lines_count) + " строк вместо " + Convert.ToString(lines_count_must_be));
                        return;
                    }
                    // ==============================================================================

                    #region КРАСОТА_ТАБЛИЦ


                    #endregion

                    statusBar1.Text = "Аудит сборки начат";
                    statusBar1.Font = new Font(FontFamily.GenericSansSerif, 08.0F, FontStyle.Regular);

                    PLANdataGrid2.DataSource = dbComponent.myDataSet.Tables["PALLET_PLAN"];
                    Beep_new_audit_started();

                    #endregion

                }
                else {





                    this.Curent_Assemble.Curent_Place = TheReaderData_Text;
                    
                        
                        #region ПРОВЕРКА_ЯЧЕЙКИ_ХРАНЕНИЯ

                        funct f = new funct();
                        f.function_name = "GET_PLACE_ITEMS";
                        this.Curent_Assemble.Curent_Place = TheReaderData_Text;
                        f.add_value("PLACEID", this.Curent_Assemble.Curent_Place);


                        Client client = nettt(f);
 
                        try
                        {
                            if (client.FUNC_Response != null)
                                if (client.FUNC_Response.Count > 0)
                                {
                                    foreach (funct g in client.FUNC_Response)
                                    {

                                        if (g.function_name == "PLACE_LINES")
                                        {
                                            lines_count_must_be = (long)Convert.ToInt64(g.strToIntMap["lines_count_must_be"]);
                                        }

                                        if (g.function_name == "ALT_SHT")
                                        { // УИД ШКШ ШКБ ШКК ШВБ ШВК
                                            DataRow dr = dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].NewRow();
                                            foreach (KeyValuePair<string, string> pair in g.strToIntMap)
                                            { dr[pair.Key] = pair.Value; }
                                            dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].Rows.Add(dr);
                                        }

                                        if (g.function_name == "PL")
                                        {
                                            DataRow dr = dbComponent.myDataSet.Tables["PALLET_PLAN"].NewRow();
                                            DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].NewRow();
                                            lines_count++;
                                            foreach (KeyValuePair<string, string> pair in g.strToIntMap)
                                            {
                                                string k1 = pair.Key;
                                                if (k1.IndexOf("СЛУЖ_") < 0)
                                                {
                                                    dr[pair.Key] = pair.Value;
                                                    if (k1 == "УИД")
                                                        dr2[pair.Key] = pair.Value;
                                                }
                                                else
                                                {
                                                    k1 = k1.Replace("СЛУЖ_", "");
                                                    dr2[k1] = pair.Value;
                                                }
                                            }
                                            dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Add(dr);
                                            dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Add(dr2);
                                        }
                                    }
                                }

                        }
                        catch (Exception ex)
                        {

                            MessageBox.Show(ex.Message);

                        }

                        if (lines_count == 0)
                        {

                            dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Clear();
                            dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Clear();

                            if (lines_count_must_be == 0)
                            {  // ТАКОГО ЛОТА НЕТ
                                m_error_log.Text = m_error_log.Text + client.Response_to_string();
                                MessageBox.Show(" Лота с таки штрих-кодом (" + this.Curent_Assemble.Curent_USSCC + ") нет. ");
                                this.Curent_Assemble.Make_Empty();
                            }
                            else
                            {
                                this.Curent_Assemble.Make_Empty();
                                m_error_log.Text = m_error_log.Text + client.Response_to_string();
                                MessageBox.Show(" Строк не загружено. client.FUNC_Response.Count= " + Convert.ToString(client.FUNC_Response.Count) + " ШК= " + TheReaderData_Text);
                            }
                            return;
                        }

                        if (lines_count != lines_count_must_be)
                        {
                            dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Clear();
                            this.Curent_Assemble.Make_Empty();
                            MessageBox.Show(" проблема связи. Загружено " + Convert.ToString(lines_count) + " строк вместо " + Convert.ToString(lines_count_must_be));
                            return;
                        }
                        // ==============================================================================


                        statusBar1.Text = "Инвентаризация ячейки хранения";
                        statusBar1.Font = new Font(FontFamily.GenericSansSerif, 08.0F, FontStyle.Regular);

                        PLANdataGrid2.DataSource = dbComponent.myDataSet.Tables["PALLET_PLAN"];
                        PLANdataGrid2.CurrentRowIndex = 0;
                        DataGridCell myDataGridCell = PLANdataGrid2.CurrentCell;

                        myDataGridCell.ColumnNumber = 1;
                        myDataGridCell.RowNumber = 1;
                        //PLANdataGrid2.CurrentCell = myDataGridCell;
                        try
                        {
                            Curent_UID = dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows[0]["УИД"].ToString();
                        }
                        catch { }


                        //PLANdataGrid2_CurrentCellChanged(
                        Beep_new_audit_started();

                        #endregion
                   
                   
                  

                }





            }
            
            #endregion
            
            #region ПРИЕМКА_ШТРИХКОДА_ТОВАРА 

            else
            {

                #region КРАТКИЙ_КОММЕНТАРИЙ
                // Это штрих-код продукта. Далее мы определяем, есть - ли продукты в ЛОТЕ
              // WMS с данным штрих кодом штуки, коробки или блочка. и 
              // Если продукта в сборке нет - идем в базу аналогов и ищем там.
              // Если нет и там, - пищим и в статус строке пишем - нет какого продукта
              // Если продукт есть в сборке, то пересчитываем отсканированное количество в штуки
              /* и Добавляем к количеству, которое уже отсканировано. (если строки с артикулом нет в факте)
               * то строку с артикулом нужно добавить. 
               * Если по артикулу количество факта больше количество плана, прищим и говорим, 
               * что артикул надо отставить
               * если совпадает с планом - помечаем строку в плане и факте как совпавшую.
               * проверяем все строки на равенство. 
               * Если все отошло - то победа:
               * Пишем в лог, что сборка проверена по кодам
               */
                

                // Если штрих-код = штрихкоду паллета, считаем, что проверка завершена.
                // Выдаем список недостающих позиций.  Если есть хоть одна недостающая, проверку не закрываем
                // Если все позиции проверены корректно, и список возвращаемых в секцию позиций пуст,
                // Закрываем проверку, отсылаем сообщение на сервер, выходим.
                // Если список возвращаемых позиций не пуст- прелагаем отставить эти возвратные позиции
                // и зафиксировать это. выходим.
                #endregion

                string shtrih_kod = TheReaderData_Text;
                if ((this.Curent_Assemble.Curent_USSCC == TheReaderData_Text) || ((this.Curent_Assemble.Curent_Order  == TheReaderData_Text)))
                {
                    return;
                }

                // Ищем продукт в плане WMS а также в таблице аналогов. Ищем = Штуку Блок Коробку
                //    DataRow dr = dbComponent.myDataSet.Tables["PALLET_PLAN"].NewRow();
                //    DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].NewRow();
                try
                {

                    #region штрих_код_найден_и_кратность_упаковки_определена
                    bool product_in_a_lot = false;
                    foreach (DataRow dr in dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows)
                    {
                         long l_inc = 0;
                        if ((dr["ШК_БЛОКА"].ToString() == shtrih_kod) || (("0" + dr["ШК_БЛОКА"]) == shtrih_kod))
                        {
                            l_inc = Convert.ToInt64(dr["ШТВБЛ"].ToString());
                        }

                        if ((dr["ШК_КОРОБ"].ToString() == shtrih_kod) || (("0" + dr["ШК_КОРОБ"]) == shtrih_kod))
                        {
                            l_inc = Convert.ToInt64(dr["ШТВБЛ"].ToString()) * Convert.ToInt64(dr["БЛВКОР"].ToString());
                        }

                        if ((dr["ШК_ШТУКИ"].ToString() == shtrih_kod) || (("0" + dr["ШК_ШТУКИ"]) == shtrih_kod))
                        {
                            l_inc=1; 
                        }

                        if (l_inc > 0)
                        {
                            string uid = dr["УИД"].ToString();
                            product_in_a_lot = add_product(uid, l_inc);
                        }
                        
                        
                        

                    }
                    #endregion
                    if (!product_in_a_lot)
                    {
                        #region ЕСЛИ_ПРОДУКТА_НЕТ_В_СБОРКЕ_ПРОВЕРЯЕМ_АЛЬТЕРНАТИВНЫЕ_ШТРИХ_КОДЫ
                        foreach (DataRow dr in dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].Rows)
                        {
                            long l_inc = 0;

                            if ((dr["ШКБ"].ToString() == shtrih_kod) || (("0" + dr["ШКБ"]) == shtrih_kod))
                            {
                                l_inc = Convert.ToInt64(dr["ШВБ"].ToString());
                            }

                            if ((dr["ШКК"].ToString() == shtrih_kod) || (("0" + dr["ШКК"]) == shtrih_kod))
                            {
                                l_inc = Convert.ToInt64(dr["ШВБ"].ToString()) * Convert.ToInt64(dr["БВК"].ToString());
                            }

                            if ((dr["ШКШ"].ToString() == shtrih_kod) || (("0" + dr["ШКШ"]) == shtrih_kod))
                            {
                                l_inc = 1;
                            }

                            if (l_inc > 0)
                            {
                                string uid = dr["УИД"].ToString();
                                product_in_a_lot = add_product(uid, l_inc);
                                break;
                            }
                            #region штрих_код_найден_и_кратность_упаковки_определена

                            #endregion
                        }

                        #endregion
                    }
                    #region ЕСЛИ_ПРОДУКТА_НЕТ_В_СБОРКЕ
                    // продукта нет в лоте - пищим и в статус строке пишем - нет какого продукта
                    if (!product_in_a_lot) {
                        statusBar1.Text = "продукта нет в сборке";
                        Beep_wrong_product();
                        // Добавляем продукт в таблицу ошибок.
                        // Для этого сначала сходим на сервер - узнаем его параметры.
                        // Сначала найдем данный продукт в таблице отклонений.
                        bool product_in_a_fault_array=false;

                        // ДОРАБОТАТЬ 
                        foreach( DataRow dr5 in dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows )
                        {
                            if (dr5["ШТРИХКОД"].ToString() == shtrih_kod) {
                                product_in_a_fault_array = true;
                                dr5["КОЛ"] = str2int( dr5["КОЛ"].ToString() ) + 1;
                            }
                        }


                        if ( product_in_a_fault_array == false)
                        {
                            #region ЗАПРАШИВАЕМ_НА_СЕРВЕРЕ_ПАРАМЕТРЫ_ПРОДУКТА
                           
                            funct f = new funct();
                            f.function_name = "GET_PRODUCT_INFO";
                            f.add_value("ШТРИХКОД", shtrih_kod);

                            Client client = nettt(f);
                            /*
                            Client client = new Client(IPAddress.Parse(this.ServerIP.Text), 20000);
                            client.FUNC_Request = f;
                            int rsize = client.Receive();
                            client.Disconnect();
                            */
                            
                            
                            bool штрих_код_найден_на_стороне_сервера = false;
                            if (client.FUNC_Response.Count > 0)
                            {
                                funct f2 = client.FUNC_Response[0];
                                if (f2.function_name == "END_GET_PRODUCT_INFO")
                                {
                                    DataRow dr4 = dbComponent.myDataSet.Tables["PALLET_AS_IS"].NewRow();
                                    dr4["АДРЕС"] = f2.strToIntMap["АДРЕС"].ToString();
                                    dr4["УИД"] = f2.strToIntMap["УИД"].ToString();
                                    dr4["ИМЯ"] = f2.strToIntMap["ИМЯ"].ToString();
                                    dr4["ШТРИХКОД"] = shtrih_kod;
                                    dr4["КОЛ"] = 1;
                                    dr4["ПЛАН_КОЛ"] = 0;
                                    dr4["ТИП"] = "ПЕРЕСОРТ";
                                    штрих_код_найден_на_стороне_сервера = true ;
                                    dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Add(dr4);
                                }
                                else
                                {
                                    trace("Ошибка на стороне сервера");
                                    trace(f.ToString());
                                }
                            }


                            if (штрих_код_найден_на_стороне_сервера)
                            {
                                statusBar1.Text = "ПЕРЕСОРТ";

                            }
                            else 
                            {
                                statusBar1.Text = "НЕИЗВЕСТНЫЙ Штрих-код";                            
                            }



                         #endregion
                        }
                       

                        /*
                                            
                                           
                         */

                        


                  }
                    #endregion

              }catch(Exception ex)
                {
                    trace("Произошла ошибка" + ex.Message);
                    MessageBox.Show(ex.Message);
                    return;
                }
            }
            #endregion

        }


        private bool add_product(string uid, long l_inc)
        {

            bool product_in_a_lot = false;
            bool проводится_инвентаризация = false ;
            if (Curent_Assemble.MODE() == "By_Place")
            {
                проводится_инвентаризация = true ;
            }

            #region штрих_код_найден_и_кратность_упаковки_определена

            DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Find(uid);
            DataRow dr_hidden = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Find(uid);
            DateTime current_picking_time =   this.server_time + (DateTime.Now- this.start_time );
            string current_picking_time_str = "'" + current_picking_time.Day + "." + current_picking_time.Month + "." + current_picking_time.Year + " " + current_picking_time.Hour + ":" + current_picking_time.Minute + ":" + current_picking_time.Second + "'";
            dr_hidden["ВРЕМЯ"] = current_picking_time;
            int index_of_dr_hidden=dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.IndexOf(dr_hidden);
            dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows[index_of_dr_hidden]["ВРЕМЯ"] = current_picking_time;

            string l_product_name = dr2["НАИМ"].ToString();
            statusBar1.Text = l_product_name;

            if (l_inc > 0)
            {
                Curent_UID = uid;
                product_in_a_lot = true;

                long current_count = (long)Convert.ToInt64(dr2["ФАКТ_КОЛ"]);
                long plan_count = (long)Convert.ToInt64(dr2["КОЛ"]);


                if ((current_count + l_inc <= plan_count) || (проводится_инвентаризация) /* либо инвентаризация */ )
                {
                    dr2["ФАКТ_КОЛ"] = current_count + l_inc;
                    if ((current_count + l_inc == plan_count) && (!проводится_инвентаризация) /* и не инвентаризация */ )
                    {
                        bool l_fault = false;
                        dr2["Р"] = "=";
                        // БЕЖИМ ПО ВСЕМ СТРОКАМ. Если все отошло - то победа:
                        // Пишем в лог, что сборка проверена по кодам
                        foreach (DataRow dr3 in dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows)
                        {
                            string l_l = dr3["Р"].ToString();
                            if ((l_l != "=") && (l_l != ">"))
                            { l_fault = true; }
                        }
                        #region ВАЖНЫЙ_ЭТАП_СБОРКА_ПОЛНОСТЬЮ_ПРОВЕРЕНА
                        if ((l_fault == false) && (!проводится_инвентаризация) /* и не инвентаризация */ )
                        {  // СБОРКА ПРОШЛА ПРОВЕРКУ

                            Beep_win();
                            // ФИКСИРУЕМ ЭТОТ РЕЗУЛЬТАТ - ПОСЫЛАЕМ НА СЕРВЕР СООБЩЕНИЕ о проверке сборки
                            // ОТСЫЛАЕМ НА СЕРВЕР ЗАДАЧУ НА возврат в секцию лишнего товара.
                            #region ФИКСИРУЕМ_РЕЗУЛЬТАТ_ПРОВЕРКИ_НА_СЕРВЕР
                            finish_check();
                           
                            #endregion

                        }
                        else
                        {
                            Beep_ok();
                            int i = Convert.ToInt32(dr2["ПП"].ToString());
                            PLANdataGrid2.CurrentRowIndex = i - 1;
                        }
                        #endregion
                    }
                    else
                    {
                        Beep_ok();
                        int i = Convert.ToInt32(dr2["ПП"].ToString());
                        PLANdataGrid2.CurrentRowIndex = i - 1;
                    }
                }
                else
                {
                    // ЕСЛИ ПРОИСХОДИТ ИНВЕНТАРИЗАЦИЯ, ИЗЛИШЕК ФИКСИРУЕМ: КОЛИЧЕСТВО
                    if (this.Curent_Assemble.MODE() == "By_Place")
                    {
                        //dr2["ФАКТ_КОЛ"] = dr2["КОЛ"];
                        dr2["Р"] = ">";
                    }


                    statusBar1.Text = "перебор: c  " + Convert.ToString(l_inc);
                    Beep_fault();

                    #region РЕГИСТРИРУЕМ_ОШИБКУ_ИЗЛИШКА
                    // Сначала ищем ошибку с таким УИДОМ товара
                    string h_tuid7 = dr_hidden["УИД"].ToString();
                    DataRow h_row7 = dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Find(h_tuid7);
                    if (h_row7!=null)
                    {
                        // В момент инвентаризации, излишек = ошибке
                        if (this.Curent_Assemble.MODE() == "By_Place")
                        {
                            h_row7["КОЛ"] =  l_inc;
                        }
                        else
                        {
                            h_row7["КОЛ"] = Convert.ToInt64(h_row7["КОЛ"].ToString()) + l_inc;
                        }
                    }else{
                        DataRow dr4 = dbComponent.myDataSet.Tables["PALLET_AS_IS"].NewRow();
                        dr4["АДРЕС"] = dr_hidden["АДР"].ToString();
                        dr4["УИД"] = dr_hidden["УИД"].ToString();
                        dr4["ИМЯ"] = l_product_name;
                        dr4["ШТРИХКОД"] = dr_hidden["ШК_ШТУКИ"].ToString();
                        dr4["КОЛ"] = l_inc;
                        dr4["ПЛАН_КОЛ"] = 0;

                        dr4["ТИП"] = "ИЗЛИШКИ";
                        dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Add(dr4);
                    }
                    #endregion

                }

            }
            #endregion

            return product_in_a_lot;
        }

        // Фиксируем результат проверки  и отсылаем данные на сервер
        private bool finish_check()
        {
            
            Dictionary<string, string> Времена_пикания= new Dictionary<string,string>();
            #region ФИКСИРУЕМ_РЕЗУЛЬТАТ_ПРОВЕРКИ_НА_СЕРВЕР
            try
            {
                #region БЕЖИМ ПО ВСЕМ СТРОКАМ
                long error_count = 0;
                foreach (DataRow dr7 in dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows)
                {
                    string uid_h11=dr7["УИД"].ToString();
                    DataRow dr7_hidden = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Find(( uid_h11));
                    DataRow dr4 = dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Find((uid_h11)); ;
                    int index_of_dr4=dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.IndexOf(dr4);
                    Dictionary<string,string> t_emp= new Dictionary<string,string>();
                    
                    Времена_пикания[uid_h11] = "";
                    if ( (dr7_hidden["ВРЕМЯ"] != null) && (dr7_hidden["ВРЕМЯ"].ToString()!="" ) )
                    {
                        DateTime current_picking_time = (DateTime)( dr7_hidden["ВРЕМЯ"]);
                        Времена_пикания[uid_h11] = "'" + current_picking_time.Day + "." + current_picking_time.Month + "." + current_picking_time.Year + " " + current_picking_time.Hour + ":" + current_picking_time.Minute + ":" + current_picking_time.Second + "'";
                    }
                       


                    if (dr7["Р"].ToString() == "<")
                    {
                         if (dr4 == null)
                        {
                            dr4 = dbComponent.myDataSet.Tables["PALLET_AS_IS"].NewRow();
                            dr4["АДРЕС"] = dr7_hidden["АДР"];
                            dr4["УИД"] = uid_h11;
                            dr4["ИМЯ"] = dr7["НАИМ"].ToString();
                            dr4["ШТРИХКОД"] = dr7_hidden["ШК_ШТУКИ"];
                            dr4["КОЛ"] = str2int(dr7["ФАКТ_КОЛ"].ToString());

                            dr4["ПЛАН_КОЛ"] = str2int(dr7["КОЛ"].ToString() );
                            dr4["ВРЕМЯ"] = dr7_hidden["ВРЕМЯ"];


                            dr4["ТИП"] = "НЕДОСТАЧА";
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Add(dr4);
                        }
                        else {
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["АДРЕС"] = dr7_hidden["АДР"];
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["УИД"] = uid_h11;
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["ИМЯ"] = dr7["НАИМ"].ToString();
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["ШТРИХКОД"] = dr7_hidden["ШК_ШТУКИ"];
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["КОЛ"] = str2int(dr7["ФАКТ_КОЛ"].ToString());
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["ПЛАН_КОЛ"] = str2int(dr7["КОЛ"].ToString());
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["ТИП"] = "НЕДОСТАЧА";
                            dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows[index_of_dr4]["ВРЕМЯ"] = dr7["ВРЕМЯ"];

                        }
                        error_count++;
                    }

                }
                #endregion

                trace("Сборка полностью проверена");
                statusBar1.Text = "Сборка полностью проверена";
                statusBar1.Font = new Font(FontFamily.GenericSansSerif, 10.0F, FontStyle.Bold);

                funct f = new funct();
                //client.FUNC_Request = f;   


                // By_USSCC By_ORDER By_Place
                if ( this.Curent_Assemble.MODE() == "By_ORDER")
                {
                    f.function_name = "ORDER_CHECK_PASSED";
                    f.add_value("ORDER", this.Curent_Assemble.Curent_Order );
                    f.add_value("error_count", Convert.ToString(error_count));
                    f.add_value("USER_ID", this.current_USER.ID);
                }
                
                if (this.Curent_Assemble.MODE() == "By_USSCC")
                {
                    f.function_name = "LOT_CHECK_PASSED";
                    f.add_value("USSCC", this.Curent_Assemble.Curent_USSCC);
                    f.add_value("USER_ID", this.current_USER.ID);
                    f.add_value("error_count", Convert.ToString(error_count));
                }

                if (this.Curent_Assemble.MODE() == "By_Place")
                {
                    f.function_name = "PLACE_CHECK_PASSED";
                    f.add_value("PALLETID", this.Curent_Assemble.Curent_Place);
                    f.add_value("error_count", Convert.ToString(error_count));
                    f.add_value("USER_ID", this.current_USER.ID);

                }
               // Client client = nettt(f); //new Client(IPAddress.Parse(this.ServerIP.Text), 20000);

                Client client = new Client(IPAddress.Parse(this.ServerIP.Text), Convert.ToInt32(this._port.Text));
                client.FUNC_Request = f;
                //БОЛЕЕ НИЧЕГО НЕ ДЕЛАЕМ.
                
                    #region СОБИРАЕМ ОШИБКИ
                    foreach (DataRow dr9 in dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows)
                    {

                        funct f2 = new funct();
                        if (this.Curent_Assemble.MODE() == "By_Place")
                        {

                            f2.function_name = "ERROR_PALLET_CHECK_LINE";
                            f2.add_value("PALLETID", this.Curent_Assemble.Curent_Place);
                            f2.add_value("УИД", dr9["УИД"].ToString());

                            f2.add_value("КОЛ", dr9["КОЛ"].ToString());
                            f2.add_value("ПЛАН_КОЛ", dr9["ПЛАН_КОЛ"].ToString());

                            f2.add_value("ТИП", dr9["ТИП"].ToString());
                            f2.add_value("ШТРИХКОД", dr9["ШТРИХКОД"].ToString());
                            f2.add_value("ШТРИХКОД2", dr9["ШТРИХКОД"].ToString());
                            client.PROGRAM_Request.Add(f2);

                        }
                        else
                        {
                            f2.function_name = "ERROR_LOT_LINE";
                            f2.add_value("USSCC", this.Curent_Assemble.Curent_USSCC);
                            f2.add_value("ORDER", this.Curent_Assemble.Curent_Order);

                            f2.add_value("УИД", dr9["УИД"].ToString());


                            f2.add_value("КОЛ", dr9["КОЛ"].ToString());
                            if (dr9["ТИП"].ToString() == "ИЗЛИШКИ")
                            {
                                f2.add_value("ПЛАН_КОЛ", dr9["ПЛАН_КОЛ"].ToString());
                            }
                            else
                            {
                                f2.add_value("ПЛАН_КОЛ", dr9["ПЛАН_КОЛ"].ToString());
                            }

                            f2.add_value("ТИП", dr9["ТИП"].ToString());
                            f2.add_value("ШТРИХКОД", dr9["ШТРИХКОД"].ToString());
                            f2.add_value("ШТРИХКОД2", dr9["ШТРИХКОД"].ToString());
                            f2.add_value("ВРЕМЯ", dr9["ВРЕМЯ"].ToString());


                            //l_prog = l_prog + f2.encode();
                            client.PROGRAM_Request.Add(f2);
                        }

                    }

                    #endregion

                    #region СОБИРАЕМ ВРЕМЯ ПИКАНИЯ
                    if (this.Curent_Assemble.MODE() == "By_Place")
                    {
                        foreach (DataRow dr67 in dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows)
                        {
                            funct f5 = new funct();
                            f5.function_name = "INVENTORY_LINE_PALLET_AUDIT";
                            string uid_h11 = dr67["УИД"].ToString();
                            f5.add_value("УИД", dr67["УИД"].ToString());
                            f5.add_value("КОЛ", dr67["ФАКТ_КОЛ"].ToString());
                            f5.add_value("PALLETID", this.Curent_Assemble.Curent_Place);
                            f5.add_value("USER_ID", this.current_USER.ID);


                            client.PROGRAM_Request.Add(f5);
                        }
                    }

                    if (this.Curent_Assemble.MODE() == "By_USSCC")
                    {
                        foreach (string kk in Времена_пикания.Keys)
                        {
                            if (Времена_пикания[kk] != "")
                            {
                                funct f5 = new funct();
                                f5.function_name = "VP";
                                f5.add_value("PALLET_UID", this.Curent_Assemble.Curent_USSCC);
                                f5.add_value("УИД", kk);
                                f5.add_value("TIME", Времена_пикания[kk]);
                                client.PROGRAM_Request.Add(f5);
                                if (client.FUNC_Request == null)
                                    client.FUNC_Request = f5;
                            }
                        }
                    }


                    #endregion

                    int rsize = client.Receive();
                    client.Disconnect();

                    #region ПЕЧАТЬ СБОРОЧНИКА НА ОШИБКИ
                    if ((this.Curent_Assemble.MODE() == "By_USSCC") || (this.Curent_Assemble.MODE() == "By_ORDER"))
                    {


                        if (error_count > 0)
                        {
                            string mess_ = " ЛОТ СОДЕРЖИТ ОШИБКИ. \r\n Отставьте Паллет в зону ошибок. \r\n Сборочник на ошибки находится у операторов.";
                            trace(mess_);
                            MessageBox.Show(mess_);
                            #region  ПЕЧАТЬ_СБОРОЧНИКА_НА_ОШИБКИ

                            if (this.Curent_Assemble.Curent_Order != "")
                            {

                                try
                                {
                                    funct f2 = new funct();
                                    Client client2;
                                    f2.function_name = "PRINT_ERROR_LIST";
                                    f2.add_value("UID_ORD", this.Curent_Assemble.Curent_Order);

                                    client2 = new Client(IPAddress.Parse(this.PrintServer.Text), 20001);
                                    client2.FUNC_Request = f2;
                                    int rsize2 = client2.Receive();
                                    trace("Получен пакет длиной=" + Convert.ToString(rsize2));
                                    client2.Disconnect();
                                }
                                catch (Exception ex)
                                {
                                    MessageBox.Show("Не удалось распечатать ИСПРАВИТЕЛЬНЫЙ ЛИСТ. Обратитесь к оператору. \r\n " + ex.Message);
                                }
                            }
                            else
                            {

                                if (this.Curent_Assemble.Curent_USSCC != "")
                                {

                                    try
                                    {
                                        funct f2 = new funct();
                                        Client client2;
                                        f2.function_name = "PRINT_ERROR_LIST";
                                        f2.add_value("UID_USSCC", this.Curent_Assemble.Curent_USSCC);

                                        client2 = new Client(IPAddress.Parse(this.PrintServer.Text), 20001);
                                        client2.FUNC_Request = f2;
                                        int rsize2 = client2.Receive();
                                        trace("Получен пакет длиной=" + Convert.ToString(rsize2));
                                        client2.Disconnect();
                                    }
                                    catch (Exception ex)
                                    {
                                        MessageBox.Show("Не удалось распечатать ИСПРАВИТЕЛЬНЫЙ ЛИСТ. Обратитесь к оператору. \r\n " + ex.Message);
                                    }
                                }

                            }

                            #endregion

                        }
                        else
                        {

                            string mess_ = " ЛОТ ПРОВЕРЕН. \r\n Переместите паллет в зону сборки. Сборочник на ошибки находится у операторов.";
                            if (dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Count > 0)
                            {
                                mess_ = " ЛОТ ПРОВЕРЕН. \r\n Переместите паллет в зону сборки. \r\n Верните лишний товар в секцию \r\n Сборочник на ошибки находится у операторов.";
                            }
                            trace(mess_);
                            MessageBox.Show(mess_);
                        }
                    }

                    if (this.Curent_Assemble.MODE() == "By_Place")
                    {



                        if (error_count > 0)
                        {
                            string mess_ = "  ПАЛЛЕТО-МЕСТО ПРОВЕРЕНО. \r\n Есть товар, который нужно отставить в зону ошибок ";
                            trace(mess_);
                            MessageBox.Show(mess_, "Есть ошибки", MessageBoxButtons.OK, MessageBoxIcon.Asterisk, MessageBoxDefaultButton.Button1);
                        }
                        else
                        {
                            string mess_ = "  ПАЛЛЕТО-МЕСТО ПРОВЕРЕНО. \r\n Ошибок нет ";
                            trace(mess_);
                            MessageBox.Show(mess_, "Нет ошибок", MessageBoxButtons.OK, MessageBoxIcon.Hand, MessageBoxDefaultButton.Button1);
                        }
                    }
                    #endregion
                

               

            }
            catch (Exception ex)
            {
                MessageBox.Show(""+ex.Message);
            }
            #endregion       


            #region ЧИСТКА


            // dbComponent.myDataSet.Tables["PALLET_AS_IS"].Rows.Clear();
            dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Clear();
            dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Clear();
            dbComponent.myDataSet.Tables["АЛЬТЕРНАТИВНЫЕ_ДАННЫЕ"].Rows.Clear();
            this.TextBox_USSCC.Text = "";
            this.Curent_Assemble.Make_Empty() ;
            this.Curent_UID = "";
            this.m_BLOCHKI.Text  = "";
            this.m_KOROBKI.Text = "";
            this.m_SHTUKI.Text = "";



            #endregion

            return true;

        }

        private void trace(string tr)
        {
            m_error_log.Text = m_error_log.Text + tr+"\r\n";
        }

        private void FormMain_Resize(object sender, EventArgs e)
        {
            if (bInitialScale == true)
            {
                return; // Return if the initial scaling (from scratch)is not complete.
            }

            if (Screen.PrimaryScreen.Bounds.Width > Screen.PrimaryScreen.Bounds.Height) // If landscape orientation
            {
                if (bPortrait != false) // If an orientation change has occured to landscape
                {
                    bPortrait = false; // Set the orientation flag accordingly.
                    bInitialScale = true; // An initial scaling is required due to orientation change.
                    Scale(this); // Scale the GUI.
                }
                else
                {   // No orientation change has occured
                    bSkipMaxLen = true; // Initial scaling is now complete, so skipping the max. length restriction is now possible.
                    Scale(this); // Scale the GUI.
                }
            }
            else
            {
                // Similarly for the portrait orientation...
                if (bPortrait != true)
                {
                    bPortrait = true;
                    bInitialScale = true;
                    Scale(this);
                }
                else
                {
                    bSkipMaxLen = true;
                    Scale(this);
                }
            }
        }




        



        private void PLANdataGrid2_CurrentCellChanged(object sender, EventArgs e)
        {
            //default_manual_input_option();
            //int cn = ((DataGrid)sender).CurrentCell.ColumnNumber;
            int rn = ((DataGrid)sender).CurrentCell.RowNumber;
            if (rn >= 0)
            {

               DataRow dr1= dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows[rn ];
               DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows[rn ];
               statusBar1.Text = dr1["НАИМ"].ToString();

               Curent_UID = Convert.ToString(dr1["УИД"].ToString());

               long fcount=Convert.ToInt64(dr1["ФАКТ_КОЛ"].ToString ());
               long fcount2=fcount;
               long shvb = Convert.ToInt64(dr2["ШТВБЛ"].ToString ());
               long blvk = Convert.ToInt64(dr2["БЛВКОР"].ToString());
               if (shvb <= 0) shvb = 1;
               if (blvk <= 0) blvk = 1;
               long l_f_k ;//=  Math.Ceiling( fcount / (shvb*blvk))-1;
               l_f_k=(long)Math.Floor((long)fcount/ (long)(shvb * blvk) ); // Количество коробок
               if (blvk == 1) { l_f_k = 0; }

               fcount = fcount - l_f_k * (shvb * blvk); //Итого осталось штук после вычета коробок

               long l_f_b = (long)Math.Floor((long)fcount / (long)(shvb ));
               if(shvb ==1){l_f_b=0;}

               long l_f_sh = fcount2 - l_f_k * (shvb * blvk) - l_f_b * shvb;

                m_SHTUKI.Text = Convert.ToString(l_f_sh);
                m_KOROBKI.Text = Convert.ToString(l_f_k);
                m_BLOCHKI.Text = Convert.ToString(l_f_b);
              
           }

        }

        private long str2int( string f)
        {
            if (f == null) return 0;
            if (f == "") return 0;
            try
            {
                return Convert.ToInt64(f);
            }catch
            {
            return 0;
            }

        }

        private void button2_Click(object sender, EventArgs e)
        {
           
            #region Добавляем_Кличество_вручную
            bool product_in_a_lot = false;    
            long l_inc = 0;
            if (Curent_UID !="")
            {
                DataRow dr1 = dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows.Find(Curent_UID);
                DataRow dr2 = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Find(Curent_UID);


                long shvb = Convert.ToInt64(dr2["ШТВБЛ"].ToString());
                long blvk = Convert.ToInt64(dr2["БЛВКОР"].ToString());
                long m_new_tobe = str2int(m_SHTUKI.Text) + str2int(m_KOROBKI.Text) * shvb * blvk + str2int(m_BLOCHKI.Text) * blvk;

                long fk= Convert.ToInt64( dr1["ФАКТ_КОЛ"].ToString());
                l_inc = m_new_tobe - fk;
                string uid = Convert.ToString(Curent_UID);
                product_in_a_lot = add_product( uid , l_inc);

            }
            #endregion

        }

        private void button3_Click(object sender, EventArgs e)
        {
            finish_check();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            m_SHTUKI.Text =  Convert.ToString( str2int( m_SHTUKI.Text)+1);
        }

        private void button5_Click(object sender, EventArgs e)
        {
            m_BLOCHKI.Text = Convert.ToString(str2int(m_BLOCHKI.Text) + 1);
        }

        private void button6_Click(object sender, EventArgs e)
        {
            m_KOROBKI.Text = Convert.ToString(str2int(m_KOROBKI.Text) + 1);
        }

        private void button7_Click(object sender, EventArgs e)
        {
            if (str2int(m_SHTUKI.Text) > 0)
            {
                m_SHTUKI.Text = Convert.ToString(str2int(m_SHTUKI.Text) - 1);
            }
        }

        private void button8_Click(object sender, EventArgs e)
        {
            if (str2int(m_BLOCHKI.Text) > 0)
            {
                m_BLOCHKI.Text = Convert.ToString(str2int(m_BLOCHKI.Text) - 1);
            }
        }

        private void button9_Click(object sender, EventArgs e)
        {
            if (str2int(m_KOROBKI.Text) > 0)
            {
                m_KOROBKI.Text = Convert.ToString(str2int(m_KOROBKI.Text) - 1);
            }
        }


        private void button10_Click(object sender, EventArgs e)
        {
            try
            {
                funct f = new funct();
                Client client;
                f.function_name = "PRINT_ERROR_LIST";
                f.add_value("UID_ORD", "5422406");

                client = new Client(IPAddress.Parse(this.PrintServer.Text), 20001);
                client.FUNC_Request = f;
                int rsize = client.Receive();
                trace("Получен пакет длиной=" + Convert.ToString(rsize));
                client.Disconnect();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message );
            }

        }






        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void prod_kol_bl_TextChanged(object sender, EventArgs e)
        {

        }

        private void П_Click(object sender, EventArgs e)
        {

        }

        private void prod_ean_type_2_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void PLANdataGrid2_DoubleClick(object sender, EventArgs e)
        {

            if (current_USER.PRAVO_EAN_PRODUCT_CHANGE==1)
            {
                DataRow dr = dbComponent.myDataSet.Tables["PALLET_PLAN"].Rows[PLANdataGrid2.CurrentRowIndex];
                string  UID =    dr["УИД"].ToString() ;
                string NAIM = dr["НАИМ"].ToString();
                ProdNaim.Text  = NAIM;
                DataRow dr_hidden = dbComponent.myDataSet.Tables["PALLET_PLAN_HIDDEN"].Rows.Find(UID);
               prod_kol_bl.Text = dr_hidden["ШТВБЛ"].ToString();
               prod_kol_v_kr.Text= dr_hidden["БЛВКОР"].ToString();
               prod_ean13_1.Text= dr_hidden["ШК_ШТУКИ"].ToString();
               prod_ean13_2.Text = dr_hidden["ШК_БЛОКА"].ToString();
               prod_ean13_3.Text = dr_hidden["ШК_КОРОБ"].ToString();
               P_UID.Text = Convert.ToString(UID);

            }
            
            
            



        }


        // Обновляем данные о штрих-кодах продуктов
        private void button11_Click(object sender, EventArgs e)
        {

            try
            {
                funct f = new funct();
                f.function_name = "UPDATE_PRODUCT_INFO";
                f.add_value("ШТВБЛ", prod_kol_bl.Text);
                f.add_value("БЛВКОР", prod_kol_v_kr.Text  );
                f.add_value("ШК_ШТУКИ", prod_ean13_1.Text );
                f.add_value("ШК_БЛОКА", prod_ean13_2.Text );
                f.add_value("ШК_КОРОБ", prod_ean13_3.Text );
                f.add_value("УИД", P_UID.Text );



                Client client = new Client(IPAddress.Parse(this.ServerIP.Text), 20000);
                client.FUNC_Request = f;
                int rsize = client.Receive();
                client.Disconnect();
                if (client.FUNC_Response.Count > 0)
                {
                    funct f2 = client.FUNC_Response[0];
                    if (f2.function_name == "ORDER_POSITION_INFO")
                    {

                    }
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }


        }

        private  string call_spf(funct f)
        {

            Client client;
            string Fault_message="NET ERROR2";
            bool _fault = true;
            try
            {
                client = new Client(IPAddress.Parse(this.ServerIP.Text), 20000);
                client.FUNC_Request = f;
                int rsize = client.Receive();
                trace("Получен пакет длиной=" + Convert.ToString(rsize));
                client.Disconnect();
                _fault = false;
            }
            catch (Exception ex)
            {


                List<string> variant_ip = new List<string>();
                List<long> variant_port = new List<long>();

                variant_ip.Add(this.ServerIP2.Text);
                variant_port.Add( Convert.ToInt32( this._port2.Text));
                variant_ip.Add(this.ServerIP3.Text);
                variant_port.Add(Convert.ToInt32(this._port3.Text));
                variant_ip.Add(this.ServerIP4.Text);
                variant_port.Add(Convert.ToInt32(this._port4.Text));

                bool _exit = false;
                int pos = 0;
               
                while (!_exit)
                {
                    try
                    {
                        this.ServerIP.Text = variant_ip[pos];
                        this._port.Text = variant_port[pos].ToString();
                        client = new Client(IPAddress.Parse(this.ServerIP.Text), Convert.ToInt32( this._port.Text ) );
                        client.FUNC_Request = f;
                        int rsize = client.Receive();
                        trace("Получен пакет длиной=" + Convert.ToString(rsize));
                        client.Disconnect();
                        _exit = true;
                        _fault = false;
                    }
                    catch (Exception ex4)
                    {
                        Fault_message = ex4.Message;
                    }

                    pos++;
                    if (pos > 2) { _exit = true; }
                }


                if (_fault)
                {
                    MessageBox.Show(ex.Message);
                }
                return "net error";
            }

            try
            {
                if (client.FUNC_Response != null)
                    if (client.FUNC_Response.Count > 0)
                    {
                        foreach (funct f5 in client.FUNC_Response)
                        {
                            if (f5.function_name == "CALL_SP_INFO")
                            {
                                return f5.strToIntMap["ok"].ToString();
                            }
                        }
                    }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        
            return "no response";
        }

        private void m_pallet_move_Click(object sender, EventArgs e)
        {

            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_INTERNAL_MOVE3");
            f.add_value("pallet_id", m_pallet_uid.Text );
            f.add_value("cell_to", m_cell.Text );
            f.add_value("count1", str2int( m_count.Text).ToString() );
            f.add_value("user_id1", (current_USER.ID)  );

            Client client;
            try
            {
                client = new Client(IPAddress.Parse(this.ServerIP.Text), 20000);
                client.FUNC_Request = f;
                int rsize = client.Receive();
                trace("Получен пакет длиной=" + Convert.ToString(rsize));
                client.Disconnect();

                if (m_pallet_uid.Text == "NO_PALLET")
                {
                    if (m_cell_history.Count >= 2)
                    {
                        m_cell.Text = m_cell_history[(m_cell_history.Count - 2)];
                        m_cell_history.Clear();
                    }
                }

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
                return;
            }

            try
            {
                if (client.FUNC_Response != null)
                    if (client.FUNC_Response.Count > 0)
                    {
                        foreach (funct f5 in client.FUNC_Response)
                        {
                            if (f5.function_name == "CALL_SP_INFO")
                            {
                                kar_info.Text = f5.strToIntMap["ok"].ToString();
                                if (GIVE_NEXT.Checked)
                                {
                                    string[] sss=kar_info.Text.Split('_');
                                    foreach (string s in sss)
                                    {m_cell.Text=s;
                                    m_pallet_uid.Text ="NEXT";


                                    И_Ячейка.Text = s;
                                    }
                                }

                            }
                        }
                    }
                Beep_ok();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }



        }

        private void button12_Click(object sender, EventArgs e)
        {
            m_pallet_uid.Text = "NO_PALLET";
        }

        private void label2_ParentChanged(object sender, EventArgs e)
        {

        }

        private void button13_Click(object sender, EventArgs e)
        {
            И_Ячейка.Text = И_Ячейка.Text.Replace(" ", "-");
            try
            {
                if (И2_Артикул.Text == "" && И2_Штрихкод.Text == "")
                {
                    MessageBox.Show("Не выбран артикул или штрих-код");
                    return;

                }

                if (Convert.ToInt32(И2_КОЛВО.Text) <= 0)
                {
                    MessageBox.Show("Не указано количество");
                    return;
                }


                if (И_Ячейка.Text == "" || И_Ячейка.Text == "A-")
                {
                    MessageBox.Show(" Не выбрана ячейка ");
                    return;
                }

                /*
                  RRL_INV_CREATE_LINE
( 
    cell1 varchar2 ,
    shk_art varchar2 , 
    articul_part varchar2,
    count1 NUMBER 
    
)  
                    */

                funct f = new funct();
                f.function_name = "CALL_SPF";
                f.add_value("SPF_NAME", "RABAEV.RRL_INV_CREATE_LINE4");
                f.add_value("cell1", И_Ячейка.Text);
                f.add_value("shk_art", И2_Штрихкод.Text);
                f.add_value("articul_part", И2_Артикул.Text);
                f.add_value("count1", И2_КОЛВО.Text);
                f.add_value("UID_DOC", УИД_ДОКУМЕНТА_ПЕРВ_ИНВЕНТАРИЗАЦИИ.Text);
                f.add_value("expiury_date", "" + И2_СГ.Value.Day + "." + И2_СГ.Value.Month + "." + И2_СГ.Value.Year );


                string resp= call_spf(f);
                if (  get_ware_by_cell(resp) != -1  )
                {
                    И_Ячейка.Text = resp;
                    m_cell.Text = resp;

                    И2_Штрихкод.Text = "";
                    И2_Артикул.Text = "";
                    И2_КОЛВО.Text = "0";
                    Beep_ok();
                }
                else {
                    MessageBox.Show("Ошибка: "+resp);
                    Beep_fault();
                }
                


            }catch( Exception ex )
            {
                MessageBox.Show(ex.Message);
            }



        }

        private void button14_Click(object sender, EventArgs e)
        {
            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_NEXT_CELL");
            f.add_value("cell1", И_Ячейка.Text);
             

            string resp = call_spf(f);
            
            
            И_Ячейка.Text = resp;
            m_cell.Text = resp;
        }

        private void plan_Click(object sender, EventArgs e)
        {

        }

        private void NAZAD1_Click(object sender, EventArgs e)
        {
            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_PREVIOUS_CELL");
            f.add_value("cell1", m_cell.Text);
            string resp = call_spf(f);
            И_Ячейка.Text = resp;
            m_cell.Text = resp;
        }

        private void VPERED1_Click(object sender, EventArgs e)
        {


            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_NEXT_CELL");
            f.add_value("cell1", m_cell.Text);
            string resp = call_spf(f);
            И_Ячейка.Text = resp;
            m_cell.Text = resp;

        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void button15_Click(object sender, EventArgs e)
        {

            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_SET_SBORKA_ZONE");
            f.add_value("PALLET_UID1", m_otg_pallet.Text);
            f.add_value("ZONE1", m_otg_place.Text);
            f.add_value("user_id1", this.current_USER.ID );
             call_spf(f);

            Beep_ok();

            /*
             * 
             * RABAEV.RRL_SET_SBORKA_ZONE(
    PALLET_UID1 varchar2  ,
    ZONE1 varchar2 ,
    user_id1 varchar2
             * 

            */

        }




        private void button16_Click(object sender, EventArgs e)
        {
            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_GIVE_KARSH_STAT_INFO");
            f.add_value("user_ud1",  this.current_USER.ID  );
            string resp = call_spf(f);
            m_otg_label.Text = resp;
            

        }

        private void m_inv_otbor_ret_button_Click(object sender, EventArgs e)
        {

            if (get_ware_by_cell(m_inv_otbor_cell.Text) <= 0)
            {
                m_inv_otbor_ret.Text = "Ячейка неверная";
                return;
            }

            if (m_inv_otbor_count.Text == "" || Convert.ToInt32(m_inv_otbor_count.Text) <= 0)
            {
                m_inv_otbor_ret.Text = "Число коробок должно быть указано.";
                return;
            }

            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "RABAEV.RRL_REVIZION_CELL_KOR");
            f.add_value("CELL1", m_inv_otbor_cell.Text.Trim());
            f.add_value("count_kor2", m_inv_otbor_count.Text);
            f.add_value("user_id1", this.current_USER.ID);
            call_spf(f);



            Beep_ok();


        }

        private void _port_TextChanged(object sender, EventArgs e)
        {

        }

        private void m_inv_otbor_ret_button_Click_1(object sender, EventArgs e)
        {


            try
            {

                if (get_ware_by_cell(m_inv_otbor_cell.Text) <= 0)
                {
                    m_inv_otbor_ret.Text = "Ячейка неверная";
                    return;
                }

                if (m_inv_otbor_count.Text == "" || Convert.ToInt32(m_inv_otbor_count.Text) < 0)
                {
                    m_inv_otbor_ret.Text = "Число коробок должно быть указано.";
                    return;
                }

                funct f = new funct();
                f.function_name = "CALL_SPF";
                f.add_value("SPF_NAME", "RABAEV.RRL_REVIZION_CELL_KOR");
                f.add_value("CELL1", m_inv_otbor_cell.Text.Trim());
                f.add_value("count_kor2", m_inv_otbor_count.Text);
                f.add_value("user_id1", this.current_USER.ID);
                m_inv_otbor_ret.Text = call_spf(f);



                Beep_ok();

            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

        }

        private void ОтборЦелымиПаллетами_Click(object sender, EventArgs e)
        {
            if ((fp_PRIHOD.Text.Trim() == "" && fp_weight.Text.Trim() == "") 
                || fp_sborka.Text.Trim() == "" || (fp_cell.Text.Trim() == "" && fp_weight.Text.Trim()=="" ) )
            {
                label11.Text = " Не указаны номера паллет , ячейка или вес ";
                return;
            }


// sborka_full_pall_pick( sb_pall_uid varchar2 , hran_pall_uid varchar2 , cell1 varchar2 ,
            // user_id1 varchar2 )


            funct f = new funct();
            f.function_name = "CALL_SPF";
            f.add_value("SPF_NAME", "compl.sborka_full_pall_pick3");
            f.add_value("sb_pall_uid_coded", fp_sborka.Text.Trim());
            f.add_value("hran_pall_uid1", fp_PRIHOD.Text.Trim());
            f.add_value("cell1", fp_cell.Text.Trim() );
            f.add_value("user_id1", this.current_USER.ID);
            f.add_value("pall_weight", fp_weight.Text.Trim().Replace( ',' , '.' )  );

            
            string r = call_spf(f);


            #region Вывод результата и обработка ошибок.
            switch ( r )
            {
                case "-1":
                    label11.Text = "нет товара на складе в доступной ячейке.";
                break;

                case "-2":
                    label11.Text = "товар размазан по 2 ячейкам ";
                    break;

                case "-3":
                    label11.Text = "нет такого паллета сборки";
                    break;

                case "-4":
                    label11.Text = "нет артикула в заказе ";
                    break;

                case "-5":
                    label11.Text = "количество товара в паллете превышает количество заказ больше чем допустимое округление";
                    break;

                case "-6":
                    label11.Text = "остаток паллета не равен первоначально принятому";
                    break;

                case "-7":
                    label11.Text = "Паллет сборки уже закрыт";
                    break;

                case "-8":
                    label11.Text = "Паллет сборки отсутствует, возможно удален.";
                    break;

                case "-9":
                    label11.Text = "Накладная на приход не закрыта.";
                    break;

                case "-11":
                    label11.Text = "Фактический вес паллета меньше первоначального более чем на 10%";
                    break;

                case "-12":
                    label11.Text = "В паллете нет строк";
                    break;

                case "-13":
                    label11.Text = "В паллете более 1 строки";
                    break;

                case "-10":
                    label11.Text = "неизвестная  ошибка";
                    break;

                default:
                    label11.Text = r;
                    fp_PRIHOD.Text = "" ;
                    fp_sborka.Text = "" ;
                    fp_cell.Text = "";
                    break;
            }

            #endregion

           

        }

 


        


    }


    public class RUSER 
    {
        public string ID="";
        public string Name = "";
        public int PRAVO_INVENTORY_EDIT=0;
        public int PRAVO_CHECK_ORDER=0;
        public int PRAVO_LIGHT_INVENTORY_CHECK=0;
        public int PRAVO_RAZVOZ_ZAYAVOK = 0;
        public int PRAVO_EAN_PRODUCT_CHANGE = 0;
        public int PRAVO_KARSHIK = 0;
        public int ware_id = 0;

        
    }

    public class ASSEMBLE_UNION
    {
        public string Curent_USSCC = "";
        public string Curent_Order = "";
        public string Curent_Place = "";


        public bool by_order()
        {
            //return true;
            //if (Curent_Order != "")
            //    return true;
            return false;
        }

        public bool Is_Empty1()
        {
            if ((Curent_Order == "") && (Curent_USSCC == "") && (Curent_Place == "") )
            { return true; }
            return false;
        }

        public void Make_Empty()
        {
            Curent_Order = "";
            Curent_USSCC = "";
            Curent_Place = "";
        }

        // By_USSCC By_ORDER By_Place
        public string MODE() // By_USSCC By_ORDER By_Place
        { 

            if (Curent_Order != "")
            {
                return "By_ORDER";
            }

            if( Curent_USSCC!="" )
            {
                return "By_USSCC";
            }



            if (Curent_Place != "")
            {
                return "By_Place";
            }


            return "null";
        }

    }



}