namespace WindowsApplication2
{
    partial class ЗаказПоставщику
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
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.йй = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.dateTimePicker1 = new System.Windows.Forms.DateTimePicker();
            this.label2 = new System.Windows.Forms.Label();
            this.comboBox1 = new System.Windows.Forms.ComboBox();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.ВыбратьПоставщика = new System.Windows.Forms.Button();
            this.МенюСтрокЗаказа = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.загрузкаДанныхИзExcelToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.label3 = new System.Windows.Forms.Label();
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.Номер = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Артикул = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Наименование = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Количество = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ЦенаЗаказа = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.автоматЗаказ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Оборачиваемость = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.МенюСтрокЗаказа.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.textBox2);
            this.splitContainer1.Panel1.Controls.Add(this.label3);
            this.splitContainer1.Panel1.Controls.Add(this.ВыбратьПоставщика);
            this.splitContainer1.Panel1.Controls.Add(this.textBox1);
            this.splitContainer1.Panel1.Controls.Add(this.comboBox1);
            this.splitContainer1.Panel1.Controls.Add(this.dateTimePicker1);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            this.splitContainer1.Panel1.Controls.Add(this.label2);
            this.splitContainer1.Panel1.Controls.Add(this.йй);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Size = new System.Drawing.Size(895, 386);
            this.splitContainer1.SplitterDistance = 60;
            this.splitContainer1.TabIndex = 0;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Номер,
            this.Артикул,
            this.Наименование,
            this.Количество,
            this.ЦенаЗаказа,
            this.автоматЗаказ,
            this.Оборачиваемость});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(895, 322);
            this.dataGridView1.TabIndex = 0;
            // 
            // йй
            // 
            this.йй.AutoSize = true;
            this.йй.Location = new System.Drawing.Point(12, 9);
            this.йй.Name = "йй";
            this.йй.Size = new System.Drawing.Size(65, 13);
            this.йй.TabIndex = 0;
            this.йй.Text = "Поставщик";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 38);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(101, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Активный договор";
            // 
            // dateTimePicker1
            // 
            this.dateTimePicker1.Location = new System.Drawing.Point(379, 34);
            this.dateTimePicker1.Name = "dateTimePicker1";
            this.dateTimePicker1.Size = new System.Drawing.Size(142, 20);
            this.dateTimePicker1.TabIndex = 1;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(290, 38);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(83, 13);
            this.label2.TabIndex = 0;
            this.label2.Text = "Дата поставки";
            // 
            // comboBox1
            // 
            this.comboBox1.FormattingEnabled = true;
            this.comboBox1.Location = new System.Drawing.Point(119, 33);
            this.comboBox1.Name = "comboBox1";
            this.comboBox1.Size = new System.Drawing.Size(165, 21);
            this.comboBox1.TabIndex = 2;
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(119, 6);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(628, 20);
            this.textBox1.TabIndex = 3;
            // 
            // ВыбратьПоставщика
            // 
            this.ВыбратьПоставщика.Location = new System.Drawing.Point(753, 4);
            this.ВыбратьПоставщика.Name = "ВыбратьПоставщика";
            this.ВыбратьПоставщика.Size = new System.Drawing.Size(130, 23);
            this.ВыбратьПоставщика.TabIndex = 4;
            this.ВыбратьПоставщика.Text = "Выбрать поставщика";
            this.ВыбратьПоставщика.UseVisualStyleBackColor = true;
            this.ВыбратьПоставщика.Click += new System.EventHandler(this.ВыбратьПоставщика_Click);
            // 
            // МенюСтрокЗаказа
            // 
            this.МенюСтрокЗаказа.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.загрузкаДанныхИзExcelToolStripMenuItem});
            this.МенюСтрокЗаказа.Name = "МенюСтрокЗаказа";
            this.МенюСтрокЗаказа.Size = new System.Drawing.Size(210, 26);
            // 
            // загрузкаДанныхИзExcelToolStripMenuItem
            // 
            this.загрузкаДанныхИзExcelToolStripMenuItem.Name = "загрузкаДанныхИзExcelToolStripMenuItem";
            this.загрузкаДанныхИзExcelToolStripMenuItem.Size = new System.Drawing.Size(209, 22);
            this.загрузкаДанныхИзExcelToolStripMenuItem.Text = "Загрузка данных из Excel";
            this.загрузкаДанныхИзExcelToolStripMenuItem.Click += new System.EventHandler(this.загрузкаДанныхИзExcelToolStripMenuItem_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(541, 38);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(80, 13);
            this.label3.TabIndex = 5;
            this.label3.Text = "Номер заказа";
            // 
            // textBox2
            // 
            this.textBox2.Location = new System.Drawing.Point(627, 33);
            this.textBox2.Name = "textBox2";
            this.textBox2.Size = new System.Drawing.Size(120, 20);
            this.textBox2.TabIndex = 6;
            // 
            // Номер
            // 
            this.Номер.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Номер.ContextMenuStrip = this.МенюСтрокЗаказа;
            this.Номер.HeaderText = "№";
            this.Номер.Name = "Номер";
            this.Номер.Width = 43;
            // 
            // Артикул
            // 
            this.Артикул.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Артикул.ContextMenuStrip = this.МенюСтрокЗаказа;
            this.Артикул.HeaderText = "Артикул";
            this.Артикул.Name = "Артикул";
            this.Артикул.Width = 73;
            // 
            // Наименование
            // 
            this.Наименование.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Наименование.ContextMenuStrip = this.МенюСтрокЗаказа;
            this.Наименование.HeaderText = "Наименование";
            this.Наименование.Name = "Наименование";
            this.Наименование.Width = 108;
            // 
            // Количество
            // 
            this.Количество.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Количество.ContextMenuStrip = this.МенюСтрокЗаказа;
            this.Количество.HeaderText = "Количество";
            this.Количество.Name = "Количество";
            this.Количество.Width = 91;
            // 
            // ЦенаЗаказа
            // 
            this.ЦенаЗаказа.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ЦенаЗаказа.ContextMenuStrip = this.МенюСтрокЗаказа;
            this.ЦенаЗаказа.HeaderText = "Цена Заказа";
            this.ЦенаЗаказа.Name = "ЦенаЗаказа";
            this.ЦенаЗаказа.Width = 98;
            // 
            // автоматЗаказ
            // 
            this.автоматЗаказ.HeaderText = "Автомат-Заказ";
            this.автоматЗаказ.Name = "автоматЗаказ";
            // 
            // Оборачиваемость
            // 
            this.Оборачиваемость.HeaderText = "Оборачиваемость";
            this.Оборачиваемость.Name = "Оборачиваемость";
            // 
            // ЗаказПоставщику
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(895, 386);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ЗаказПоставщику";
            this.Text = "ЗаказПоставщику";
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.МенюСтрокЗаказа.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.ComboBox comboBox1;
        private System.Windows.Forms.DateTimePicker dateTimePicker1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label йй;
        private System.Windows.Forms.Button ВыбратьПоставщика;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.ContextMenuStrip МенюСтрокЗаказа;
        private System.Windows.Forms.ToolStripMenuItem загрузкаДанныхИзExcelToolStripMenuItem;
        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.DataGridViewTextBoxColumn Номер;
        private System.Windows.Forms.DataGridViewTextBoxColumn Артикул;
        private System.Windows.Forms.DataGridViewTextBoxColumn Наименование;
        private System.Windows.Forms.DataGridViewTextBoxColumn Количество;
        private System.Windows.Forms.DataGridViewTextBoxColumn ЦенаЗаказа;
        private System.Windows.Forms.DataGridViewTextBoxColumn автоматЗаказ;
        private System.Windows.Forms.DataGridViewTextBoxColumn Оборачиваемость;
    }
}