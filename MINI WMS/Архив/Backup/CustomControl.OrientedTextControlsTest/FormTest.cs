using System;
using System.Drawing;
using System.Collections;
using System.ComponentModel;
using System.Windows.Forms;
using System.Data;

namespace CustomControl.RotatableControl
{
	/// <summary>
	/// Summary description for Form1.
	/// </summary>
	public class FormTest : System.Windows.Forms.Form
	{
		private System.Windows.Forms.GroupBox groupBox1;
		private System.Windows.Forms.GroupBox groupBox2;
		private System.Windows.Forms.GroupBox groupBox3;
		private System.Windows.Forms.Button btnClose;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel1;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel2;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel3;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel4;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel5;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel6;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel7;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel8;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel9;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel10;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel11;
		private CustomControl.OrientAbleTextControls.OrientedTextLabel orientedTextLabel12;
		/// <summary>
		/// Required designer variable.
		/// </summary>
		private System.ComponentModel.Container components = null;

		public FormTest()
		{
			//
			// Required for Windows Form Designer support
			//
			InitializeComponent();

			//
			// TODO: Add any constructor code after InitializeComponent call
			//
		}

		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		protected override void Dispose( bool disposing )
		{
			if( disposing )
			{
				if (components != null) 
				{
					components.Dispose();
				}
			}
			base.Dispose( disposing );
		}

		#region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		private void InitializeComponent()
		{
			this.groupBox1 = new System.Windows.Forms.GroupBox();
			this.groupBox2 = new System.Windows.Forms.GroupBox();
			this.groupBox3 = new System.Windows.Forms.GroupBox();
			this.btnClose = new System.Windows.Forms.Button();
			this.orientedTextLabel1 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel2 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel3 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel4 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel5 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel6 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel7 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel8 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel9 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel10 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel11 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.orientedTextLabel12 = new CustomControl.OrientAbleTextControls.OrientedTextLabel();
			this.groupBox1.SuspendLayout();
			this.groupBox2.SuspendLayout();
			this.groupBox3.SuspendLayout();
			this.SuspendLayout();
			// 
			// groupBox1
			// 
			this.groupBox1.Controls.Add(this.orientedTextLabel12);
			this.groupBox1.Controls.Add(this.orientedTextLabel11);
			this.groupBox1.Controls.Add(this.orientedTextLabel10);
			this.groupBox1.Controls.Add(this.orientedTextLabel9);
			this.groupBox1.Controls.Add(this.orientedTextLabel8);
			this.groupBox1.Controls.Add(this.orientedTextLabel7);
			this.groupBox1.Location = new System.Drawing.Point(8, 8);
			this.groupBox1.Name = "groupBox1";
			this.groupBox1.Size = new System.Drawing.Size(416, 136);
			this.groupBox1.TabIndex = 6;
			this.groupBox1.TabStop = false;
			this.groupBox1.Text = "Rotate";
			// 
			// groupBox2
			// 
			this.groupBox2.Controls.Add(this.orientedTextLabel6);
			this.groupBox2.Controls.Add(this.orientedTextLabel5);
			this.groupBox2.Controls.Add(this.orientedTextLabel4);
			this.groupBox2.Location = new System.Drawing.Point(8, 152);
			this.groupBox2.Name = "groupBox2";
			this.groupBox2.Size = new System.Drawing.Size(416, 128);
			this.groupBox2.TabIndex = 7;
			this.groupBox2.TabStop = false;
			this.groupBox2.Text = "Arc";
			// 
			// groupBox3
			// 
			this.groupBox3.Controls.Add(this.orientedTextLabel3);
			this.groupBox3.Controls.Add(this.orientedTextLabel2);
			this.groupBox3.Controls.Add(this.orientedTextLabel1);
			this.groupBox3.Location = new System.Drawing.Point(8, 288);
			this.groupBox3.Name = "groupBox3";
			this.groupBox3.Size = new System.Drawing.Size(416, 128);
			this.groupBox3.TabIndex = 8;
			this.groupBox3.TabStop = false;
			this.groupBox3.Text = "Circle";
			// 
			// btnClose
			// 
			this.btnClose.Location = new System.Drawing.Point(348, 427);
			this.btnClose.Name = "btnClose";
			this.btnClose.TabIndex = 9;
			this.btnClose.Text = "Close";
			this.btnClose.Click += new System.EventHandler(this.btnClose_Click);
			// 
			// orientedTextLabel1
			// 
			this.orientedTextLabel1.Location = new System.Drawing.Point(24, 24);
			this.orientedTextLabel1.Name = "orientedTextLabel1";
			this.orientedTextLabel1.RotationAngle = 0;
			this.orientedTextLabel1.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel1.TabIndex = 0;
			this.orientedTextLabel1.Text = "How is this Control?";
			this.orientedTextLabel1.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel1.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Circle;
			// 
			// orientedTextLabel2
			// 
			this.orientedTextLabel2.Location = new System.Drawing.Point(288, 24);
			this.orientedTextLabel2.Name = "orientedTextLabel2";
			this.orientedTextLabel2.RotationAngle = 90;
			this.orientedTextLabel2.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel2.TabIndex = 1;
			this.orientedTextLabel2.Text = "How is this Control?";
			this.orientedTextLabel2.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel2.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Circle;
			// 
			// orientedTextLabel3
			// 
			this.orientedTextLabel3.Location = new System.Drawing.Point(152, 24);
			this.orientedTextLabel3.Name = "orientedTextLabel3";
			this.orientedTextLabel3.RotationAngle = 0;
			this.orientedTextLabel3.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel3.TabIndex = 2;
			this.orientedTextLabel3.Text = "How is this Control? ";
			this.orientedTextLabel3.TextDirection = CustomControl.OrientAbleTextControls.Direction.AntiClockwise;
			this.orientedTextLabel3.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Circle;
			// 
			// orientedTextLabel4
			// 
			this.orientedTextLabel4.Location = new System.Drawing.Point(288, 24);
			this.orientedTextLabel4.Name = "orientedTextLabel4";
			this.orientedTextLabel4.RotationAngle = 90;
			this.orientedTextLabel4.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel4.TabIndex = 0;
			this.orientedTextLabel4.Text = "How is this Control?";
			this.orientedTextLabel4.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel4.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Arc;
			// 
			// orientedTextLabel5
			// 
			this.orientedTextLabel5.Location = new System.Drawing.Point(152, 24);
			this.orientedTextLabel5.Name = "orientedTextLabel5";
			this.orientedTextLabel5.RotationAngle = 0;
			this.orientedTextLabel5.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel5.TabIndex = 1;
			this.orientedTextLabel5.Text = "How is this Control?";
			this.orientedTextLabel5.TextDirection = CustomControl.OrientAbleTextControls.Direction.AntiClockwise;
			this.orientedTextLabel5.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Arc;
			// 
			// orientedTextLabel6
			// 
			this.orientedTextLabel6.Location = new System.Drawing.Point(16, 24);
			this.orientedTextLabel6.Name = "orientedTextLabel6";
			this.orientedTextLabel6.RotationAngle = 0;
			this.orientedTextLabel6.Size = new System.Drawing.Size(105, 96);
			this.orientedTextLabel6.TabIndex = 2;
			this.orientedTextLabel6.Text = "How is this Control?";
			this.orientedTextLabel6.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel6.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Arc;
			// 
			// orientedTextLabel7
			// 
			this.orientedTextLabel7.Location = new System.Drawing.Point(8, 48);
			this.orientedTextLabel7.Name = "orientedTextLabel7";
			this.orientedTextLabel7.RotationAngle = 0;
			this.orientedTextLabel7.Size = new System.Drawing.Size(105, 12);
			this.orientedTextLabel7.TabIndex = 0;
			this.orientedTextLabel7.Text = "How is this Control?";
			this.orientedTextLabel7.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel7.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// orientedTextLabel8
			// 
			this.orientedTextLabel8.Location = new System.Drawing.Point(8, 88);
			this.orientedTextLabel8.Name = "orientedTextLabel8";
			this.orientedTextLabel8.RotationAngle = 180;
			this.orientedTextLabel8.Size = new System.Drawing.Size(104, 12);
			this.orientedTextLabel8.TabIndex = 1;
			this.orientedTextLabel8.Text = "How is this Control?";
			this.orientedTextLabel8.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel8.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// orientedTextLabel9
			// 
			this.orientedTextLabel9.Location = new System.Drawing.Point(124, 24);
			this.orientedTextLabel9.Name = "orientedTextLabel9";
			this.orientedTextLabel9.RotationAngle = 45;
			this.orientedTextLabel9.Size = new System.Drawing.Size(105, 104);
			this.orientedTextLabel9.TabIndex = 2;
			this.orientedTextLabel9.Text = "How is this Control?";
			this.orientedTextLabel9.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel9.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// orientedTextLabel10
			// 
			this.orientedTextLabel10.Location = new System.Drawing.Point(244, 24);
			this.orientedTextLabel10.Name = "orientedTextLabel10";
			this.orientedTextLabel10.RotationAngle = -45;
			this.orientedTextLabel10.Size = new System.Drawing.Size(105, 104);
			this.orientedTextLabel10.TabIndex = 3;
			this.orientedTextLabel10.Text = "How is this Control?";
			this.orientedTextLabel10.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel10.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// orientedTextLabel11
			// 
			this.orientedTextLabel11.Location = new System.Drawing.Point(361, 20);
			this.orientedTextLabel11.Name = "orientedTextLabel11";
			this.orientedTextLabel11.RotationAngle = 90;
			this.orientedTextLabel11.Size = new System.Drawing.Size(16, 104);
			this.orientedTextLabel11.TabIndex = 4;
			this.orientedTextLabel11.Text = "How is this Control?";
			this.orientedTextLabel11.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel11.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// orientedTextLabel12
			// 
			this.orientedTextLabel12.Location = new System.Drawing.Point(391, 18);
			this.orientedTextLabel12.Name = "orientedTextLabel12";
			this.orientedTextLabel12.RotationAngle = -90;
			this.orientedTextLabel12.Size = new System.Drawing.Size(16, 104);
			this.orientedTextLabel12.TabIndex = 5;
			this.orientedTextLabel12.Text = "How is this Control?";
			this.orientedTextLabel12.TextDirection = CustomControl.OrientAbleTextControls.Direction.Clockwise;
			this.orientedTextLabel12.TextOrientation = CustomControl.OrientAbleTextControls.Orientation.Rotate;
			// 
			// FormTest
			// 
			this.AutoScaleBaseSize = new System.Drawing.Size(5, 13);
			this.ClientSize = new System.Drawing.Size(432, 461);
			this.Controls.Add(this.btnClose);
			this.Controls.Add(this.groupBox3);
			this.Controls.Add(this.groupBox2);
			this.Controls.Add(this.groupBox1);
			this.Name = "FormTest";
			this.Text = "Oriented Text Controls Test Form";
			this.groupBox1.ResumeLayout(false);
			this.groupBox2.ResumeLayout(false);
			this.groupBox3.ResumeLayout(false);
			this.ResumeLayout(false);

		}
		#endregion

		/// <summary>
		/// The main entry point for the application.
		/// </summary>
		[STAThread]
		static void Main() 
		{
			Application.Run(new FormTest());
		}

		private void btnClose_Click(object sender, System.EventArgs e)
		{
			Application.Exit();
		}
	}
}
