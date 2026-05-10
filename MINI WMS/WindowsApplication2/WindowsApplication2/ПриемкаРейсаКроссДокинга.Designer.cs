namespace WindowsApplication2
{
    partial class ПриемкаРейсаКроссДокинга
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
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.ПоказыватьНеПринятые = new System.Windows.Forms.CheckBox();
            this.ЗафиксироватьПринятие = new System.Windows.Forms.Button();
            this.ПоказатьПаллеты = new System.Windows.Forms.Button();
            this.НомерРейса = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.Паллет = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Адрес = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ВесОтгрузки = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ВесПринятый = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Принять = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.REMOTE_TT_ID1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.TRANSTASK_ID1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Склад = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.ПоказыватьНеПринятые);
            this.splitContainer1.Panel1.Controls.Add(this.ЗафиксироватьПринятие);
            this.splitContainer1.Panel1.Controls.Add(this.ПоказатьПаллеты);
            this.splitContainer1.Panel1.Controls.Add(this.НомерРейса);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Size = new System.Drawing.Size(794, 427);
            this.splitContainer1.SplitterDistance = 213;
            this.splitContainer1.TabIndex = 0;
            // 
            // ПоказыватьНеПринятые
            // 
            this.ПоказыватьНеПринятые.AutoSize = true;
            this.ПоказыватьНеПринятые.Checked = true;
            this.ПоказыватьНеПринятые.CheckState = System.Windows.Forms.CheckState.Checked;
            this.ПоказыватьНеПринятые.Location = new System.Drawing.Point(6, 30);
            this.ПоказыватьНеПринятые.Name = "ПоказыватьНеПринятые";
            this.ПоказыватьНеПринятые.Size = new System.Drawing.Size(194, 17);
            this.ПоказыватьНеПринятые.TabIndex = 4;
            this.ПоказыватьНеПринятые.Text = "Показывать только не принятые";
            this.ПоказыватьНеПринятые.UseVisualStyleBackColor = true;
            // 
            // ЗафиксироватьПринятие
            // 
            this.ЗафиксироватьПринятие.Location = new System.Drawing.Point(370, 4);
            this.ЗафиксироватьПринятие.Name = "ЗафиксироватьПринятие";
            this.ЗафиксироватьПринятие.Size = new System.Drawing.Size(190, 23);
            this.ЗафиксироватьПринятие.TabIndex = 3;
            this.ЗафиксироватьПринятие.Text = "Принять Паллеты на склад";
            this.ЗафиксироватьПринятие.UseVisualStyleBackColor = true;
            this.ЗафиксироватьПринятие.Click += new System.EventHandler(this.ЗафиксироватьПринятие_Click);
            // 
            // ПоказатьПаллеты
            // 
            this.ПоказатьПаллеты.Location = new System.Drawing.Point(191, 4);
            this.ПоказатьПаллеты.Name = "ПоказатьПаллеты";
            this.ПоказатьПаллеты.Size = new System.Drawing.Size(173, 23);
            this.ПоказатьПаллеты.TabIndex = 2;
            this.ПоказатьПаллеты.Text = "Показать Паллеты";
            this.ПоказатьПаллеты.UseVisualStyleBackColor = true;
            this.ПоказатьПаллеты.Click += new System.EventHandler(this.ПоказатьПаллеты_Click);
            // 
            // НомерРейса
            // 
            this.НомерРейса.Location = new System.Drawing.Point(83, 6);
            this.НомерРейса.Name = "НомерРейса";
            this.НомерРейса.Size = new System.Drawing.Size(100, 20);
            this.НомерРейса.TabIndex = 1;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(3, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(78, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "Номер Рейса:";
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToAddRows = false;
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Паллет,
            this.Адрес,
            this.ВесОтгрузки,
            this.ВесПринятый,
            this.Принять,
            this.REMOTE_TT_ID1,
            this.TRANSTASK_ID1,
            this.Склад});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(794, 210);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            this.dataGridView1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.dataGridView1_KeyDown);
            this.dataGridView1.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.dataGridView1_KeyPress);
            // 
            // Паллет
            // 
            this.Паллет.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Паллет.HeaderText = "Паллет";
            this.Паллет.Name = "Паллет";
            this.Паллет.ReadOnly = true;
            this.Паллет.Width = 69;
            // 
            // Адрес
            // 
            this.Адрес.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Адрес.HeaderText = "Адрес";
            this.Адрес.Name = "Адрес";
            this.Адрес.ReadOnly = true;
            this.Адрес.Width = 63;
            // 
            // ВесОтгрузки
            // 
            this.ВесОтгрузки.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            dataGridViewCellStyle1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(224)))), ((int)(((byte)(224)))), ((int)(((byte)(224)))));
            this.ВесОтгрузки.DefaultCellStyle = dataGridViewCellStyle1;
            this.ВесОтгрузки.HeaderText = "Вес на отгрузке";
            this.ВесОтгрузки.Name = "ВесОтгрузки";
            this.ВесОтгрузки.ReadOnly = true;
            this.ВесОтгрузки.Width = 105;
            // 
            // ВесПринятый
            // 
            this.ВесПринятый.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            dataGridViewCellStyle2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(128)))), ((int)(((byte)(255)))), ((int)(((byte)(128)))));
            this.ВесПринятый.DefaultCellStyle = dataGridViewCellStyle2;
            this.ВесПринятый.HeaderText = "ВесПринятый";
            this.ВесПринятый.Name = "ВесПринятый";
            this.ВесПринятый.Width = 102;
            // 
            // Принять
            // 
            this.Принять.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Принять.HeaderText = "Принять";
            this.Принять.Name = "Принять";
            this.Принять.Width = 56;
            // 
            // REMOTE_TT_ID1
            // 
            this.REMOTE_TT_ID1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.REMOTE_TT_ID1.HeaderText = "REMOTE_TT_ID";
            this.REMOTE_TT_ID1.Name = "REMOTE_TT_ID1";
            this.REMOTE_TT_ID1.ReadOnly = true;
            this.REMOTE_TT_ID1.Width = 115;
            // 
            // TRANSTASK_ID1
            // 
            this.TRANSTASK_ID1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.TRANSTASK_ID1.HeaderText = "TRANSTASK_ID";
            this.TRANSTASK_ID1.Name = "TRANSTASK_ID1";
            this.TRANSTASK_ID1.ReadOnly = true;
            this.TRANSTASK_ID1.Width = 114;
            // 
            // Склад
            // 
            this.Склад.HeaderText = "Склад";
            this.Склад.Name = "Склад";
            this.Склад.ReadOnly = true;
            // 
            // ПриемкаРейсаКроссДокинга
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(794, 427);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ПриемкаРейсаКроссДокинга";
            this.Text = "ПриемкаРейсаКроссДокинга";
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button ПоказатьПаллеты;
        private System.Windows.Forms.TextBox НомерРейса;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Button ЗафиксироватьПринятие;
        private System.Windows.Forms.CheckBox ПоказыватьНеПринятые;
        private System.Windows.Forms.DataGridViewTextBoxColumn Паллет;
        private System.Windows.Forms.DataGridViewTextBoxColumn Адрес;
        private System.Windows.Forms.DataGridViewTextBoxColumn ВесОтгрузки;
        private System.Windows.Forms.DataGridViewTextBoxColumn ВесПринятый;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Принять;
        private System.Windows.Forms.DataGridViewTextBoxColumn REMOTE_TT_ID1;
        private System.Windows.Forms.DataGridViewTextBoxColumn TRANSTASK_ID1;
        private System.Windows.Forms.DataGridViewTextBoxColumn Склад;
    }
}