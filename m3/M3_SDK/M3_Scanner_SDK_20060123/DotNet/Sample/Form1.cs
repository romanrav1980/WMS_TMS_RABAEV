using System;
using System.Drawing;
using System.Collections;
using System.Windows.Forms;
using System.Data;
using MCSSLibNet;

namespace MCSSTestNet
{
	/// <summary>
	/// Form1에 대한 요약 설명입니다.
	/// </summary>
	public class Form1 : System.Windows.Forms.Form
	{
		private System.Windows.Forms.TabControl tabControl1;
		private System.Windows.Forms.TabPage ReadPage;
		private System.Windows.Forms.TabPage OptionPage;
		private System.Windows.Forms.TabPage SymbologyPage;
		private System.Windows.Forms.TabPage PDF417Page;
		private System.Windows.Forms.ColumnHeader BarType;
		private System.Windows.Forms.ColumnHeader BarData;
		private System.Windows.Forms.CheckBox cbErrorCheck;
		private System.Windows.Forms.CheckBox cbReturnCheck;
		private System.Windows.Forms.CheckBox cbHighFilter;
		private System.Windows.Forms.CheckBox cbWideScan;
		private System.Windows.Forms.NumericUpDown nupSecurity;
		private System.Windows.Forms.NumericUpDown nupMinBarLen;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.ListView lvBarCode;
		private System.Windows.Forms.Button btnRead;
		private System.Windows.Forms.Button btnCancel;
		private System.Windows.Forms.Button btnNewForm;
		private System.Windows.Forms.CheckBox cbUPCA;
		private System.Windows.Forms.CheckBox cbUPCE;
		private System.Windows.Forms.CheckBox cbPDF417;
		private System.Windows.Forms.CheckBox cbUCCEAN_128;
		private System.Windows.Forms.CheckBox cbCODE_I25;
		private System.Windows.Forms.CheckBox cbEAN_8;
		private System.Windows.Forms.CheckBox cbCODE_35;
		private System.Windows.Forms.CheckBox cbCODE_93;
		private System.Windows.Forms.CheckBox cbCODE_128;
		private System.Windows.Forms.CheckBox cbCODE_39;
		private System.Windows.Forms.CheckBox cbEAN_13;
		private System.Windows.Forms.CheckBox cbCODA_BAR;
		private System.Windows.Forms.CheckBox cbUPCE_ADDON;
		private System.Windows.Forms.CheckBox cbEAN_13_ADDON;
		private System.Windows.Forms.CheckBox cbEAN_8_ADDON;
		private System.Windows.Forms.CheckBox cbUPCA_ADDON;
		private System.Windows.Forms.CheckBox cbISBN;
		private System.Windows.Forms.Button btnConfirmSy;
		private System.Windows.Forms.Button btnConfirmOp;
		private System.Windows.Forms.Label label4;
		private System.Windows.Forms.Label label5;
		private System.Windows.Forms.Label label6;
		private System.Windows.Forms.Label label7;
		private System.Windows.Forms.NumericUpDown nupQuality;
		private System.Windows.Forms.NumericUpDown nupTilt;
		private System.Windows.Forms.Button btnConfirmpd;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.NumericUpDown nupTimeOut;
		private MCSSLibNet.ScannerControl ScanCtrl;

		bool bDownFlag = true;

		public Form1()
		{
			//
			// Windows Form 디자이너 지원에 필요합니다.
			//
			InitializeComponent();

			//
			// TODO: InitializeComponent를 호출한 다음 생성자 코드를 추가합니다.
			//
			ScanCtrl = new ScannerControl();
			ScanCtrl.ScannerDataEvent += new ScannerDataDelegate(OnScanData);
			this.Activated +=new EventHandler(Form1_Activated);


			tabControl1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
			tabControl1.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);
			ReadPage.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
			ReadPage.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);
			lvBarCode.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
			lvBarCode.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);	
			btnRead.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
			btnRead.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);	
			btnCancel.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
			btnCancel.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);

		}
		/// <summary>
		/// 사용 중인 모든 리소스를 정리합니다.
		/// </summary>
		protected override void Dispose( bool disposing )
		{
			base.Dispose( disposing );
		}
		#region Windows Form 디자이너에서 생성한 코드
		/// <summary>
		/// 디자이너 지원에 필요한 메서드입니다.
		/// 이 메서드의 내용을 코드 편집기로 수정하지 마십시오.
		/// </summary>
		private void InitializeComponent()
		{
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.ReadPage = new System.Windows.Forms.TabPage();
            this.btnNewForm = new System.Windows.Forms.Button();
            this.btnRead = new System.Windows.Forms.Button();
            this.lvBarCode = new System.Windows.Forms.ListView();
            this.BarType = new System.Windows.Forms.ColumnHeader();
            this.BarData = new System.Windows.Forms.ColumnHeader();
            this.btnCancel = new System.Windows.Forms.Button();
            this.OptionPage = new System.Windows.Forms.TabPage();
            this.btnConfirmOp = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.nupSecurity = new System.Windows.Forms.NumericUpDown();
            this.cbErrorCheck = new System.Windows.Forms.CheckBox();
            this.cbReturnCheck = new System.Windows.Forms.CheckBox();
            this.cbHighFilter = new System.Windows.Forms.CheckBox();
            this.cbWideScan = new System.Windows.Forms.CheckBox();
            this.nupTimeOut = new System.Windows.Forms.NumericUpDown();
            this.nupMinBarLen = new System.Windows.Forms.NumericUpDown();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.SymbologyPage = new System.Windows.Forms.TabPage();
            this.btnConfirmSy = new System.Windows.Forms.Button();
            this.cbUPCA = new System.Windows.Forms.CheckBox();
            this.cbUPCE = new System.Windows.Forms.CheckBox();
            this.cbPDF417 = new System.Windows.Forms.CheckBox();
            this.cbUCCEAN_128 = new System.Windows.Forms.CheckBox();
            this.cbCODE_I25 = new System.Windows.Forms.CheckBox();
            this.cbEAN_8 = new System.Windows.Forms.CheckBox();
            this.cbCODE_35 = new System.Windows.Forms.CheckBox();
            this.cbCODE_93 = new System.Windows.Forms.CheckBox();
            this.cbCODE_128 = new System.Windows.Forms.CheckBox();
            this.cbCODE_39 = new System.Windows.Forms.CheckBox();
            this.cbEAN_13 = new System.Windows.Forms.CheckBox();
            this.cbCODA_BAR = new System.Windows.Forms.CheckBox();
            this.cbUPCE_ADDON = new System.Windows.Forms.CheckBox();
            this.cbEAN_13_ADDON = new System.Windows.Forms.CheckBox();
            this.cbEAN_8_ADDON = new System.Windows.Forms.CheckBox();
            this.cbUPCA_ADDON = new System.Windows.Forms.CheckBox();
            this.cbISBN = new System.Windows.Forms.CheckBox();
            this.PDF417Page = new System.Windows.Forms.TabPage();
            this.btnConfirmpd = new System.Windows.Forms.Button();
            this.nupQuality = new System.Windows.Forms.NumericUpDown();
            this.label7 = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.nupTilt = new System.Windows.Forms.NumericUpDown();
            this.tabControl1.SuspendLayout();
            this.ReadPage.SuspendLayout();
            this.OptionPage.SuspendLayout();
            this.SymbologyPage.SuspendLayout();
            this.PDF417Page.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.ReadPage);
            this.tabControl1.Controls.Add(this.OptionPage);
            this.tabControl1.Controls.Add(this.SymbologyPage);
            this.tabControl1.Controls.Add(this.PDF417Page);
            this.tabControl1.Location = new System.Drawing.Point(0, 0);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(240, 279);
            this.tabControl1.TabIndex = 0;
            this.tabControl1.SelectedIndexChanged += new System.EventHandler(this.tabControl1_SelectedIndexChanged);
            // 
            // ReadPage
            // 
            this.ReadPage.Controls.Add(this.btnNewForm);
            this.ReadPage.Controls.Add(this.btnRead);
            this.ReadPage.Controls.Add(this.lvBarCode);
            this.ReadPage.Controls.Add(this.btnCancel);
            this.ReadPage.Location = new System.Drawing.Point(4, 25);
            this.ReadPage.Name = "ReadPage";
            this.ReadPage.Size = new System.Drawing.Size(232, 250);
            this.ReadPage.Text = "ReadTest";
            // 
            // btnNewForm
            // 
            this.btnNewForm.Location = new System.Drawing.Point(64, 208);
            this.btnNewForm.Name = "btnNewForm";
            this.btnNewForm.Size = new System.Drawing.Size(104, 32);
            this.btnNewForm.TabIndex = 0;
            this.btnNewForm.Text = "NewForm";
            this.btnNewForm.Click += new System.EventHandler(this.btnNewForm_Click);
            // 
            // btnRead
            // 
            this.btnRead.Location = new System.Drawing.Point(8, 168);
            this.btnRead.Name = "btnRead";
            this.btnRead.Size = new System.Drawing.Size(80, 32);
            this.btnRead.TabIndex = 1;
            this.btnRead.Text = "READ";
            this.btnRead.Click += new System.EventHandler(this.btnRead_Click);
            // 
            // lvBarCode
            // 
            this.lvBarCode.Columns.Add(this.BarType);
            this.lvBarCode.Columns.Add(this.BarData);
            this.lvBarCode.FullRowSelect = true;
            this.lvBarCode.Location = new System.Drawing.Point(0, 16);
            this.lvBarCode.Name = "lvBarCode";
            this.lvBarCode.Size = new System.Drawing.Size(232, 144);
            this.lvBarCode.TabIndex = 2;
            this.lvBarCode.View = System.Windows.Forms.View.Details;
            // 
            // BarType
            // 
            this.BarType.Text = "TYPE";
            this.BarType.Width = 60;
            // 
            // BarData
            // 
            this.BarData.Text = "DATA";
            this.BarData.Width = 160;
            // 
            // btnCancel
            // 
            this.btnCancel.Location = new System.Drawing.Point(144, 168);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(80, 32);
            this.btnCancel.TabIndex = 3;
            this.btnCancel.Text = "CANCEL";
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);
            // 
            // OptionPage
            // 
            this.OptionPage.Controls.Add(this.btnConfirmOp);
            this.OptionPage.Controls.Add(this.label1);
            this.OptionPage.Controls.Add(this.nupSecurity);
            this.OptionPage.Controls.Add(this.cbErrorCheck);
            this.OptionPage.Controls.Add(this.cbReturnCheck);
            this.OptionPage.Controls.Add(this.cbHighFilter);
            this.OptionPage.Controls.Add(this.cbWideScan);
            this.OptionPage.Controls.Add(this.nupTimeOut);
            this.OptionPage.Controls.Add(this.nupMinBarLen);
            this.OptionPage.Controls.Add(this.label2);
            this.OptionPage.Controls.Add(this.label3);
            this.OptionPage.Location = new System.Drawing.Point(4, 25);
            this.OptionPage.Name = "OptionPage";
            this.OptionPage.Size = new System.Drawing.Size(232, 250);
            this.OptionPage.Text = "Option";
            // 
            // btnConfirmOp
            // 
            this.btnConfirmOp.Location = new System.Drawing.Point(120, 200);
            this.btnConfirmOp.Name = "btnConfirmOp";
            this.btnConfirmOp.Size = new System.Drawing.Size(96, 40);
            this.btnConfirmOp.TabIndex = 0;
            this.btnConfirmOp.Text = "Confirm";
            this.btnConfirmOp.Click += new System.EventHandler(this.btnConfirmOp_Click);
            // 
            // label1
            // 
            this.label1.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.label1.Location = new System.Drawing.Point(80, 16);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(88, 20);
            this.label1.Text = "Security";
            this.label1.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // nupSecurity
            // 
            this.nupSecurity.Location = new System.Drawing.Point(176, 16);
            this.nupSecurity.Maximum = new decimal(new int[] {
            5,
            0,
            0,
            0});
            this.nupSecurity.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.nupSecurity.Name = "nupSecurity";
            this.nupSecurity.Size = new System.Drawing.Size(48, 24);
            this.nupSecurity.TabIndex = 2;
            this.nupSecurity.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            // 
            // cbErrorCheck
            // 
            this.cbErrorCheck.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbErrorCheck.Location = new System.Drawing.Point(8, 40);
            this.cbErrorCheck.Name = "cbErrorCheck";
            this.cbErrorCheck.Size = new System.Drawing.Size(72, 20);
            this.cbErrorCheck.TabIndex = 3;
            this.cbErrorCheck.Text = "ErrorCheck";
            // 
            // cbReturnCheck
            // 
            this.cbReturnCheck.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbReturnCheck.Location = new System.Drawing.Point(8, 64);
            this.cbReturnCheck.Name = "cbReturnCheck";
            this.cbReturnCheck.Size = new System.Drawing.Size(72, 20);
            this.cbReturnCheck.TabIndex = 4;
            this.cbReturnCheck.Text = "checkDigit";
            // 
            // cbHighFilter
            // 
            this.cbHighFilter.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbHighFilter.Location = new System.Drawing.Point(8, 88);
            this.cbHighFilter.Name = "cbHighFilter";
            this.cbHighFilter.Size = new System.Drawing.Size(72, 20);
            this.cbHighFilter.TabIndex = 5;
            this.cbHighFilter.Text = "HighFilter";
            // 
            // cbWideScan
            // 
            this.cbWideScan.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbWideScan.Location = new System.Drawing.Point(8, 16);
            this.cbWideScan.Name = "cbWideScan";
            this.cbWideScan.Size = new System.Drawing.Size(72, 16);
            this.cbWideScan.TabIndex = 6;
            this.cbWideScan.Text = "WideScan";
            // 
            // nupTimeOut
            // 
            this.nupTimeOut.Location = new System.Drawing.Point(176, 52);
            this.nupTimeOut.Name = "nupTimeOut";
            this.nupTimeOut.Size = new System.Drawing.Size(48, 24);
            this.nupTimeOut.TabIndex = 7;
            // 
            // nupMinBarLen
            // 
            this.nupMinBarLen.Location = new System.Drawing.Point(176, 88);
            this.nupMinBarLen.Name = "nupMinBarLen";
            this.nupMinBarLen.Size = new System.Drawing.Size(48, 24);
            this.nupMinBarLen.TabIndex = 8;
            this.nupMinBarLen.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            // 
            // label2
            // 
            this.label2.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.label2.Location = new System.Drawing.Point(104, 52);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(64, 20);
            this.label2.Text = "TimeOut";
            this.label2.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // label3
            // 
            this.label3.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.label3.Location = new System.Drawing.Point(80, 89);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(88, 16);
            this.label3.Text = "Min.BarLength";
            this.label3.TextAlign = System.Drawing.ContentAlignment.TopRight;
            // 
            // SymbologyPage
            // 
            this.SymbologyPage.Controls.Add(this.btnConfirmSy);
            this.SymbologyPage.Controls.Add(this.cbUPCA);
            this.SymbologyPage.Controls.Add(this.cbUPCE);
            this.SymbologyPage.Controls.Add(this.cbPDF417);
            this.SymbologyPage.Controls.Add(this.cbUCCEAN_128);
            this.SymbologyPage.Controls.Add(this.cbCODE_I25);
            this.SymbologyPage.Controls.Add(this.cbEAN_8);
            this.SymbologyPage.Controls.Add(this.cbCODE_35);
            this.SymbologyPage.Controls.Add(this.cbCODE_93);
            this.SymbologyPage.Controls.Add(this.cbCODE_128);
            this.SymbologyPage.Controls.Add(this.cbCODE_39);
            this.SymbologyPage.Controls.Add(this.cbEAN_13);
            this.SymbologyPage.Controls.Add(this.cbCODA_BAR);
            this.SymbologyPage.Controls.Add(this.cbUPCE_ADDON);
            this.SymbologyPage.Controls.Add(this.cbEAN_13_ADDON);
            this.SymbologyPage.Controls.Add(this.cbEAN_8_ADDON);
            this.SymbologyPage.Controls.Add(this.cbUPCA_ADDON);
            this.SymbologyPage.Controls.Add(this.cbISBN);
            this.SymbologyPage.Location = new System.Drawing.Point(4, 25);
            this.SymbologyPage.Name = "SymbologyPage";
            this.SymbologyPage.Size = new System.Drawing.Size(232, 250);
            this.SymbologyPage.Text = "Symbology";
            // 
            // btnConfirmSy
            // 
            this.btnConfirmSy.Location = new System.Drawing.Point(120, 200);
            this.btnConfirmSy.Name = "btnConfirmSy";
            this.btnConfirmSy.Size = new System.Drawing.Size(96, 40);
            this.btnConfirmSy.TabIndex = 0;
            this.btnConfirmSy.Text = "Confirm";
            this.btnConfirmSy.Click += new System.EventHandler(this.btnConfirmSy_Click);
            // 
            // cbUPCA
            // 
            this.cbUPCA.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbUPCA.Location = new System.Drawing.Point(8, 125);
            this.cbUPCA.Name = "cbUPCA";
            this.cbUPCA.Size = new System.Drawing.Size(96, 16);
            this.cbUPCA.TabIndex = 1;
            this.cbUPCA.Text = "UPCA";
            // 
            // cbUPCE
            // 
            this.cbUPCE.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbUPCE.Location = new System.Drawing.Point(129, 125);
            this.cbUPCE.Name = "cbUPCE";
            this.cbUPCE.Size = new System.Drawing.Size(96, 16);
            this.cbUPCE.TabIndex = 2;
            this.cbUPCE.Text = "UPCE";
            // 
            // cbPDF417
            // 
            this.cbPDF417.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbPDF417.Location = new System.Drawing.Point(8, 100);
            this.cbPDF417.Name = "cbPDF417";
            this.cbPDF417.Size = new System.Drawing.Size(96, 16);
            this.cbPDF417.TabIndex = 3;
            this.cbPDF417.Text = "PDF417";
            // 
            // cbUCCEAN_128
            // 
            this.cbUCCEAN_128.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbUCCEAN_128.Location = new System.Drawing.Point(129, 100);
            this.cbUCCEAN_128.Name = "cbUCCEAN_128";
            this.cbUCCEAN_128.Size = new System.Drawing.Size(96, 16);
            this.cbUCCEAN_128.TabIndex = 4;
            this.cbUCCEAN_128.Text = "UCCEAN_128";
            // 
            // cbCODE_I25
            // 
            this.cbCODE_I25.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODE_I25.Location = new System.Drawing.Point(8, 77);
            this.cbCODE_I25.Name = "cbCODE_I25";
            this.cbCODE_I25.Size = new System.Drawing.Size(96, 16);
            this.cbCODE_I25.TabIndex = 5;
            this.cbCODE_I25.Text = "Inter 2of5";
            // 
            // cbEAN_8
            // 
            this.cbEAN_8.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbEAN_8.Location = new System.Drawing.Point(129, 9);
            this.cbEAN_8.Name = "cbEAN_8";
            this.cbEAN_8.Size = new System.Drawing.Size(96, 16);
            this.cbEAN_8.TabIndex = 6;
            this.cbEAN_8.Text = "EAN_8";
            // 
            // cbCODE_35
            // 
            this.cbCODE_35.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODE_35.Location = new System.Drawing.Point(8, 57);
            this.cbCODE_35.Name = "cbCODE_35";
            this.cbCODE_35.Size = new System.Drawing.Size(96, 16);
            this.cbCODE_35.TabIndex = 7;
            this.cbCODE_35.Text = "3 of 5";
            // 
            // cbCODE_93
            // 
            this.cbCODE_93.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODE_93.Location = new System.Drawing.Point(129, 57);
            this.cbCODE_93.Name = "cbCODE_93";
            this.cbCODE_93.Size = new System.Drawing.Size(96, 16);
            this.cbCODE_93.TabIndex = 8;
            this.cbCODE_93.Text = "CODE_93";
            // 
            // cbCODE_128
            // 
            this.cbCODE_128.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODE_128.Location = new System.Drawing.Point(8, 33);
            this.cbCODE_128.Name = "cbCODE_128";
            this.cbCODE_128.Size = new System.Drawing.Size(96, 16);
            this.cbCODE_128.TabIndex = 9;
            this.cbCODE_128.Text = "CODE_128";
            // 
            // cbCODE_39
            // 
            this.cbCODE_39.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODE_39.Location = new System.Drawing.Point(129, 33);
            this.cbCODE_39.Name = "cbCODE_39";
            this.cbCODE_39.Size = new System.Drawing.Size(96, 16);
            this.cbCODE_39.TabIndex = 10;
            this.cbCODE_39.Text = "CODE_39";
            // 
            // cbEAN_13
            // 
            this.cbEAN_13.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbEAN_13.Location = new System.Drawing.Point(8, 9);
            this.cbEAN_13.Name = "cbEAN_13";
            this.cbEAN_13.Size = new System.Drawing.Size(96, 16);
            this.cbEAN_13.TabIndex = 11;
            this.cbEAN_13.Text = "EAN_13";
            // 
            // cbCODA_BAR
            // 
            this.cbCODA_BAR.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbCODA_BAR.Location = new System.Drawing.Point(130, 77);
            this.cbCODA_BAR.Name = "cbCODA_BAR";
            this.cbCODA_BAR.Size = new System.Drawing.Size(95, 16);
            this.cbCODA_BAR.TabIndex = 12;
            this.cbCODA_BAR.Text = "CODA_BAR";
            // 
            // cbUPCE_ADDON
            // 
            this.cbUPCE_ADDON.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbUPCE_ADDON.Location = new System.Drawing.Point(8, 150);
            this.cbUPCE_ADDON.Name = "cbUPCE_ADDON";
            this.cbUPCE_ADDON.Size = new System.Drawing.Size(96, 16);
            this.cbUPCE_ADDON.TabIndex = 13;
            this.cbUPCE_ADDON.Text = "UPCE_ADDON";
            // 
            // cbEAN_13_ADDON
            // 
            this.cbEAN_13_ADDON.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbEAN_13_ADDON.Location = new System.Drawing.Point(8, 175);
            this.cbEAN_13_ADDON.Name = "cbEAN_13_ADDON";
            this.cbEAN_13_ADDON.Size = new System.Drawing.Size(112, 16);
            this.cbEAN_13_ADDON.TabIndex = 14;
            this.cbEAN_13_ADDON.Text = "EAN_13_ADDON";
            // 
            // cbEAN_8_ADDON
            // 
            this.cbEAN_8_ADDON.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbEAN_8_ADDON.Location = new System.Drawing.Point(129, 175);
            this.cbEAN_8_ADDON.Name = "cbEAN_8_ADDON";
            this.cbEAN_8_ADDON.Size = new System.Drawing.Size(96, 16);
            this.cbEAN_8_ADDON.TabIndex = 15;
            this.cbEAN_8_ADDON.Text = "EAN_8_ADDON ";
            // 
            // cbUPCA_ADDON
            // 
            this.cbUPCA_ADDON.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbUPCA_ADDON.Location = new System.Drawing.Point(129, 150);
            this.cbUPCA_ADDON.Name = "cbUPCA_ADDON";
            this.cbUPCA_ADDON.Size = new System.Drawing.Size(96, 16);
            this.cbUPCA_ADDON.TabIndex = 16;
            this.cbUPCA_ADDON.Text = "UPCA_ADDON";
            // 
            // cbISBN
            // 
            this.cbISBN.Font = new System.Drawing.Font("Tahoma", 8.25F, System.Drawing.FontStyle.Regular);
            this.cbISBN.Location = new System.Drawing.Point(8, 200);
            this.cbISBN.Name = "cbISBN";
            this.cbISBN.Size = new System.Drawing.Size(96, 16);
            this.cbISBN.TabIndex = 17;
            this.cbISBN.Text = "ISBN";
            // 
            // PDF417Page
            // 
            this.PDF417Page.Controls.Add(this.btnConfirmpd);
            this.PDF417Page.Controls.Add(this.nupQuality);
            this.PDF417Page.Controls.Add(this.label7);
            this.PDF417Page.Controls.Add(this.label6);
            this.PDF417Page.Controls.Add(this.label5);
            this.PDF417Page.Controls.Add(this.label4);
            this.PDF417Page.Controls.Add(this.nupTilt);
            this.PDF417Page.Location = new System.Drawing.Point(4, 25);
            this.PDF417Page.Name = "PDF417Page";
            this.PDF417Page.Size = new System.Drawing.Size(232, 250);
            this.PDF417Page.Text = "PDF417";
            // 
            // btnConfirmpd
            // 
            this.btnConfirmpd.Location = new System.Drawing.Point(120, 200);
            this.btnConfirmpd.Name = "btnConfirmpd";
            this.btnConfirmpd.Size = new System.Drawing.Size(96, 40);
            this.btnConfirmpd.TabIndex = 0;
            this.btnConfirmpd.Text = "Confirm";
            this.btnConfirmpd.Click += new System.EventHandler(this.btnConfirmpd_Click);
            // 
            // nupQuality
            // 
            this.nupQuality.Location = new System.Drawing.Point(168, 48);
            this.nupQuality.Maximum = new decimal(new int[] {
            4,
            0,
            0,
            0});
            this.nupQuality.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.nupQuality.Name = "nupQuality";
            this.nupQuality.Size = new System.Drawing.Size(56, 24);
            this.nupQuality.TabIndex = 1;
            this.nupQuality.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            // 
            // label7
            // 
            this.label7.Location = new System.Drawing.Point(8, 104);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(32, 16);
            this.label7.Text = "Tilt";
            // 
            // label6
            // 
            this.label6.Location = new System.Drawing.Point(8, 120);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(152, 56);
            this.label6.Text = "Maximum number of rows a scan line can span. Use a smaller number.";
            // 
            // label5
            // 
            this.label5.Location = new System.Drawing.Point(8, 24);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(100, 14);
            this.label5.Text = "Quality";
            // 
            // label4
            // 
            this.label4.ForeColor = System.Drawing.Color.Black;
            this.label4.Location = new System.Drawing.Point(8, 40);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(152, 48);
            this.label4.Text = "Quality affects how much of error correction capability is used.";
            // 
            // nupTilt
            // 
            this.nupTilt.Location = new System.Drawing.Point(168, 136);
            this.nupTilt.Maximum = new decimal(new int[] {
            6,
            0,
            0,
            0});
            this.nupTilt.Minimum = new decimal(new int[] {
            2,
            0,
            0,
            0});
            this.nupTilt.Name = "nupTilt";
            this.nupTilt.Size = new System.Drawing.Size(56, 24);
            this.nupTilt.TabIndex = 6;
            this.nupTilt.Value = new decimal(new int[] {
            2,
            0,
            0,
            0});
            // 
            // Form1
            // 
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Inherit;
            this.ClientSize = new System.Drawing.Size(638, 455);
            this.Controls.Add(this.tabControl1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
            this.Load += new System.EventHandler(this.Form1_Load);
            this.Closing += new System.ComponentModel.CancelEventHandler(this.Form1_Closing);
            this.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyUp);
            this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form1_KeyDown);
            this.tabControl1.ResumeLayout(false);
            this.ReadPage.ResumeLayout(false);
            this.OptionPage.ResumeLayout(false);
            this.SymbologyPage.ResumeLayout(false);
            this.PDF417Page.ResumeLayout(false);
            this.ResumeLayout(false);

		}
		#endregion

		/// <summary>
		/// 해당 응용 프로그램의 주 진입점입니다.
		/// </summary>

		static void Main() 
		{
			Application.Run(new Form1());
		}
		private void OnScanData(object sender,ScannerDataArgs e)
		{				
			ListViewItem BarcodeItem =new ListViewItem();
			BarcodeItem.Text = e.ScanType;
			BarcodeItem.SubItems.Add(e.ScanData);
	                
			lvBarCode.Items.Add(BarcodeItem);		
		}
		private void Form1_Activated(object sender, EventArgs e)
		{
			//If a form is intended to process scan message, this function should be called 
			//when a form is initialized or activated.
			ScanCtrl.RegisterRecieveForm();   
		}

		private void btnRead_Click(object sender, System.EventArgs e)
		{
            //My
            ScanCtrl.SetDefaultOption();
            //ScanCtrl.UseResumeMsg(true);
            //ScanCtrl.bSyncMode = false;
            //My
			ScanCtrl.ScanRead();		
		}

		private void btnCancel_Click(object sender, System.EventArgs e)
		{
			ScanCtrl.ScanReadCancel();			
		}

		private void btnNewForm_Click(object sender, System.EventArgs e)
		{
			Form2 form2 = new Form2();
			form2.Show();			
		}

		private void Form1_Load(object sender, System.EventArgs e)
		{
			ReadPage.BackColor = System.Drawing.Color.White;
			OptionPage.BackColor = System.Drawing.Color.White;
			SymbologyPage.BackColor = System.Drawing.Color.White;
			PDF417Page.BackColor = System.Drawing.Color.White;

			int nRet;				
			nRet = ScanCtrl.ScanInit();	
			if(nRet != 0)		
				MessageBox.Show("Scanner Init Fail~ \n OTL");
			//If a form is intended to process scan message, this function should be called 
			//when a form is initialized or activated.
			ScanCtrl.RegisterRecieveForm();            
			ScanCtrl.UseDefaultSound(true,"");	
			ScanCtrl.UseResumeMsg(true);

			this.Focus();
            
		}

		private void Form1_Closing(object sender, System.ComponentModel.CancelEventArgs e)
		{
			ScanCtrl.ScanClose();
		}

		private void tabControl1_SelectedIndexChanged(object sender, System.EventArgs e)
		{
			switch(tabControl1.SelectedIndex) 
			{
				case 0:

					
					break;
				case 1:

					MCModuleOption mdo = new MCModuleOption();
					ScanCtrl.GetModuleOption(out mdo);

					nupMinBarLen.Value  = mdo.nMC_MinLen;
					nupSecurity.Value   = mdo.nMC_SecurityLevel; 
					nupTimeOut.Value    = mdo.nMC_TimeOutSec;
            
					MCReadOption rdo = new MCReadOption();
					ScanCtrl.GetReadOption(out rdo);

					cbErrorCheck.Checked  =rdo.bMC_ERRORCHECK;
					cbReturnCheck.Checked =rdo.bMC_RETURNCHECK;
					cbHighFilter.Checked  =rdo.bMC_HIGHFILTERMODE;
					cbWideScan.Checked    =rdo.bMC_WIDESCANANGLE; 
					 
					break;
				case 2:
					MCBarCodeType bct = new MCBarCodeType();
					ScanCtrl.GetBarCodeType(out bct);

					cbEAN_13.Checked		=			bct.bMC_EAN_13;	
					cbCODA_BAR.Checked		=			bct.bMC_CODA_BAR;	
					cbCODE_128.Checked		=			bct.bMC_CODE_128;	
					cbCODE_39.Checked		=			bct.bMC_CODE_39;	
					cbCODE_35.Checked		=			bct.bMC_CODE_35;	
					cbCODE_93.Checked		=			bct.bMC_CODE_93;	
					cbCODE_I25.Checked		=		    bct.bMC_CODE_I25;	
					cbEAN_8.Checked   	   	=		    bct.bMC_EAN_8;	
					cbPDF417.Checked		=			bct.bMC_PDF417;	
					cbUCCEAN_128.Checked	=			bct.bMC_UCCEAN_128;	
					cbUPCA.Checked   	    =			bct.bMC_UPCA;	
					cbUPCE.Checked    		=		    bct.bMC_UPCE;	
					cbUPCE_ADDON.Checked    =     		bct.bMC_UPCE_ADDON;	
					cbUPCA_ADDON.Checked    =           bct.bMC_UPCA_ADDON;	
					cbISBN.Checked          =           bct.bMC_BOOKLAND;		
					cbEAN_13_ADDON.Checked  =           bct.bMC_EAN_13_ADDON;	
					cbEAN_8_ADDON.Checked   =           bct.bMC_EAN_8_ADDON;
					
					break;
				case 3:
					MCPDF417Option pfo = new MCPDF417Option();
					ScanCtrl.GetPDF417Option(out pfo);

					nupQuality.Value = pfo.nMC_Quality;
					nupTilt.Value    = pfo.nMC_Tilt;
                    				
					break;
			}   
                       
			
		}

		private void btnConfirmOp_Click(object sender, System.EventArgs e)
		{  
			MCModuleOption mdo = new MCModuleOption(Convert.ToInt32(nupTimeOut.Value),
				Convert.ToInt32(nupMinBarLen.Value),Convert.ToInt32(nupSecurity.Value));
			ScanCtrl.SetModuleOption(ref mdo);
            
			MCReadOption rdo = new MCReadOption(cbWideScan.Checked,cbReturnCheck.Checked,
				cbErrorCheck.Checked,cbHighFilter.Checked);
			ScanCtrl.SetReadOption(ref rdo);

			tabControl1.SelectedIndex = 0;    
			this.Focus();
		}

		private void btnConfirmSy_Click(object sender, System.EventArgs e)
		{
			MCBarCodeType bct = new MCBarCodeType(cbEAN_13.Checked,cbCODA_BAR.Checked,cbCODE_128.Checked,cbCODE_39.Checked,cbCODE_35.Checked,cbCODE_93.Checked,cbCODE_I25.Checked,cbEAN_8.Checked, cbPDF417.Checked,cbUCCEAN_128.Checked,cbUPCA.Checked,cbUPCE.Checked , false , cbUPCE_ADDON.Checked,cbUPCA_ADDON.Checked,cbISBN.Checked,cbEAN_13_ADDON.Checked,cbEAN_8_ADDON.Checked);
			ScanCtrl.SetBarCodeType(ref bct);

            // 勍�
            MCReadOption rdo = new MCReadOption(true, true ,
            cbErrorCheck.Checked, cbHighFilter.Checked);
            ScanCtrl.SetReadOption(ref rdo);



            // 勍�

			tabControl1.SelectedIndex = 0;
			this.Focus();
		}

		private void btnConfirmpd_Click(object sender, System.EventArgs e)
		{
			MCPDF417Option pfo = new MCPDF417Option(Convert.ToInt32(nupQuality.Value),
				Convert.ToInt32(nupTilt.Value),3);
			ScanCtrl.SetPDF417Option(ref pfo);

			tabControl1.SelectedIndex = 0;
			this.Focus();
		
		}

		private void Form1_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
		{			
			if(bDownFlag)
			{				
				if(e.KeyCode == Keys.F22)
				{
                    ScanCtrl.ScanRead();
				}
                bDownFlag = false;
			}
		
		}

		private void Form1_KeyUp(object sender, System.Windows.Forms.KeyEventArgs e)
		{
			if(!bDownFlag)
			{

				if(e.KeyCode == Keys.F22)
				{
                    ScanCtrl.ScanReadCancel();
				}
				bDownFlag = true;

			}

		}


	}
}
