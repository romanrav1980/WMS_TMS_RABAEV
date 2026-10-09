namespace WindowsApplication2
{
    partial class TRANSPORT
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
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle1 = new System.Windows.Forms.DataGridViewCellStyle();
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle2 = new System.Windows.Forms.DataGridViewCellStyle();
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle3 = new System.Windows.Forms.DataGridViewCellStyle();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.RefRejim = new System.Windows.Forms.ComboBox();
            this.comboBox2 = new System.Windows.Forms.ComboBox();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.panel1 = new System.Windows.Forms.Panel();
            this.button2 = new System.Windows.Forms.Button();
            this.button1 = new System.Windows.Forms.Button();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.ID5 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Номер = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТИП = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.МАРКА = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.РефРежим = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.Работает = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.ПАЛЛ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.УДАЛЕН = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.Лопата = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.panel1.SuspendLayout();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.SuspendLayout();
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ID5,
            this.Номер,
            this.ТИП,
            this.МАРКА,
            this.РефРежим,
            this.Работает,
            this.ПАЛЛ,
            this.УДАЛЕН,
            this.Лопата});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(902, 426);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            this.dataGridView1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.dataGridView1_KeyDown);
            this.dataGridView1.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.dataGridView1_KeyPress);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(82, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(64, 13);
            this.label1.TabIndex = 1;
            this.label1.Text = "Номер ТС=";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(213, 9);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(42, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "ТИП = ";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(463, 9);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(74, 13);
            this.label4.TabIndex = 4;
            this.label4.Text = "Реф-режим =";
            // 
            // RefRejim
            // 
            this.RefRejim.FormattingEnabled = true;
            this.RefRejim.Items.AddRange(new object[] {
            "нет",
            "-40 +15",
            "-5 +15",
            "+5+15"});
            this.RefRejim.Location = new System.Drawing.Point(539, 6);
            this.RefRejim.Name = "RefRejim";
            this.RefRejim.Size = new System.Drawing.Size(87, 21);
            this.RefRejim.TabIndex = 5;
            this.RefRejim.Text = "нет";
            // 
            // comboBox2
            // 
            this.comboBox2.FormattingEnabled = true;
            this.comboBox2.Items.AddRange(new object[] {
            "15",
            "10",
            "15реф",
            "10реф",
            "5",
            "5реф",
            "20реф",
            "20",
            "30",
            "30реф",
            "нет"});
            this.comboBox2.Location = new System.Drawing.Point(252, 5);
            this.comboBox2.Name = "comboBox2";
            this.comboBox2.Size = new System.Drawing.Size(89, 21);
            this.comboBox2.TabIndex = 7;
            this.comboBox2.Text = "нет";
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(146, 6);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(64, 20);
            this.textBox1.TabIndex = 8;
            // 
            // panel1
            // 
            this.panel1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(255)))), ((int)(((byte)(128)))));
            this.panel1.Controls.Add(this.button2);
            this.panel1.Controls.Add(this.button1);
            this.panel1.Controls.Add(this.RefRejim);
            this.panel1.Controls.Add(this.comboBox2);
            this.panel1.Controls.Add(this.textBox1);
            this.panel1.Controls.Add(this.label4);
            this.panel1.Controls.Add(this.label2);
            this.panel1.Controls.Add(this.label1);
            this.panel1.Location = new System.Drawing.Point(3, 3);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(765, 32);
            this.panel1.TabIndex = 9;
            // 
            // button2
            // 
            this.button2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(192)))), ((int)(((byte)(0)))));
            this.button2.Location = new System.Drawing.Point(632, 5);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(55, 23);
            this.button2.TabIndex = 10;
            this.button2.Text = "Поиск";
            this.button2.UseVisualStyleBackColor = false;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // button1
            // 
            this.button1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(128)))), ((int)(((byte)(128)))));
            this.button1.Location = new System.Drawing.Point(6, 5);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(71, 22);
            this.button1.TabIndex = 10;
            this.button1.Text = "Выбрать";
            this.button1.UseVisualStyleBackColor = false;
            this.button1.Click += new System.EventHandler(this.button1_Click);
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
            this.splitContainer1.Panel1.Controls.Add(this.dataGridView1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.panel1);
            this.splitContainer1.Size = new System.Drawing.Size(902, 467);
            this.splitContainer1.SplitterDistance = 426;
            this.splitContainer1.TabIndex = 10;
            // 
            // ID5
            // 
            this.ID5.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ID5.HeaderText = "ID";
            this.ID5.Name = "ID5";
            this.ID5.ReadOnly = true;
            this.ID5.Width = 43;
            // 
            // Номер
            // 
            this.Номер.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Номер.HeaderText = "НомерТС";
            this.Номер.Name = "Номер";
            this.Номер.Width = 80;
            // 
            // ТИП
            // 
            this.ТИП.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            dataGridViewCellStyle1.NullValue = "нет";
            this.ТИП.DefaultCellStyle = dataGridViewCellStyle1;
            this.ТИП.HeaderText = "ТИП";
            this.ТИП.Items.AddRange(new object[] {
            "15",
            "10",
            "15реф",
            "10реф",
            "5",
            "5реф",
            "20реф",
            "20",
            "30",
            "30реф",
            "нет",
            "4"});
            this.ТИП.MaxDropDownItems = 12;
            this.ТИП.Name = "ТИП";
            this.ТИП.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.ТИП.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.ТИП.Width = 55;
            // 
            // МАРКА
            // 
            this.МАРКА.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            dataGridViewCellStyle2.NullValue = "нет";
            this.МАРКА.DefaultCellStyle = dataGridViewCellStyle2;
            this.МАРКА.HeaderText = "МАРКА";
            this.МАРКА.Items.AddRange(new object[] {
            "нет",
            "МАЗ",
            "КАМАЗ",
            "MAN",
            "DAF",
            "SCANIA",
            "VOLVO",
            "MERCEDES",
            "MITSUBISHI",
            "ЗИЛ",
            "КРАЗ",
            "NISSAN",
            "РЕНО",
            "ИНТЕР",
            "IVEKO",
            "ФРЕДЛАЙНЕР",
            "HINO",
            "TOYOTA",
            "Hyundai",
            "Стерлинг"});
            this.МАРКА.MaxDropDownItems = 25;
            this.МАРКА.Name = "МАРКА";
            this.МАРКА.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.МАРКА.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.МАРКА.Width = 69;
            // 
            // РефРежим
            // 
            this.РефРежим.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            dataGridViewCellStyle3.NullValue = "нет";
            this.РефРежим.DefaultCellStyle = dataGridViewCellStyle3;
            this.РефРежим.HeaderText = "РефРежим";
            this.РефРежим.Items.AddRange(new object[] {
            "нет",
            "холод+тепло",
            "тепло",
            "холод"});
            this.РефРежим.Name = "РефРежим";
            this.РефРежим.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.РефРежим.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.РефРежим.Width = 88;
            // 
            // Работает
            // 
            this.Работает.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Работает.HeaderText = "Работает";
            this.Работает.Name = "Работает";
            this.Работает.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.Работает.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.Работает.Width = 79;
            // 
            // ПАЛЛ
            // 
            this.ПАЛЛ.HeaderText = "ПАЛЛ";
            this.ПАЛЛ.Name = "ПАЛЛ";
            // 
            // УДАЛЕН
            // 
            this.УДАЛЕН.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.УДАЛЕН.HeaderText = "УДАЛЕН";
            this.УДАЛЕН.Name = "УДАЛЕН";
            this.УДАЛЕН.ReadOnly = true;
            this.УДАЛЕН.Width = 60;
            // 
            // Лопата
            // 
            this.Лопата.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Лопата.HeaderText = "Лопата";
            this.Лопата.Name = "Лопата";
            this.Лопата.Width = 50;
            // 
            // TRANSPORT
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(902, 467);
            this.Controls.Add(this.splitContainer1);
            this.Name = "TRANSPORT";
            this.Text = "Автомобили";
            this.Load += new System.EventHandler(this.TRANSPORT_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.ComboBox RefRejim;
        private System.Windows.Forms.ComboBox comboBox2;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID5;
        private System.Windows.Forms.DataGridViewTextBoxColumn Номер;
        private System.Windows.Forms.DataGridViewComboBoxColumn ТИП;
        private System.Windows.Forms.DataGridViewComboBoxColumn МАРКА;
        private System.Windows.Forms.DataGridViewComboBoxColumn РефРежим;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Работает;
        private System.Windows.Forms.DataGridViewTextBoxColumn ПАЛЛ;
        private System.Windows.Forms.DataGridViewCheckBoxColumn УДАЛЕН;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Лопата;
    }
}