namespace WindowsApplication2
{
    partial class Расстояния
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
            this.contextMenuStrip1 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.label1 = new System.Windows.Forms.Label();
            this.ТИП_ИЗМЕРЕНИЯ = new System.Windows.Forms.ComboBox();
            this.comboBox1 = new System.Windows.Forms.ComboBox();
            this.Отобразить = new System.Windows.Forms.Button();
            this.АвтоматическийПересчет = new System.Windows.Forms.CheckBox();
            this.Скорость = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.contextMenuStrip1.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.dataGridView1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.label2);
            this.splitContainer1.Panel2.Controls.Add(this.Скорость);
            this.splitContainer1.Panel2.Controls.Add(this.АвтоматическийПересчет);
            this.splitContainer1.Panel2.Controls.Add(this.label1);
            this.splitContainer1.Panel2.Controls.Add(this.ТИП_ИЗМЕРЕНИЯ);
            this.splitContainer1.Panel2.Controls.Add(this.comboBox1);
            this.splitContainer1.Panel2.Controls.Add(this.Отобразить);
            this.splitContainer1.Size = new System.Drawing.Size(793, 511);
            this.splitContainer1.SplitterDistance = 421;
            this.splitContainer1.TabIndex = 0;
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToAddRows = false;
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.ContextMenuStrip = this.contextMenuStrip1;
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(793, 421);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(297, 26);
            // 
            // управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem
            // 
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem.Name = "управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem";
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem.Size = new System.Drawing.Size(296, 22);
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem.Text = "Управление таблицей и загрузка данных";
            this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem.Click += new System.EventHandler(this.управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(604, 4);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(83, 13);
            this.label1.TabIndex = 2;
            this.label1.Text = "тип измерения";
            // 
            // ТИП_ИЗМЕРЕНИЯ
            // 
            this.ТИП_ИЗМЕРЕНИЯ.FormattingEnabled = true;
            this.ТИП_ИЗМЕРЕНИЯ.Items.AddRange(new object[] {
            "ВРЕМЯ",
            "РАССТОЯНИЕ"});
            this.ТИП_ИЗМЕРЕНИЯ.Location = new System.Drawing.Point(693, 1);
            this.ТИП_ИЗМЕРЕНИЯ.Name = "ТИП_ИЗМЕРЕНИЯ";
            this.ТИП_ИЗМЕРЕНИЯ.Size = new System.Drawing.Size(97, 21);
            this.ТИП_ИЗМЕРЕНИЯ.TabIndex = 1;
            this.ТИП_ИЗМЕРЕНИЯ.Text = "ВРЕМЯ";
            // 
            // comboBox1
            // 
            this.comboBox1.FormattingEnabled = true;
            this.comboBox1.Location = new System.Drawing.Point(0, 2);
            this.comboBox1.Name = "comboBox1";
            this.comboBox1.Size = new System.Drawing.Size(222, 21);
            this.comboBox1.TabIndex = 0;
            // 
            // Отобразить
            // 
            this.Отобразить.Location = new System.Drawing.Point(228, 1);
            this.Отобразить.Name = "Отобразить";
            this.Отобразить.Size = new System.Drawing.Size(121, 23);
            this.Отобразить.TabIndex = 0;
            this.Отобразить.Text = "Отобразить";
            this.Отобразить.UseVisualStyleBackColor = true;
            this.Отобразить.Click += new System.EventHandler(this.Отобразить_Click);
            // 
            // АвтоматическийПересчет
            // 
            this.АвтоматическийПересчет.AutoSize = true;
            this.АвтоматическийПересчет.Location = new System.Drawing.Point(607, 28);
            this.АвтоматическийПересчет.Name = "АвтоматическийПересчет";
            this.АвтоматическийПересчет.Size = new System.Drawing.Size(183, 17);
            this.АвтоматическийПересчет.TabIndex = 3;
            this.АвтоматическийПересчет.Text = "автоматически пересчитывать";
            this.АвтоматическийПересчет.UseVisualStyleBackColor = true;
            // 
            // Скорость
            // 
            this.Скорость.Location = new System.Drawing.Point(693, 51);
            this.Скорость.Name = "Скорость";
            this.Скорость.Size = new System.Drawing.Size(97, 20);
            this.Скорость.TabIndex = 4;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(629, 54);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(58, 13);
            this.label2.TabIndex = 5;
            this.label2.Text = "Скорость:";
            // 
            // Расстояния
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(793, 511);
            this.Controls.Add(this.splitContainer1);
            this.Name = "Расстояния";
            this.Text = "Расстояния";
            this.Load += new System.EventHandler(this.Расстояния_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.contextMenuStrip1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.Button Отобразить;
        private System.Windows.Forms.ComboBox comboBox1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.ComboBox ТИП_ИЗМЕРЕНИЯ;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ContextMenuStrip contextMenuStrip1;
        private System.Windows.Forms.ToolStripMenuItem управлениеТаблицейИЗагрузкаДанныхToolStripMenuItem;
        private System.Windows.Forms.CheckBox АвтоматическийПересчет;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox Скорость;
    }
}