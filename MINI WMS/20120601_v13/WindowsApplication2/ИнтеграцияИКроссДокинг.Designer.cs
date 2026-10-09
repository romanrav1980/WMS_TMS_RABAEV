namespace WindowsApplication2
{
    partial class ИнтеграцияИКроссДокинг
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
            this.СинхронизоватьПаллеты = new System.Windows.Forms.Button();
            this.ДатаОт = new System.Windows.Forms.DateTimePicker();
            this.ДатаДо = new System.Windows.Forms.DateTimePicker();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.Паллет = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Адрес = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Рейс = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Состояние = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.НомерРейса = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.НомерАвто = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Собран = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ware_id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.чек = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.ВывестиСписокПаллет = new System.Windows.Forms.Button();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.label3 = new System.Windows.Forms.Label();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.SuspendLayout();
            // 
            // СинхронизоватьПаллеты
            // 
            this.СинхронизоватьПаллеты.Location = new System.Drawing.Point(429, 13);
            this.СинхронизоватьПаллеты.Name = "СинхронизоватьПаллеты";
            this.СинхронизоватьПаллеты.Size = new System.Drawing.Size(189, 23);
            this.СинхронизоватьПаллеты.TabIndex = 0;
            this.СинхронизоватьПаллеты.Text = "Кросс-докинг: отправить паллеты";
            this.СинхронизоватьПаллеты.UseVisualStyleBackColor = true;
            this.СинхронизоватьПаллеты.Click += new System.EventHandler(this.СинхронизоватьПаллеты_Click);
            // 
            // ДатаОт
            // 
            this.ДатаОт.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.ДатаОт.Location = new System.Drawing.Point(38, 14);
            this.ДатаОт.Name = "ДатаОт";
            this.ДатаОт.Size = new System.Drawing.Size(77, 20);
            this.ДатаОт.TabIndex = 1;
            // 
            // ДатаДо
            // 
            this.ДатаДо.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.ДатаДо.Location = new System.Drawing.Point(158, 14);
            this.ДатаДо.Name = "ДатаДо";
            this.ДатаДо.Size = new System.Drawing.Size(81, 20);
            this.ДатаДо.TabIndex = 2;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 18);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(20, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "От";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(132, 18);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(22, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "До";
            // 
            // dataGridView1
            // 
            this.dataGridView1.AllowUserToAddRows = false;
            this.dataGridView1.AllowUserToDeleteRows = false;
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Паллет,
            this.Адрес,
            this.Рейс,
            this.Состояние,
            this.НомерРейса,
            this.НомерАвто,
            this.Собран,
            this.ware_id,
            this.чек});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(882, 282);
            this.dataGridView1.TabIndex = 4;
            this.dataGridView1.CellFormatting += new System.Windows.Forms.DataGridViewCellFormattingEventHandler(this.dataGridView1_CellFormatting);
            this.dataGridView1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.dataGridView1_KeyDown);
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
            // Рейс
            // 
            this.Рейс.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Рейс.HeaderText = "Рейс";
            this.Рейс.Name = "Рейс";
            this.Рейс.ReadOnly = true;
            this.Рейс.Width = 57;
            // 
            // Состояние
            // 
            this.Состояние.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Состояние.HeaderText = "Состояние";
            this.Состояние.Name = "Состояние";
            this.Состояние.ReadOnly = true;
            this.Состояние.Width = 86;
            // 
            // НомерРейса
            // 
            this.НомерРейса.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.НомерРейса.HeaderText = "Номер Рейса";
            this.НомерРейса.Name = "НомерРейса";
            this.НомерРейса.ReadOnly = true;
            // 
            // НомерАвто
            // 
            this.НомерАвто.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.НомерАвто.HeaderText = "НомерАвто";
            this.НомерАвто.Name = "НомерАвто";
            this.НомерАвто.ReadOnly = true;
            this.НомерАвто.Width = 90;
            // 
            // Собран
            // 
            this.Собран.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Собран.HeaderText = "Собран";
            this.Собран.Name = "Собран";
            this.Собран.ReadOnly = true;
            this.Собран.Width = 69;
            // 
            // ware_id
            // 
            this.ware_id.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ware_id.HeaderText = "Склад";
            this.ware_id.Name = "ware_id";
            this.ware_id.ReadOnly = true;
            this.ware_id.Width = 63;
            // 
            // чек
            // 
            this.чек.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.чек.HeaderText = "+";
            this.чек.Name = "чек";
            this.чек.Width = 19;
            // 
            // ВывестиСписокПаллет
            // 
            this.ВывестиСписокПаллет.Location = new System.Drawing.Point(259, 13);
            this.ВывестиСписокПаллет.Name = "ВывестиСписокПаллет";
            this.ВывестиСписокПаллет.Size = new System.Drawing.Size(139, 23);
            this.ВывестиСписокПаллет.TabIndex = 5;
            this.ВывестиСписокПаллет.Text = "Вывести список паллет";
            this.ВывестиСписокПаллет.UseVisualStyleBackColor = true;
            this.ВывестиСписокПаллет.Click += new System.EventHandler(this.ВывестиСписокПаллет_Click);
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
            this.splitContainer1.Panel1.Controls.Add(this.label3);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            this.splitContainer1.Panel1.Controls.Add(this.ВывестиСписокПаллет);
            this.splitContainer1.Panel1.Controls.Add(this.СинхронизоватьПаллеты);
            this.splitContainer1.Panel1.Controls.Add(this.label2);
            this.splitContainer1.Panel1.Controls.Add(this.ДатаОт);
            this.splitContainer1.Panel1.Controls.Add(this.ДатаДо);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Size = new System.Drawing.Size(882, 331);
            this.splitContainer1.SplitterDistance = 45;
            this.splitContainer1.TabIndex = 6;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.label3.Location = new System.Drawing.Point(624, 14);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(244, 20);
            this.label3.TabIndex = 6;
            this.label3.Text = "Список не прогруженных СТ";
            // 
            // ИнтеграцияИКроссДокинг
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(882, 331);
            this.Controls.Add(this.splitContainer1);
            this.Name = "ИнтеграцияИКроссДокинг";
            this.Text = "ИнтеграцияИКроссДокинг";
            this.Load += new System.EventHandler(this.ИнтеграцияИКроссДокинг_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button СинхронизоватьПаллеты;
        private System.Windows.Forms.DateTimePicker ДатаОт;
        private System.Windows.Forms.DateTimePicker ДатаДо;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button ВывестиСписокПаллет;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.DataGridViewTextBoxColumn Паллет;
        private System.Windows.Forms.DataGridViewTextBoxColumn Адрес;
        private System.Windows.Forms.DataGridViewTextBoxColumn Рейс;
        private System.Windows.Forms.DataGridViewTextBoxColumn Состояние;
        private System.Windows.Forms.DataGridViewTextBoxColumn НомерРейса;
        private System.Windows.Forms.DataGridViewTextBoxColumn НомерАвто;
        private System.Windows.Forms.DataGridViewTextBoxColumn Собран;
        private System.Windows.Forms.DataGridViewTextBoxColumn ware_id;
        private System.Windows.Forms.DataGridViewCheckBoxColumn чек;
    }
}