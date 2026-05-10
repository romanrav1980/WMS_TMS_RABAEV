using System;
using System.Drawing;
using System.Collections;
using System.Windows.Forms;
using System.Data;
using System.Text;
using GSMCoreNet;
using Microsoft.WindowsCE.Forms;

namespace GSMCoreNetDemo
{
	/// <summary>
	/// Form1에 대한 요약 설명입니다.
	/// </summary>
	public class Form1 : System.Windows.Forms.Form
	{
		public GSMCoreNet.WWan MCGSM;
		private System.Windows.Forms.Button BtnGetRSSI;
		private System.Windows.Forms.Button BtnGetTime;
		private System.Windows.Forms.Label Label_GSMTime;
		private System.Windows.Forms.Label Label_RSSI;
		private System.Windows.Forms.StatusBar ST_Bar;
		private System.Windows.Forms.Button Btn_Get_IMEI;
		private System.Windows.Forms.Label Label_IMEI;
		private System.Windows.Forms.Button btn_RAS_PB;
		private System.Windows.Forms.Button btn_TeleSms;
		private System.Windows.Forms.Label Label_SIM_State;
		private System.Windows.Forms.Button btn_SIMState;
		private System.Windows.Forms.TextBox tb_SIM_PIN;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.Button btn_Enter_PIN;
		private System.Windows.Forms.Button btn_Enter_PUK;
		private System.Windows.Forms.TextBox tb_SIM_PUK;
		private System.Windows.Forms.TextBox tb_New_PIN;
		Form	parentForm;

		public Form1()
		{
			//
			// Windows Form 디자이너 지원에 필요합니다.
			//
			InitializeComponent();

			this.parentForm = (Form)this.TopLevelControl;
			MCGSM = new WWan();
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
			System.Resources.ResourceManager resources = new System.Resources.ResourceManager(typeof(Form1));
			this.BtnGetRSSI = new System.Windows.Forms.Button();
			this.BtnGetTime = new System.Windows.Forms.Button();
			this.Label_GSMTime = new System.Windows.Forms.Label();
			this.Label_RSSI = new System.Windows.Forms.Label();
			this.ST_Bar = new System.Windows.Forms.StatusBar();
			this.Btn_Get_IMEI = new System.Windows.Forms.Button();
			this.Label_IMEI = new System.Windows.Forms.Label();
			this.btn_RAS_PB = new System.Windows.Forms.Button();
			this.btn_TeleSms = new System.Windows.Forms.Button();
			this.Label_SIM_State = new System.Windows.Forms.Label();
			this.btn_SIMState = new System.Windows.Forms.Button();
			this.tb_SIM_PIN = new System.Windows.Forms.TextBox();
			this.tb_SIM_PUK = new System.Windows.Forms.TextBox();
			this.tb_New_PIN = new System.Windows.Forms.TextBox();
			this.label1 = new System.Windows.Forms.Label();
			this.label2 = new System.Windows.Forms.Label();
			this.label3 = new System.Windows.Forms.Label();
			this.btn_Enter_PIN = new System.Windows.Forms.Button();
			this.btn_Enter_PUK = new System.Windows.Forms.Button();
			// 
			// BtnGetRSSI
			// 
			this.BtnGetRSSI.Location = new System.Drawing.Point(2, 21);
			this.BtnGetRSSI.Size = new System.Drawing.Size(88, 20);
			this.BtnGetRSSI.Text = "GetRSSI";
			this.BtnGetRSSI.Click += new System.EventHandler(this.BtnRSSI_Click);
			// 
			// BtnGetTime
			// 
			this.BtnGetTime.Location = new System.Drawing.Point(2, 1);
			this.BtnGetTime.Size = new System.Drawing.Size(88, 20);
			this.BtnGetTime.Text = "GetGSMTime";
			this.BtnGetTime.Click += new System.EventHandler(this.BtnGetTime_Click);
			// 
			// Label_GSMTime
			// 
			this.Label_GSMTime.Font = new System.Drawing.Font("굴림", 9F, System.Drawing.FontStyle.Regular);
			this.Label_GSMTime.Location = new System.Drawing.Point(93, 6);
			this.Label_GSMTime.Size = new System.Drawing.Size(142, 13);
			this.Label_GSMTime.TextAlign = System.Drawing.ContentAlignment.TopCenter;
			// 
			// Label_RSSI
			// 
			this.Label_RSSI.Font = new System.Drawing.Font("굴림", 9F, System.Drawing.FontStyle.Regular);
			this.Label_RSSI.Location = new System.Drawing.Point(93, 24);
			this.Label_RSSI.Size = new System.Drawing.Size(142, 12);
			this.Label_RSSI.TextAlign = System.Drawing.ContentAlignment.TopCenter;
			// 
			// ST_Bar
			// 
			this.ST_Bar.Location = new System.Drawing.Point(0, 242);
			this.ST_Bar.Size = new System.Drawing.Size(238, 22);
			this.ST_Bar.Text = "Ready";
			// 
			// Btn_Get_IMEI
			// 
			this.Btn_Get_IMEI.Location = new System.Drawing.Point(2, 41);
			this.Btn_Get_IMEI.Size = new System.Drawing.Size(88, 20);
			this.Btn_Get_IMEI.Text = "Get IMEI";
			this.Btn_Get_IMEI.Click += new System.EventHandler(this.Btn_Get_IMEI_Click);
			// 
			// Label_IMEI
			// 
			this.Label_IMEI.Location = new System.Drawing.Point(92, 43);
			this.Label_IMEI.Size = new System.Drawing.Size(155, 16);
			this.Label_IMEI.TextAlign = System.Drawing.ContentAlignment.TopCenter;
			// 
			// btn_RAS_PB
			// 
			this.btn_RAS_PB.Location = new System.Drawing.Point(4, 219);
			this.btn_RAS_PB.Size = new System.Drawing.Size(230, 21);
			this.btn_RAS_PB.Text = "RAS / Phone Book";
			this.btn_RAS_PB.Click += new System.EventHandler(this.btn_RAS_PB_Click);
			// 
			// btn_TeleSms
			// 
			this.btn_TeleSms.Location = new System.Drawing.Point(4, 196);
			this.btn_TeleSms.Size = new System.Drawing.Size(230, 21);
			this.btn_TeleSms.Text = "Telephony / SMS";
			this.btn_TeleSms.Click += new System.EventHandler(this.btn_TeleSms_Click);
			// 
			// Label_SIM_State
			// 
			this.Label_SIM_State.Location = new System.Drawing.Point(97, 67);
			this.Label_SIM_State.Size = new System.Drawing.Size(133, 16);
			this.Label_SIM_State.TextAlign = System.Drawing.ContentAlignment.TopCenter;
			// 
			// btn_SIMState
			// 
			this.btn_SIMState.Location = new System.Drawing.Point(2, 65);
			this.btn_SIMState.Size = new System.Drawing.Size(88, 20);
			this.btn_SIMState.Text = "SIM State";
			this.btn_SIMState.Click += new System.EventHandler(this.btn_SIMState_Click);
			// 
			// tb_SIM_PIN
			// 
			this.tb_SIM_PIN.Location = new System.Drawing.Point(94, 87);
			this.tb_SIM_PIN.MaxLength = 8;
			this.tb_SIM_PIN.Size = new System.Drawing.Size(139, 20);
			this.tb_SIM_PIN.Text = "";
			// 
			// tb_SIM_PUK
			// 
			this.tb_SIM_PUK.Location = new System.Drawing.Point(94, 131);
			this.tb_SIM_PUK.MaxLength = 8;
			this.tb_SIM_PUK.Size = new System.Drawing.Size(139, 20);
			this.tb_SIM_PUK.Text = "";
			// 
			// tb_New_PIN
			// 
			this.tb_New_PIN.Location = new System.Drawing.Point(94, 153);
			this.tb_New_PIN.MaxLength = 8;
			this.tb_New_PIN.Size = new System.Drawing.Size(139, 20);
			this.tb_New_PIN.Text = "";
			// 
			// label1
			// 
			this.label1.Location = new System.Drawing.Point(8, 91);
			this.label1.Size = new System.Drawing.Size(64, 12);
			this.label1.Text = "SIM PIN";
			// 
			// label2
			// 
			this.label2.Location = new System.Drawing.Point(8, 138);
			this.label2.Size = new System.Drawing.Size(64, 12);
			this.label2.Text = "SIM PUK";
			// 
			// label3
			// 
			this.label3.Location = new System.Drawing.Point(8, 160);
			this.label3.Size = new System.Drawing.Size(64, 12);
			this.label3.Text = "New PIN";
			// 
			// btn_Enter_PIN
			// 
			this.btn_Enter_PIN.Location = new System.Drawing.Point(96, 110);
			this.btn_Enter_PIN.Size = new System.Drawing.Size(137, 20);
			this.btn_Enter_PIN.Text = "Enter PIN";
			this.btn_Enter_PIN.Click += new System.EventHandler(this.btn_Enter_PIN_Click);
			// 
			// btn_Enter_PUK
			// 
			this.btn_Enter_PUK.Location = new System.Drawing.Point(97, 175);
			this.btn_Enter_PUK.Size = new System.Drawing.Size(137, 20);
			this.btn_Enter_PUK.Text = "Enter PUK";
			this.btn_Enter_PUK.Click += new System.EventHandler(this.btn_Enter_PUK_Click);
			// 
			// Form1
			// 
			this.ClientSize = new System.Drawing.Size(238, 264);
			this.Controls.Add(this.btn_Enter_PUK);
			this.Controls.Add(this.btn_Enter_PIN);
			this.Controls.Add(this.label3);
			this.Controls.Add(this.label2);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.tb_New_PIN);
			this.Controls.Add(this.tb_SIM_PUK);
			this.Controls.Add(this.tb_SIM_PIN);
			this.Controls.Add(this.Label_SIM_State);
			this.Controls.Add(this.btn_SIMState);
			this.Controls.Add(this.btn_TeleSms);
			this.Controls.Add(this.btn_RAS_PB);
			this.Controls.Add(this.Label_IMEI);
			this.Controls.Add(this.Btn_Get_IMEI);
			this.Controls.Add(this.ST_Bar);
			this.Controls.Add(this.Label_RSSI);
			this.Controls.Add(this.Label_GSMTime);
			this.Controls.Add(this.BtnGetTime);
			this.Controls.Add(this.BtnGetRSSI);
			this.Font = new System.Drawing.Font("굴림", 8.25F, System.Drawing.FontStyle.Regular);
			this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Text = "GSMCore Demo";
			this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
			this.Load += new System.EventHandler(this.Form1_Load);
			this.Closed += new System.EventHandler(this.Form1_Closed);

		}
		#endregion

		/// <summary>
		/// 해당 응용 프로그램의 주 진입점입니다.
		/// </summary>

		static void Main() 
		{
			Application.Run(new Form1());
		}

		private void Form1_Load(object sender, System.EventArgs e)
		{
			MCGSM.Initialize (this.parentForm.Text);
		}

		private void Form1_Closed(object sender, System.EventArgs e)
		{
			MCGSM.UnInitialize ();
		}

		private void BtnGetTime_Click(object sender, System.EventArgs e)
		{
			StringBuilder sOut = new StringBuilder (50);

			MCGSM.GetGSMTime(sOut);

			Label_GSMTime.Text = sOut.ToString();
		}

		private void BtnRSSI_Click(object sender, System.EventArgs e)
		{
			int		nRSSI = 0;
	
			MCGSM.GetRSSI (ref nRSSI);

			Label_RSSI.Text = String.Format("{0}", nRSSI);
		}

		private void Btn_Get_IMEI_Click(object sender, System.EventArgs e)
		{
			int nRet = 0;
			StringBuilder sOut = new StringBuilder (50);

			nRet = MCGSM.GetIMEI (sOut);

			Label_IMEI.Text = sOut.ToString();
		}

		private void btn_SIMState_Click(object sender, System.EventArgs e)
		{
			int nSIMState = 0;

			int nRet = MCGSM.CheckSIMPin (ref nSIMState);
			if (nRet == 0)
			{
				switch (nSIMState) 
				{
					case 0:
						Label_SIM_State.Text = "SIM Ready";
						break;
					case 1:
						Label_SIM_State.Text = "SIM PIN";
						break;
					case 2:
						Label_SIM_State.Text = "SIM PUK";
						break;
					case 3:
						Label_SIM_State.Text = "SIM PUK2";
						break;
					default:
						Label_SIM_State.Text = "....";
						break;
				}
			}		
		}

		private void btn_Enter_PIN_Click(object sender, System.EventArgs e)
		{
			int nRet = MCGSM.EnterSIMPin (tb_SIM_PIN.Text);
			if (nRet == 0)
			{
				ST_Bar.Text = "Success EnterSIMPin";
			}
			else
			{
				ST_Bar.Text = "Error EnterSIMPin";

			}
		
		}

		private void btn_Enter_PUK_Click(object sender, System.EventArgs e)
		{
			int nRet = MCGSM.EnterPUKNumber (tb_SIM_PUK.Text, tb_New_PIN.Text);
			if (nRet == 0)
			{
				ST_Bar.Text = "Success EnterPUKNumber";
			}	
			else
			{
				ST_Bar.Text = "Error EnterPUKNumber";

			}
		}

		private void btn_RAS_PB_Click(object sender, System.EventArgs e)
		{
			FormRasPb dlg;
			dlg = new FormRasPb (MCGSM);
			dlg.ShowDialog ();
		}

		private void btn_TeleSms_Click(object sender, System.EventArgs e)
		{
			FormTeleSms dlg;
			dlg = new FormTeleSms (MCGSM);
			dlg.ShowDialog ();		
		}

	}
}
