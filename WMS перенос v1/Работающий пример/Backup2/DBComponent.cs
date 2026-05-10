using System;
using System.Collections.Generic;
using System.Text;
using System.Data;
using System.IO;


namespace MCSSTestNet
{

    public class DBComponent
    {
       // public SqlCeConnection mySqlConnection;
       // private SqlCeCommand mySqlCommand = null;
       // private SqlCeDataAdapter mySqlDataAdapter = null;
       // private SqlCeEngine mySqlEngine = null;
        public DataSet myDataSet = null;
    
        private string myDBName;
        // Gets or sets the database name
        public string DBName
        {
            get
            {
                return myDBName;
            }
            set
            {
                myDBName = value;
            }
        }

        private string myDBPassword;
        // Gets or sets the password for database
        public string DBPassword
        {
            get
            {
                return myDBPassword;
            }
            set
            {
                myDBPassword = value;
            }
        }

        private bool myDBEncrypt = true;
        // Enable or disable database encryption
        public bool DBEncrypt
        {
            get
            {
                return myDBEncrypt;
            }
            set
            {
                myDBEncrypt = value;
            }
        }

        // If set to true, delete the the database in DBCreate() if already exists and then create a new one. 
        // If set to false, use the existing one.  
        private bool myDBDelete = false;
        public bool DBDelete
        {
            get
            {
                return myDBDelete;
            }
            set
            {
                myDBDelete = value;
            }
        }


        public void FlushPlannedLot()
        {
            if (myDataSet.Tables["PALLET_PLAN"] == null)
            { 
            
            }
        
        }

        //Create a databse using the name provided in DBName
        public void DBCreate()
        {
            DataColumn column;
           

            myDataSet = new DataSet("operator");


            #region ÒÀÁËÈÖÀ_ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ

            // ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ
            myDataSet.Tables.Add("ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ");
                // ÑÅÊ 0 İÒ 1 ÊÎË 4 ÊÎĞ 5 ÁË 6 ÓÈÄ 7 ÍÀÈÌ 8 ÀÄĞ 9 ñğêë 10 ñğêõ 11

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÑÅÊ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "İÒ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÊÎË";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÊÎĞ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÁË";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÓÈÄ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÍÀÈÌ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÀÄĞ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ñğêë";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ñğêõ";
                myDataSet.Tables["ÓÒĞÅÍÍßß_ÏĞÎÂÅĞÊÀ"].Columns.Add(column);



            #endregion


            #region ÒÀÁËÈÖÀ_ÀËÜÒÅĞÍÀÒÈÂÍÛÕ_ÄÀÍÍÛÕ

            myDataSet.Tables.Add("ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"); 

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ÓÈÄ";
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊØ";
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊÁ";
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);


            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊÊ";
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);


            column = new DataColumn();
            column.DataType = System.Type.GetType("System.Int64");
            column.ColumnName = "ØÂÁ";
            column.AllowDBNull = false;
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);


            column = new DataColumn();
            column.DataType = System.Type.GetType("System.Int64");
            column.AllowDBNull = false;
            column.ColumnName = "ÁÂÊ";
            myDataSet.Tables["ÀËÜÒÅĞÍÀÒÈÂÍÛÅ_ÄÀÍÍÛÅ"].Columns.Add(column);


            // Make the ÓÈÄ column the primary key column.
  //          DataColumn[] PrimaryKeyColumns2 = new DataColumn[1];
 //           PrimaryKeyColumns2[0] = myDataSet.Tables["PALLET_PLAN"].Columns["ÓÈÄ"];
//            myDataSet.Tables["PALLET_PLAN"].PrimaryKey = PrimaryKeyColumns2;

            #endregion

            #region ÒÀÁËÈÖÀ_ÄÎÏÎËÍÈÒÅËÜÍÛÕ_ÄÀÍÍÛÕ

            myDataSet.Tables.Add("PALLET_PLAN_HIDDEN");

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ÓÈÄ";
            column.ReadOnly = true;
            column.Unique = true;
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ÀÄĞ";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);


            column = new DataColumn();
            column.DataType = System.Type.GetType("System.Int64");
            column.ColumnName = "ØÒÂÁË";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.Int64");
            column.ColumnName = "ÁËÂÊÎĞ";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊ_ØÒÓÊÈ";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊ_ÁËÎÊÀ";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ØÊ_ÊÎĞÎÁ";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);



            column = new DataColumn();
            column.DataType = System.Type.GetType("System.DateTime");
            column.ColumnName = "ÂĞÅÌß";
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns.Add(column);

            // Make the ÓÈÄ column the primary key column.
            DataColumn[] PrimaryKeyColumns = new DataColumn[1];
            PrimaryKeyColumns[0] = myDataSet.Tables["PALLET_PLAN_HIDDEN"].Columns["ÓÈÄ"];
            myDataSet.Tables["PALLET_PLAN_HIDDEN"].PrimaryKey = PrimaryKeyColumns;

            // ---------------------------------------------------------------------
            #endregion

            #region ÒÀÁËÈÖÀ_ËÎÒÀ

            myDataSet.Tables.Add("PALLET_PLAN"); // ÓÈÄ ; ÍÀÈÌ ; ÊÎËÈ×ÅÑÒÂÎ ; ÂÅÑ ; ÓÄÀËÅÍ ; ÏĞÎÂÅĞÅÍ ; 

            column = new DataColumn();
            column.DataType = System.Type.GetType("System.String");
            column.ColumnName = "ÏÏ";
            column.ReadOnly = true;
            column.Unique = true;
            myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÓÈÄ";
                column.ReadOnly = true;
                column.Unique = true ;
                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);




                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÍÀÈÌ";
                column.ReadOnly = true;
                column.Unique = false ;
                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.Int32");
                column.ColumnName = "ÔÀÊÒ_ÊÎË";
                column.DefaultValue = 0;
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.Int32");
                column.ColumnName = "ÊÎË";
                column.ReadOnly = true;
                column.Unique = false;
                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "Ó"; // Óäàëåí
                column.ReadOnly = true;
                column.DefaultValue="";
                column.Unique = false;
 
                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "Ğ"; // Ïğîâåğåí
                column.ReadOnly = false;
                column.DefaultValue = "<";
                column.Unique = false;

                myDataSet.Tables["PALLET_PLAN"].Columns.Add(column);
            
                // Make the ÓÈÄ column the primary key column.
                DataColumn[] PrimaryKeyColumns2 = new DataColumn[1];
                PrimaryKeyColumns2[0] = myDataSet.Tables["PALLET_PLAN"].Columns["ÓÈÄ"];
                myDataSet.Tables["PALLET_PLAN"].PrimaryKey = PrimaryKeyColumns2;

            #endregion

            #region ÒÀÁËÈÖÀ ÎØÈÁÎÊ
                //=====================================================================================
                //=====================================================================================
                //=====================================================================================
                myDataSet.Tables.Add("PALLET_AS_IS");

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÀÄĞÅÑ";
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.Int64");
                column.ColumnName = "ÊÎË";
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);



                column = new DataColumn();
                column.DataType = System.Type.GetType("System.Int64");
                column.ColumnName = "ÏËÀÍ_ÊÎË";
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);


                // Create new DataColumn, set DataType, 
                // ColumnName and add to DataTable.    
                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÓÈÄ";
                column.ReadOnly = true;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);

                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÈÌß";
                column.AutoIncrement = false;
                column.Caption = "ÈÌß";
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);


                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ÒÈÏ";
                column.AutoIncrement = false;
                column.Caption = "ÒÈÏ";
                column.ReadOnly = false;
                column.Unique = false;
                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);


                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "ØÒĞÈÕÊÎÄ";
                column.AutoIncrement = false;
                column.Caption = "ØÒĞÈÕÊÎÄ";
                column.ReadOnly = false;
                column.Unique = false;

                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);
                
                column = new DataColumn();
                column.DataType = System.Type.GetType("System.String");
                column.ColumnName = "USSCC";
                column.AutoIncrement = false;
                column.Caption = "USSCC";
                column.ReadOnly = false;
                column.Unique = false;

                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);


                column = new DataColumn();
                column.DataType = System.Type.GetType("System.DateTime");
                column.ColumnName = "ÂĞÅÌß";
                column.AutoIncrement = false;
                column.Caption = "ÂĞÅÌß";
                column.ReadOnly = false;
                column.Unique = false;

                myDataSet.Tables["PALLET_AS_IS"].Columns.Add(column);


                // Make the ÓÈÄ column the primary key column.
                DataColumn[] PrimaryKeyColumns3 = new DataColumn[1];
                PrimaryKeyColumns3[0] = myDataSet.Tables["PALLET_AS_IS"].Columns["ÓÈÄ"];
                myDataSet.Tables["PALLET_AS_IS"].PrimaryKey = PrimaryKeyColumns3;
            #endregion


        }

        public void  add_row_to_pallet_as_is( string itf , string  USSCC )
        {
                DataRow row;
                row = myDataSet.Tables["PALLET_AS_IS"].NewRow();
                row["ÈÌß"] = "??";
                row["ØÒ"] = 1;
                row["ÓÈÄ"] = "??";
                row["ITF"] = itf;
                row["ITF"] = USSCC;

                myDataSet.Tables["PALLET_AS_IS"].Rows.Add(row);

        }


        // Open the database and get it ready for transactions
        public void DBOpen()
        {
        
        }

        // Provides the state of the connection 
        /*public ConnectionState DBConnectionState()
        {
            return null;
        }*/

        
        public void DBClose()
        {
         
        }

        // Query the database and return the resultset
        public DataSet DBQuery(string queryStr)
        {
            return myDataSet;
        }

        // Execute Delete, Insert and Update commands
        public int DBExecute(string executeStr)
        {
            int rowsAffected = 0;
            return rowsAffected;
        }
    }
}
