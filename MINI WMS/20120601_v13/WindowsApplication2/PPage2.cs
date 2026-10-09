using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Drawing.Printing;
using System.Data.SqlClient;




using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Data.OracleClient;
using System.Data.OleDb;
using System.IO;
using System.Reflection;
using GenCode128;


namespace PPage2
{
    public class PPage
    {

        public class PLabel
        {
            public bool repeat=false;
            public string Label;
            public System.Drawing.Point _point;
            public long width_limit = 0;
            public long height_limit = 0;
            public FontStyle fs = FontStyle.Bold;
            public Brush br = Brushes.Black;
            long font_size = 12;
            public System.Drawing.Font printFont;
            StringFormat sf = new StringFormat();
            public string type = "text"; // text , EAN
            float angle = 0;

            public PLabel(string ttext, Point pp, long font_size_)
            {
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
            }

            public PLabel clone()
            {
                PLabel n = new PLabel(this.Label, this._point, this.font_size);
                n.angle = angle;
                n.type = type;
                n.width_limit = width_limit;
                n.height_limit = height_limit;
                n.type = type;
                n.repeat = repeat;
                return n;
            }

            public PLabel(string ttext, Point pp, long font_size_ , float angle1)
            {
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                angle = angle1;
            }

            public PLabel(string ttext, Point pp, long font_size_, Brush br2)
            {
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.br = br2;
            }

            public PLabel(string ttext, Point pp, long font_size_, Brush br2, float angle1)
            {
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.br = br2;
                angle = angle1;
            }

            public PLabel(string ttext, Point pp, long font_size_, string type_of_label)
            {

                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.type = type_of_label;

            }


            public PLabel(string ttext, Point pp, long font_size_, string type_of_label, float angle1)
            {

                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.type = type_of_label;
                angle = angle1;
            }


            public PLabel(string ttext, Point pp, long font_size_, string type_of_label, long wl, long hl)
            {
                this.width_limit = wl;
                this.height_limit = hl;
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.type = type_of_label;
            }

 


            public PLabel(string ttext, Point pp, long font_size_, string type_of_label, long wl, long hl, float angle1)
            {
                this.width_limit = wl;
                this.height_limit = hl;
                this.Label = ttext;
                this.font_size = font_size_;
                this._point = pp;
                this.type = type_of_label;
                angle = angle1;
            }



            public void print(PrintPageEventArgs ev)
            {
                int width=700, height=500;

                if ((this.type == "text") || (this.type == "string"))
                {
                    printFont = new Font("ARIAL", font_size, fs, GraphicsUnit.Pixel);
                    if (width_limit == 0)
                    {
                        //ev.Graphics.DrawString(Label, printFont, br, _point.X, _point.Y, sf);
                        if (angle == 0)
                        {
                            ev.Graphics.DrawString(Label, printFont, br, _point.X, _point.Y, sf);
                        }
                        else {

                            Image myimg = new System.Drawing.Bitmap(width, height);
                            using (Graphics gr = Graphics.FromImage(myimg))
                            {
                                gr.RotateTransform(angle);
                                gr.DrawString(Label, printFont, br, printFont.Size, 0, sf);
                            }
                            ev.Graphics.DrawImage(myimg, _point);
                        }

                    }
                    else
                    {
                        if (angle == 0)
                        {
                            ev.Graphics.DrawString(Label, printFont, br, new RectangleF(_point.X, _point.Y, width_limit, font_size + 2), sf);
                        }
                        else { 
                            Image myimg = new System.Drawing.Bitmap(width, height);
                            using (Graphics gr = Graphics.FromImage(myimg))
                            {
                                gr.RotateTransform(angle);
                                gr.DrawString(Label, printFont, br, new RectangleF(_point.X, _point.Y, width_limit, font_size + 2), sf);
                            }
                            ev.Graphics.DrawImageUnscaled(myimg, _point);
                        }

                    }
                }

                if (this.type == "EAN")
                {
                    if (height_limit == 0)
                    {
                        height_limit = 100;
                    }

                    Image r ;
                    if (angle == 0)
                    {
                        r = Code128Rendering.MakeBarcodeImage2(Label, 1, true, (int)width_limit, (int)height_limit);
                    }
                    else {
                        r = Code128Rendering.MakeBarcodeImage2F(Label, 1, true, (int)width_limit, (int)height_limit , angle);
                    
                    }
                    ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }


                if (this.type == "EAN2")
                {
                    Image r = Code128Rendering.MakeBarcodeImage2(Label, 2, true, (int)width_limit, (int)height_limit);
                    ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }
                if (this.type == "EAN3")
                {
                    Image r = Code128Rendering.MakeBarcodeImage2(Label, 3, true, (int)width_limit, (int)height_limit);
                    ev.Graphics.DrawImage(r, _point.X, _point.Y);
                }

            }
        }

        public class _Box3d
        {
            public int x_limit_from = 0;
            public int x_limit_to = 700;
            int border_x = 10;
            int border_y = 10;

            public Point rect;
            public int depth;

            public  _Box3d( Point _rect , int _depth , int ylimit )
            {
                x_limit_to = ylimit;
                depth = _depth;
                rect = _rect;
                border_x = _depth;
                border_y = _depth;
            }
            
            public Point print(PrintPageEventArgs ev , Point start_point  )
            {
                int x=start_point.X;
                int y=start_point.Y;
                if (start_point.X + this.rect.X > x_limit_to)
                { // Перенос строки
                    x = x_limit_from + border_x;
                    y = y + rect.Y + border_y;
                }
                else {
                    x = x + border_x;
                    
                }
                ev.Graphics.DrawRectangle(Pens.Brown , new Rectangle( x , y ,rect.X,rect.Y ));
                return new Point( x+rect.X , y );
            }


        }

        public class PTable
        {
            public bool repeat = false;
            public List<PColumnGroup> column_groups = new List<PColumnGroup>(); // Группировки колонок
            public Dictionary<string, string> print_columns_styles = new Dictionary<string, string>();
            public Point bottom_point_of_table = new Point();
            long Row_height;
            public List<PColumn> columns = new List<PColumn>();
            List<Dictionary<string, string>> rows = new List<Dictionary<string, string>>();
            public Point start_point_4_table = new Point();
            public int font_size_4_table = 12;
            public int height_of_row_override = 0;
            Pen pen = new Pen(Brushes.Black);
            Dictionary<int, List<_Box3d>> boxes= new Dictionary<int,List<_Box3d>>();


       
            public void add_box(Point _rect, int _depth , int ylimit)
            {
                int nomer_stroki=1;
                if (rows != null)
                    nomer_stroki = (rows.Count);

                if (!boxes.ContainsKey(nomer_stroki))
                {
                    boxes.Add(nomer_stroki ,   new List<_Box3d>())   ;
                    boxes[ nomer_stroki ].Add( new _Box3d(  _rect ,  _depth ,ylimit ));
                }
                else {
                    boxes[nomer_stroki].Add(new _Box3d(_rect, _depth , ylimit ));
                }

               
            }

            public void add_row(Dictionary<string, string> _row)
            {
                this.rows.Add(_row);
            }


            public void add_column(string name2, string type2)
            {
                PColumn c = new PColumn(name2, type2);
                columns.Add(c);
            }

            public void add_column(string name2, string type2, string to_pr, long width)
            {
                PColumn c = new PColumn(name2, type2, to_pr, width);
                columns.Add(c);
            }

            public void add_column(string name2, string type2, string to_pr)
            {
                PColumn c = new PColumn(name2, type2, to_pr);
                columns.Add(c);
            }

            public Point print(PrintPageEventArgs ev)
            {
                Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold, GraphicsUnit.Pixel);
                Font printFont2 = new Font("ARIAL", font_size_4_table, FontStyle.Regular, GraphicsUnit.Pixel);

                int _position_x = this.start_point_4_table.X;
                int _position_y = this.start_point_4_table.Y;


                int pos_uio = 0;
                foreach (PColumn _col in columns)
                {
                    int local_font_size = font_size_4_table;
                    int start_point_4_table_Y = this.start_point_4_table.Y;
                    // сначала определим - находится - ли данная колонка в группировке. Берем первую группировку по порядку.
                    if (_col.font > 0) local_font_size = (int) _col.font;

                    for (int pcg = 0; pcg < column_groups.Count; pcg++)
                    {
                        if ((pos_uio >= column_groups[pcg].first_column) && (pos_uio <= column_groups[pcg].last_column))
                        { // Понижаем позицию по оси У на высоту объединенной ячейки
                            start_point_4_table_Y = this.start_point_4_table.Y - column_groups[pcg].height_of_column_group;
                            column_groups[pcg].extend(_position_x, start_point_4_table_Y);
                            column_groups[pcg].extend(_position_x + (int)_col.Width_(local_font_size), this.start_point_4_table.Y);
                        }
                    }

                    ev.Graphics.DrawRectangle( pen, _position_x, start_point_4_table_Y, _col.Width_(local_font_size), font_size_4_table + 4 );
                    ev.Graphics.DrawString(  _col.To_print, printFont, Brushes.Black, new RectangleF(_position_x, start_point_4_table_Y, _col.Width_(local_font_size), font_size_4_table + 4)  );
                    _position_x = _position_x + (int)_col.Width_(local_font_size);
                    pos_uio++;
                }

                for (int pcg = 0; pcg < column_groups.Count; pcg++)
                {
                    ev.Graphics.DrawRectangle(pen, new Rectangle(column_groups[pcg].left_top,
                        column_groups[pcg].size()));

                    ev.Graphics.DrawString(column_groups[pcg].name, printFont, Brushes.Black,
                        new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));

                }

                //  По всем строкам    
                int НомерСтроки = 0;
                foreach (Dictionary<string, string> _row in rows)
                {
                    long local_row_height = font_size_4_table;
                    foreach (PColumn _col in columns)
                            local_row_height = Math.Max(local_row_height, _col.font);

                    _position_y = _position_y + (int) local_row_height + 4;
                    _position_x = this.start_point_4_table.X;

                    #region КУБИКИ 
                    // проверяем  - есть ли кубики перед этой строкой??
                    if (boxes.ContainsKey(НомерСтроки))
                    {
                        List<_Box3d> gg = boxes[НомерСтроки];
                        if (gg.Count > 0)
                            _position_y = _position_y + gg[0].depth;

                        Point p = new Point(_position_x, _position_y );
                        int h_y = 0;
                        foreach (_Box3d g in gg)
                        {
                           g.x_limit_from = this.start_point_4_table.X;
                           p= g.print(ev, p);
                           h_y=g.rect.Y;
                        }
                        _position_y = p.Y + h_y;
                        if (gg.Count > 0)
                            _position_y = _position_y + gg[0].depth;
                    }
                    #endregion 


                    
                    if (height_of_row_override > 0)
                    {
                        local_row_height = height_of_row_override + 4;
                    }




                    // Рисуем строку по всем колонкам
                    foreach (PColumn _col in columns) 
                    {
                        _col.bottom_point.X = _position_x;
                        _col.bottom_point.Y = _position_y;
                        

                        string tp = "";
                        if( _row.ContainsKey(_col.Name) )
                            tp = _row[_col.Name];

                        tp = tp.Replace('\t', ' ');
                        tp = tp.Replace("  ", " ");

                        if (_col.font <= 0)
                        {
                            ev.Graphics.DrawRectangle(pen, _position_x, _position_y,
                                _col.Width_(font_size_4_table), local_row_height + 4);

                            if (_col.align == "left" || _col.align == "")
                            {
                                ev.Graphics.DrawString(tp, printFont2, Brushes.Black,
                                    new RectangleF(_position_x, _position_y, _col.Width_(font_size_4_table), local_row_height + 4));
                            }
                            else {
                                SizeF sizef = ev.Graphics.MeasureString(tp, printFont2);
                                ev.Graphics.DrawString(tp, printFont2, Brushes.Black,
                                    new RectangleF(_position_x + (int)_col.Width_(font_size_4_table) - sizef.Width, _position_y, _col.Width_(font_size_4_table), local_row_height + 4));
                            
                            }
                            
                            _position_x = _position_x + (int)_col.Width_(font_size_4_table);



                        }
                        else
                        {// ФОНТ ПЕРЕОПРЕДЕЛЕН
                            Font local_print_font = new Font("ARIAL", _col.font, FontStyle.Regular, GraphicsUnit.Pixel);
                            ev.Graphics.DrawRectangle(pen, _position_x, _position_y,
                                _col.Width_( (int)_col.font), local_row_height + 4);

                            if ( _col.align == "left" || _col.align == "" )
                            {

                                ev.Graphics.DrawString(tp, local_print_font, Brushes.Black,
                                    new RectangleF(_position_x, _position_y, _col.Width_((int)_col.font), local_row_height + 4));
                            }
                            else {
                               SizeF sizef = ev.Graphics.MeasureString(tp, local_print_font);
                                ev.Graphics.DrawString(tp, local_print_font, Brushes.Black,
                                    new RectangleF(_position_x + (int)_col.Width_((int)_col.font) - sizef.Width /*(local_print_font.SizeInPoints-1)*tp.Length */  ,
                                        _position_y, 
                                        _col.Width_((int)_col.font), 
                                        local_row_height + 4)  );

                            }
                            
                            _position_x = _position_x + (int)_col.Width_((int)_col.font);
                            
                        }// ФОНТ ПЕРЕОПРЕДЕЛЕН

                    }

                    НомерСтроки++;
                }

                bottom_point_of_table = new Point(_position_x, _position_y);
                return bottom_point_of_table;
            }

            /*Вычисляет позицию таблицы на основании позиций других таблиц и собственного положения*/
           static public long eval_table_position(Dictionary<string, long> table_positions , string position_y)
            {
                long ret=0;
                string py = position_y;
                foreach (string key in table_positions.Keys)
                {
                    if (key != "")
                    {
                        py = py.Replace(key, table_positions[key].ToString());
                    }
                }
                foreach (string h in py.Split('+'))
                {
                    string h1 = h.Replace("+", "");
                    ret = ret + Convert.ToInt32(h1);
                }
                return ret;
            }

           static public bool eval_bool_cond(string expression, Dictionary<string, string> vals)
           {
               string expr = expression;
               foreach (string val in vals.Keys)
               {
                   expr=expr.Replace( "["+val+"]" , vals[val] );
               }
               string [] a= expr.Split('=');
               if(a.Length==2)
                   if (a[0] == a[1])
                   {
                       return true;
                   }

               return false;
           }


           static public double obj2double(object o)
           {
               try
               {
                   if (o == null) return 0;
                   return Convert.ToDouble(o.ToString().Replace(".", ","));
               }
               catch { }
               return 0;
           }

           static public double eval_math(object expression)
           {
               string expression1 = ( expression.ToString() ) ;
               double ret=0;
               foreach (string s in expression1.Split('+'))
               {
                   ret = ret + obj2double(s);
               }
               return ret;
           }

            /* Высота таблицы, вычисленная еще до печати самой таблицы */
            public long table_height() 
            {
                long local_row_height = font_size_4_table+4 ;
                if (height_of_row_override > 0)
                {
                    local_row_height = height_of_row_override+4  ;
                }
                return (rows.Count + 1) * local_row_height;
            }

        }




        public class PColumn
        {
            public long font = 0;
            public string Name;
            public string Type;
            public string To_print;
            public string align= "left";
            public string style = "";
            private long Width = 0;
            public Point bottom_point = new Point();

            public long Width_(int font_size1)
            {

                // int mul=Convert.ToInt32( System.Math.Ceiling(Convert.ToSingle(font_size1) * .15F));

                if (Width > 0)
                {
                    return Width * font_size1;
                }

                return To_print.Length * font_size1;
            }

            public long Width_of_str(string pr, int font_size1)
            {
                return pr.Length * font_size1;
            }

            public PColumn(string name1, string Type1, string To_print1, long w , long font1)
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = To_print1;
                Width = w;
                this.font = font1;
            }

            public PColumn(string name1, string Type1, string To_print1, long w)
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = To_print1;
                Width = w;
            }



            public PColumn(string name1, string Type1, string To_print1)
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = To_print1;

            }

            public PColumn()
            { }

            public PColumn(string name1, string Type1)
            {
                this.Name = name1;
                this.Type = Type1;
                this.To_print = name1;
            }


        }

        public class PColumnGroup
        {
            public PColumn column;
            public int first_column = 0;
            public int last_column = 0;
            public int height_of_column_group = 0;
            public string name;
            public Point left_top = new Point();
            public Point right_bottom = new Point();

            public void extend(int X, int Y)
            {
                if ((left_top.X > X) || (left_top.X == 0)) { left_top.X = X; }
                if ((left_top.Y > Y) || (left_top.Y == 0)) { left_top.Y = Y; }

                if ((right_bottom.X < X) || (right_bottom.X == 0)) { right_bottom.X = X; }
                if ((right_bottom.Y < Y) || (right_bottom.Y == 0)) { right_bottom.Y = Y; }

            }
            public Size size()
            {
                return new Size(-left_top.X + right_bottom.X, -left_top.Y + right_bottom.Y);
            }

            public PColumnGroup(string name4, int first1, int last1, int h)
            {
                first_column = first1;
                last_column = last1;
                name = name4;
                height_of_column_group = h;
                column = new PColumn(name4, "string");
            }

        }

        public class PArrow
        {
            public bool repeat = false;
            Point start = new Point();
            Point end = new Point();
            string style = "";
            public int fill = 0;

            public PArrow(int x1, int y1, int x2, int y2 , bool rep )
            {
                start.X = x1;
                start.Y = y1;
                end.X = x2;
                end.Y = y2;
                repeat = rep;
            }

            public PArrow(int x1, int y1, int x2, int y2)
            {
                start.X = x1;
                start.Y = y1;
                end.X = x2;
                end.Y = y2;
            }

            public void print(PrintPageEventArgs ev)
            {
                ev.Graphics.DrawLine(Pens.Black, start, end);
            }

            public void print_rect(PrintPageEventArgs ev)
            {
               // ev.Graphics.DrawLine(Pens.Black, start, end);
               // ev.Graphics.DrawRectangle(Pens.Black, start.X, start.Y, end.X-start.X  , end.Y-start.Y );
                ev.Graphics.FillRectangle(Brushes.Black, start.X, start.Y, end.X - start.X, end.Y - start.Y);
            }

            public void print_rect_no_fill(PrintPageEventArgs ev)
            {
                
                 ev.Graphics.DrawRectangle(Pens.Black, start.X, start.Y, end.X-start.X  , end.Y-start.Y );
                //ev.Graphics.FillRectangle(Brushes.Black, start.X, start.Y, end.X - start.X, end.Y - start.Y);
            }
        }


        public List<PColumnGroup> column_groups = new List<PColumnGroup>(); // Группировки колонок
        public Point bottom_point_of_table = new Point();  // Сюда заносится информация о нижней точке в таблице
        public List<PLabel> labels = new List<PLabel>();
        public List<PTable> tables = new List<PTable>();
        public List<PArrow> rects = new List<PArrow>();
        public string header;
        long Row_height;
        public List<PColumn> columns = new List<PColumn>();
        public List<PArrow> arrows = new List<PArrow>();
        List<Dictionary<string, string>> rows = new List<Dictionary<string, string>>();
        public Dictionary<string, string> column_styles;

        public Point start_point_4_table = new Point();
        public int font_size_4_table = 12;
        public int height_of_row_override = 0;
        public int height_of_column = 0;
        Pen pen = new Pen(Brushes.Black);
        public int Landscape = -1; //-1-по умолчанию, 0- нет , 1 - да

        public void add_row(Dictionary<string, string> _row)
        {
            this.rows.Add(_row);
        }

        public void set_page_number(int pn , int page_count)
        {
            foreach (PLabel pl in labels)
            {
                pl.Label = pl.Label.Replace("[page_number]", pn.ToString()).Replace("[page_count]", page_count.ToString());
            }
        }

        public void print_axes(PrintPageEventArgs ev)
        {
            Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold, GraphicsUnit.Pixel);
            ev.Graphics.DrawLine(Pens.Black, 5, 5, 1000, 5);
            ev.Graphics.DrawString("X", printFont, Brushes.Black, 450, 10);
            ev.Graphics.DrawLine(Pens.Black, 5, 5, 5, 1000);
            ev.Graphics.DrawString("Y", printFont, Brushes.Black, 10, 450);

            for (int i = 100; i < 1000; i = i + 100)
            {

                ev.Graphics.DrawString(i.ToString() + "Y", printFont, Brushes.Black, (float)7, (float)i);
                ev.Graphics.DrawString(i.ToString() + "X", printFont, Brushes.Black, (float)i, (float)7);

            }

        }

        public void print_axes()
        {
            
            this.arrows.Add(new PPage.PArrow(5, 5, 1000, 5));
            this.arrows.Add(new PPage.PArrow(5, 5, 5, 1000));
            this.labels.Add(new PPage.PLabel("X", new Point(450, 10), font_size_4_table));
            this.labels.Add(new PPage.PLabel("Y", new Point(10, 450 ), font_size_4_table));


            for (int i = 100; i < 1000; i = i + 100)
            {
                this.labels.Add(new PPage.PLabel(i.ToString() + "Y", new Point(7, i), font_size_4_table));
                this.labels.Add(new PPage.PLabel(i.ToString() + "X", new Point(i, 7), font_size_4_table));
            }

        }

        public Point print(PrintPageEventArgs ev)
        {

            //            this.print_axes(ev);

            Font printFont = new Font("ARIAL", font_size_4_table, FontStyle.Bold, GraphicsUnit.Pixel);
            Font printFont2 = new Font("ARIAL", font_size_4_table, FontStyle.Regular, GraphicsUnit.Pixel);

            foreach (PLabel pl in labels)
            {
                pl.print(ev);
            }

            int _position_x = this.start_point_4_table.X;
            int _position_y = this.start_point_4_table.Y;

            int jk;
            if (height_of_column > 0)
            { jk = height_of_column; }
            else
            {
                jk = font_size_4_table;
            }


            int pos_uio = 0;
            foreach (PColumn _col in columns)
            {
                int jk2 = 0;
                int start_point_4_table_Y = this.start_point_4_table.Y;
                // сначала определим - находится - ли данная колонка в группировке. Берем первую группировку по порядку.
                for (int pcg = 0; pcg < column_groups.Count; pcg++)
                {
                    if ((pos_uio >= column_groups[pcg].first_column) && (pos_uio <= column_groups[pcg].last_column))
                    { // Понижаем позицию по оси У на высоту объединенной ячейки
                        start_point_4_table_Y = this.start_point_4_table.Y + column_groups[pcg].height_of_column_group;
                        jk2 = column_groups[pcg].height_of_column_group;
                        column_groups[pcg].extend(_position_x, start_point_4_table_Y);
                        column_groups[pcg].extend(_position_x + (int)_col.Width_(font_size_4_table), this.start_point_4_table.Y);
                    }
                }

                ev.Graphics.DrawRectangle(pen, _position_x, start_point_4_table_Y, _col.Width_(font_size_4_table), jk - jk2 + 4);
                ev.Graphics.DrawString(_col.To_print, printFont, Brushes.Black, new RectangleF(_position_x, start_point_4_table_Y, _col.Width_(font_size_4_table), jk - jk2 + 4));
                _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                pos_uio++;
            }

            for (int pcg = 0; pcg < column_groups.Count; pcg++)
            {
                ev.Graphics.DrawRectangle(pen, new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));
                ev.Graphics.DrawString(column_groups[pcg].name, printFont, Brushes.Black, new Rectangle(column_groups[pcg].left_top, column_groups[pcg].size()));

            }

            int local_row_height = font_size_4_table;
            if (height_of_row_override > 0)
            {
                local_row_height = height_of_row_override;
            }


            _position_y = _position_y + jk - local_row_height;
            foreach (Dictionary<string, string> _row in rows)
            {
                _position_y = _position_y + local_row_height + 4;
                _position_x = this.start_point_4_table.X;
                foreach (PColumn _col in columns)
                {
                    string l_style = "";
                    if (column_styles!=null)
                    try
                    {
                        if (column_styles.ContainsKey(_col.Name))
                        {
                            l_style = column_styles[_col.Name];
                        }
                    }
                    catch { }

                    string tp = _row[_col.Name];
                    tp = tp.Replace('\t', ' ');
                    tp = tp.Replace("  ", " ");


                    ev.Graphics.DrawRectangle(pen, _position_x, _position_y, _col.Width_(font_size_4_table), local_row_height + 4);
                    if (_col.Type != "EAN")
                    {
                        Font l_f = printFont2;
                        Pen l_p= new Pen( Brushes.Aqua );
                        bool bold_if_0=false;
                        foreach(string l_s in l_style.Split(';'))
                        {
                            if ((l_s.IndexOf("bold_if_0") != -1) && (tp.Trim() == "0" ))
                            {
                                l_f = printFont;
                                ev.Graphics.FillRectangle(Brushes.Aquamarine, _position_x, _position_y, _col.Width_(font_size_4_table), local_row_height + 4);
                            }
                            if ((l_s.IndexOf("bold_if_not_0") != -1) && (tp.Trim() != "0"))
                            {
                                l_f = printFont;
                                ev.Graphics.FillRectangle(Brushes.Aquamarine, _position_x, _position_y, _col.Width_(font_size_4_table), local_row_height + 4);
                            }
                        }


                       

                        ev.Graphics.DrawString(tp, l_f, 
                            Brushes.Black, 
                            new RectangleF(_position_x, _position_y, _col.Width_(font_size_4_table),
                            local_row_height + 4) );

                        

                    }
                    else
                    {

                        Image r = Code128Rendering.MakeBarcodeImage2(tp, 1, true, (int)_col.Width_(font_size_4_table) - 4, (int)local_row_height - 1  );
                        ev.Graphics.DrawImage(r, _position_x + 2, _position_y + 2, (int)_col.Width_(font_size_4_table) - 4, (int)local_row_height - 1);

                    }

                    _position_x = _position_x + (int)_col.Width_(font_size_4_table);
                }

            }



            foreach (PTable _table in tables)
            {
                _table.print(ev);
            }
            bottom_point_of_table = new Point(_position_x, _position_y);

            foreach (PArrow _arrow in arrows)
            {
                _arrow.print(ev);
            }

            foreach (PArrow _arrow in  this.rects )
            {
                if (_arrow.fill == 1)
                {
                    _arrow.print_rect(ev);
                }
                else {
                    _arrow.print_rect_no_fill (ev);
                
                }
            }


            return bottom_point_of_table;
        }

        public void add_column(string name2, string type2)
        {
            PColumn c = new PColumn(name2, type2);
            columns.Add(c);
        }

        public void add_column(string name2, string type2, string to_pr, long width)
        {
            PColumn c = new PColumn(name2, type2, to_pr, width);
            columns.Add(c);
        }

        public void add_column(string name2, string type2, string to_pr)
        {
            PColumn c = new PColumn(name2, type2, to_pr);
            columns.Add(c);
        }

        string footer;

        public PPage()
        {

        }

    }

}
