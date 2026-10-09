namespace WindowsApplication2
{
    partial class Список_прайсов
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
            this.comboBox1 = new System.Windows.Forms.ComboBox();
            this.ВывестиВсе = new System.Windows.Forms.Button();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            this.label1 = new System.Windows.Forms.Label();
            this.ID = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.PRICE_NAME = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.PRICE = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.COMPANY = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.RANGE1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.PRICE_FOR_HOURS = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.TYPE_TR = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.PRICE_FOR_ADDR = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.НормативЧасов = new System.Windows.Forms.DataGridViewTextBoxColumn();
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
            this.splitContainer1.Panel1.Controls.Add(this.dataGridView1);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.label1);
            this.splitContainer1.Panel2.Controls.Add(this.ВывестиВсе);
            this.splitContainer1.Panel2.Controls.Add(this.comboBox1);
            this.splitContainer1.Size = new System.Drawing.Size(859, 500);
            this.splitContainer1.SplitterDistance = 429;
            this.splitContainer1.TabIndex = 0;
            // 
            // comboBox1
            // 
            this.comboBox1.FormattingEnabled = true;
            this.comboBox1.Items.AddRange(new object[] {
            "МОНЕТКА"});
            this.comboBox1.Location = new System.Drawing.Point(234, 3);
            this.comboBox1.Name = "comboBox1";
            this.comboBox1.Size = new System.Drawing.Size(121, 21);
            this.comboBox1.TabIndex = 0;
            // 
            // ВывестиВсе
            // 
            this.ВывестиВсе.Location = new System.Drawing.Point(3, 2);
            this.ВывестиВсе.Name = "ВывестиВсе";
            this.ВывестиВсе.Size = new System.Drawing.Size(113, 23);
            this.ВывестиВсе.TabIndex = 1;
            this.ВывестиВсе.Text = "Вывести ставки";
            this.ВывестиВсе.UseVisualStyleBackColor = true;
            this.ВывестиВсе.Click += new System.EventHandler(this.ВывестиВсе_Click);
            // 
            // dataGridView1
            // 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ID,
            this.PRICE_NAME,
            this.PRICE,
            this.COMPANY,
            this.RANGE1,
            this.PRICE_FOR_HOURS,
            this.TYPE_TR,
            this.PRICE_FOR_ADDR,
            this.НормативЧасов});
            this.dataGridView1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dataGridView1.Location = new System.Drawing.Point(0, 0);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.Size = new System.Drawing.Size(859, 429);
            this.dataGridView1.TabIndex = 0;
            this.dataGridView1.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.dataGridView1_CellEndEdit);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(146, 7);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(82, 13);
            this.label1.TabIndex = 2;
            this.label1.Text = "Фильтр по ТК:";
            // 
            // ID
            // 
            this.ID.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.ID.HeaderText = "ID";
            this.ID.Name = "ID";
            this.ID.ReadOnly = true;
            this.ID.Width = 43;
            // 
            // PRICE_NAME
            // 
            this.PRICE_NAME.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.PRICE_NAME.HeaderText = "Регион";
            this.PRICE_NAME.Name = "PRICE_NAME";
            this.PRICE_NAME.ReadOnly = true;
            this.PRICE_NAME.Width = 68;
            // 
            // PRICE
            // 
            this.PRICE.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.PRICE.HeaderText = "Стоимость";
            this.PRICE.Name = "PRICE";
            this.PRICE.Width = 87;
            // 
            // COMPANY
            // 
            this.COMPANY.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.COMPANY.HeaderText = "Компания";
            this.COMPANY.Name = "COMPANY";
            this.COMPANY.ReadOnly = true;
            this.COMPANY.Width = 83;
            // 
            // RANGE1
            // 
            this.RANGE1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.RANGE1.HeaderText = "Расстояние";
            this.RANGE1.Name = "RANGE1";
            this.RANGE1.Width = 92;
            // 
            // PRICE_FOR_HOURS
            // 
            this.PRICE_FOR_HOURS.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.PRICE_FOR_HOURS.HeaderText = "Стоимость часа";
            this.PRICE_FOR_HOURS.Name = "PRICE_FOR_HOURS";
            this.PRICE_FOR_HOURS.Width = 104;
            // 
            // TYPE_TR
            // 
            this.TYPE_TR.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.TYPE_TR.HeaderText = "ТИП ТС";
            this.TYPE_TR.Name = "TYPE_TR";
            this.TYPE_TR.Width = 67;
            // 
            // PRICE_FOR_ADDR
            // 
            this.PRICE_FOR_ADDR.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.AllCells;
            this.PRICE_FOR_ADDR.HeaderText = "Цена за точку";
            this.PRICE_FOR_ADDR.Name = "PRICE_FOR_ADDR";
            this.PRICE_FOR_ADDR.Width = 95;
            // 
            // НормативЧасов
            // 
            this.НормативЧасов.HeaderText = "НормативЧасов";
            this.НормативЧасов.Name = "НормативЧасов";
            // 
            // Список_прайсов
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(859, 500);
            this.Controls.Add(this.splitContainer1);
            this.Name = "Список_прайсов";
            this.Text = "Список_прайсов";
            this.Load += new System.EventHandler(this.Список_прайсов_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            this.splitContainer1.Panel2.PerformLayout();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView dataGridView1;
        private System.Windows.Forms.Button ВывестиВсе;
        private System.Windows.Forms.ComboBox comboBox1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.DataGridViewTextBoxColumn ID;
        private System.Windows.Forms.DataGridViewTextBoxColumn PRICE_NAME;
        private System.Windows.Forms.DataGridViewTextBoxColumn PRICE;
        private System.Windows.Forms.DataGridViewTextBoxColumn COMPANY;
        private System.Windows.Forms.DataGridViewTextBoxColumn RANGE1;
        private System.Windows.Forms.DataGridViewTextBoxColumn PRICE_FOR_HOURS;
        private System.Windows.Forms.DataGridViewTextBoxColumn TYPE_TR;
        private System.Windows.Forms.DataGridViewTextBoxColumn PRICE_FOR_ADDR;
        private System.Windows.Forms.DataGridViewTextBoxColumn НормативЧасов;
    }
}