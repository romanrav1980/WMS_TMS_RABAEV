namespace WindowsApplication2
{
    partial class BillingTransport
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
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle1 = new System.Windows.Forms.DataGridViewCellStyle();
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle2 = new System.Windows.Forms.DataGridViewCellStyle();
            System.Windows.Forms.DataGridViewCellStyle dataGridViewCellStyle3 = new System.Windows.Forms.DataGridViewCellStyle();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.Filter_company = new System.Windows.Forms.ComboBox();
            this.button2 = new System.Windows.Forms.Button();
            this.dateTimePicker2 = new System.Windows.Forms.DateTimePicker();
            this.dateTimePicker1 = new System.Windows.Forms.DateTimePicker();
            this.button1 = new System.Windows.Forms.Button();
            this.splitContainer2 = new System.Windows.Forms.SplitContainer();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.ID9 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.context_bills = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.пересчитатьВсеРейсыToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.закрытьToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.установитьОплатуToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.открытьToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.Num = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Company = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.ДатаСчета = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ДатаОт = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ДатаДо = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Сумма = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Закрыт = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.Оплачен = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.Номер_Плат = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridView2 = new System.Windows.Forms.DataGridView();
            this.ID1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.context_рейсы2 = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.рассчитатьСтоимостьРейсаToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.ВКЛ = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.Сумма2 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Регион = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТипТС = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТРАНСП = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Дата1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Водитель = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Вес = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.BILL_ID = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Часы = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.печатьToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.splitContainer2.Panel1.SuspendLayout();
            this.splitContainer2.Panel2.SuspendLayout();
            this.splitContainer2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.context_bills.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView2)).BeginInit();
            this.context_рейсы2.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.textBox1);
            this.splitContainer1.Panel1.Controls.Add(this.label3);
            this.splitContainer1.Panel1.Controls.Add(this.label2);
            this.splitContainer1.Panel1.Controls.Add(this.label1);
            this.splitContainer1.Panel1.Controls.Add(this.Filter_company);
            this.splitContainer1.Panel1.Controls.Add(this.button2);
            this.splitContainer1.Panel1.Controls.Add(this.dateTimePicker2);
            this.splitContainer1.Panel1.Controls.Add(this.dateTimePicker1);
            this.splitContainer1.Panel1.Controls.Add(this.button1);
            this.splitContainer1.Panel1.Paint += new System.Windows.Forms.PaintEventHandler(this.splitContainer1_Panel1_Paint);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.splitContainer2);
            this.splitContainer1.Size = new System.Drawing.Size(1030, 498);
            this.splitContainer1.SplitterDistance = 55;
            this.splitContainer1.TabIndex = 0;
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(794, 5);
            this.textBox1.Multiline = true;
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(100, 45);
            this.textBox1.TabIndex = 8;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(263, 9);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(57, 13);
            this.label3.TabIndex = 7;
            this.label3.Text = "компания";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(106, 35);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(45, 13);
            this.label2.TabIndex = 6;
            this.label2.Text = "дата до";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(106, 8);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(44, 13);
            this.label1.TabIndex = 5;
            this.label1.Text = "дата от";
            // 
            // Filter_company
            // 
            this.Filter_company.FormattingEnabled = true;
            this.Filter_company.Location = new System.Drawing.Point(326, 4);
            this.Filter_company.Name = "Filter_company";
            this.Filter_company.Size = new System.Drawing.Size(121, 21);
            this.Filter_company.TabIndex = 4;
            // 
            // button2
            // 
            this.button2.BackColor = System.Drawing.SystemColors.InactiveCaption;
            this.button2.Location = new System.Drawing.Point(900, 4);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(127, 46);
            this.button2.TabIndex = 3;
            this.button2.Text = "< Добавить рейсы с данными УИДами в счет";
            this.button2.UseVisualStyleBackColor = false;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // dateTimePicker2
            // 
            this.dateTimePicker2.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dateTimePicker2.Location = new System.Drawing.Point(156, 31);
            this.dateTimePicker2.Name = "dateTimePicker2";
            this.dateTimePicker2.Size = new System.Drawing.Size(80, 20);
            this.dateTimePicker2.TabIndex = 2;
            // 
            // dateTimePicker1
            // 
            this.dateTimePicker1.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dateTimePicker1.Location = new System.Drawing.Point(156, 5);
            this.dateTimePicker1.Name = "dateTimePicker1";
            this.dateTimePicker1.Size = new System.Drawing.Size(80, 20);
            this.dateTimePicker1.TabIndex = 1;
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(12, 4);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(75, 35);
            this.button1.TabIndex = 0;
            this.button1.Text = "подгрузить";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // splitContainer2
            // 
            this.splitContainer2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer2.Location = new System.Drawing.Point(0, 0);
            this.splitContainer2.Name = "splitContainer2";
            this.splitContainer2.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainer2.Panel1
            // 
            this.splitContainer2.Panel1.Controls.Add(this.dataGridView1);
            // 
            // splitContainer2.Panel2
            // 
            this.splitContainer2.Panel2.Controls.Add(this.dataGridView2);
            this.splitContainer2.Size = new System.Drawing.Size(1030, 439);
            this.splitContainer2.SplitterDistance = 259;
            this.splitContainer2.TabIndex = 1;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ID9,
            this.Num,
            this.Company,
            this.ДатаСчета,
            this.ДатаОт,
            this.ДатаДо,
            this.Сумма,
            this.Закрыт,
            this.Оплачен,
            this.Номер_Плат});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(1030, 259);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            this.dataGridView1.CellEnter += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEnter);
            // 
            // ID9
            // 
            this.ID9.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ID9.ContextMenuStrip = this.context_bills;
            this.ID9.HeaderText = "ID";
            this.ID9.Name = "ID9";
            this.ID9.ReadOnly = true;
            this.ID9.Width = 43;
            // 
            // context_bills
            // 
            this.context_bills.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.пересчитатьВсеРейсыToolStripMenuItem,
            this.закрытьToolStripMenuItem,
            this.установитьОплатуToolStripMenuItem,
            this.открытьToolStripMenuItem,
            this.печатьToolStripMenuItem});
            this.context_bills.Name = "context_bills";
            this.context_bills.Size = new System.Drawing.Size(296, 136);
            // 
            // пересчитатьВсеРейсыToolStripMenuItem
            // 
            this.пересчитатьВсеРейсыToolStripMenuItem.Name = "пересчитатьВсеРейсыToolStripMenuItem";
            this.пересчитатьВсеРейсыToolStripMenuItem.Size = new System.Drawing.Size(295, 22);
            this.пересчитатьВсеРейсыToolStripMenuItem.Text = "Пересчитать все не рассчитанные рейсы";
            this.пересчитатьВсеРейсыToolStripMenuItem.Click += new System.EventHandler(this.пересчитатьВсеРейсыToolStripMenuItem_Click);
            // 
            // закрытьToolStripMenuItem
            // 
            this.закрытьToolStripMenuItem.Name = "закрытьToolStripMenuItem";
            this.закрытьToolStripMenuItem.Size = new System.Drawing.Size(295, 22);
            this.закрытьToolStripMenuItem.Text = "Закрыть";
            this.закрытьToolStripMenuItem.Click += new System.EventHandler(this.закрытьToolStripMenuItem_Click);
            // 
            // установитьОплатуToolStripMenuItem
            // 
            this.установитьОплатуToolStripMenuItem.Name = "установитьОплатуToolStripMenuItem";
            this.установитьОплатуToolStripMenuItem.Size = new System.Drawing.Size(295, 22);
            this.установитьОплатуToolStripMenuItem.Text = "Установить оплату";
            this.установитьОплатуToolStripMenuItem.Click += new System.EventHandler(this.установитьОплатуToolStripMenuItem_Click);
            // 
            // открытьToolStripMenuItem
            // 
            this.открытьToolStripMenuItem.Name = "открытьToolStripMenuItem";
            this.открытьToolStripMenuItem.Size = new System.Drawing.Size(295, 22);
            this.открытьToolStripMenuItem.Text = "Открыть";
            this.открытьToolStripMenuItem.Click += new System.EventHandler(this.открытьToolStripMenuItem_Click);
            // 
            // Num
            // 
            this.Num.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Num.ContextMenuStrip = this.context_bills;
            this.Num.HeaderText = "Num";
            this.Num.Name = "Num";
            this.Num.Width = 54;
            // 
            // Company
            // 
            this.Company.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Company.ContextMenuStrip = this.context_bills;
            this.Company.HeaderText = "Company";
            this.Company.Name = "Company";
            this.Company.Width = 57;
            // 
            // ДатаСчета
            // 
            this.ДатаСчета.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ДатаСчета.ContextMenuStrip = this.context_bills;
            dataGridViewCellStyle1.Format = "d";
            dataGridViewCellStyle1.NullValue = null;
            this.ДатаСчета.DefaultCellStyle = dataGridViewCellStyle1;
            this.ДатаСчета.HeaderText = "ДатаСчета";
            this.ДатаСчета.Name = "ДатаСчета";
            this.ДатаСчета.Width = 87;
            // 
            // ДатаОт
            // 
            this.ДатаОт.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ДатаОт.ContextMenuStrip = this.context_bills;
            dataGridViewCellStyle2.Format = "d";
            dataGridViewCellStyle2.NullValue = null;
            this.ДатаОт.DefaultCellStyle = dataGridViewCellStyle2;
            this.ДатаОт.HeaderText = "ДатаОт";
            this.ДатаОт.Name = "ДатаОт";
            this.ДатаОт.Width = 71;
            // 
            // ДатаДо
            // 
            this.ДатаДо.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ДатаДо.ContextMenuStrip = this.context_bills;
            dataGridViewCellStyle3.Format = "d";
            dataGridViewCellStyle3.NullValue = null;
            this.ДатаДо.DefaultCellStyle = dataGridViewCellStyle3;
            this.ДатаДо.HeaderText = "ДатаДо";
            this.ДатаДо.Name = "ДатаДо";
            this.ДатаДо.Width = 73;
            // 
            // Сумма
            // 
            this.Сумма.ContextMenuStrip = this.context_bills;
            this.Сумма.HeaderText = "Сумма";
            this.Сумма.Name = "Сумма";
            this.Сумма.ReadOnly = true;
            // 
            // Закрыт
            // 
            this.Закрыт.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Закрыт.ContextMenuStrip = this.context_bills;
            this.Закрыт.HeaderText = "закрыт";
            this.Закрыт.Name = "Закрыт";
            this.Закрыт.ReadOnly = true;
            this.Закрыт.Width = 50;
            // 
            // Оплачен
            // 
            this.Оплачен.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Оплачен.ContextMenuStrip = this.context_bills;
            this.Оплачен.HeaderText = "Оплачен";
            this.Оплачен.Name = "Оплачен";
            this.Оплачен.ReadOnly = true;
            this.Оплачен.Width = 56;
            // 
            // Номер_Плат
            // 
            this.Номер_Плат.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Номер_Плат.ContextMenuStrip = this.context_bills;
            this.Номер_Плат.HeaderText = "Номер_Плат";
            this.Номер_Плат.Name = "Номер_Плат";
            this.Номер_Плат.Width = 97;
            // 
            // dataGridView2
            // 
            this.dataGridView2.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView2.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ID1,
            this.ВКЛ,
            this.Сумма2,
            this.Регион,
            this.ТипТС,
            this.ТРАНСП,
            this.Дата1,
            this.Водитель,
            this.Вес,
            this.BILL_ID,
            this.Часы});
            this.dataGridView2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView2.Location = new System.Drawing.Point(0, 0);
            this.dataGridView2.Name = "dataGridView2";
            this.dataGridView2.Size = new System.Drawing.Size(1030, 176);
            this.dataGridView2.TabIndex = 0;
            this.dataGridView2.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView2_CellEndEdit);
            // 
            // ID1
            // 
            this.ID1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ID1.ContextMenuStrip = this.context_рейсы2;
            this.ID1.HeaderText = "ID";
            this.ID1.Name = "ID1";
            this.ID1.ReadOnly = true;
            this.ID1.Width = 43;
            // 
            // context_рейсы2
            // 
            this.context_рейсы2.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.рассчитатьСтоимостьРейсаToolStripMenuItem});
            this.context_рейсы2.Name = "context_рейсы2";
            this.context_рейсы2.Size = new System.Drawing.Size(231, 26);
            // 
            // рассчитатьСтоимостьРейсаToolStripMenuItem
            // 
            this.рассчитатьСтоимостьРейсаToolStripMenuItem.Name = "рассчитатьСтоимостьРейсаToolStripMenuItem";
            this.рассчитатьСтоимостьРейсаToolStripMenuItem.Size = new System.Drawing.Size(230, 22);
            this.рассчитатьСтоимостьРейсаToolStripMenuItem.Text = "Рассчитать стоимость рейса";
            this.рассчитатьСтоимостьРейсаToolStripMenuItem.Click += new System.EventHandler(this.рассчитатьСтоимостьРейсаToolStripMenuItem_Click);
            // 
            // ВКЛ
            // 
            this.ВКЛ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ВКЛ.ContextMenuStrip = this.context_рейсы2;
            this.ВКЛ.HeaderText = "ВКЛ";
            this.ВКЛ.Name = "ВКЛ";
            this.ВКЛ.Width = 35;
            // 
            // Сумма2
            // 
            this.Сумма2.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Сумма2.ContextMenuStrip = this.context_рейсы2;
            this.Сумма2.HeaderText = "Сумма";
            this.Сумма2.Name = "Сумма2";
            this.Сумма2.ReadOnly = true;
            this.Сумма2.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.Сумма2.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.NotSortable;
            this.Сумма2.Width = 47;
            // 
            // Регион
            // 
            this.Регион.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Регион.ContextMenuStrip = this.context_рейсы2;
            this.Регион.HeaderText = "Регион";
            this.Регион.Name = "Регион";
            this.Регион.ReadOnly = true;
            this.Регион.Width = 68;
            // 
            // ТипТС
            // 
            this.ТипТС.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ТипТС.ContextMenuStrip = this.context_рейсы2;
            this.ТипТС.HeaderText = "ТипТС";
            this.ТипТС.Name = "ТипТС";
            this.ТипТС.ReadOnly = true;
            this.ТипТС.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.ТипТС.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.NotSortable;
            this.ТипТС.Width = 46;
            // 
            // ТРАНСП
            // 
            this.ТРАНСП.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ТРАНСП.ContextMenuStrip = this.context_рейсы2;
            this.ТРАНСП.HeaderText = "ТРАНСП";
            this.ТРАНСП.Name = "ТРАНСП";
            this.ТРАНСП.ReadOnly = true;
            this.ТРАНСП.Width = 76;
            // 
            // Дата1
            // 
            this.Дата1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Дата1.ContextMenuStrip = this.context_рейсы2;
            this.Дата1.HeaderText = "Дата";
            this.Дата1.Name = "Дата1";
            this.Дата1.ReadOnly = true;
            this.Дата1.Width = 58;
            // 
            // Водитель
            // 
            this.Водитель.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Водитель.ContextMenuStrip = this.context_рейсы2;
            this.Водитель.HeaderText = "Водитель";
            this.Водитель.Name = "Водитель";
            this.Водитель.ReadOnly = true;
            this.Водитель.Width = 80;
            // 
            // Вес
            // 
            this.Вес.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Вес.ContextMenuStrip = this.context_рейсы2;
            this.Вес.HeaderText = "Вес";
            this.Вес.Name = "Вес";
            this.Вес.ReadOnly = true;
            this.Вес.Width = 51;
            // 
            // BILL_ID
            // 
            this.BILL_ID.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.BILL_ID.ContextMenuStrip = this.context_рейсы2;
            this.BILL_ID.HeaderText = "BILL_ID";
            this.BILL_ID.Name = "BILL_ID";
            this.BILL_ID.ReadOnly = true;
            this.BILL_ID.Width = 71;
            // 
            // Часы
            // 
            this.Часы.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Часы.HeaderText = "Время в часах";
            this.Часы.Name = "Часы";
            this.Часы.Width = 71;
            // 
            // печатьToolStripMenuItem
            // 
            this.печатьToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem});
            this.печатьToolStripMenuItem.Name = "печатьToolStripMenuItem";
            this.печатьToolStripMenuItem.Size = new System.Drawing.Size(295, 22);
            this.печатьToolStripMenuItem.Text = "Печать";
            // 
            // распечататьРеестрРейсовПоСчетуToolStripMenuItem
            // 
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem.Name = "распечататьРеестрРейсовПоСчетуToolStripMenuItem";
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem.Size = new System.Drawing.Size(273, 22);
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem.Text = "Распечатать реестр рейсов по счету";
            this.распечататьРеестрРейсовПоСчетуToolStripMenuItem.Click += new System.EventHandler(this.распечататьРеестрРейсовПоСчетуToolStripMenuItem_Click);
            // 
            // BillingTransport
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1030, 498);
            this.Controls.Add(this.splitContainer1);
            this.Name = "BillingTransport";
            this.Text = "BillingTransport";
            this.Load += new System.EventHandler(this.BillingTransport_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel1.PerformLayout();
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.splitContainer2.Panel1.ResumeLayout(false);
            this.splitContainer2.Panel2.ResumeLayout(false);
            this.splitContainer2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.context_bills.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView2)).EndInit();
            this.context_рейсы2.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.DateTimePicker dateTimePicker2;
        private System.Windows.Forms.DateTimePicker dateTimePicker1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.ComboBox Filter_company;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.SplitContainer splitContainer2;
        private System.Windows.Forms.DataGridView dataGridView2;
        private System.Windows.Forms.ContextMenuStrip context_bills;
        private System.Windows.Forms.ToolStripMenuItem пересчитатьВсеРейсыToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem закрытьToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem установитьОплатуToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem открытьToolStripMenuItem;
        private System.Windows.Forms.ContextMenuStrip context_рейсы2;
        private System.Windows.Forms.ToolStripMenuItem рассчитатьСтоимостьРейсаToolStripMenuItem;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID1;
        private System.Windows.Forms.DataGridViewCheckBoxColumn ВКЛ;
        private System.Windows.Forms.DataGridViewTextBoxColumn Сумма2;
        private System.Windows.Forms.DataGridViewTextBoxColumn Регион;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТипТС;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТРАНСП;
        private System.Windows.Forms.DataGridViewTextBoxColumn Дата1;
        private System.Windows.Forms.DataGridViewTextBoxColumn Водитель;
        private System.Windows.Forms.DataGridViewTextBoxColumn Вес;
        private System.Windows.Forms.DataGridViewTextBoxColumn BILL_ID;
        private System.Windows.Forms.DataGridViewTextBoxColumn Часы;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID9;
        private System.Windows.Forms.DataGridViewTextBoxColumn Num;
        private System.Windows.Forms.DataGridViewComboBoxColumn Company;
        private System.Windows.Forms.DataGridViewTextBoxColumn ДатаСчета;
        private System.Windows.Forms.DataGridViewTextBoxColumn ДатаОт;
        private System.Windows.Forms.DataGridViewTextBoxColumn ДатаДо;
        private System.Windows.Forms.DataGridViewTextBoxColumn Сумма;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Закрыт;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Оплачен;
        private System.Windows.Forms.DataGridViewTextBoxColumn Номер_Плат;
        private System.Windows.Forms.ToolStripMenuItem печатьToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem распечататьРеестрРейсовПоСчетуToolStripMenuItem;
    }
}