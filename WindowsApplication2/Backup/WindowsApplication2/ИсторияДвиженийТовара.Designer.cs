namespace WindowsApplication2
{
    partial class ИсторияДвиженийТовара
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
            this.Поиск = new System.Windows.Forms.Button();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.m_cell = new System.Windows.Forms.TextBox();
            this.m_articul = new System.Windows.Forms.TextBox();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.ПоДокументам = new System.Windows.Forms.TabPage();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.ТИП = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Дата = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ОстаткиДо = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ОстаткиПосле = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Движение = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ПоПроводкам = new System.Windows.Forms.TabPage();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.ПоДокументам.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.Поиск);
            this.splitContainer1.Panel1.Controls.Add(this.label2);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            this.splitContainer1.Panel1.Controls.Add(this.m_cell);
            this.splitContainer1.Panel1.Controls.Add(this.m_articul);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.tabControl1);
            this.splitContainer1.Size = new System.Drawing.Size(945, 458);
            this.splitContainer1.SplitterDistance = 37;
            this.splitContainer1.TabIndex = 0;
            // 
            // Поиск
            // 
            this.Поиск.Location = new System.Drawing.Point(412, 6);
            this.Поиск.Name = "Поиск";
            this.Поиск.Size = new System.Drawing.Size(75, 23);
            this.Поиск.TabIndex = 4;
            this.Поиск.Text = "Поиск";
            this.Поиск.UseVisualStyleBackColor = true;
            this.Поиск.Click += new System.EventHandler(this.Поиск_Click);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(197, 11);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(44, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "Ячейка";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 11);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(48, 13);
            this.label1.TabIndex = 2;
            this.label1.Text = "Артикул";
            // 
            // m_cell
            // 
            this.m_cell.Location = new System.Drawing.Point(247, 8);
            this.m_cell.Name = "m_cell";
            this.m_cell.Size = new System.Drawing.Size(100, 20);
            this.m_cell.TabIndex = 1;
            // 
            // m_articul
            // 
            this.m_articul.Location = new System.Drawing.Point(66, 8);
            this.m_articul.Name = "m_articul";
            this.m_articul.Size = new System.Drawing.Size(100, 20);
            this.m_articul.TabIndex = 0;
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.ПоДокументам);
            this.tabControl1.Controls.Add(this.ПоПроводкам);
            this.tabControl1.Location = new System.Drawing.Point(0, 3);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(945, 414);
            this.tabControl1.TabIndex = 0;
            // 
            // ПоДокументам
            // 
            this.ПоДокументам.Controls.Add(this.dataGridView1);
            this.ПоДокументам.Location = new System.Drawing.Point(4, 22);
            this.ПоДокументам.Name = "ПоДокументам";
            this.ПоДокументам.Padding = new System.Windows.Forms.Padding(3);
            this.ПоДокументам.Size = new System.Drawing.Size(937, 388);
            this.ПоДокументам.TabIndex = 0;
            this.ПоДокументам.Text = "По документам";
            this.ПоДокументам.UseVisualStyleBackColor = true;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ТИП,
            this.Дата,
            this.ОстаткиДо,
            this.ОстаткиПосле,
            this.Движение});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(3, 3);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(931, 382);
            this.dataGridView1.TabIndex = 0;
            // 
            // ТИП
            // 
            this.ТИП.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ТИП.HeaderText = "ТИП";
            this.ТИП.Name = "ТИП";
            this.ТИП.ReadOnly = true;
            this.ТИП.Width = 55;
            // 
            // Дата
            // 
            this.Дата.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Дата.HeaderText = "Дата";
            this.Дата.Name = "Дата";
            this.Дата.ReadOnly = true;
            this.Дата.Width = 58;
            // 
            // ОстаткиДо
            // 
            this.ОстаткиДо.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ОстаткиДо.HeaderText = "ОстаткиДо";
            this.ОстаткиДо.Name = "ОстаткиДо";
            this.ОстаткиДо.ReadOnly = true;
            this.ОстаткиДо.Width = 89;
            // 
            // ОстаткиПосле
            // 
            this.ОстаткиПосле.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ОстаткиПосле.HeaderText = "Остатки после";
            this.ОстаткиПосле.Name = "ОстаткиПосле";
            this.ОстаткиПосле.ReadOnly = true;
            this.ОстаткиПосле.Width = 98;
            // 
            // Движение
            // 
            this.Движение.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Движение.HeaderText = "Движение";
            this.Движение.Name = "Движение";
            this.Движение.ReadOnly = true;
            this.Движение.Width = 85;
            // 
            // ПоПроводкам
            // 
            this.ПоПроводкам.Location = new System.Drawing.Point(4, 22);
            this.ПоПроводкам.Name = "ПоПроводкам";
            this.ПоПроводкам.Padding = new System.Windows.Forms.Padding(3);
            this.ПоПроводкам.Size = new System.Drawing.Size(937, 388);
            this.ПоПроводкам.TabIndex = 1;
            this.ПоПроводкам.Text = "По проводкам";
            this.ПоПроводкам.UseVisualStyleBackColor = true;
            // 
            // ИсторияДвиженийТовара
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(945, 458);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ИсторияДвиженийТовара";
            this.Text = "ИсторияДвиженийТовара";
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.tabControl1.ResumeLayout(false);
            this.ПоДокументам.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox m_cell;
        private System.Windows.Forms.TextBox m_articul;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage ПоДокументам;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.TabPage ПоПроводкам;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТИП;
        private System.Windows.Forms.DataGridViewTextBoxColumn Дата;
        private System.Windows.Forms.DataGridViewTextBoxColumn ОстаткиДо;
        private System.Windows.Forms.DataGridViewTextBoxColumn ОстаткиПосле;
        private System.Windows.Forms.DataGridViewTextBoxColumn Движение;
        private System.Windows.Forms.Button Поиск;
    }
}