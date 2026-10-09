namespace WindowsApplication2
{
    partial class Поставщики
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
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.Поставщики1 = new System.Windows.Forms.TabPage();
            this.splitContainer2 = new System.Windows.Forms.SplitContainer();
            this.ТаблицаПоставщиков = new System.Windows.Forms.DataGridView();
            this.ГруппыПоставщиков = new System.Windows.Forms.TabPage();
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.МенюПоставщиков = new System.Windows.Forms.ContextMenuStrip(this.components);
            this.подгрузитьЦеныПоставщикаToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.Название = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ИНН = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.КПП = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Группа = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Юр_Адрес = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Адрес = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ID = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.ID_ = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.DOG_NAME = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ТипДог = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Начало = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Окончание = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Пост_оплата = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Федеральный = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.tabControl1.SuspendLayout();
            this.Поставщики1.SuspendLayout();
            this.splitContainer2.Panel1.SuspendLayout();
            this.splitContainer2.Panel2.SuspendLayout();
            this.splitContainer2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.ТаблицаПоставщиков)).BeginInit();
            this.МенюПоставщиков.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.tabControl1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer1.Size = new System.Drawing.Size(886, 541);
            this.splitContainer1.SplitterDistance = 361;
            this.splitContainer1.TabIndex = 0;
            // 
            // tabControl1
            // 
            this.tabControl1.Controls.Add(this.Поставщики1);
            this.tabControl1.Controls.Add(this.ГруппыПоставщиков);
            this.tabControl1.Location = new System.Drawing.Point(3, 3);
            this.tabControl1.Name = "tabControl1";
            this.tabControl1.SelectedIndex = 0;
            this.tabControl1.Size = new System.Drawing.Size(880, 359);
            this.tabControl1.TabIndex = 1;
            // 
            // Поставщики1
            // 
            this.Поставщики1.Controls.Add(this.splitContainer2);
            this.Поставщики1.Location = new System.Drawing.Point(4, 22);
            this.Поставщики1.Name = "Поставщики1";
            this.Поставщики1.Padding = new System.Windows.Forms.Padding(3);
            this.Поставщики1.Size = new System.Drawing.Size(872, 333);
            this.Поставщики1.TabIndex = 0;
            this.Поставщики1.Text = "Поставщики";
            this.Поставщики1.UseVisualStyleBackColor = true;
            // 
            // splitContainer2
            // 
            this.splitContainer2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer2.Location = new System.Drawing.Point(3, 3);
            this.splitContainer2.Name = "splitContainer2";
            // 
            // splitContainer2.Panel1
            // 
            this.splitContainer2.Panel1.Controls.Add(this.treeView1);
            // 
            // splitContainer2.Panel2
            // 
            this.splitContainer2.Panel2.Controls.Add(this.ТаблицаПоставщиков);
            this.splitContainer2.Size = new System.Drawing.Size(866, 327);
            this.splitContainer2.SplitterDistance = 202;
            this.splitContainer2.TabIndex = 1;
            // 
            // ТаблицаПоставщиков
            // 
            this.ТаблицаПоставщиков.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.ТаблицаПоставщиков.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Название,
            this.ИНН,
            this.КПП,
            this.Группа,
            this.Юр_Адрес,
            this.Адрес,
            this.ID});
            this.ТаблицаПоставщиков.Dock = System.Windows.Forms.DockStyle.Fill;
            this.ТаблицаПоставщиков.Location = new System.Drawing.Point(0, 0);
            this.ТаблицаПоставщиков.Name = "ТаблицаПоставщиков";
            this.ТаблицаПоставщиков.Size = new System.Drawing.Size(660, 327);
            this.ТаблицаПоставщиков.TabIndex = 0;
            this.ТаблицаПоставщиков.CellEnter += new System.Windows.Forms.DataGridViewCellEventHandler(this.ТаблицаПоставщиков_CellEnter);
            // 
            // ГруппыПоставщиков
            // 
            this.ГруппыПоставщиков.Location = new System.Drawing.Point(4, 22);
            this.ГруппыПоставщиков.Name = "ГруппыПоставщиков";
            this.ГруппыПоставщиков.Padding = new System.Windows.Forms.Padding(3);
            this.ГруппыПоставщиков.Size = new System.Drawing.Size(872, 333);
            this.ГруппыПоставщиков.TabIndex = 1;
            this.ГруппыПоставщиков.Text = "ГруппыПоставщиков";
            this.ГруппыПоставщиков.UseVisualStyleBackColor = true;
            // 
            // treeView1
            // 
            this.treeView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.treeView1.Location = new System.Drawing.Point(0, 0);
            this.treeView1.Name = "treeView1";
            this.treeView1.Size = new System.Drawing.Size(202, 327);
            this.treeView1.TabIndex = 0;
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            // 
            // МенюПоставщиков
            // 
            this.МенюПоставщиков.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.подгрузитьЦеныПоставщикаToolStripMenuItem});
            this.МенюПоставщиков.Name = "МенюПоставщиков";
            this.МенюПоставщиков.Size = new System.Drawing.Size(240, 26);
            // 
            // подгрузитьЦеныПоставщикаToolStripMenuItem
            // 
            this.подгрузитьЦеныПоставщикаToolStripMenuItem.Name = "подгрузитьЦеныПоставщикаToolStripMenuItem";
            this.подгрузитьЦеныПоставщикаToolStripMenuItem.Size = new System.Drawing.Size(239, 22);
            this.подгрузитьЦеныПоставщикаToolStripMenuItem.Text = "Подгрузить цены поставщика";
            // 
            // Название
            // 
            this.Название.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Название.HeaderText = "Название";
            this.Название.Name = "Название";
            this.Название.Width = 82;
            // 
            // ИНН
            // 
            this.ИНН.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ИНН.HeaderText = "ИНН";
            this.ИНН.Name = "ИНН";
            this.ИНН.Width = 56;
            // 
            // КПП
            // 
            this.КПП.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.КПП.HeaderText = "КПП";
            this.КПП.Name = "КПП";
            this.КПП.Width = 55;
            // 
            // Группа
            // 
            this.Группа.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.Группа.HeaderText = "Группа";
            this.Группа.Name = "Группа";
            this.Группа.Visible = false;
            this.Группа.Width = 67;
            // 
            // Юр_Адрес
            // 
            this.Юр_Адрес.HeaderText = "Юр_Адрес";
            this.Юр_Адрес.Name = "Юр_Адрес";
            // 
            // Адрес
            // 
            this.Адрес.HeaderText = "Адрес";
            this.Адрес.Name = "Адрес";
            // 
            // ID
            // 
            this.ID.HeaderText = "ID";
            this.ID.Name = "ID";
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ID_,
            this.DOG_NAME,
            this.ТипДог,
            this.Начало,
            this.Окончание,
            this.Пост_оплата,
            this.Федеральный});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(886, 176);
            this.dataGridView1.TabIndex = 0;
            // 
            // ID_
            // 
            this.ID_.HeaderText = "ID";
            this.ID_.Name = "ID_";
            // 
            // DOG_NAME
            // 
            this.DOG_NAME.HeaderText = "Имя договора";
            this.DOG_NAME.Name = "DOG_NAME";
            // 
            // ТипДог
            // 
            this.ТипДог.HeaderText = "Тип";
            this.ТипДог.Name = "ТипДог";
            // 
            // Начало
            // 
            this.Начало.HeaderText = "Начало";
            this.Начало.Name = "Начало";
            // 
            // Окончание
            // 
            this.Окончание.HeaderText = "Окончание";
            this.Окончание.Name = "Окончание";
            // 
            // Пост_оплата
            // 
            this.Пост_оплата.HeaderText = "Пост оплата";
            this.Пост_оплата.Name = "Пост_оплата";
            // 
            // Федеральный
            // 
            this.Федеральный.HeaderText = "Федеральный";
            this.Федеральный.Name = "Федеральный";
            // 
            // Поставщики
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(886, 541);
            this.Controls.Add(this.splitContainer1);
            this.Name = "Поставщики";
            this.Text = "Поставщики";
            this.Load += new System.EventHandler(this.Поставщики_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.tabControl1.ResumeLayout(false);
            this.Поставщики1.ResumeLayout(false);
            this.splitContainer2.Panel1.ResumeLayout(false);
            this.splitContainer2.Panel2.ResumeLayout(false);
            this.splitContainer2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.ТаблицаПоставщиков)).EndInit();
            this.МенюПоставщиков.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView ТаблицаПоставщиков;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage Поставщики1;
        private System.Windows.Forms.TabPage ГруппыПоставщиков;
        private System.Windows.Forms.SplitContainer splitContainer2;
        private System.Windows.Forms.TreeView treeView1;
        private System.Windows.Forms.ContextMenuStrip МенюПоставщиков;
        private System.Windows.Forms.ToolStripMenuItem подгрузитьЦеныПоставщикаToolStripMenuItem;
        private System.Windows.Forms.DataGridViewTextBoxColumn Название;
        private System.Windows.Forms.DataGridViewTextBoxColumn ИНН;
        private System.Windows.Forms.DataGridViewTextBoxColumn КПП;
        private System.Windows.Forms.DataGridViewTextBoxColumn Группа;
        private System.Windows.Forms.DataGridViewTextBoxColumn Юр_Адрес;
        private System.Windows.Forms.DataGridViewTextBoxColumn Адрес;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID_;
        private System.Windows.Forms.DataGridViewTextBoxColumn DOG_NAME;
        private System.Windows.Forms.DataGridViewTextBoxColumn ТипДог;
        private System.Windows.Forms.DataGridViewTextBoxColumn Начало;
        private System.Windows.Forms.DataGridViewTextBoxColumn Окончание;
        private System.Windows.Forms.DataGridViewTextBoxColumn Пост_оплата;
        private System.Windows.Forms.DataGridViewTextBoxColumn Федеральный;
    }
}