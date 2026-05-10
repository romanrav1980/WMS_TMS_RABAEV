using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;
using System.Text;

namespace GSMCoreNetDemo
{
	/// <summary>
	/// FormRasPb에 대한 요약 설명입니다.
	/// </summary>
	public class FormRasPb : System.Windows.Forms.Form
	{
		private System.Windows.Forms.Button Btn_RAS_HangUp;
		private System.Windows.Forms.Button Btn_RAS_Connect;
		private System.Windows.Forms.Button Btn_CreateRasEntry;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.Button btn_PB_Write;
		private System.Windows.Forms.Button btn_PB_Rdad;
		private System.Windows.Forms.TextBox tb_Index;
		private System.Windows.Forms.TextBox tb_PhoneNum;
		private System.Windows.Forms.TextBox tb_Name;
		private System.Windows.Forms.Button btn_PB_Delete;
		private System.Windows.Forms.StatusBar st_Result;
		public GSMCoreNet.WWan MCGSM;
	
		public FormRasPb(GSMCoreNet.WWan GSM)
		{
			//
			// Windows Form 디자이너 지원에 필요합니다.
			//
			InitializeComponent();

			MCGSM = GSM;
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
			this.Btn_RAS_HangUp = new System.Windows.Forms.Button();
			this.Btn_RAS_Connect = new System.Windows.Forms.Button();
			this.Btn_CreateRasEntry = new System.Windows.Forms.Button();
			this.tb_Index = new System.Windows.Forms.TextBox();
			this.tb_PhoneNum = new System.Windows.Forms.TextBox();
			this.tb_Name = new System.Windows.Forms.TextBox();
			this.label1 = new System.Windows.Forms.Label();
			this.label2 = new System.Windows.Forms.Label();
			this.label3 = new System.Windows.Forms.Label();
			this.btn_PB_Write = new System.Windows.Forms.Button();
			this.btn_PB_Rdad = new System.Windows.Forms.Button();
			this.btn_PB_Delete = new System.Windows.Forms.Button();
			this.st_Result = new System.Windows.Forms.StatusBar();
			// 
			// Btn_RAS_HangUp
			// 
			this.Btn_RAS_HangUp.Location = new System.Drawing.Point(30, 59);
			this.Btn_RAS_HangUp.Size = new System.Drawing.Size(167, 20);
			this.Btn_RAS_HangUp.Text = "RAS HangUp";
			this.Btn_RAS_HangUp.Click += new System.EventHandler(this.Btn_RAS_HangUp_Click);
			// 
			// Btn_RAS_Connect
			// 
			this.Btn_RAS_Connect.Location = new System.Drawing.Point(30, 38);
			this.Btn_RAS_Connect.Size = new System.Drawing.Size(167, 20);
			this.Btn_RAS_Connect.Text = "RAS Connect";
			this.Btn_RAS_Connect.Click += new System.EventHandler(this.Btn_RAS_Connect_Click);
			// 
			// Btn_CreateRasEntry
			// 
			this.Btn_CreateRasEntry.Location = new System.Drawing.Point(30, 17);
			this.Btn_CreateRasEntry.Size = new System.Drawing.Size(167, 20);
			this.Btn_CreateRasEntry.Text = "Create RAS Entry";
			this.Btn_CreateRasEntry.Click += new System.EventHandler(this.Btn_CreateRasEntry_Click);
			// 
			// tb_Index
			// 
			this.tb_Index.Location = new System.Drawing.Point(118, 100);
			this.tb_Index.Text = "";
			// 
			// tb_PhoneNum
			// 
			this.tb_PhoneNum.Location = new System.Drawing.Point(118, 122);
			this.tb_PhoneNum.Text = "";
			// 
			// tb_Name
			// 
			this.tb_Name.Location = new System.Drawing.Point(118, 145);
			this.tb_Name.Text = "";
			// 
			// label1
			// 
			this.label1.Location = new System.Drawing.Point(17, 104);
			this.label1.Size = new System.Drawing.Size(89, 14);
			this.label1.Text = "Index";
			// 
			// label2
			// 
			this.label2.Location = new System.Drawing.Point(17, 125);
			this.label2.Size = new System.Drawing.Size(97, 14);
			this.label2.Text = "Phone Number";
			// 
			// label3
			// 
			this.label3.Location = new System.Drawing.Point(17, 147);
			this.label3.Size = new System.Drawing.Size(89, 14);
			this.label3.Text = "Name";
			// 
			// btn_PB_Write
			// 
			this.btn_PB_Write.Location = new System.Drawing.Point(19, 170);
			this.btn_PB_Write.Size = new System.Drawing.Size(200, 20);
			this.btn_PB_Write.Text = "Write Phone Book";
			this.btn_PB_Write.Click += new System.EventHandler(this.btn_PB_Write_Click);
			// 
			// btn_PB_Rdad
			// 
			this.btn_PB_Rdad.Location = new System.Drawing.Point(19, 192);
			this.btn_PB_Rdad.Size = new System.Drawing.Size(200, 20);
			this.btn_PB_Rdad.Text = "Read Phone Book";
			this.btn_PB_Rdad.Click += new System.EventHandler(this.btn_PB_Rdad_Click);
			// 
			// btn_PB_Delete
			// 
			this.btn_PB_Delete.Location = new System.Drawing.Point(19, 213);
			this.btn_PB_Delete.Size = new System.Drawing.Size(200, 20);
			this.btn_PB_Delete.Text = "Delete Phone Book";
			this.btn_PB_Delete.Click += new System.EventHandler(this.btn_PB_Delete_Click);
			// 
			// st_Result
			// 
			this.st_Result.Location = new System.Drawing.Point(0, 242);
			this.st_Result.Size = new System.Drawing.Size(238, 22);
			this.st_Result.Text = "Ready";
			this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
			// 
			// FormRasPb
			// 
			this.ClientSize = new System.Drawing.Size(238, 264);
			this.Controls.Add(this.st_Result);
			this.Controls.Add(this.btn_PB_Delete);
			this.Controls.Add(this.btn_PB_Rdad);
			this.Controls.Add(this.btn_PB_Write);
			this.Controls.Add(this.label3);
			this.Controls.Add(this.label2);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.tb_Name);
			this.Controls.Add(this.tb_PhoneNum);
			this.Controls.Add(this.tb_Index);
			this.Controls.Add(this.Btn_RAS_HangUp);
			this.Controls.Add(this.Btn_RAS_Connect);
			this.Controls.Add(this.Btn_CreateRasEntry);
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Text = "FormRasPb";
			this.WindowState = System.Windows.Forms.FormWindowState.Maximized;

		}
		#endregion

		private void Btn_CreateRasEntry_Click(object sender, System.EventArgs e)
		{
			int nRet = 0;

			nRet = MCGSM.CreateRasEntry ("My GPRS", 115200, "*99***1#", "+CGDCONT=1,\"IP\",\"kipa\"",
				"", "", "", "", "", "", "", "" );
			if (nRet == 0)
			{
				st_Result.Text = "Success CreateRasEntry";
			}		
		}

		private void Btn_RAS_Connect_Click(object sender, System.EventArgs e)
		{
			int nRet = 0;

			nRet = MCGSM.DoRASConnect ("My GPRS");
			if (nRet == 0)
			{
				st_Result.Text = "Success DoRASConnect";
			}
		
		}

		private void Btn_RAS_HangUp_Click(object sender, System.EventArgs e)
		{
			int nRet = 0;

			nRet = MCGSM.DoRASHangup ();
			if (nRet == 0)
			{
				st_Result.Text = "Success DoRASHangup";
			}		
		}

		private void btn_PB_Write_Click(object sender, System.EventArgs e)
		{
			int nIndex = Convert.ToInt32(tb_Index.Text);

			int nRet = MCGSM.WritePhoneBookEntry (nIndex, tb_PhoneNum.Text, tb_Name.Text);
			if (nRet == 0)
			{
				st_Result.Text = "Success WritePhoneBookEntry";
			}		
		
		}

		private void btn_PB_Rdad_Click(object sender, System.EventArgs e)
		{
			int nIndex = Convert.ToInt32(tb_Index.Text);
			StringBuilder szPhoneNum = new StringBuilder (50);
			StringBuilder szName = new StringBuilder (50);

			int nRet = MCGSM.ReadPhoneBookEntry (nIndex, szPhoneNum, szName);
			if (nRet == 0)
			{
				tb_PhoneNum.Text = szPhoneNum.ToString ();
				tb_Name.Text = szName.ToString ();

				st_Result.Text = "Success ReadPhoneBookEntry";
			}				
		}

		private void btn_PB_Delete_Click(object sender, System.EventArgs e)
		{
			int nIndex = Convert.ToInt32(tb_Index.Text);

			int nRet = MCGSM.DeletePhoneBookEntry (nIndex);
			if (nRet == 0)
			{
				st_Result.Text = "Success DeletePhoneBookEntry";
			}				
		}
	}
}
