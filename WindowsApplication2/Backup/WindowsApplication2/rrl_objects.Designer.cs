namespace WindowsApplication2
{
    partial class rrl_objects
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
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.splitContainer2 = new System.Windows.Forms.SplitContainer();
            this.treeView1 = new System.Windows.Forms.TreeView();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.OBJECT_NAME = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.BUSINESS_FIELD = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.TYPE1 = new System.Windows.Forms.DataGridViewComboBoxColumn();
            this.COMMENT1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ARTICLE1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            this.splitContainer2.Panel1.SuspendLayout();
            this.splitContainer2.Panel2.SuspendLayout();
            this.splitContainer2.SuspendLayout();
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
            this.splitContainer1.Panel1.Controls.Add(this.splitContainer2);
            this.splitContainer1.Size = new System.Drawing.Size(1005, 463);
            this.splitContainer1.SplitterDistance = 400;
            this.splitContainer1.TabIndex = 0;
            // 
            // splitContainer2
            // 
            this.splitContainer2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer2.Location = new System.Drawing.Point(0, 0);
            this.splitContainer2.Name = "splitContainer2";
            // 
            // splitContainer2.Panel1
            // 
            this.splitContainer2.Panel1.Controls.Add(this.treeView1);
            // 
            // splitContainer2.Panel2
            // 
            this.splitContainer2.Panel2.Controls.Add(this.dataGridView1);
            this.splitContainer2.Size = new System.Drawing.Size(1005, 400);
            this.splitContainer2.SplitterDistance = 265;
            this.splitContainer2.TabIndex = 0;
            // 
            // treeView1
            // 
            this.treeView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.treeView1.Location = new System.Drawing.Point(0, 0);
            this.treeView1.Name = "treeView1";
            this.treeView1.Size = new System.Drawing.Size(265, 400);
            this.treeView1.TabIndex = 0;
            this.treeView1.BeforeExpand += new System.Windows.Forms.TreeViewCancelEventHandler(this.treeView1_BeforeExpand);
            this.treeView1.AfterSelect += new System.Windows.Forms.TreeViewEventHandler(this.treeView1_AfterSelect);
            this.treeView1.LocationChanged += new System.EventHandler(this.treeView1_LocationChanged);
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.OBJECT_NAME,
            this.BUSINESS_FIELD,
            this.TYPE1,
            this.COMMENT1,
            this.ARTICLE1});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(736, 400);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            // 
            // OBJECT_NAME
            // 
            this.OBJECT_NAME.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.OBJECT_NAME.HeaderText = "Имя объекта";
            this.OBJECT_NAME.Name = "OBJECT_NAME";
            this.OBJECT_NAME.Width = 99;
            // 
            // BUSINESS_FIELD
            // 
            this.BUSINESS_FIELD.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.BUSINESS_FIELD.HeaderText = "Предметная область";
            this.BUSINESS_FIELD.Items.AddRange(new object[] {
            "СКЛАД",
            "ТРАНСПОРТ"});
            this.BUSINESS_FIELD.Name = "BUSINESS_FIELD";
            this.BUSINESS_FIELD.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.BUSINESS_FIELD.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.BUSINESS_FIELD.Width = 127;
            // 
            // TYPE1
            // 
            this.TYPE1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.TYPE1.HeaderText = "ТИП";
            this.TYPE1.Items.AddRange(new object[] {
            "TABLE",
            "FIELD",
            "PROCEDURE"});
            this.TYPE1.Name = "TYPE1";
            this.TYPE1.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.TYPE1.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.TYPE1.Width = 55;
            // 
            // COMMENT1
            // 
            this.COMMENT1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.COMMENT1.HeaderText = "Комментарий";
            this.COMMENT1.Name = "COMMENT1";
            this.COMMENT1.Width = 102;
            // 
            // ARTICLE1
            // 
            this.ARTICLE1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ARTICLE1.HeaderText = "Статья";
            this.ARTICLE1.Name = "ARTICLE1";
            this.ARTICLE1.Width = 67;
            // 
            // rrl_objects
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1005, 463);
            this.Controls.Add(this.splitContainer1);
            this.Name = "rrl_objects";
            this.Text = "rrl_objects";
            this.Load += new System.EventHandler(this.rrl_objects_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.ResumeLayout(false);
            this.splitContainer2.Panel1.ResumeLayout(false);
            this.splitContainer2.Panel2.ResumeLayout(false);
            this.splitContainer2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.SplitContainer splitContainer2;
        private System.Windows.Forms.TreeView treeView1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.DataGridViewTextBoxColumn OBJECT_NAME;
        private System.Windows.Forms.DataGridViewComboBoxColumn BUSINESS_FIELD;
        private System.Windows.Forms.DataGridViewComboBoxColumn TYPE1;
        private System.Windows.Forms.DataGridViewTextBoxColumn COMMENT1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ARTICLE1;
    }
}