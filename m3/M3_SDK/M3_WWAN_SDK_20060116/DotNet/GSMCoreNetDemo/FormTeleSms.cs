using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;

namespace GSMCoreNetDemo
{
	/// <summary>
	/// FormTeleSms에 대한 요약 설명입니다.
	/// </summary>
	public class FormTeleSms : System.Windows.Forms.Form
	{
		private System.Windows.Forms.Button btn_SendDTMF;
		private System.Windows.Forms.TextBox TB_SendDTMF;
		private System.Windows.Forms.Button Btn_EndCall;
		private System.Windows.Forms.TextBox TB_SMS_Data;
		private System.Windows.Forms.Button Btn_SendSMS;
		private System.Windows.Forms.TextBox TB_SMS_PhoneNum;
		private System.Windows.Forms.Button Btn_MakeCall;
		private System.Windows.Forms.TextBox TB_Call_PhoneNum;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.Label label4;
		private System.Windows.Forms.StatusBar st_Result;
		public GSMCoreNet.WWan MCGSM;
	
		public FormTeleSms(GSMCoreNet.WWan GSM)
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
			this.btn_SendDTMF = new System.Windows.Forms.Button();
			this.TB_SendDTMF = new System.Windows.Forms.TextBox();
			this.Btn_EndCall = new System.Windows.Forms.Button();
			this.TB_SMS_Data = new System.Windows.Forms.TextBox();
			this.Btn_SendSMS = new System.Windows.Forms.Button();
			this.TB_SMS_PhoneNum = new System.Windows.Forms.TextBox();
			this.Btn_MakeCall = new System.Windows.Forms.Button();
			this.TB_Call_PhoneNum = new System.Windows.Forms.TextBox();
			this.label1 = new System.Windows.Forms.Label();
			this.label2 = new System.Windows.Forms.Label();
			this.label3 = new System.Windows.Forms.Label();
			this.label4 = new System.Windows.Forms.Label();
			this.st_Result = new System.Windows.Forms.StatusBar();
			// 
			// btn_SendDTMF
			// 
			this.btn_SendDTMF.Location = new System.Drawing.Point(11, 86);
			this.btn_SendDTMF.Size = new System.Drawing.Size(221, 21);
			this.btn_SendDTMF.Text = "Send DTMF";
			this.btn_SendDTMF.Click += new System.EventHandler(this.btn_SendDTMF_Click);
			// 
			// TB_SendDTMF
			// 
			this.TB_SendDTMF.Location = new System.Drawing.Point(113, 62);
			this.TB_SendDTMF.Size = new System.Drawing.Size(118, 21);
			this.TB_SendDTMF.Text = "";
			// 
			// Btn_EndCall
			// 
			this.Btn_EndCall.Location = new System.Drawing.Point(121, 34);
			this.Btn_EndCall.Size = new System.Drawing.Size(105, 21);
			this.Btn_EndCall.Text = "End Call";
			this.Btn_EndCall.Click += new System.EventHandler(this.Btn_EndCall_Click);
			// 
			// TB_SMS_Data
			// 
			this.TB_SMS_Data.Location = new System.Drawing.Point(10, 160);
			this.TB_SMS_Data.Multiline = true;
			this.TB_SMS_Data.Size = new System.Drawing.Size(221, 56);
			this.TB_SMS_Data.Text = "";
			// 
			// Btn_SendSMS
			// 
			this.Btn_SendSMS.Location = new System.Drawing.Point(113, 221);
			this.Btn_SendSMS.Size = new System.Drawing.Size(118, 20);
			this.Btn_SendSMS.Text = "Send SMS";
			this.Btn_SendSMS.Click += new System.EventHandler(this.Btn_SendSMS_Click);
			// 
			// TB_SMS_PhoneNum
			// 
			this.TB_SMS_PhoneNum.Location = new System.Drawing.Point(113, 118);
			this.TB_SMS_PhoneNum.Size = new System.Drawing.Size(118, 21);
			this.TB_SMS_PhoneNum.Text = "";
			// 
			// Btn_MakeCall
			// 
			this.Btn_MakeCall.Location = new System.Drawing.Point(10, 34);
			this.Btn_MakeCall.Size = new System.Drawing.Size(105, 21);
			this.Btn_MakeCall.Text = "Make Call";
			this.Btn_MakeCall.Click += new System.EventHandler(this.Btn_MakeCall_Click);
			// 
			// TB_Call_PhoneNum
			// 
			this.TB_Call_PhoneNum.Location = new System.Drawing.Point(113, 8);
			this.TB_Call_PhoneNum.Size = new System.Drawing.Size(118, 21);
			this.TB_Call_PhoneNum.Text = "";
			// 
			// label1
			// 
			this.label1.Location = new System.Drawing.Point(6, 13);
			this.label1.Size = new System.Drawing.Size(100, 17);
			this.label1.Text = "Phone Number";
			// 
			// label2
			// 
			this.label2.Location = new System.Drawing.Point(10, 68);
			this.label2.Size = new System.Drawing.Size(100, 12);
			this.label2.Text = "DTMF String";
			// 
			// label3
			// 
			this.label3.Location = new System.Drawing.Point(10, 124);
			this.label3.Size = new System.Drawing.Size(100, 17);
			this.label3.Text = "Phone Number";
			// 
			// label4
			// 
			this.label4.Location = new System.Drawing.Point(11, 144);
			this.label4.Size = new System.Drawing.Size(100, 17);
			this.label4.Text = "SMS Data";
			// 
			// st_Result
			// 
			this.st_Result.Location = new System.Drawing.Point(0, 242);
			this.st_Result.Size = new System.Drawing.Size(238, 22);
			this.st_Result.Text = "Ready";
			// 
			// FormTeleSms
			// 
			this.ClientSize = new System.Drawing.Size(238, 264);
			this.Controls.Add(this.st_Result);
			this.Controls.Add(this.label4);
			this.Controls.Add(this.label3);
			this.Controls.Add(this.label2);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.btn_SendDTMF);
			this.Controls.Add(this.TB_SendDTMF);
			this.Controls.Add(this.Btn_EndCall);
			this.Controls.Add(this.TB_SMS_Data);
			this.Controls.Add(this.Btn_SendSMS);
			this.Controls.Add(this.TB_SMS_PhoneNum);
			this.Controls.Add(this.Btn_MakeCall);
			this.Controls.Add(this.TB_Call_PhoneNum);
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Text = "FormTeleSms";
			this.WindowState = System.Windows.Forms.FormWindowState.Maximized;

		}
		#endregion

		private void Btn_MakeCall_Click(object sender, System.EventArgs e)
		{
			int nRet = MCGSM.MakeCall(TB_Call_PhoneNum.Text);
			if (nRet == 0)
			{
				st_Result.Text = "Success MakeCall";
			}
		}

		private void Btn_EndCall_Click(object sender, System.EventArgs e)
		{
			int nRet = MCGSM.EndCall();
			if (nRet == 0)
			{
				st_Result.Text = "Success EndCall";
			}
		}

		private void Btn_SendSMS_Click(object sender, System.EventArgs e)
		{
			int nRet = 0;

			nRet = MCGSM.SendSMS(TB_SMS_PhoneNum.Text, TB_SMS_Data.Text);
			if (nRet == 0)
			{
				st_Result.Text = "Success SendSMS";
			}	
		}

		private void btn_SendDTMF_Click(object sender, System.EventArgs e)
		{
			int nRet = MCGSM.DTMFSend (TB_SendDTMF.Text);
			if (nRet == 0)
			{
				st_Result.Text = "Success DTMFSend";
			}	
		}
	}
}
