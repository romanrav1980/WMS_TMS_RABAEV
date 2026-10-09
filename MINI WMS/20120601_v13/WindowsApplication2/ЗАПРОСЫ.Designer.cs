namespace WindowsApplication2
{
    partial class ЗАПРОСЫ
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
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.contextMenuStrip1 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.перевестиДанныеВExcelToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.Кнопки = new System.Windows.Forms.TabPage();
            this.button1 = new System.Windows.Forms.Button();
            this.button4 = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.ЗапросТЕКСТ = new System.Windows.Forms.TabPage();
            this.Переделать_запрос = new System.Windows.Forms.Button();
            this.Запрос2 = new System.Windows.Forms.TextBox();
            this.Данные = new System.Windows.Forms.TabPage();
            this.label2 = new System.Windows.Forms.Label();
            this.timer1 = new System.Windows.Forms.Timer(this.components);
            this.СкрытьПанель = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.contextMenuStrip1.SuspendLayout();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.Кнопки.SuspendLayout();
            this.ЗапросТЕКСТ.SuspendLayout();
            this.SuspendLayout();
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
            this.dataGridView1.ReadOnly = true;
            this.dataGridView1.Size = new System.Drawing.Size(1110, 314);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.MouseDoubleClick += new System.Windows.Forms.MouseEventHandler(this.dataGridView1_MouseDoubleClick);
            this.dataGridView1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.dataGridView1_KeyDown);
            this.dataGridView1.CellEnter += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEnter);
            this.dataGridView1.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.dataGridView1_KeyPress);
            this.dataGridView1.SelectionChanged += new System.EventHandler(this.dataGridView1_SelectionChanged);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.перевестиДанныеВExcelToolStripMenuItem});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(219, 26);
            // 
            // перевестиДанныеВExcelToolStripMenuItem
            // 
            this.перевестиДанныеВExcelToolStripMenuItem.Name = "перевестиДанныеВExcelToolStripMenuItem";
            this.перевестиДанныеВExcelToolStripMenuItem.Size = new System.Drawing.Size(218, 22);
            this.перевестиДанныеВExcelToolStripMenuItem.Text = "Перевести данные в Excel";
            this.перевестиДанныеВExcelToolStripMenuItem.Click += new System.EventHandler(this.перевестиДанныеВExcelToolStripMenuItem_Click);
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.FixedPanel = System.Windows.Forms.FixedPanel.Panel2;
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
            this.splitContainer1.Panel2.Controls.Add(this.tabControl1);
            this.splitContainer1.Panel2.Controls.Add(this.label2);
            this.splitContainer1.Size = new System.Drawing.Size(1110, 401);
            this.splitContainer1.SplitterDistance = 314;
            this.splitContainer1.TabIndex = 1;
            // 
            // tabControl1
            // 
            this.tabControl1.Alignment = System.Windows.Forms.TabAlignment.Left;
            this.tabControl1.Controls.Add(this.Кнопки);
            this.tabControl1.Controls.Add(this.ЗапросТЕКСТ);
            this.tabControl1.Controls.Add(this.Данные);
            this.tabControl1.Dock = System.Windows.Forms.DockStyle.Left;
            this.tabControl1.Location = new System.Drawing.Point(0, 0);
            this.tabControl1.Multiline = true;
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(1110, 83);
            this.tabControl1.SizeMode = System.Windows.Forms.TabSizeMode.FillToRight;
            this.tabControl1.TabIndex = 6;
            // 
            // Кнопки
            // 
            this.Кнопки.Controls.Add(this.СкрытьПанель);
            this.Кнопки.Controls.Add(this.button1);
            this.Кнопки.Controls.Add(this.button4);
            this.Кнопки.Controls.Add(this.button3);
            this.Кнопки.Controls.Add(this.button2);
            this.Кнопки.Controls.Add(this.label1);
            this.Кнопки.Location = new System.Drawing.Point(61, 4);
            this.Кнопки.Name = "Кнопки";
            this.Кнопки.Padding = new System.Windows.Forms.Padding(3);
            this.Кнопки.Size = new System.Drawing.Size(1045, 75);
            this.Кнопки.TabIndex = 0;
            this.Кнопки.Text = "Кнопки";
            this.Кнопки.UseVisualStyleBackColor = true;
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(6, 6);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(75, 23);
            this.button1.TabIndex = 0;
            this.button1.Text = "Выбрать";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // button4
            // 
            this.button4.Location = new System.Drawing.Point(168, 6);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(75, 23);
            this.button4.TabIndex = 5;
            this.button4.Text = "Печать";
            this.button4.UseVisualStyleBackColor = true;
            this.button4.Click += new System.EventHandler(this.button4_Click);
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(249, 6);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(75, 23);
            this.button3.TabIndex = 2;
            this.button3.Text = "В EXCEL!";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
            // 
            // button2
            // 
            this.button2.Location = new System.Drawing.Point(87, 6);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(75, 23);
            this.button2.TabIndex = 1;
            this.button2.Text = "Закрыть";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(8, 32);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(35, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "label1";
            // 
            // ЗапросТЕКСТ
            // 
            this.ЗапросТЕКСТ.Controls.Add(this.Переделать_запрос);
            this.ЗапросТЕКСТ.Controls.Add(this.Запрос2);
            this.ЗапросТЕКСТ.Location = new System.Drawing.Point(61, 4);
            this.ЗапросТЕКСТ.Name = "ЗапросТЕКСТ";
            this.ЗапросТЕКСТ.Padding = new System.Windows.Forms.Padding(3);
            this.ЗапросТЕКСТ.Size = new System.Drawing.Size(1045, 75);
            this.ЗапросТЕКСТ.TabIndex = 1;
            this.ЗапросТЕКСТ.Text = "Запрос";
            this.ЗапросТЕКСТ.UseVisualStyleBackColor = true;
            // 
            // Переделать_запрос
            // 
            this.Переделать_запрос.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(192)))), ((int)(((byte)(255)))), ((int)(((byte)(192)))));
            this.Переделать_запрос.Location = new System.Drawing.Point(872, 2);
            this.Переделать_запрос.Name = "Переделать_запрос";
            this.Переделать_запрос.Size = new System.Drawing.Size(75, 71);
            this.Переделать_запрос.TabIndex = 1;
            this.Переделать_запрос.Text = "Послать запрос";
            this.Переделать_запрос.UseVisualStyleBackColor = false;
            this.Переделать_запрос.Click += new System.EventHandler(this.Переделать_запрос_Click);
            // 
            // Запрос2
            // 
            this.Запрос2.Location = new System.Drawing.Point(0, 0);
            this.Запрос2.Multiline = true;
            this.Запрос2.Name = "Запрос2";
            this.Запрос2.Size = new System.Drawing.Size(866, 80);
            this.Запрос2.TabIndex = 0;
            // 
            // Данные
            // 
            this.Данные.Location = new System.Drawing.Point(61, 4);
            this.Данные.Name = "Данные";
            this.Данные.Size = new System.Drawing.Size(1045, 75);
            this.Данные.TabIndex = 2;
            this.Данные.Text = "данные";
            this.Данные.UseVisualStyleBackColor = true;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(573, 13);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(0, 13);
            this.label2.TabIndex = 4;
            // 
            // timer1
            // 
            this.timer1.Tick += new System.EventHandler(this.timer1_Tick);
            // 
            // СкрытьПанель
            // 
            this.СкрытьПанель.Location = new System.Drawing.Point(330, 6);
            this.СкрытьПанель.Name = "СкрытьПанель";
            this.СкрытьПанель.Size = new System.Drawing.Size(17, 23);
            this.СкрытьПанель.TabIndex = 6;
            this.СкрытьПанель.Text = "Х";
            this.СкрытьПанель.UseVisualStyleBackColor = true;
            this.СкрытьПанель.Click += new System.EventHandler(this.СкрытьПанель_Click);
            // 
            // ЗАПРОСЫ
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1110, 401);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ЗАПРОСЫ";
            this.Text = "ЗАПРОСЫ";
            this.Load += new System.EventHandler(this.ЗАПРОСЫ_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.contextMenuStrip1.ResumeLayout(false);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            this.splitContainer1.ResumeLayout(false);
            this.tabControl1.ResumeLayout(false);
            this.Кнопки.ResumeLayout(false);
            this.Кнопки.PerformLayout();
            this.ЗапросТЕКСТ.ResumeLayout(false);
            this.ЗапросТЕКСТ.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button button4;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage Кнопки;
        private System.Windows.Forms.TabPage ЗапросТЕКСТ;
        private System.Windows.Forms.Button Переделать_запрос;
        private System.Windows.Forms.TextBox Запрос2;
        private System.Windows.Forms.TabPage Данные;
        private System.Windows.Forms.Timer timer1;
        private System.Windows.Forms.ContextMenuStrip contextMenuStrip1;
        private System.Windows.Forms.ToolStripMenuItem перевестиДанныеВExcelToolStripMenuItem;
        private System.Windows.Forms.Button СкрытьПанель;
    }
}