namespace WindowsApplication2
{
    partial class ЗаказНаОтгрузку
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
            this.components = new System.ComponentModel.Container();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.label1 = new System.Windows.Forms.Label();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.dateTimePicker1 = new System.Windows.Forms.DateTimePicker();
            this.label2 = new System.Windows.Forms.Label();
            this.dateTimePicker2 = new System.Windows.Forms.DateTimePicker();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.Е_Склад = new System.Windows.Forms.ComboBox();
            this.Е_НомерЗаказа = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.МенюСозданияЗаказа = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.данныеExcelToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.Номер = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Артикул = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Имя_позиции = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Заказ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ПредложениеЗаказ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Наличие = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.НаскладеИВПути = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.МенюСозданияЗаказа.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.Е_НомерЗаказа);
            this.splitContainer1.Panel1.Controls.Add(this.Е_Склад);
            this.splitContainer1.Panel1.Controls.Add(this.label5);
            this.splitContainer1.Panel1.Controls.Add(this.label4);
            this.splitContainer1.Panel1.Controls.Add(this.label3);
            this.splitContainer1.Panel1.Controls.Add(this.label2);
            this.splitContainer1.Panel1.Controls.Add(this.dateTimePicker2);
            this.splitContainer1.Panel1.Controls.Add(this.dateTimePicker1);
            this.splitContainer1.Panel1.Controls.Add(this.textBox1);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Size = new System.Drawing.Size(758, 311);
            this.splitContainer1.SplitterDistance = 77;
            this.splitContainer1.TabIndex = 0;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(3, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(41, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Адрес:";
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(50, 6);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(696, 20);
            this.textBox1.TabIndex = 1;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Номер,
            this.Артикул,
            this.Имя_позиции,
            this.Заказ,
            this.ПредложениеЗаказ,
            this.Наличие,
            this.НаскладеИВПути});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(758, 230);
            this.dataGridView1.TabIndex = 0;
            // 
            // dateTimePicker1
            // 
            this.dateTimePicker1.Location = new System.Drawing.Point(162, 29);
            this.dateTimePicker1.Name = "dateTimePicker1";
            this.dateTimePicker1.Size = new System.Drawing.Size(127, 20);
            this.dateTimePicker1.TabIndex = 2;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 32);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(144, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "Дата отгрузки по графику:";
            // 
            // dateTimePicker2
            // 
            this.dateTimePicker2.Location = new System.Drawing.Point(162, 53);
            this.dateTimePicker2.Name = "dateTimePicker2";
            this.dateTimePicker2.Size = new System.Drawing.Size(127, 20);
            this.dateTimePicker2.TabIndex = 2;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(12, 52);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(86, 13);
            this.label3.TabIndex = 3;
            this.label3.Text = "Дата доставки:";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(310, 32);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(38, 13);
            this.label4.TabIndex = 4;
            this.label4.Text = "Склад";
            // 
            // Е_Склад
            // 
            this.Е_Склад.FormattingEnabled = true;
            this.Е_Склад.Items.AddRange(new object[] {
            "ЕКБ"});
            this.Е_Склад.Location = new System.Drawing.Point(389, 29);
            this.Е_Склад.Name = "Е_Склад";
            this.Е_Склад.Size = new System.Drawing.Size(100, 21);
            this.Е_Склад.TabIndex = 5;
            this.Е_Склад.Text = "ЕКБ";
            // 
            // Е_НомерЗаказа
            // 
            this.Е_НомерЗаказа.Location = new System.Drawing.Point(389, 53);
            this.Е_НомерЗаказа.Name = "Е_НомерЗаказа";
            this.Е_НомерЗаказа.Size = new System.Drawing.Size(100, 20);
            this.Е_НомерЗаказа.TabIndex = 6;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(310, 57);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(81, 13);
            this.label5.TabIndex = 4;
            this.label5.Text = "Номер Заказа";
            // 
            // МенюСозданияЗаказа
            // 
            this.МенюСозданияЗаказа.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.данныеExcelToolStripMenuItem});
            this.МенюСозданияЗаказа.Name = "МенюСозданияЗаказа";
            this.МенюСозданияЗаказа.Size = new System.Drawing.Size(147, 26);
            // 
            // данныеExcelToolStripMenuItem
            // 
            this.данныеExcelToolStripMenuItem.Name = "данныеExcelToolStripMenuItem";
            this.данныеExcelToolStripMenuItem.Size = new System.Drawing.Size(152, 22);
            this.данныеExcelToolStripMenuItem.Text = "Данные Excel";
            this.данныеExcelToolStripMenuItem.Click += new System.EventHandler(this.данныеExcelToolStripMenuItem_Click);
            // 
            // Номер
            // 
            this.Номер.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Номер.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.Номер.HeaderText = "№";
            this.Номер.Name = "Номер";
            this.Номер.Width = 43;
            // 
            // Артикул
            // 
            this.Артикул.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Артикул.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.Артикул.HeaderText = "Артикул";
            this.Артикул.Name = "Артикул";
            this.Артикул.Width = 73;
            // 
            // Имя_позиции
            // 
            this.Имя_позиции.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Имя_позиции.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.Имя_позиции.HeaderText = "Имя позиции";
            this.Имя_позиции.Name = "Имя_позиции";
            this.Имя_позиции.Width = 99;
            // 
            // Заказ
            // 
            this.Заказ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Заказ.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.Заказ.HeaderText = "Заказ";
            this.Заказ.Name = "Заказ";
            this.Заказ.Width = 63;
            // 
            // ПредложениеЗаказ
            // 
            this.ПредложениеЗаказ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ПредложениеЗаказ.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.ПредложениеЗаказ.HeaderText = "Автомат-заказ";
            this.ПредложениеЗаказ.Name = "ПредложениеЗаказ";
            this.ПредложениеЗаказ.Width = 108;
            // 
            // Наличие
            // 
            this.Наличие.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Наличие.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.Наличие.HeaderText = "К-во Складе";
            this.Наличие.Name = "Наличие";
            this.Наличие.Width = 94;
            // 
            // НаскладеИВПути
            // 
            this.НаскладеИВПути.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.НаскладеИВПути.ContextMenuStrip = this.МенюСозданияЗаказа;
            this.НаскладеИВПути.HeaderText = "В пути+на складе";
            this.НаскладеИВПути.Name = "НаскладеИВПути";
            this.НаскладеИВПути.Width = 111;
            // 
            // ЗаказНаОтгрузку
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(758, 311);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ЗаказНаОтгрузку";
            this.Text = "ЗаказНаОтгрузку";
            this.Load += new System.EventHandler(this.ЗаказНаОтгрузку_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.МенюСозданияЗаказа.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.DateTimePicker dateTimePicker2;
        private System.Windows.Forms.DateTimePicker dateTimePicker1;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox Е_НомерЗаказа;
        private System.Windows.Forms.ComboBox Е_Склад;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.ContextMenuStrip МенюСозданияЗаказа;
        private System.Windows.Forms.ToolStripMenuItem данныеExcelToolStripMenuItem;
        private System.Windows.Forms.DataGridViewTextBoxColumn Номер;
        private System.Windows.Forms.DataGridViewTextBoxColumn Артикул;
        private System.Windows.Forms.DataGridViewTextBoxColumn Имя_позиции;
        private System.Windows.Forms.DataGridViewTextBoxColumn Заказ;
        private System.Windows.Forms.DataGridViewTextBoxColumn ПредложениеЗаказ;
        private System.Windows.Forms.DataGridViewTextBoxColumn Наличие;
        private System.Windows.Forms.DataGridViewTextBoxColumn НаскладеИВПути;
    }
}