namespace DeviceApplication3
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.MainMenu mainMenu1;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.mainMenu1 = new System.Windows.Forms.MainMenu();
            this.button1 = new System.Windows.Forms.Button();
            this.barcode1 = new Barcode.Barcode();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.nakladBindingSource = new System.Windows.Forms.BindingSource(this.components);
            this.dataGrid1 = new System.Windows.Forms.DataGrid();
            this.dataGridTableStyle1 = new System.Windows.Forms.DataGridTableStyle();
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.listBox1 = new System.Windows.Forms.ListBox();
            this.tabControl1.SuspendLayout();
            this.tabPage1.SuspendLayout();
            this.tabPage2.SuspendLayout();
            this.SuspendLayout();
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(151, 240);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(55, 20);
            this.button1.TabIndex = 0;
            this.button1.Text = "button1";
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // barcode1
            // 
            this.barcode1.DecoderParameters.CODABAR = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.CODABARParams.ClsiEditing = false;
            this.barcode1.DecoderParameters.CODABARParams.NotisEditing = false;
            this.barcode1.DecoderParameters.CODABARParams.Redundancy = true;
            this.barcode1.DecoderParameters.CODE128 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.CODE128Params.EAN128 = true;
            this.barcode1.DecoderParameters.CODE128Params.ISBT128 = true;
            this.barcode1.DecoderParameters.CODE128Params.Other128 = true;
            this.barcode1.DecoderParameters.CODE128Params.Redundancy = false;
            this.barcode1.DecoderParameters.CODE39 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.CODE39Params.Code32Prefix = false;
            this.barcode1.DecoderParameters.CODE39Params.Concatenation = false;
            this.barcode1.DecoderParameters.CODE39Params.ConvertToCode32 = false;
            this.barcode1.DecoderParameters.CODE39Params.FullAscii = false;
            this.barcode1.DecoderParameters.CODE39Params.Redundancy = false;
            this.barcode1.DecoderParameters.CODE39Params.ReportCheckDigit = false;
            this.barcode1.DecoderParameters.CODE39Params.VerifyCheckDigit = false;
            this.barcode1.DecoderParameters.CODE93 = Barcode.DisabledEnabled.Undefined;
            this.barcode1.DecoderParameters.CODE93Params.Redundancy = false;
            this.barcode1.DecoderParameters.D2OF5 = Barcode.DisabledEnabled.Disabled;
            this.barcode1.DecoderParameters.D2OF5Params.Redundancy = true;
            this.barcode1.DecoderParameters.EAN13 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.EAN8 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.EAN8Params.ConvertToEAN13 = false;
            this.barcode1.DecoderParameters.I2OF5 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.I2OF5Params.CheckDigitScheme = Symbol.Barcode.I2OF5.CheckDigitSchemes.None;
            this.barcode1.DecoderParameters.I2OF5Params.ConvertToEAN13 = false;
            this.barcode1.DecoderParameters.I2OF5Params.Redundancy = true;
            this.barcode1.DecoderParameters.I2OF5Params.ReportCheckDigit = false;
            this.barcode1.DecoderParameters.KOREAN_3OF5 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.MSI = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.MSIParams.CheckDigitCount = Symbol.Barcode.MSI.CheckDigitCounts.One;
            this.barcode1.DecoderParameters.MSIParams.CheckDigitScheme = Symbol.Barcode.MSI.CheckDigitSchemes.Mod_11_10;
            this.barcode1.DecoderParameters.MSIParams.Redundancy = true;
            this.barcode1.DecoderParameters.MSIParams.ReportCheckDigit = false;
            this.barcode1.DecoderParameters.UPCA = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.UPCAParams.Preamble = Symbol.Barcode.UPC.Preambles.System;
            this.barcode1.DecoderParameters.UPCAParams.ReportCheckDigit = true;
            this.barcode1.DecoderParameters.UPCE0 = Barcode.DisabledEnabled.Enabled;
            this.barcode1.DecoderParameters.UPCE0Params.ConvertToUPCA = false;
            this.barcode1.DecoderParameters.UPCE0Params.Preamble = Symbol.Barcode.UPC.Preambles.None;
            this.barcode1.DecoderParameters.UPCE0Params.ReportCheckDigit = false;
            this.barcode1.DeviceName = null;
            this.barcode1.EnableScanner = false;
            this.barcode1.ReaderParameters.ReaderSpecific.ContactSpecific.InitialScanTime = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ContactSpecific.PulseDelay = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ContactSpecific.QuietZoneRatio = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.AimDuration = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.AimMode = Barcode.AIM_MODE.AIM_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.AimType = Barcode.AIM_TYPE.AIM_TYPE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.BeamTimer = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.DPMMode = Barcode.DPM_MODE.DPM_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.FocusMode = Barcode.FOCUS_MODE.FOCUS_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.FocusPosition = Barcode.FOCUS_POSITION.FOCUS_POSITION_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.IlluminationMode = Barcode.ILLUMINATION_MODE.ILLUMINATION_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.ImageCaptureTimeout = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.ImageCompressionTimeout = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.Inverse1DMode = Barcode.INVERSE1D_MODE.INVERSE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.LinearSecurityLevel = Barcode.LINEAR_SECURITY_LEVEL.SECURITY_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.PicklistMode = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.PicklistModeEx = Barcode.PICKLIST_MODE.PICKLIST_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.PointerTimer = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.PoorQuality1DMode = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFFeedback = Barcode.VIEWFINDER_FEEDBACK.VIEWFINDER_FEEDBACK_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFFeedbackTime = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFMode = Barcode.VIEWFINDER_MODE.VIEWFINDER_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFPosition.Bottom = 0;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFPosition.Left = 0;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFPosition.Right = 0;
            this.barcode1.ReaderParameters.ReaderSpecific.ImagerSpecific.VFPosition.Top = 0;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.AimDuration = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.AimMode = Barcode.AIM_MODE.AIM_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.AimType = Barcode.AIM_TYPE.AIM_TYPE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.BeamTimer = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.BidirRedundancy = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.ControlScanLed = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.DBPMode = Barcode.DBP_MODE.DBP_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.KlasseEinsEnable = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.LinearSecurityLevel = Barcode.LINEAR_SECURITY_LEVEL.SECURITY_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.NarrowBeam = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.PointerTimer = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.RasterHeight = -1;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.RasterMode = Barcode.RASTER_MODE.RASTER_MODE_UNDEFINED;
            this.barcode1.ReaderParameters.ReaderSpecific.LaserSpecific.ScanLedLogicLevel = Barcode.DisabledEnabled.Undefined;
            this.barcode1.ScanParameters.BeepFrequency = 2670;
            this.barcode1.ScanParameters.BeepTime = 200;
            this.barcode1.ScanParameters.CodeIdType = Barcode.CodeIdTypes.None;
            this.barcode1.ScanParameters.LedTime = 3000;
            this.barcode1.ScanParameters.ScanType = Barcode.ScanTypes.Foreground;
            this.barcode1.ScanParameters.WaveFile = "";
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPage1);
            this.tabControl1.Controls.Add(this.tabPage2);
            this.tabControl1.Location = new System.Drawing.Point(4, 5);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(200, 229);
            this.tabControl1.TabIndex = 1;
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.dataGrid1);
            this.tabPage1.Location = new System.Drawing.Point(4, 25);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Size = new System.Drawing.Size(192, 200);
            this.tabPage1.Text = "tabPage1";
            // 
            // nakladBindingSource
            // 
            this.nakladBindingSource.DataSource = typeof(DeviceApplication3.Naklad);
            // 
            // dataGrid1
            // 
            this.dataGrid1.BackgroundColor = System.Drawing.Color.FromArgb(((int)(((byte)(128)))), ((int)(((byte)(128)))), ((int)(((byte)(128)))));
            this.dataGrid1.DataSource = this.nakladBindingSource;
            this.dataGrid1.Location = new System.Drawing.Point(3, 0);
            this.dataGrid1.Name = "dataGrid1";
            this.dataGrid1.Size = new System.Drawing.Size(177, 179);
            this.dataGrid1.TabIndex = 2;
            this.dataGrid1.TableStyles.Add(this.dataGridTableStyle1);
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.listBox1);
            this.tabPage2.Location = new System.Drawing.Point(4, 25);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Size = new System.Drawing.Size(192, 200);
            this.tabPage2.Text = "tabPage2";
            // 
            // listBox1
            // 
            this.listBox1.Location = new System.Drawing.Point(3, 11);
            this.listBox1.Name = "listBox1";
            this.listBox1.Size = new System.Drawing.Size(138, 114);
            this.listBox1.TabIndex = 0;
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(96F, 96F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Dpi;
            this.AutoScroll = true;
            this.ClientSize = new System.Drawing.Size(209, 263);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.button1);
            this.Menu = this.mainMenu1;
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.tabControl1.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            this.tabPage2.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button button1;
        private Barcode.Barcode barcode1;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPage1;
        private System.Windows.Forms.TabPage tabPage2;
        private System.Windows.Forms.DataGrid dataGrid1;
        public System.Windows.Forms.DataGridTableStyle dataGridTableStyle1;
        private System.Windows.Forms.ListBox listBox1;
        private System.Windows.Forms.BindingSource nakladBindingSource;
       
    }
}

