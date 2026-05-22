namespace WindowsApplication2
{
    partial class VODITEL
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
            this.рейсыДаннойМашиныToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.panel1 = new System.Windows.Forms.Panel();
            this.label2 = new System.Windows.Forms.Label();
            this.НОМЕР_МАШ = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.ФИО = new System.Windows.Forms.TextBox();
            this.button2 = new System.Windows.Forms.Button();
            this.button1 = new System.Windows.Forms.Button();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.button3 = new System.Windows.Forms.Button();
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.ID = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.F = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.I = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.O = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Deleted = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.Собственный = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.TRANSPORT_NUM = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТЕЛ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ADDR = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ДоверенностьОт = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.Паспортные_данные = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.таб_номер = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.инн_орг = new System.Windows.Forms.DataGridViewTextBoxColumn();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.contextMenuStrip1.SuspendLayout();
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
            this.ID,
            this.F,
            this.I,
            this.O,
            this.Deleted,
            this.Собственный,
            this.TRANSPORT_NUM,
            this.ТЕЛ,
            this.ADDR,
            this.ДоверенностьОт,
            this.Паспортные_данные,
            this.таб_номер,
            this.инн_орг});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(1117, 471);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            this.dataGridView1.DataError += new System.Windows.Forms.DataGridViewDataErrorEventHandler(this.dataGridView1_DataError);
            this.dataGridView1.KeyDown += new System.Windows.Forms.KeyEventHandler(this.dataGridView1_KeyDown);
            // 
            // contextMenuStrip1
            // 
            this.contextMenuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.рейсыДаннойМашиныToolStripMenuItem,
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem});
            this.contextMenuStrip1.Name = "contextMenuStrip1";
            this.contextMenuStrip1.Size = new System.Drawing.Size(298, 48);
            // 
            // рейсыДаннойМашиныToolStripMenuItem
            // 
            this.рейсыДаннойМашиныToolStripMenuItem.Name = "рейсыДаннойМашиныToolStripMenuItem";
            this.рейсыДаннойМашиныToolStripMenuItem.Size = new System.Drawing.Size(297, 22);
            this.рейсыДаннойМашиныToolStripMenuItem.Text = "Рейсы данной машины";
            this.рейсыДаннойМашиныToolStripMenuItem.Click += new System.EventHandler(this.рейсыДаннойМашиныToolStripMenuItem_Click);
            // 
            // panel1
            // 
            this.panel1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(128)))), ((int)(((byte)(255)))), ((int)(((byte)(128)))));
            this.panel1.Controls.Add(this.label2);
            this.panel1.Controls.Add(this.НОМЕР_МАШ);
            this.panel1.Controls.Add(this.label1);
            this.panel1.Controls.Add(this.ФИО);
            this.panel1.Controls.Add(this.button2);
            this.panel1.Location = new System.Drawing.Point(117, 5);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(706, 39);
            this.panel1.TabIndex = 1;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(406, 12);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(89, 13);
            this.label2.TabIndex = 5;
            this.label2.Text = "Номер машины:";
            // 
            // НОМЕР_МАШ
            // 
            this.НОМЕР_МАШ.Location = new System.Drawing.Point(501, 9);
            this.НОМЕР_МАШ.Name = "НОМЕР_МАШ";
            this.НОМЕР_МАШ.Size = new System.Drawing.Size(100, 20);
            this.НОМЕР_МАШ.TabIndex = 4;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(190, 12);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(68, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "часть ФИО:";
            this.label1.Click += new System.EventHandler(this.label1_Click);
            // 
            // ФИО
            // 
            this.ФИО.Location = new System.Drawing.Point(264, 10);
            this.ФИО.Name = "ФИО";
            this.ФИО.Size = new System.Drawing.Size(126, 20);
            this.ФИО.TabIndex = 2;
            // 
            // button2
            // 
            this.button2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(192)))), ((int)(((byte)(192)))), ((int)(((byte)(0)))));
            this.button2.Location = new System.Drawing.Point(607, 7);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(86, 23);
            this.button2.TabIndex = 1;
            this.button2.Text = "Фильтр!";
            this.button2.UseVisualStyleBackColor = false;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // button1
            // 
            this.button1.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(128)))), ((int)(((byte)(0)))));
            this.button1.Location = new System.Drawing.Point(25, 12);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(86, 23);
            this.button1.TabIndex = 0;
            this.button1.Text = "Выбрать!";
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
            this.splitContainer1.Panel2.Controls.Add(this.button3);
            this.splitContainer1.Panel2.Controls.Add(this.button1);
            this.splitContainer1.Panel2.Controls.Add(this.panel1);
            this.splitContainer1.Panel2.Paint += new System.Windows.Forms.PaintEventHandler(this.splitContainer1_Panel2_Paint);
            this.splitContainer1.Size = new System.Drawing.Size(1117, 521);
            this.splitContainer1.SplitterDistance = 471;
            this.splitContainer1.TabIndex = 2;
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(892, 11);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(75, 23);
            this.button3.TabIndex = 2;
            this.button3.Text = "в Excel";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
            // 
            // закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem
            // 
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem.Name = "закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem";
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem.Size = new System.Drawing.Size(297, 22);
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem.Text = "Закачка данных и управление столбцами";
            this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem.Click += new System.EventHandler(this.закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem_Click);
            // 
            // ID
            // 
            this.ID.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ID.ContextMenuStrip = this.contextMenuStrip1;
            this.ID.HeaderText = "ID";
            this.ID.Name = "ID";
            this.ID.Width = 43;
            // 
            // F
            // 
            this.F.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.F.ContextMenuStrip = this.contextMenuStrip1;
            this.F.HeaderText = "Фамилия";
            this.F.Name = "F";
            this.F.Width = 81;
            // 
            // I
            // 
            this.I.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.I.ContextMenuStrip = this.contextMenuStrip1;
            this.I.HeaderText = "Имя";
            this.I.Name = "I";
            this.I.Width = 54;
            // 
            // O
            // 
            this.O.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.O.ContextMenuStrip = this.contextMenuStrip1;
            this.O.HeaderText = "Отчество";
            this.O.Name = "O";
            this.O.Width = 79;
            // 
            // Deleted
            // 
            this.Deleted.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Deleted.ContextMenuStrip = this.contextMenuStrip1;
            this.Deleted.HeaderText = "Уд";
            this.Deleted.Name = "Deleted";
            this.Deleted.Width = 27;
            // 
            // Собственный
            // 
            this.Собственный.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Собственный.ContextMenuStrip = this.contextMenuStrip1;
            this.Собственный.HeaderText = "СОБ";
            this.Собственный.Name = "Собственный";
            this.Собственный.Width = 35;
            // 
            // TRANSPORT_NUM
            // 
            this.TRANSPORT_NUM.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.TRANSPORT_NUM.ContextMenuStrip = this.contextMenuStrip1;
            this.TRANSPORT_NUM.HeaderText = "НомерМашины";
            this.TRANSPORT_NUM.Name = "TRANSPORT_NUM";
            this.TRANSPORT_NUM.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.TRANSPORT_NUM.Width = 109;
            // 
            // ТЕЛ
            // 
            this.ТЕЛ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ТЕЛ.ContextMenuStrip = this.contextMenuStrip1;
            this.ТЕЛ.HeaderText = "ТЕЛЕФОН";
            this.ТЕЛ.Name = "ТЕЛ";
            this.ТЕЛ.Width = 88;
            // 
            // ADDR
            // 
            this.ADDR.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ADDR.ContextMenuStrip = this.contextMenuStrip1;
            this.ADDR.HeaderText = "Адрес проживания";
            this.ADDR.Name = "ADDR";
            this.ADDR.Width = 117;
            // 
            // ДоверенностьОт
            // 
            this.ДоверенностьОт.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ДоверенностьОт.ContextMenuStrip = this.contextMenuStrip1;
            this.ДоверенностьОт.HeaderText = "ДоверенностьОТ";
            this.ДоверенностьОт.Items.AddRange(new object[] {
            "МОНЕТКА",
            "Сфера Доставки",
            "Трансгранит",
            "Перевозчик",
            "ЕСЛ",
            "ЮТК",
            "АТЛ",
            "Альфа-логистик",
            "Транстехнологии",
            "Каскад",
            "ТСУ",
            "ТСГ",
            "КапиталТренд"});
            this.ДоверенностьОт.MaxDropDownItems = 10;
            this.ДоверенностьОт.Name = "ДоверенностьОт";
            this.ДоверенностьОт.Width = 102;
            // 
            // Паспортные_данные
            // 
            this.Паспортные_данные.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Паспортные_данные.ContextMenuStrip = this.contextMenuStrip1;
            this.Паспортные_данные.HeaderText = "Паспортные_данные";
            this.Паспортные_данные.Name = "Паспортные_данные";
            this.Паспортные_данные.Width = 139;
            // 
            // таб_номер
            // 
            this.таб_номер.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.таб_номер.ContextMenuStrip = this.contextMenuStrip1;
            this.таб_номер.HeaderText = "таб_номер";
            this.таб_номер.Name = "таб_номер";
            this.таб_номер.Width = 87;
            // 
            // инн_орг
            // 
            this.инн_орг.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.инн_орг.ContextMenuStrip = this.contextMenuStrip1;
            this.инн_орг.HeaderText = "инн";
            this.инн_орг.Name = "инн_орг";
            this.инн_орг.Width = 50;
            // 
            // VODITEL
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1117, 521);
            this.Controls.Add(this.splitContainer1);
            this.Name = "VODITEL";
            this.Text = "VODITEL";
            this.Load += new System.EventHandler(this.VODITEL_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.contextMenuStrip1.ResumeLayout(false);
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.TextBox ФИО;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox НОМЕР_МАШ;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.ContextMenuStrip contextMenuStrip1;
        private System.Windows.Forms.ToolStripMenuItem рейсыДаннойМашиныToolStripMenuItem;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.ToolStripMenuItem закачкаДанныхИУправлениеСтолбцамиToolStripMenuItem;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID;
        private System.Windows.Forms.DataGridViewTextBoxColumn F;
        private System.Windows.Forms.DataGridViewTextBoxColumn I;
        private System.Windows.Forms.DataGridViewTextBoxColumn O;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Deleted;
        private System.Windows.Forms.DataGridViewCheckBoxColumn Собственный;
        private System.Windows.Forms.DataGridViewTextBoxColumn TRANSPORT_NUM;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТЕЛ;
        private System.Windows.Forms.DataGridViewTextBoxColumn ADDR;
        private System.Windows.Forms.DataGridViewComboBoxColumn ДоверенностьОт;
        private System.Windows.Forms.DataGridViewTextBoxColumn Паспортные_данные;
        private System.Windows.Forms.DataGridViewTextBoxColumn таб_номер;
        private System.Windows.Forms.DataGridViewTextBoxColumn инн_орг;
    }
}