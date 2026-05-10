using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;
using MCSSLibNet;

namespace MCSSTestNet
{
	/// <summary>
	/// Form2에 대한 요약 설명입니다.
	/// </summary>
	public class Form2 : System.Windows.Forms.Form
	{
		private System.Windows.Forms.TextBox textBox1;
		private System.Windows.Forms.TextBox textBox2;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private MCSSLibNet.ScannerControl ScanCtrl;

		bool bDownFlag = true;
	
		public Form2()
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

			this.Activated +=new EventHandler(Form2_Activated);
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
			this.textBox1 = new System.Windows.Forms.TextBox();
			this.textBox2 = new System.Windows.Forms.TextBox();
			this.label1 = new System.Windows.Forms.Label();
			this.label2 = new System.Windows.Forms.Label();
			// 
			// textBox1
			// 
			this.textBox1.Location = new System.Drawing.Point(48, 40);
			this.textBox1.Size = new System.Drawing.Size(144, 21);
			this.textBox1.Text = "";
			this.textBox1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyDown);
			this.textBox1.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyUp);
			// 
			// textBox2
			// 
			this.textBox2.Location = new System.Drawing.Point(48, 80);
			this.textBox2.Size = new System.Drawing.Size(144, 21);
			this.textBox2.Text = "";
			this.textBox2.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyDown);
			this.textBox2.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyUp);
			// 
			// label1
			// 
			this.label1.Location = new System.Drawing.Point(8, 43);
			this.label1.Size = new System.Drawing.Size(32, 17);
			this.label1.Text = "Type";
			this.label1.TextAlign = System.Drawing.ContentAlignment.TopRight;
			// 
			// label2
			// 
			this.label2.Location = new System.Drawing.Point(9, 83);
			this.label2.Size = new System.Drawing.Size(32, 16);
			this.label2.Text = "Data";
			this.label2.TextAlign = System.Drawing.ContentAlignment.TopRight;
			// 
			// Form2
			// 
			this.ClientSize = new System.Drawing.Size(194, 183);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.textBox1);
			this.Controls.Add(this.textBox2);
			this.Controls.Add(this.label2);
			this.Text = "Form2";
			this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyDown);
			this.Load += new System.EventHandler(this.Form2_Load);
			this.KeyUp += new System.Windows.Forms.KeyEventHandler(this.Form2_KeyUp);

		}
		#endregion

		private void Form2_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e)
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

		private void Form2_KeyUp(object sender, System.Windows.Forms.KeyEventArgs e)
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

		private void Form2_Load(object sender, System.EventArgs e)
		{
			ScanCtrl.RegisterRecieveForm();		
		}
		private void OnScanData(object sender,ScannerDataArgs e)
		{	
			textBox1.Text = e.ScanType;
			textBox2.Text = e.ScanData;            				
		}
		private void Form2_Activated(object sender, EventArgs e)
		{
			// Reset the scan event handler for the Scanning object to the form's delegate. 
			ScanCtrl.RegisterRecieveForm();   
		}
	}
}

