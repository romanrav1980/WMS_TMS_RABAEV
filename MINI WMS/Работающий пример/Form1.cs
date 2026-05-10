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
        private System.Windows.Forms.Button btnConfirmOp;
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
            this.btnRead = new System.Windows.Forms.Button();
            this.lvBarCode = new System.Windows.Forms.ListView();
            this.BarType = new System.Windows.Forms.ColumnHeader();
            this.BarData = new System.Windows.Forms.ColumnHeader();
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
            this.PDF417Page = new System.Windows.Forms.TabPage();
            this.tabControl1.SuspendLayout();
            this.ReadPage.SuspendLayout();
            this.OptionPage.SuspendLayout();
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
            this.tabControl1.Size = new System.Drawing.Size(362, 279);
            this.tabControl1.TabIndex = 0;
            this.tabControl1.SelectedIndexChanged += new System.EventHandler(this.tabControl1_SelectedIndexChanged);
            // 
            // ReadPage
            // 
            this.ReadPage.Controls.Add(this.btnRead);
            this.ReadPage.Controls.Add(this.lvBarCode);
            this.ReadPage.Location = new System.Drawing.Point(4, 25);
            this.ReadPage.Name = "ReadPage";
            this.ReadPage.Size = new System.Drawing.Size(354, 250);
            this.ReadPage.Text = "ReadTest";
            // 
            // btnRead
            // 
            this.btnRead.Location = new System.Drawing.Point(152, 215);
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
            this.lvBarCode.Size = new System.Drawing.Size(232, 147);
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
            this.OptionPage.Size = new System.Drawing.Size(354, 250);
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
            this.nupMinBarLen.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
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
            this.SymbologyPage.Location = new System.Drawing.Point(4, 25);
            this.SymbologyPage.Name = "SymbologyPage";
            this.SymbologyPage.Size = new System.Drawing.Size(354, 250);
            this.SymbologyPage.Text = "Symbology";
            // 
            // PDF417Page
            // 
            this.PDF417Page.Location = new System.Drawing.Point(4, 25);
            this.PDF417Page.Name = "PDF417Page";
            this.PDF417Page.Size = new System.Drawing.Size(354, 250);
            this.PDF417Page.Text = "PDF417";
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
            this.ResumeLayout(false);

		}
		#endregion

		/// <summary>
		/// 해당 응용 프로그램의 주 진입점입니다.
		/// </summary>
        
		static void Main3() 
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
            ScanCtrl.ScanRead();
		}

		private void btnRead_Click(object sender, System.EventArgs e)
		{
			ScanCtrl.ScanRead();		
		}

		private void btnCancel_Click(object sender, System.EventArgs e)
		{
			ScanCtrl.ScanReadCancel();			
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
			MCBarCodeType bct = new MCBarCodeType( true , true , true,true, true , true , 
                true ,true , true , true,true, true , true , true ,true,true,true,true );

			ScanCtrl.SetBarCodeType(ref bct);

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
