namespace WindowsApplication2
{
    partial class Поставщики
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
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.Поставщики1 = new System.Windows.Forms.TabPage();
            this.ТаблицаПоставщиков = new System.Windows.Forms.DataGridView();
            this.ГруппыПоставщиков = new System.Windows.Forms.TabPage();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.ИНН = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Название = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Группа = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.Поставщики1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.ТаблицаПоставщиков)).BeginInit();
            this.ГруппыПоставщиков.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.SuspendLayout();
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.Location = new System.Drawing.Point(0, 0);
            this.splitContainer1.Name = "splitContainer1";
            this.splitContainer1.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.tabControl1);
            this.splitContainer1.Size = new System.Drawing.Size(886, 541);
            this.splitContainer1.SplitterDistance = 449;
            this.splitContainer1.TabIndex = 0;
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.Поставщики1);
            this.tabControl1.Controls.Add(this.ГруппыПоставщиков);
            this.tabControl1.Location = new System.Drawing.Point(3, 3);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(880, 443);
            this.tabControl1.TabIndex = 1;
            // 
            // Поставщики1
            // 
            this.Поставщики1.Controls.Add(this.ТаблицаПоставщиков);
            this.Поставщики1.Location = new System.Drawing.Point(4, 22);
            this.Поставщики1.Name = "Поставщики1";
            this.Поставщики1.Padding = new System.Windows.Forms.Padding(3);
            this.Поставщики1.Size = new System.Drawing.Size(872, 417);
            this.Поставщики1.TabIndex = 0;
            this.Поставщики1.Text = "Поставщики";
            this.Поставщики1.UseVisualStyleBackColor = true;
            // 
            // ТаблицаПоставщиков
            // 
            this.ТаблицаПоставщиков.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.ТаблицаПоставщиков.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ИНН,
            this.Название,
            this.Группа});
            this.ТаблицаПоставщиков.Dock = System.Windows.Forms.DockStyle.Fill;
            this.ТаблицаПоставщиков.Location = new System.Drawing.Point(3, 3);
            this.ТаблицаПоставщиков.Name = "ТаблицаПоставщиков";
            this.ТаблицаПоставщиков.Size = new System.Drawing.Size(866, 411);
            this.ТаблицаПоставщиков.TabIndex = 0;
            // 
            // ГруппыПоставщиков
            // 
            this.ГруппыПоставщиков.Controls.Add(this.dataGridView1);
            this.ГруппыПоставщиков.Location = new System.Drawing.Point(4, 22);
            this.ГруппыПоставщиков.Name = "ГруппыПоставщиков";
            this.ГруппыПоставщиков.Padding = new System.Windows.Forms.Padding(3);
            this.ГруппыПоставщиков.Size = new System.Drawing.Size(872, 417);
            this.ГруппыПоставщиков.TabIndex = 1;
            this.ГруппыПоставщиков.Text = "ГруппыПоставщиков";
            this.ГруппыПоставщиков.UseVisualStyleBackColor = true;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Location = new System.Drawing.Point(3, 3);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(240, 315);
            this.dataGridView1.TabIndex = 0;
            // 
            // ИНН
            // 
            this.ИНН.HeaderText = "ИНН";
            this.ИНН.Name = "ИНН";
            // 
            // Название
            // 
            this.Название.HeaderText = "Название";
            this.Название.Name = "Название";
            // 
            // Группа
            // 
            this.Группа.HeaderText = "Группа";
            this.Группа.Name = "Группа";
            // 
            // Поставщики
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(886, 541);
            this.Controls.Add(this.splitContainer1);
            this.Name = "Поставщики";
            this.Text = "Поставщики";
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.tabControl1.ResumeLayout(false);
            this.Поставщики1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.ТаблицаПоставщиков)).EndInit();
            this.ГруппыПоставщиков.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView ТаблицаПоставщиков;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage Поставщики1;
        private System.Windows.Forms.TabPage ГруппыПоставщиков;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ИНН;
        private System.Windows.Forms.DataGridViewTextBoxColumn Название;
        private System.Windows.Forms.DataGridViewTextBoxColumn Группа;
    }
}