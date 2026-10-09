namespace WindowsApplication2
{
    partial class СоздатьАртикул
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
            this.Создать_товар = new System.Windows.Forms.Button();
            this.button2 = new System.Windows.Forms.Button();
            this.Код_группы_товаров = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.Артикул_товара = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.Наименование_товара = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.label4 = new System.Windows.Forms.Label();
            this.НормаУкладки = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.Штрих_код = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.Ячейка_отбора = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // Создать_товар
            // 
            this.Создать_товар.Location = new System.Drawing.Point(138, 255);
            this.Создать_товар.Name = "Создать_товар";
            this.Создать_товар.Size = new System.Drawing.Size(119, 25);
            this.Создать_товар.TabIndex = 0;
            this.Создать_товар.Text = "Создать товар";
            this.Создать_товар.UseVisualStyleBackColor = true;
            this.Создать_товар.Click += new System.EventHandler(this.Создать_товар_Click);
            // 
            // button2
            // 
            this.button2.Location = new System.Drawing.Point(257, 12);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(75, 23);
            this.button2.TabIndex = 1;
            this.button2.Text = "Выбрать";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
            // 
            // Код_группы_товаров
            // 
            this.Код_группы_товаров.Location = new System.Drawing.Point(104, 12);
            this.Код_группы_товаров.Name = "Код_группы_товаров";
            this.Код_группы_товаров.Size = new System.Drawing.Size(147, 20);
            this.Код_группы_товаров.TabIndex = 2;
            this.Код_группы_товаров.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 15);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(86, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "Группа товаров";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(50, 48);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(48, 13);
            this.label2.TabIndex = 4;
            this.label2.Text = "Артикул";
            // 
            // Артикул_товара
            // 
            this.Артикул_товара.Location = new System.Drawing.Point(104, 45);
            this.Артикул_товара.Name = "Артикул_товара";
            this.Артикул_товара.Size = new System.Drawing.Size(147, 20);
            this.Артикул_товара.TabIndex = 5;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(15, 79);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(83, 13);
            this.label3.TabIndex = 4;
            this.label3.Text = "Наименование";
            // 
            // Наименование_товара
            // 
            this.Наименование_товара.Location = new System.Drawing.Point(104, 76);
            this.Наименование_товара.Name = "Наименование_товара";
            this.Наименование_товара.Size = new System.Drawing.Size(147, 20);
            this.Наименование_товара.TabIndex = 5;
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(18, 255);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(119, 25);
            this.button1.TabIndex = 0;
            this.button1.Text = "Отмена";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(15, 108);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(86, 13);
            this.label4.TabIndex = 4;
            this.label4.Text = "Штук в поддоне";
            // 
            // НормаУкладки
            // 
            this.НормаУкладки.Location = new System.Drawing.Point(104, 105);
            this.НормаУкладки.Name = "НормаУкладки";
            this.НормаУкладки.Size = new System.Drawing.Size(147, 20);
            this.НормаУкладки.TabIndex = 5;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(15, 138);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(58, 13);
            this.label5.TabIndex = 4;
            this.label5.Text = "штрих-код";
            // 
            // Штрих_код
            // 
            this.Штрих_код.Location = new System.Drawing.Point(104, 135);
            this.Штрих_код.Name = "Штрих_код";
            this.Штрих_код.Size = new System.Drawing.Size(147, 20);
            this.Штрих_код.TabIndex = 5;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(15, 170);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(82, 13);
            this.label6.TabIndex = 6;
            this.label6.Text = "Ячейка отбора";
            // 
            // Ячейка_отбора
            // 
            this.Ячейка_отбора.Location = new System.Drawing.Point(104, 167);
            this.Ячейка_отбора.Name = "Ячейка_отбора";
            this.Ячейка_отбора.Size = new System.Drawing.Size(147, 20);
            this.Ячейка_отбора.TabIndex = 7;
            // 
            // СоздатьАртикул
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(574, 292);
            this.Controls.Add(this.Ячейка_отбора);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.Штрих_код);
            this.Controls.Add(this.НормаУкладки);
            this.Controls.Add(this.Наименование_товара);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.Артикул_товара);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.Код_группы_товаров);
            this.Controls.Add(this.button2);
            this.Controls.Add(this.button1);
            this.Controls.Add(this.Создать_товар);
            this.Name = "СоздатьАртикул";
            this.Text = "СоздатьАртикул";
            this.Load += new System.EventHandler(this.СоздатьАртикул_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button Создать_товар;
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.TextBox Код_группы_товаров;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox Артикул_товара;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox Наименование_товара;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox НормаУкладки;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox Штрих_код;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox Ячейка_отбора;
    }
}