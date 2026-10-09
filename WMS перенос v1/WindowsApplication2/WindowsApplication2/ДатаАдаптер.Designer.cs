namespace WindowsApplication2
{
    partial class ДатаАдаптер
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
            this.Подгрузить = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // Подгрузить
            // 
            this.Подгрузить.Location = new System.Drawing.Point(12, 12);
            this.Подгрузить.Name = "Подгрузить";
            this.Подгрузить.Size = new System.Drawing.Size(156, 23);
            this.Подгрузить.TabIndex = 0;
            this.Подгрузить.Text = "Подгрузить Данные";
            this.Подгрузить.UseVisualStyleBackColor = true;
            this.Подгрузить.Click += new System.EventHandler(this.Подгрузить_Click);
            // 
            // ДатаАдаптер
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(514, 341);
            this.Controls.Add(this.Подгрузить);
            this.Name = "ДатаАдаптер";
            this.Text = "ДатаАдаптер";
            this.Load += new System.EventHandler(this.ДатаАдаптер_Load);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button Подгрузить;
    }
}