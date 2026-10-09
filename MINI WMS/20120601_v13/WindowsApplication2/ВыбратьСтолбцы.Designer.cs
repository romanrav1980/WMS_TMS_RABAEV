namespace WindowsApplication2
{
    partial class ВыбратьСтолбцы
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
            this.checkedListBox1 = new System.Windows.Forms.CheckedListBox();
            this.OK = new System.Windows.Forms.Button();
            this.Закрыть = new System.Windows.Forms.Button();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.ПоказатьСтолбцы = new System.Windows.Forms.TabPage();
            this.Подгрузить = new System.Windows.Forms.TabPage();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.Загрузить_Excel = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.button1 = new System.Windows.Forms.Button();
            this.label2 = new System.Windows.Forms.Label();
            this.КлючиСопоставленияСтрок = new System.Windows.Forms.CheckedListBox();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.ВыгрузитьРодительскуютаблицувExcel = new System.Windows.Forms.Button();
            this.tabControl1.SuspendLayout();
            this.ПоказатьСтолбцы.SuspendLayout();
            this.Подгрузить.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.groupBox1.SuspendLayout();
            this.SuspendLayout();
            // 
            // checkedListBox1
            // 
            this.checkedListBox1.FormattingEnabled = true;
            this.checkedListBox1.Location = new System.Drawing.Point(6, 6);
            this.checkedListBox1.Name = "checkedListBox1";
            this.checkedListBox1.Size = new System.Drawing.Size(191, 274);
            this.checkedListBox1.TabIndex = 0;
            // 
            // OK
            // 
            this.OK.Location = new System.Drawing.Point(6, 286);
            this.OK.Name = "OK";
            this.OK.Size = new System.Drawing.Size(75, 23);
            this.OK.TabIndex = 1;
            this.OK.Text = "ОК";
            this.OK.UseVisualStyleBackColor = true;
            this.OK.Click += new System.EventHandler(this.OK_Click);
            // 
            // Закрыть
            // 
            this.Закрыть.Location = new System.Drawing.Point(122, 286);
            this.Закрыть.Name = "Закрыть";
            this.Закрыть.Size = new System.Drawing.Size(75, 23);
            this.Закрыть.TabIndex = 2;
            this.Закрыть.Text = "Закрыть";
            this.Закрыть.UseVisualStyleBackColor = true;
            this.Закрыть.Click += new System.EventHandler(this.Закрыть_Click);
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.ПоказатьСтолбцы);
            this.tabControl1.Controls.Add(this.Подгрузить);
            this.tabControl1.Location = new System.Drawing.Point(2, 3);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(745, 520);
            this.tabControl1.TabIndex = 3;
            // 
            // ПоказатьСтолбцы
            // 
            this.ПоказатьСтолбцы.Controls.Add(this.checkedListBox1);
            this.ПоказатьСтолбцы.Controls.Add(this.Закрыть);
            this.ПоказатьСтолбцы.Controls.Add(this.OK);
            this.ПоказатьСтолбцы.Location = new System.Drawing.Point(4, 22);
            this.ПоказатьСтолбцы.Name = "ПоказатьСтолбцы";
            this.ПоказатьСтолбцы.Padding = new System.Windows.Forms.Padding(3);
            this.ПоказатьСтолбцы.Size = new System.Drawing.Size(737, 494);
            this.ПоказатьСтолбцы.TabIndex = 0;
            this.ПоказатьСтолбцы.Text = "Показать";
            this.ПоказатьСтолбцы.UseVisualStyleBackColor = true;
            // 
            // Подгрузить
            // 
            this.Подгрузить.Controls.Add(this.ВыгрузитьРодительскуютаблицувExcel);
            this.Подгрузить.Controls.Add(this.groupBox1);
            this.Подгрузить.Controls.Add(this.button1);
            this.Подгрузить.Controls.Add(this.label2);
            this.Подгрузить.Controls.Add(this.label1);
            this.Подгрузить.Controls.Add(this.Загрузить_Excel);
            this.Подгрузить.Controls.Add(this.dataGridView1);
            this.Подгрузить.Location = new System.Drawing.Point(4, 22);
            this.Подгрузить.Name = "Подгрузить";
            this.Подгрузить.Padding = new System.Windows.Forms.Padding(3);
            this.Подгрузить.Size = new System.Drawing.Size(737, 494);
            this.Подгрузить.TabIndex = 1;
            this.Подгрузить.Text = "Подгрузить";
            this.Подгрузить.UseVisualStyleBackColor = true;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Location = new System.Drawing.Point(6, 3);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(728, 378);
            this.dataGridView1.TabIndex = 0;
            // 
            // Загрузить_Excel
            // 
            this.Загрузить_Excel.Location = new System.Drawing.Point(37, 387);
            this.Загрузить_Excel.Name = "Загрузить_Excel";
            this.Загрузить_Excel.Size = new System.Drawing.Size(212, 23);
            this.Загрузить_Excel.TabIndex = 1;
            this.Загрузить_Excel.Text = "Загрузить файл Excel в таблицу";
            this.Загрузить_Excel.UseVisualStyleBackColor = true;
            this.Загрузить_Excel.Click += new System.EventHandler(this.Загрузить_Excel_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.label1.Location = new System.Drawing.Point(6, 390);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(25, 20);
            this.label1.TabIndex = 2;
            this.label1.Text = "1)";
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(37, 422);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(328, 23);
            this.button1.TabIndex = 3;
            this.button1.Text = "Иммитировать ввод с клавиатуры согласно данных таблицы";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(204)));
            this.label2.Location = new System.Drawing.Point(6, 422);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(25, 20);
            this.label2.TabIndex = 2;
            this.label2.Text = "2)";
            // 
            // КлючиСопоставленияСтрок
            // 
            this.КлючиСопоставленияСтрок.FormattingEnabled = true;
            this.КлючиСопоставленияСтрок.Location = new System.Drawing.Point(6, 19);
            this.КлючиСопоставленияСтрок.Name = "КлючиСопоставленияСтрок";
            this.КлючиСопоставленияСтрок.Size = new System.Drawing.Size(191, 79);
            this.КлючиСопоставленияСтрок.TabIndex = 4;
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.КлючиСопоставленияСтрок);
            this.groupBox1.Location = new System.Drawing.Point(531, 385);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(203, 109);
            this.groupBox1.TabIndex = 5;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Ключи сопоставления строк";
            // 
            // ВыгрузитьРодительскуютаблицувExcel
            // 
            this.ВыгрузитьРодительскуютаблицувExcel.Location = new System.Drawing.Point(37, 460);
            this.ВыгрузитьРодительскуютаблицувExcel.Name = "ВыгрузитьРодительскуютаблицувExcel";
            this.ВыгрузитьРодительскуютаблицувExcel.Size = new System.Drawing.Size(328, 23);
            this.ВыгрузитьРодительскуютаблицувExcel.TabIndex = 6;
            this.ВыгрузитьРодительскуютаблицувExcel.Text = "Выгрузить Родительскую таблицу в Excel";
            this.ВыгрузитьРодительскуютаблицувExcel.UseVisualStyleBackColor = true;
            this.ВыгрузитьРодительскуютаблицувExcel.Click += new System.EventHandler(this.ВыгрузитьРодительскуютаблицувExcel_Click);
            // 
            // ВыбратьСтолбцы
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(748, 524);
            this.Controls.Add(this.tabControl1);
            this.Name = "ВыбратьСтолбцы";
            this.Text = "ВыбратьСтолбцы";
            this.Load += new System.EventHandler(this.ВыбратьСтолбцы_Load);
            this.tabControl1.ResumeLayout(false);
            this.ПоказатьСтолбцы.ResumeLayout(false);
            this.Подгрузить.ResumeLayout(false);
            this.Подгрузить.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.groupBox1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        public System.Windows.Forms.CheckedListBox checkedListBox1;
        private System.Windows.Forms.Button OK;
        private System.Windows.Forms.Button Закрыть;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage ПоказатьСтолбцы;
        private System.Windows.Forms.TabPage Подгрузить;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button Загрузить_Excel;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.CheckedListBox КлючиСопоставленияСтрок;
        private System.Windows.Forms.Button ВыгрузитьРодительскуютаблицувExcel;
    }
}