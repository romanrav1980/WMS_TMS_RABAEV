using System;
using System.Drawing;
using System.Collections;
using System.Windows.Forms;
using System.Data;
using System.Text;
using CamCoreNet;

namespace CamCoreNetDemo
{
	/// <summary>
	/// Form1에 대한 요약 설명입니다.
	/// </summary>
	public class Form1 : System.Windows.Forms.Form
	{
		private System.Windows.Forms.Button btn_Preview_Start;
		private System.Windows.Forms.Panel panel1;
		private System.Windows.Forms.ComboBox combo_Compress;
		private System.Windows.Forms.Button btn_Capture;
		private System.Windows.Forms.ComboBox combo_Capture_Size;
		private CamCoreNet.CameraControl cameraControl1;
		private System.Windows.Forms.Button btn_Preview_Stop;

		public Form1()
		{
			//
			// Windows Form 디자이너 지원에 필요합니다.
			//
			InitializeComponent();

			cameraControl1.CameraStateChanged += new CameraStateChangedDelegate(OnCameraStateChanged);

			combo_Compress.SelectedIndex = 4;
			combo_Capture_Size.SelectedIndex = 0;

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
			this.btn_Preview_Start = new System.Windows.Forms.Button();
			this.btn_Preview_Stop = new System.Windows.Forms.Button();
			this.panel1 = new System.Windows.Forms.Panel();
			this.btn_Capture = new System.Windows.Forms.Button();
			this.combo_Capture_Size = new System.Windows.Forms.ComboBox();
			this.combo_Compress = new System.Windows.Forms.ComboBox();
			this.cameraControl1 = new CamCoreNet.CameraControl();
			// 
			// btn_Preview_Start
			// 
			this.btn_Preview_Start.Location = new System.Drawing.Point(6, 162);
			this.btn_Preview_Start.Size = new System.Drawing.Size(112, 24);
			this.btn_Preview_Start.Text = "Preview Start";
			this.btn_Preview_Start.Click += new System.EventHandler(this.btn_Preview_Start_Click);
			// 
			// btn_Preview_Stop
			// 
			this.btn_Preview_Stop.Location = new System.Drawing.Point(122, 162);
			this.btn_Preview_Stop.Size = new System.Drawing.Size(112, 24);
			this.btn_Preview_Stop.Text = "Preview Stop";
			this.btn_Preview_Stop.Click += new System.EventHandler(this.btn_Preview_Stop_Click);
			// 
			// panel1
			// 
			this.panel1.BackColor = System.Drawing.Color.WhiteSmoke;
			this.panel1.Controls.Add(this.btn_Capture);
			this.panel1.Controls.Add(this.combo_Capture_Size);
			this.panel1.Controls.Add(this.combo_Compress);
			this.panel1.Location = new System.Drawing.Point(4, 188);
			this.panel1.Size = new System.Drawing.Size(229, 72);
			// 
			// btn_Capture
			// 
			this.btn_Capture.Font = new System.Drawing.Font("굴림", 9.75F, System.Drawing.FontStyle.Regular);
			this.btn_Capture.Location = new System.Drawing.Point(10, 32);
			this.btn_Capture.Size = new System.Drawing.Size(213, 34);
			this.btn_Capture.Text = "Capture";
			this.btn_Capture.Click += new System.EventHandler(this.btn_Capture_Click);
			// 
			// combo_Capture_Size
			// 
			this.combo_Capture_Size.Items.Add("160 X 120");
			this.combo_Capture_Size.Items.Add("320 X 240");
			this.combo_Capture_Size.Items.Add("640 X 480");
			this.combo_Capture_Size.Location = new System.Drawing.Point(116, 7);
			this.combo_Capture_Size.Size = new System.Drawing.Size(106, 20);
			// 
			// combo_Compress
			// 
			this.combo_Compress.Items.Add("Quality 01");
			this.combo_Compress.Items.Add("Quality 02");
			this.combo_Compress.Items.Add("Quality 03");
			this.combo_Compress.Items.Add("Quality 04");
			this.combo_Compress.Items.Add("Quality 05");
			this.combo_Compress.Items.Add("Quality 06");
			this.combo_Compress.Items.Add("Quality 07");
			this.combo_Compress.Location = new System.Drawing.Point(9, 7);
			this.combo_Compress.Size = new System.Drawing.Size(107, 20);
			// 
			// cameraControl1
			// 
			this.cameraControl1.Location = new System.Drawing.Point(19, 16);
			this.cameraControl1.Size = new System.Drawing.Size(202, 118);
			// 
			// Form1
			// 
			this.ClientSize = new System.Drawing.Size(238, 264);
			this.Controls.Add(this.cameraControl1);
			this.Controls.Add(this.panel1);
			this.Controls.Add(this.btn_Preview_Stop);
			this.Controls.Add(this.btn_Preview_Start);
			this.MaximizeBox = false;
			this.MinimizeBox = false;
			this.Text = "CamCoreNetDome";
			this.WindowState = System.Windows.Forms.FormWindowState.Maximized;

		}
		#endregion

		/// <summary>
		/// 해당 응용 프로그램의 주 진입점입니다.
		/// </summary>

		static void Main() 
		{
			Application.Run(new Form1());
		}

		private void btn_Preview_Start_Click(object sender, System.EventArgs e)
		{
			int nRet = cameraControl1.PreviewStart (cameraControl1.Hwnd);
			if (nRet != CameraControl.ERROR_NONE)
			{
				ErrorMsgBox (nRet);
			}
		}

		private void btn_Preview_Stop_Click(object sender, System.EventArgs e)
		{
			cameraControl1.PreviewStop ();
		}

		private void OnCameraStateChanged(int nState)
		{
			MessageBox.Show("OnCameraStateChanged");
		}

		private void btn_Capture_Click(object sender, System.EventArgs e)
		{
			string szFileName = ".\\Capture.jpg";
			int		nCompressLevel = combo_Compress.SelectedIndex;
			int		nCaptureSize = combo_Capture_Size.SelectedIndex;
			int		nRet = CameraControl.ERROR_NONE;

			nRet = cameraControl1.CamCapture (nCompressLevel, nCaptureSize, szFileName);
			if (nRet != CameraControl.ERROR_NONE)
			{
				ErrorMsgBox (nRet);
			}
		}

		private void ErrorMsgBox (int nErrorCode)
		{
			StringBuilder szErrorString = new StringBuilder (256);

			// 에러코드에 대한 에러내용을 얻어온다.
			cameraControl1.GetErrorString(nErrorCode, szErrorString);

			MessageBox.Show(szErrorString.ToString());
		}

	}
}
