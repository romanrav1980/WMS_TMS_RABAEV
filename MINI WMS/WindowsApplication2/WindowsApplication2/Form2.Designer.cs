namespace WindowsApplication2
{
    partial class Form2
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

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
            this.m_login = new System.Windows.Forms.TextBox();
            this.m_pass = new System.Windows.Forms.MaskedTextBox();
            this.Логин = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.button1 = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.DBNAME = new System.Windows.Forms.ComboBox();
            this.SuspendLayout();
            // 
            // m_login
            // 
            this.m_login.Location = new System.Drawing.Point(139, 12);
            this.m_login.Name = "m_login";
            this.m_login.Size = new System.Drawing.Size(141, 20);
            this.m_login.TabIndex = 0;
            // 
            // m_pass
            // 
            this.m_pass.HidePromptOnLeave = true;
            this.m_pass.Location = new System.Drawing.Point(139, 48);
            this.m_pass.Name = "m_pass";
            this.m_pass.PasswordChar = '#';
            this.m_pass.PromptChar = '*';
            this.m_pass.Size = new System.Drawing.Size(141, 20);
            this.m_pass.TabIndex = 1;
            // 
            // Логин
            // 
            this.Логин.AutoSize = true;
            this.Логин.Location = new System.Drawing.Point(12, 19);
            this.Логин.Name = "Логин";
            this.Логин.Size = new System.Drawing.Size(38, 13);
            this.Логин.TabIndex = 2;
            this.Логин.Text = "Логин";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 55);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(45, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "Пароль";
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(139, 79);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(141, 23);
            this.button1.TabIndex = 4;
            this.button1.Text = "Войти";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(165, 172);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(115, 13);
            this.label1.TabIndex = 5;
            this.label1.Text = "Версия от 08.04.2010";
            // 
            // DBNAME
            // 
            this.DBNAME.FormattingEnabled = true;
            this.DBNAME.Items.AddRange(new object[] {
            "DBWMS",
            "DBWMSSUR",
            "DBWMSUFA"});
            this.DBNAME.Location = new System.Drawing.Point(139, 139);
            this.DBNAME.Name = "DBNAME";
            this.DBNAME.Size = new System.Drawing.Size(141, 21);
            this.DBNAME.TabIndex = 6;
            this.DBNAME.Text = "DBWMS";
            this.DBNAME.TextChanged += new System.EventHandler(this.DBNAME_TextChanged);
            // 
            // Form2
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(293, 194);
            this.Controls.Add(this.DBNAME);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.button1);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.Логин);
            this.Controls.Add(this.m_pass);
            this.Controls.Add(this.m_login);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "Form2";
            this.Text = "Логин \\ Пароль";
            this.Load += new System.EventHandler(this.Form2_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TextBox m_login;
        private System.Windows.Forms.MaskedTextBox m_pass;
        private System.Windows.Forms.Label Логин;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox DBNAME;
    }
}