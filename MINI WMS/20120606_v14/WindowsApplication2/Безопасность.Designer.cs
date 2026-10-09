namespace WindowsApplication2
{
    partial class Безопасность
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
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.CONDITION = new System.Windows.Forms.TextBox();
            this.TRANSPORT = new System.Windows.Forms.TextBox();
            this.FIO = new System.Windows.Forms.TextBox();
            this.DOVERENNOST_OT = new System.Windows.Forms.TextBox();
            this.TEL = new System.Windows.Forms.TextBox();
            this.Состояние = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.PASSPORT = new System.Windows.Forms.TextBox();
            this.ADDR = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.ID_LABEL = new System.Windows.Forms.Label();
            this.ID_ = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.ВидДокумента = new System.Windows.Forms.TextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabPage1 = new System.Windows.Forms.TabPage();
            this.tabPage2 = new System.Windows.Forms.TabPage();
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.ВызванныеПриходыУбирать = new System.Windows.Forms.CheckBox();
            this.НазначитьКПП2 = new System.Windows.Forms.Button();
            this.НазначитьКПП1 = new System.Windows.Forms.Button();
            this.ОбновитьСписокПриходов = new System.Windows.Forms.Button();
            this.ПП = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.УИД = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ПОСТАВЩИК = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ДОК = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.МАШИНА = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.OHRANA_KPP = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТЕЛ_ВОДИТЕЛЯ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.СКЛАД = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ПРИОРИТЕТ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Время_Вызова_на_док = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Новый = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.tabControl1.SuspendLayout();
            this.tabPage1.SuspendLayout();
            this.tabPage2.SuspendLayout();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.SuspendLayout();
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(349, 14);
            this.textBox1.Multiline = true;
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(164, 216);
            this.textBox1.TabIndex = 0;
            this.textBox1.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            this.textBox1.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.textBox1_KeyPress);
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(168, 240);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(175, 23);
            this.button1.TabIndex = 1;
            this.button1.Text = "ВЫПУСТИТЬ МАШИНУ";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Visible = false;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // CONDITION
            // 
            this.CONDITION.Enabled = false;
            this.CONDITION.Location = new System.Drawing.Point(73, 11);
            this.CONDITION.Name = "CONDITION";
            this.CONDITION.ReadOnly = true;
            this.CONDITION.Size = new System.Drawing.Size(270, 20);
            this.CONDITION.TabIndex = 2;
            // 
            // TRANSPORT
            // 
            this.TRANSPORT.Enabled = false;
            this.TRANSPORT.Location = new System.Drawing.Point(73, 37);
            this.TRANSPORT.Name = "TRANSPORT";
            this.TRANSPORT.ReadOnly = true;
            this.TRANSPORT.Size = new System.Drawing.Size(270, 20);
            this.TRANSPORT.TabIndex = 2;
            // 
            // FIO
            // 
            this.FIO.Enabled = false;
            this.FIO.Location = new System.Drawing.Point(73, 61);
            this.FIO.Name = "FIO";
            this.FIO.ReadOnly = true;
            this.FIO.Size = new System.Drawing.Size(270, 20);
            this.FIO.TabIndex = 2;
            // 
            // DOVERENNOST_OT
            // 
            this.DOVERENNOST_OT.Enabled = false;
            this.DOVERENNOST_OT.Location = new System.Drawing.Point(73, 87);
            this.DOVERENNOST_OT.Name = "DOVERENNOST_OT";
            this.DOVERENNOST_OT.ReadOnly = true;
            this.DOVERENNOST_OT.Size = new System.Drawing.Size(270, 20);
            this.DOVERENNOST_OT.TabIndex = 2;
            // 
            // TEL
            // 
            this.TEL.Enabled = false;
            this.TEL.Location = new System.Drawing.Point(73, 113);
            this.TEL.Name = "TEL";
            this.TEL.ReadOnly = true;
            this.TEL.Size = new System.Drawing.Size(270, 20);
            this.TEL.TabIndex = 2;
            // 
            // Состояние
            // 
            this.Состояние.AutoSize = true;
            this.Состояние.Location = new System.Drawing.Point(6, 14);
            this.Состояние.Name = "Состояние";
            this.Состояние.Size = new System.Drawing.Size(61, 13);
            this.Состояние.TabIndex = 3;
            this.Состояние.Text = "Состояние";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(6, 40);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(61, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "Транспорт";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(6, 64);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(34, 13);
            this.label2.TabIndex = 3;
            this.label2.Text = "ФИО";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(6, 87);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(58, 13);
            this.label3.TabIndex = 3;
            this.label3.Text = "Компания";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(6, 116);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(29, 13);
            this.label4.TabIndex = 3;
            this.label4.Text = "ТЕЛ";
            // 
            // PASSPORT
            // 
            this.PASSPORT.Enabled = false;
            this.PASSPORT.Location = new System.Drawing.Point(73, 139);
            this.PASSPORT.Name = "PASSPORT";
            this.PASSPORT.ReadOnly = true;
            this.PASSPORT.Size = new System.Drawing.Size(270, 20);
            this.PASSPORT.TabIndex = 2;
            // 
            // ADDR
            // 
            this.ADDR.Enabled = false;
            this.ADDR.Location = new System.Drawing.Point(73, 165);
            this.ADDR.Name = "ADDR";
            this.ADDR.ReadOnly = true;
            this.ADDR.Size = new System.Drawing.Size(270, 20);
            this.ADDR.TabIndex = 2;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(6, 139);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(50, 13);
            this.label5.TabIndex = 3;
            this.label5.Text = "Паспорт";
            // 
            // ID_LABEL
            // 
            this.ID_LABEL.AutoSize = true;
            this.ID_LABEL.Location = new System.Drawing.Point(6, 192);
            this.ID_LABEL.Name = "ID_LABEL";
            this.ID_LABEL.Size = new System.Drawing.Size(18, 13);
            this.ID_LABEL.TabIndex = 3;
            this.ID_LABEL.Text = "ID";
            // 
            // ID_
            // 
            this.ID_.Enabled = false;
            this.ID_.Location = new System.Drawing.Point(73, 189);
            this.ID_.Name = "ID_";
            this.ID_.ReadOnly = true;
            this.ID_.Size = new System.Drawing.Size(270, 20);
            this.ID_.TabIndex = 2;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(6, 168);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(38, 13);
            this.label6.TabIndex = 3;
            this.label6.Text = "Адрес";
            // 
            // ВидДокумента
            // 
            this.ВидДокумента.Enabled = false;
            this.ВидДокумента.Location = new System.Drawing.Point(95, 214);
            this.ВидДокумента.Name = "ВидДокумента";
            this.ВидДокумента.ReadOnly = true;
            this.ВидДокумента.Size = new System.Drawing.Size(248, 20);
            this.ВидДокумента.TabIndex = 2;
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(6, 217);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(83, 13);
            this.label7.TabIndex = 3;
            this.label7.Text = "Вид документа";
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.tabPage1);
            this.tabControl1.Controls.Add(this.tabPage2);
            this.tabControl1.Location = new System.Drawing.Point(4, 6);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(1129, 533);
            this.tabControl1.TabIndex = 4;
            // 
            // tabPage1
            // 
            this.tabPage1.Controls.Add(this.Состояние);
            this.tabPage1.Controls.Add(this.label6);
            this.tabPage1.Controls.Add(this.textBox1);
            this.tabPage1.Controls.Add(this.label7);
            this.tabPage1.Controls.Add(this.button1);
            this.tabPage1.Controls.Add(this.ID_LABEL);
            this.tabPage1.Controls.Add(this.CONDITION);
            this.tabPage1.Controls.Add(this.label5);
            this.tabPage1.Controls.Add(this.TRANSPORT);
            this.tabPage1.Controls.Add(this.label4);
            this.tabPage1.Controls.Add(this.FIO);
            this.tabPage1.Controls.Add(this.label3);
            this.tabPage1.Controls.Add(this.DOVERENNOST_OT);
            this.tabPage1.Controls.Add(this.label2);
            this.tabPage1.Controls.Add(this.TEL);
            this.tabPage1.Controls.Add(this.label1);
            this.tabPage1.Controls.Add(this.PASSPORT);
            this.tabPage1.Controls.Add(this.ADDR);
            this.tabPage1.Controls.Add(this.ВидДокумента);
            this.tabPage1.Controls.Add(this.ID_);
            this.tabPage1.Location = new System.Drawing.Point(4, 22);
            this.tabPage1.Name = "tabPage1";
            this.tabPage1.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage1.Size = new System.Drawing.Size(1121, 507);
            this.tabPage1.TabIndex = 0;
            this.tabPage1.Text = "Выпуск";
            this.tabPage1.UseVisualStyleBackColor = true;
            // 
            // tabPage2
            // 
            this.tabPage2.Controls.Add(this.splitContainer1);
            this.tabPage2.Location = new System.Drawing.Point(4, 22);
            this.tabPage2.Name = "tabPage2";
            this.tabPage2.Padding = new System.Windows.Forms.Padding(3);
            this.tabPage2.Size = new System.Drawing.Size(1121, 507);
            this.tabPage2.TabIndex = 1;
            this.tabPage2.Text = "Приходы";
            this.tabPage2.UseVisualStyleBackColor = true;
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.Location = new System.Drawing.Point(3, 3);
            this.splitContainer1.Name = "splitContainer1";
            this.splitContainer1.Orientation = System.Windows.Forms.Orientation.Horizontal;
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.dataGridView1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.ВызванныеПриходыУбирать);
            this.splitContainer1.Panel2.Controls.Add(this.НазначитьКПП2);
            this.splitContainer1.Panel2.Controls.Add(this.НазначитьКПП1);
            this.splitContainer1.Panel2.Controls.Add(this.ОбновитьСписокПриходов);
            this.splitContainer1.Size = new System.Drawing.Size(1115, 501);
            this.splitContainer1.SplitterDistance = 444;
            this.splitContainer1.TabIndex = 1;
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ПП,
            this.УИД,
            this.ПОСТАВЩИК,
            this.ДОК,
            this.МАШИНА,
            this.OHRANA_KPP,
            this.ТЕЛ_ВОДИТЕЛЯ,
            this.СКЛАД,
            this.ПРИОРИТЕТ,
            this.Время_Вызова_на_док,
            this.Новый});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(1115, 444);
            this.dataGridView1.TabIndex = 0;
            // 
            // ВызванныеПриходыУбирать
            // 
            this.ВызванныеПриходыУбирать.AutoSize = true;
            this.ВызванныеПриходыУбирать.Location = new System.Drawing.Point(84, 6);
            this.ВызванныеПриходыУбирать.Name = "ВызванныеПриходыУбирать";
            this.ВызванныеПриходыУбирать.Size = new System.Drawing.Size(139, 17);
            this.ВызванныеПриходыУбирать.TabIndex = 2;
            this.ВызванныеПриходыУбирать.Text = "Только не вызванные";
            this.ВызванныеПриходыУбирать.UseVisualStyleBackColor = true;
            // 
            // НазначитьКПП2
            // 
            this.НазначитьКПП2.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(128)))), ((int)(((byte)(0)))));
            this.НазначитьКПП2.Location = new System.Drawing.Point(837, 4);
            this.НазначитьКПП2.Name = "НазначитьКПП2";
            this.НазначитьКПП2.Size = new System.Drawing.Size(129, 23);
            this.НазначитьКПП2.TabIndex = 1;
            this.НазначитьКПП2.Text = "Назначить КПП2";
            this.НазначитьКПП2.UseVisualStyleBackColor = false;
            this.НазначитьКПП2.Click += new System.EventHandler(this.НазначитьКПП2_Click);
            // 
            // НазначитьКПП1
            // 
            this.НазначитьКПП1.BackColor = System.Drawing.Color.Lime;
            this.НазначитьКПП1.Location = new System.Drawing.Point(702, 4);
            this.НазначитьКПП1.Name = "НазначитьКПП1";
            this.НазначитьКПП1.Size = new System.Drawing.Size(129, 23);
            this.НазначитьКПП1.TabIndex = 1;
            this.НазначитьКПП1.Text = "Назначить КПП1";
            this.НазначитьКПП1.UseVisualStyleBackColor = false;
            this.НазначитьКПП1.Click += new System.EventHandler(this.НазначитьКПП1_Click);
            // 
            // ОбновитьСписокПриходов
            // 
            this.ОбновитьСписокПриходов.Location = new System.Drawing.Point(3, 2);
            this.ОбновитьСписокПриходов.Name = "ОбновитьСписокПриходов";
            this.ОбновитьСписокПриходов.Size = new System.Drawing.Size(75, 23);
            this.ОбновитьСписокПриходов.TabIndex = 0;
            this.ОбновитьСписокПриходов.Text = "Обновить";
            this.ОбновитьСписокПриходов.UseVisualStyleBackColor = true;
            this.ОбновитьСписокПриходов.Click += new System.EventHandler(this.ОбновитьСписокПриходов_Click);
            // 
            // ПП
            // 
            this.ПП.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ПП.HeaderText = "ПП";
            this.ПП.Name = "ПП";
            this.ПП.ReadOnly = true;
            this.ПП.Width = 48;
            // 
            // УИД
            // 
            this.УИД.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.УИД.HeaderText = "УИД";
            this.УИД.Name = "УИД";
            this.УИД.ReadOnly = true;
            this.УИД.Width = 57;
            // 
            // ПОСТАВЩИК
            // 
            this.ПОСТАВЩИК.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ПОСТАВЩИК.HeaderText = "ПОСТАВЩИК";
            this.ПОСТАВЩИК.Name = "ПОСТАВЩИК";
            this.ПОСТАВЩИК.ReadOnly = true;
            this.ПОСТАВЩИК.Width = 101;
            // 
            // ДОК
            // 
            this.ДОК.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ДОК.HeaderText = "ДОК";
            this.ДОК.Name = "ДОК";
            this.ДОК.ReadOnly = true;
            this.ДОК.Width = 56;
            // 
            // МАШИНА
            // 
            this.МАШИНА.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.МАШИНА.HeaderText = "МАШИНА";
            this.МАШИНА.Name = "МАШИНА";
            this.МАШИНА.ReadOnly = true;
            this.МАШИНА.Width = 80;
            // 
            // OHRANA_KPP
            // 
            this.OHRANA_KPP.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.OHRANA_KPP.HeaderText = "ОХРАНА КПП";
            this.OHRANA_KPP.Name = "OHRANA_KPP";
            this.OHRANA_KPP.ReadOnly = true;
            this.OHRANA_KPP.Width = 102;
            // 
            // ТЕЛ_ВОДИТЕЛЯ
            // 
            this.ТЕЛ_ВОДИТЕЛЯ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ТЕЛ_ВОДИТЕЛЯ.HeaderText = "ТЕЛ_ВОДИТЕЛЯ";
            this.ТЕЛ_ВОДИТЕЛЯ.Name = "ТЕЛ_ВОДИТЕЛЯ";
            this.ТЕЛ_ВОДИТЕЛЯ.ReadOnly = true;
            this.ТЕЛ_ВОДИТЕЛЯ.Width = 122;
            // 
            // СКЛАД
            // 
            this.СКЛАД.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.СКЛАД.HeaderText = "СКЛАД";
            this.СКЛАД.Name = "СКЛАД";
            this.СКЛАД.ReadOnly = true;
            this.СКЛАД.Width = 70;
            // 
            // ПРИОРИТЕТ
            // 
            this.ПРИОРИТЕТ.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ПРИОРИТЕТ.HeaderText = "ПРИОР";
            this.ПРИОРИТЕТ.Name = "ПРИОРИТЕТ";
            this.ПРИОРИТЕТ.ReadOnly = true;
            this.ПРИОРИТЕТ.Width = 70;
            // 
            // Время_Вызова_на_док
            // 
            this.Время_Вызова_на_док.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Время_Вызова_на_док.HeaderText = "Время Вызова на док";
            this.Время_Вызова_на_док.Name = "Время_Вызова_на_док";
            this.Время_Вызова_на_док.ReadOnly = true;
            this.Время_Вызова_на_док.Width = 115;
            // 
            // Новый
            // 
            this.Новый.HeaderText = "новый";
            this.Новый.Name = "Новый";
            this.Новый.ReadOnly = true;
            this.Новый.Visible = false;
            // 
            // Безопасность
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1136, 546);
            this.Controls.Add(this.tabControl1);
            this.Name = "Безопасность";
            this.Text = "Безопасность";
            this.tabControl1.ResumeLayout(false);
            this.tabPage1.ResumeLayout(false);
            this.tabPage1.PerformLayout();
            this.tabPage2.ResumeLayout(false);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.TextBox CONDITION;
        private System.Windows.Forms.TextBox TRANSPORT;
        private System.Windows.Forms.TextBox FIO;
        private System.Windows.Forms.TextBox DOVERENNOST_OT;
        private System.Windows.Forms.TextBox TEL;
        private System.Windows.Forms.Label Состояние;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox PASSPORT;
        private System.Windows.Forms.TextBox ADDR;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label ID_LABEL;
        private System.Windows.Forms.TextBox ID_;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox ВидДокумента;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabPage1;
        private System.Windows.Forms.TabPage tabPage2;
        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button ОбновитьСписокПриходов;
        private System.Windows.Forms.Button НазначитьКПП2;
        private System.Windows.Forms.Button НазначитьКПП1;
        private System.Windows.Forms.CheckBox ВызванныеПриходыУбирать;
        private System.Windows.Forms.DataGridViewTextBoxColumn ПП;
        private System.Windows.Forms.DataGridViewTextBoxColumn УИД;
        private System.Windows.Forms.DataGridViewTextBoxColumn ПОСТАВЩИК;
        private System.Windows.Forms.DataGridViewTextBoxColumn ДОК;
        private System.Windows.Forms.DataGridViewTextBoxColumn МАШИНА;
        private System.Windows.Forms.DataGridViewTextBoxColumn OHRANA_KPP;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТЕЛ_ВОДИТЕЛЯ;
        private System.Windows.Forms.DataGridViewTextBoxColumn СКЛАД;
        private System.Windows.Forms.DataGridViewTextBoxColumn ПРИОРИТЕТ;
        private System.Windows.Forms.DataGridViewTextBoxColumn Время_Вызова_на_док;
        private System.Windows.Forms.DataGridViewTextBoxColumn Новый;
    }
}