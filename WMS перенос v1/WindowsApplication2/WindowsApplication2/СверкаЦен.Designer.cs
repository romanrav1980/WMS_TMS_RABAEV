namespace WindowsApplication2
{
    partial class СверкаЦен
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
            this.label1 = new System.Windows.Forms.Label();
            this.t_ID = new System.Windows.Forms.TextBox();
            this.t_SUPPLIER = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.t_INN = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.t_ZAKAZ_NUMBER = new System.Windows.Forms.TextBox();
            this.СверкаПройдена = new System.Windows.Forms.Button();
            this.СверкаНеПройдена = new System.Windows.Forms.Button();
            this.label5 = new System.Windows.Forms.Label();
            this.t_VEH_NUMBER = new System.Windows.Forms.TextBox();
            this.label6 = new System.Windows.Forms.Label();
            this.t_DRIVER_PHONE_NUMBER = new System.Windows.Forms.TextBox();
            this.ОбновитьДанныеПоЗаказу = new System.Windows.Forms.Button();
            this.t_KPP = new System.Windows.Forms.TextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.label8 = new System.Windows.Forms.Label();
            this.t_FIO = new System.Windows.Forms.TextBox();
            this.label9 = new System.Windows.Forms.Label();
            this.comboBox1 = new System.Windows.Forms.ComboBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(24, 13);
            this.label1.TabIndex = 0;
            this.label1.Text = "ID=";
            // 
            // t_ID
            // 
            this.t_ID.Enabled = false;
            this.t_ID.Location = new System.Drawing.Point(116, 2);
            this.t_ID.Name = "t_ID";
            this.t_ID.Size = new System.Drawing.Size(282, 20);
            this.t_ID.TabIndex = 15;
            // 
            // t_SUPPLIER
            // 
            this.t_SUPPLIER.Location = new System.Drawing.Point(116, 30);
            this.t_SUPPLIER.Name = "t_SUPPLIER";
            this.t_SUPPLIER.Size = new System.Drawing.Size(282, 20);
            this.t_SUPPLIER.TabIndex = 10;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 35);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(71, 13);
            this.label2.TabIndex = 2;
            this.label2.Text = "Поставщик=";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(12, 61);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(101, 13);
            this.label3.TabIndex = 2;
            this.label3.Text = "ИНН Поставщика:";
            // 
            // t_INN
            // 
            this.t_INN.Location = new System.Drawing.Point(116, 58);
            this.t_INN.Name = "t_INN";
            this.t_INN.Size = new System.Drawing.Size(282, 20);
            this.t_INN.TabIndex = 9;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(12, 111);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(83, 13);
            this.label4.TabIndex = 2;
            this.label4.Text = "Номер заказа:";
            // 
            // t_ZAKAZ_NUMBER
            // 
            this.t_ZAKAZ_NUMBER.Location = new System.Drawing.Point(116, 108);
            this.t_ZAKAZ_NUMBER.Name = "t_ZAKAZ_NUMBER";
            this.t_ZAKAZ_NUMBER.Size = new System.Drawing.Size(282, 20);
            this.t_ZAKAZ_NUMBER.TabIndex = 0;
            // 
            // СверкаПройдена
            // 
            this.СверкаПройдена.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(128)))), ((int)(((byte)(255)))), ((int)(((byte)(128)))));
            this.СверкаПройдена.Location = new System.Drawing.Point(136, 232);
            this.СверкаПройдена.Name = "СверкаПройдена";
            this.СверкаПройдена.Size = new System.Drawing.Size(122, 23);
            this.СверкаПройдена.TabIndex = 5;
            this.СверкаПройдена.Text = "Сверка Пройдена";
            this.СверкаПройдена.UseVisualStyleBackColor = false;
            this.СверкаПройдена.Click += new System.EventHandler(this.СверкаПройдена_Click);
            // 
            // СверкаНеПройдена
            // 
            this.СверкаНеПройдена.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(255)))), ((int)(((byte)(128)))), ((int)(((byte)(128)))));
            this.СверкаНеПройдена.Location = new System.Drawing.Point(264, 232);
            this.СверкаНеПройдена.Name = "СверкаНеПройдена";
            this.СверкаНеПройдена.Size = new System.Drawing.Size(134, 23);
            this.СверкаНеПройдена.TabIndex = 6;
            this.СверкаНеПройдена.Text = "Сверка не пройдена";
            this.СверкаНеПройдена.UseVisualStyleBackColor = false;
            this.СверкаНеПройдена.Click += new System.EventHandler(this.СверкаНеПройдена_Click);
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(12, 142);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(89, 13);
            this.label5.TabIndex = 2;
            this.label5.Text = "Номер машины:";
            // 
            // t_VEH_NUMBER
            // 
            this.t_VEH_NUMBER.Location = new System.Drawing.Point(116, 139);
            this.t_VEH_NUMBER.Name = "t_VEH_NUMBER";
            this.t_VEH_NUMBER.Size = new System.Drawing.Size(282, 20);
            this.t_VEH_NUMBER.TabIndex = 1;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(12, 170);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(105, 13);
            this.label6.TabIndex = 2;
            this.label6.Text = "Телефон водителя:";
            // 
            // t_DRIVER_PHONE_NUMBER
            // 
            this.t_DRIVER_PHONE_NUMBER.Location = new System.Drawing.Point(116, 167);
            this.t_DRIVER_PHONE_NUMBER.Name = "t_DRIVER_PHONE_NUMBER";
            this.t_DRIVER_PHONE_NUMBER.Size = new System.Drawing.Size(282, 20);
            this.t_DRIVER_PHONE_NUMBER.TabIndex = 2;
            // 
            // ОбновитьДанныеПоЗаказу
            // 
            this.ОбновитьДанныеПоЗаказу.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(128)))), ((int)(((byte)(128)))), ((int)(((byte)(255)))));
            this.ОбновитьДанныеПоЗаказу.Location = new System.Drawing.Point(404, 108);
            this.ОбновитьДанныеПоЗаказу.Name = "ОбновитьДанныеПоЗаказу";
            this.ОбновитьДанныеПоЗаказу.Size = new System.Drawing.Size(75, 20);
            this.ОбновитьДанныеПоЗаказу.TabIndex = 4;
            this.ОбновитьДанныеПоЗаказу.Text = "Обновить";
            this.ОбновитьДанныеПоЗаказу.UseVisualStyleBackColor = false;
            this.ОбновитьДанныеПоЗаказу.Click += new System.EventHandler(this.ОбновитьДанныеПоЗаказу_Click);
            // 
            // t_KPP
            // 
            this.t_KPP.Location = new System.Drawing.Point(116, 83);
            this.t_KPP.Name = "t_KPP";
            this.t_KPP.Size = new System.Drawing.Size(282, 20);
            this.t_KPP.TabIndex = 8;
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(12, 86);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(100, 13);
            this.label7.TabIndex = 7;
            this.label7.Text = "КПП Поставщика:";
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(12, 196);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(87, 13);
            this.label8.TabIndex = 2;
            this.label8.Text = "ФИО водителя:";
            // 
            // t_FIO
            // 
            this.t_FIO.Location = new System.Drawing.Point(116, 193);
            this.t_FIO.Name = "t_FIO";
            this.t_FIO.Size = new System.Drawing.Size(282, 20);
            this.t_FIO.TabIndex = 3;
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.Location = new System.Drawing.Point(12, 267);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(41, 13);
            this.label9.TabIndex = 2;
            this.label9.Text = "Склад:";
            // 
            // comboBox1
            // 
            this.comboBox1.FormattingEnabled = true;
            this.comboBox1.Location = new System.Drawing.Point(116, 267);
            this.comboBox1.Name = "comboBox1";
            this.comboBox1.Size = new System.Drawing.Size(282, 21);
            this.comboBox1.TabIndex = 16;
            this.comboBox1.SelectedValueChanged += new System.EventHandler(this.comboBox1_SelectedValueChanged);
            // 
            // СверкаЦен
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(580, 328);
            this.Controls.Add(this.comboBox1);
            this.Controls.Add(this.t_KPP);
            this.Controls.Add(this.label7);
            this.Controls.Add(this.ОбновитьДанныеПоЗаказу);
            this.Controls.Add(this.СверкаНеПройдена);
            this.Controls.Add(this.СверкаПройдена);
            this.Controls.Add(this.t_FIO);
            this.Controls.Add(this.t_DRIVER_PHONE_NUMBER);
            this.Controls.Add(this.t_VEH_NUMBER);
            this.Controls.Add(this.t_ZAKAZ_NUMBER);
            this.Controls.Add(this.t_INN);
            this.Controls.Add(this.t_SUPPLIER);
            this.Controls.Add(this.label9);
            this.Controls.Add(this.label8);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.t_ID);
            this.Controls.Add(this.label1);
            this.Name = "СверкаЦен";
            this.Text = "СверкаЦен";
            this.Load += new System.EventHandler(this.СверкаЦен_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox t_ID;
        private System.Windows.Forms.TextBox t_SUPPLIER;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox t_INN;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox t_ZAKAZ_NUMBER;
        private System.Windows.Forms.Button СверкаПройдена;
        private System.Windows.Forms.Button СверкаНеПройдена;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox t_VEH_NUMBER;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox t_DRIVER_PHONE_NUMBER;
        private System.Windows.Forms.Button ОбновитьДанныеПоЗаказу;
        private System.Windows.Forms.TextBox t_KPP;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.TextBox t_FIO;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.ComboBox comboBox1;
    }
}