using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

using System;
using System.Xml;
//using System.Xml.;
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
using System.Security.AccessControl;

namespace WindowsApplication2
{


    public partial class ДатаАдаптер : Form
    {

       public Form1 _parent;
       public bool run_in_hidden_mode = false;

        public ДатаАдаптер()
        {
            InitializeComponent();
        }

        private void ДатаАдаптер_Load(object sender, EventArgs e)
        {

        }

        private void Подгрузить_Click(object sender, EventArgs e)
        {
            ПодгрузитьXML();
        }

        public void ПодгрузитьXML()
        {
            long ord = 1;
            Dictionary<string, long> per_log = new Dictionary<string, long>();
            per_log["Адрес-создано"] = 0;
            per_log["Адрес-обновлено"]=0;
            per_log["Адрес - ошибка"]=0;


            string filename = "otdelenya.xml";
            string text = File.ReadAllText(@"C:\WMS перенос\WindowsApplication2\" + filename,
                Encoding.GetEncoding("UTF-8")
                /*Encoding.GetEncoding("windows-1251") */);
          XmlDocument doc = new XmlDocument();
    
              doc = new XmlDocument();
              doc.LoadXml(text);



              foreach (XmlNode node0 in doc.ChildNodes )
              {

                  #region ОТДЕЛЕНИЯ
                if (node0.Name == "Отделения")
                {
                    foreach (XmlNode node in node0.ChildNodes)
                    {

                        #region
                        if (node.Name == "Адрес")
                        {
                            Dictionary<string, string> Addr = new Dictionary<string, string>();
                            foreach (XmlNode node2 in node.ChildNodes)
                            {

                                if (node2.Name == "Представление") Addr["Представление"] = node2.InnerText;
                                if (node2.Name == "ЯвляетсяОтделением") Addr["ЯвляетсяОтделением"] = node2.InnerText;
                                if (node2.Name == "ИмяПодразделения") Addr["ИмяПодразделения"] = node2.InnerText;

                                if (node2.Name == "КодПодразделения") Addr["КодПодразделения"] = node2.InnerText;
                                if ( node2.Name == "ОСБ" ) Addr["ОСБ"] = node2.InnerText;
                                if (node2.Name == "КодБанка") Addr["КодБанка"] = node2.InnerText;

                                if (node2.Name == "АдресноеПоле")
                                {
                                    string ТипАдресногоПоля  = node2.Attributes["Тип"].Value;
                                    string ЗначениеАдресногоПоля = node2.Attributes["Значение"].Value;
                                    Addr[ТипАдресногоПоля] = ЗначениеАдресногоПоля;
                                }

                               
                            }

                            #region Теперь адрес заполнен. Надо сохранять в БД
                                Dictionary<string ,object > pars =  new Dictionary<string,object>();

                                pars["i_REMOTE_ID"] = Addr["КодПодразделения"] ;
                                pars["i_ORD"] = ord++;
                                pars["i_REGION"] = Addr["Регион"];

                                pars["i_RAION"] = Addr["Район"];
                                pars["i_ADDR"] = Addr["город"] + " " + Addr["улица"] + " " + Addr["дом"] + " " + Addr["корпус"];
                                pars["i_STORE_NICK"] = Addr["ИмяПодразделения"]; // ИмяПодразделения 
                                pars["i_POST_INDEX"] = Addr["Индекс"];
                                pars["i_POST_CITY"] = Addr["город"];
                                pars["i_POST_STREET"] = Addr["улица"];
                                pars["i_POST_HOUSE"] = Addr["дом"];
                                pars["i_POST_KORPUS"] = Addr["корпус"];
                                pars["i_BANK_UID"] = Addr["КодБанка"];
                                pars["i_BANK_OSB"] = Addr["ОСБ"];
                                pars["i_RESERVATION_ORDER"] = 0;//- Приоритет резервирования остатков 
                                pars["i_PRIM2"] = "";
                                pars["i_PRIM1"] = "";
                                pars["i_DOCK_DEFAULT"] = "";
                                pars["i_SHIPPING_TIME"] = "";
                                pars["i_CLIENT_GROUP"] = "";
                                pars["i_LEAD_TIME"] = 1;
                                pars["i_SHIROTA"] = 0;
                                pars["i_DOLGOTA"] = 0;
                                pars["i_STOL"] = 1;
   

                               object ret= _parent.wms_get_spfunction_value2("RABAEV.RRL_UPDATE_ADDR",
                                    pars, OracleType.Int32, 0);

                               if (ret != null)
                               {
                                   switch (ret.ToString())
                                   {
                                       case "2":
                                           per_log["Адрес-создано"] = per_log["Адрес-создано"] + 1;
                                           break;
                                       case "3":
                                           per_log["Адрес-обновлено"] = per_log["Адрес-обновлено"] + 1;
                                           break;
                                       default:
                                           per_log["Адрес - ошибка"] = per_log["Адрес - ошибка"] + 1;
                                           break;

                                   }
                               }
                               else {
                                   per_log["Адрес - ошибка"] = per_log["Адрес - ошибка"] + 1;
                               }

                                /* Обновляем адрес через функцию в оракле
                                 * <Представление>620014, г.Екатеринбург, ул.Малышева, д.31-в, ул. Куйбышева, 67</Представление>
      <АдресноеПоле Тип="Индекс" Значение="620014" ></АдресноеПоле>
      <АдресноеПоле Тип="город" Значение=" г.Екатеринбург" ></АдресноеПоле>
      <АдресноеПоле Тип="улица" Значение=" ул.Малышева" ></АдресноеПоле>
      <АдресноеПоле Тип="дом" Значение=" д.31-в" ></АдресноеПоле>
      <АдресноеПоле Тип="корпус" Значение="" ></АдресноеПоле>
                                 * 
      <ЯвляетсяОтделением>1</ЯвляетсяОтделением>
      <АдресноеПоле Тип="Регион" Значение="Екатеринбург" ></АдресноеПоле>
      <АдресноеПоле Тип="Район" Значение="Ленинский" ></АдресноеПоле>
      <ИмяПодразделения>Уральский банк</ИмяПодразделения>
      <КодПодразделения>16</КодПодразделения>
      <ОСБ></ОСБ>
      <КодПодразделения>16</КодПодразделения>
      <КодБанка>16</КодБанка>
          */

                            #endregion
                        }
                        #endregion

                    }

                }
                  #endregion
              }

              string otcet="";
              foreach (string a in per_log.Keys)
              {
                  otcet = otcet +" "+ a +" = "+ per_log[a]+" \n\r ";
              }
              MessageBox.Show(otcet);


        }

    }
}
