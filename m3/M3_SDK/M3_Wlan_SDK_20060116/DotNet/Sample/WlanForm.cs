using System;
using System.Drawing;
using System.Collections;
using System.Windows.Forms;
using System.Data;
using System.Text;
using WlanUtilCF;

namespace WlanSampleNet
{
	/// <summary>
	/// WlanForm에 대한 요약 설명입니다.
	/// </summary>
	public class WlanForm : System.Windows.Forms.Form
	{
		private System.Windows.Forms.TabControl tabControl1;
		private System.Windows.Forms.TabPage AssociatedPage;
		private System.Windows.Forms.TabPage BssidListPage;
		private System.Windows.Forms.Label label1;
		private System.Windows.Forms.Label label2;
		private System.Windows.Forms.Label label3;
		private System.Windows.Forms.Label label4;
		private System.Windows.Forms.Label label5;
		private System.Windows.Forms.Label label6;
		private System.Windows.Forms.Label label7;
		private System.Windows.Forms.Label label8;
		private System.Windows.Forms.ProgressBar progressBar1;
		private System.Windows.Forms.Label lbRssi;
		private System.Windows.Forms.Label lbZCMsg;
		private System.Windows.Forms.TabPage AboutPage1;
		private System.Windows.Forms.TextBox tbAdapter;
		private System.Windows.Forms.TextBox tbState;
		private System.Windows.Forms.TextBox tbSsid;
		private System.Windows.Forms.TextBox tbBssid;
		private System.Windows.Forms.TextBox tbChannel;
		private System.Windows.Forms.TextBox tbLinkSpeed;
		private System.Windows.Forms.TextBox tbBeacon;
		private System.Windows.Forms.TextBox tbAtim;
		private System.Windows.Forms.Timer timer1;
		private System.Windows.Forms.ColumnHeader Ssid;
		private System.Windows.Forms.ListView lvBssid;
		private System.Windows.Forms.ColumnHeader Bssid;
		private System.Windows.Forms.ColumnHeader Rssi;
		private System.Windows.Forms.ColumnHeader Channel;
		private System.Windows.Forms.ColumnHeader Privacy;
		private System.Windows.Forms.Button btnsearch;
		private System.Windows.Forms.Label label9;
		private System.Windows.Forms.TextBox tbNicMac;
		private System.Windows.Forms.ColumnHeader Infra;
		private WlanUtilCF.WlanControl WlanControl1;
	
		public WlanForm()
		{
			//
			// Windows Form 디자이너 지원에 필요합니다.
			//
			InitializeComponent();

			WlanControl1 = new WlanUtilCF.WlanControl();
			
		}
		/// <summary>
		/// 사용 중인 모든 리소스를 정리합니다.
		/// </summary>
		protected override void Dispose( bool disposing )
		{
			base.Dispose( disposing );
		}
		#region Windows Form 디자이너에서 생성한 코드
		/// <summary>
		/// 디자이너 지원에 필요한 메서드입니다.
		/// 이 메서드의 내용을 코드 편집기로 수정하지 마십시오.
		/// </summary>
		private void InitializeComponent()
		{
			this.tabControl1 = new System.Windows.Forms.TabControl();
			this.AssociatedPage = new System.Windows.Forms.TabPage();
			this.lbZCMsg = new System.Windows.Forms.Label();
			this.lbRssi = new System.Windows.Forms.Label();
			this.progressBar1 = new System.Windows.Forms.ProgressBar();
			this.label1 = new System.Windows.Forms.Label();
			this.tbAdapter = new System.Windows.Forms.TextBox();
			this.tbState = new System.Windows.Forms.TextBox();
			this.tbSsid = new System.Windows.Forms.TextBox();
			this.tbBssid = new System.Windows.Forms.TextBox();
			this.tbChannel = new System.Windows.Forms.TextBox();
			this.tbLinkSpeed = new System.Windows.Forms.TextBox();
			this.tbBeacon = new System.Windows.Forms.TextBox();
			this.tbAtim = new System.Windows.Forms.TextBox();
			this.label2 = new System.Windows.Forms.Label();
			this.label3 = new System.Windows.Forms.Label();
			this.label4 = new System.Windows.Forms.Label();
			this.label5 = new System.Windows.Forms.Label();
			this.label6 = new System.Windows.Forms.Label();
			this.label7 = new System.Windows.Forms.Label();
			this.label8 = new System.Windows.Forms.Label();
			this.BssidListPage = new System.Windows.Forms.TabPage();
			this.btnsearch = new System.Windows.Forms.Button();
			this.lvBssid = new System.Windows.Forms.ListView();
			this.Ssid = new System.Windows.Forms.ColumnHeader();
			this.Bssid = new System.Windows.Forms.ColumnHeader();
			this.Rssi = new System.Windows.Forms.ColumnHeader();
			this.Channel = new System.Windows.Forms.ColumnHeader();
			this.Privacy = new System.Windows.Forms.ColumnHeader();
			this.AboutPage1 = new System.Windows.Forms.TabPage();
			this.tbNicMac = new System.Windows.Forms.TextBox();
			this.label9 = new System.Windows.Forms.Label();
			this.timer1 = new System.Windows.Forms.Timer();
			this.Infra = new System.Windows.Forms.ColumnHeader();
			// 
			// tabControl1
			// 
			this.tabControl1.Controls.Add(this.AssociatedPage);
			this.tabControl1.Controls.Add(this.BssidListPage);
			this.tabControl1.Controls.Add(this.AboutPage1);
			this.tabControl1.SelectedIndex = 0;
			this.tabControl1.Size = new System.Drawing.Size(240, 279);
			// 
			// AssociatedPage
			// 
			this.AssociatedPage.Controls.Add(this.lbZCMsg);
			this.AssociatedPage.Controls.Add(this.lbRssi);
			this.AssociatedPage.Controls.Add(this.progressBar1);
			this.AssociatedPage.Controls.Add(this.label1);
			this.AssociatedPage.Controls.Add(this.tbAdapter);
			this.AssociatedPage.Controls.Add(this.tbState);
			this.AssociatedPage.Controls.Add(this.tbSsid);
			this.AssociatedPage.Controls.Add(this.tbBssid);
			this.AssociatedPage.Controls.Add(this.tbChannel);
			this.AssociatedPage.Controls.Add(this.tbLinkSpeed);
			this.AssociatedPage.Controls.Add(this.tbBeacon);
			this.AssociatedPage.Controls.Add(this.tbAtim);
			this.AssociatedPage.Controls.Add(this.label2);
			this.AssociatedPage.Controls.Add(this.label3);
			this.AssociatedPage.Controls.Add(this.label4);
			this.AssociatedPage.Controls.Add(this.label5);
			this.AssociatedPage.Controls.Add(this.label6);
			this.AssociatedPage.Controls.Add(this.label7);
			this.AssociatedPage.Controls.Add(this.label8);
			this.AssociatedPage.Location = new System.Drawing.Point(4, 21);
			this.AssociatedPage.Size = new System.Drawing.Size(232, 254);
			this.AssociatedPage.Text = "Associated";
			this.AssociatedPage.EnabledChanged += new System.EventHandler(this.AssociatedPage_EnabledChanged);
			// 
			// lbZCMsg
			// 
			this.lbZCMsg.Location = new System.Drawing.Point(80, 224);
			this.lbZCMsg.Size = new System.Drawing.Size(80, 18);
			this.lbZCMsg.Text = "zcfg";
			// 
			// lbRssi
			// 
			this.lbRssi.Location = new System.Drawing.Point(168, 224);
			this.lbRssi.Size = new System.Drawing.Size(56, 13);
			this.lbRssi.Text = "RSSI";
			this.lbRssi.TextAlign = System.Drawing.ContentAlignment.TopRight;
			// 
			// progressBar1
			// 
			this.progressBar1.Location = new System.Drawing.Point(5, 204);
			this.progressBar1.Size = new System.Drawing.Size(219, 16);
			// 
			// label1
			// 
			this.label1.Location = new System.Drawing.Point(8, 13);
			this.label1.Size = new System.Drawing.Size(70, 16);
			this.label1.Text = "Adapter";
			// 
			// tbAdapter
			// 
			this.tbAdapter.Enabled = false;
			this.tbAdapter.Location = new System.Drawing.Point(88, 8);
			this.tbAdapter.Size = new System.Drawing.Size(137, 21);
			this.tbAdapter.Text = "";
			// 
			// tbState
			// 
			this.tbState.Enabled = false;
			this.tbState.Location = new System.Drawing.Point(88, 32);
			this.tbState.Size = new System.Drawing.Size(137, 21);
			this.tbState.Text = "";
			// 
			// tbSsid
			// 
			this.tbSsid.Enabled = false;
			this.tbSsid.Location = new System.Drawing.Point(88, 56);
			this.tbSsid.Size = new System.Drawing.Size(137, 21);
			this.tbSsid.Text = "";
			// 
			// tbBssid
			// 
			this.tbBssid.Enabled = false;
			this.tbBssid.Location = new System.Drawing.Point(88, 80);
			this.tbBssid.Size = new System.Drawing.Size(137, 21);
			this.tbBssid.Text = "";
			// 
			// tbChannel
			// 
			this.tbChannel.Enabled = false;
			this.tbChannel.Location = new System.Drawing.Point(88, 104);
			this.tbChannel.Size = new System.Drawing.Size(137, 21);
			this.tbChannel.Text = "";
			// 
			// tbLinkSpeed
			// 
			this.tbLinkSpeed.Enabled = false;
			this.tbLinkSpeed.Location = new System.Drawing.Point(88, 128);
			this.tbLinkSpeed.Size = new System.Drawing.Size(137, 21);
			this.tbLinkSpeed.Text = "";
			// 
			// tbBeacon
			// 
			this.tbBeacon.Enabled = false;
			this.tbBeacon.Location = new System.Drawing.Point(88, 152);
			this.tbBeacon.Size = new System.Drawing.Size(137, 21);
			this.tbBeacon.Text = "";
			// 
			// tbAtim
			// 
			this.tbAtim.Enabled = false;
			this.tbAtim.Location = new System.Drawing.Point(88, 176);
			this.tbAtim.Size = new System.Drawing.Size(137, 21);
			this.tbAtim.Text = "";
			// 
			// label2
			// 
			this.label2.Location = new System.Drawing.Point(8, 38);
			this.label2.Size = new System.Drawing.Size(70, 13);
			this.label2.Text = "State";
			// 
			// label3
			// 
			this.label3.Location = new System.Drawing.Point(8, 62);
			this.label3.Size = new System.Drawing.Size(70, 13);
			this.label3.Text = "SSID";
			// 
			// label4
			// 
			this.label4.Location = new System.Drawing.Point(8, 85);
			this.label4.Size = new System.Drawing.Size(70, 13);
			this.label4.Text = "BSSID";
			// 
			// label5
			// 
			this.label5.Location = new System.Drawing.Point(8, 111);
			this.label5.Size = new System.Drawing.Size(70, 13);
			this.label5.Text = "Channel";
			// 
			// label6
			// 
			this.label6.Location = new System.Drawing.Point(8, 134);
			this.label6.Size = new System.Drawing.Size(70, 15);
			this.label6.Text = "Link Speed";
			// 
			// label7
			// 
			this.label7.Location = new System.Drawing.Point(8, 158);
			this.label7.Size = new System.Drawing.Size(70, 13);
			this.label7.Text = "Beacon";
			// 
			// label8
			// 
			this.label8.Location = new System.Drawing.Point(8, 181);
			this.label8.Size = new System.Drawing.Size(70, 13);
			this.label8.Text = "ATIM";
			// 
			// BssidListPage
			// 
			this.BssidListPage.Controls.Add(this.btnsearch);
			this.BssidListPage.Controls.Add(this.lvBssid);
			this.BssidListPage.Location = new System.Drawing.Point(4, 21);
			this.BssidListPage.Size = new System.Drawing.Size(232, 254);
			this.BssidListPage.Text = "Bssid List";
			this.BssidListPage.EnabledChanged += new System.EventHandler(this.BssidListPage_EnabledChanged);
			// 
			// btnsearch
			// 
			this.btnsearch.Location = new System.Drawing.Point(8, 216);
			this.btnsearch.Text = "Search";
			this.btnsearch.Click += new System.EventHandler(this.btnsearch_Click);
			// 
			// lvBssid
			// 
			this.lvBssid.Columns.Add(this.Ssid);
			this.lvBssid.Columns.Add(this.Bssid);
			this.lvBssid.Columns.Add(this.Rssi);
			this.lvBssid.Columns.Add(this.Channel);
			this.lvBssid.Columns.Add(this.Privacy);
			this.lvBssid.Columns.Add(this.Infra);
			this.lvBssid.FullRowSelect = true;
			this.lvBssid.Size = new System.Drawing.Size(232, 200);
			this.lvBssid.View = System.Windows.Forms.View.Details;
			// 
			// Ssid
			// 
			this.Ssid.Text = "SSID";
			this.Ssid.Width = 42;
			// 
			// Bssid
			// 
			this.Bssid.Text = "BSSID";
			this.Bssid.Width = 88;
			// 
			// Rssi
			// 
			this.Rssi.Text = "RSSI";
			this.Rssi.Width = 44;
			// 
			// Channel
			// 
			this.Channel.Text = "Ch";
			this.Channel.Width = 30;
			// 
			// Privacy
			// 
			this.Privacy.Text = "Privacy";
			this.Privacy.Width = 26;
			// 
			// AboutPage1
			// 
			this.AboutPage1.Controls.Add(this.tbNicMac);
			this.AboutPage1.Controls.Add(this.label9);
			this.AboutPage1.Location = new System.Drawing.Point(4, 21);
			this.AboutPage1.Size = new System.Drawing.Size(232, 254);
			this.AboutPage1.Text = "About";
			this.AboutPage1.EnabledChanged += new System.EventHandler(this.AboutPage1_EnabledChanged);
			this.AboutPage1.Validated += new System.EventHandler(this.AboutPage1_EnabledChanged);
			// 
			// tbNicMac
			// 
			this.tbNicMac.Enabled = false;
			this.tbNicMac.Location = new System.Drawing.Point(96, 128);
			this.tbNicMac.Size = new System.Drawing.Size(128, 21);
			this.tbNicMac.Text = "";
			// 
			// label9
			// 
			this.label9.Location = new System.Drawing.Point(8, 128);
			this.label9.Size = new System.Drawing.Size(80, 20);
			this.label9.Text = "MacAddress";
			// 
			// Infra
			// 
			this.Infra.Text = "Infra";
			this.Infra.Width = 60;
			// 
			// WlanForm
			// 
			this.BackColor = System.Drawing.Color.White;
			this.ClientSize = new System.Drawing.Size(239, 279);
			this.Controls.Add(this.tabControl1);
			this.Text = "Wlan Sample";
			this.WindowState = System.Windows.Forms.FormWindowState.Maximized;
			this.Load += new System.EventHandler(this.WlanForm_Load);

		}
		#endregion

		/// <summary>
		/// 해당 응용 프로그램의 주 진입점입니다.
		/// </summary>

		static void Main() 
		{
			Application.Run(new WlanForm());
		}

		private void AssociatedPage_EnabledChanged(object sender, System.EventArgs e)
		{
		
		}

		private void WlanForm_Load(object sender, System.EventArgs e)
		{
			AssociatedPage.BackColor = System.Drawing.Color.White;
			BssidListPage.BackColor = System.Drawing.Color.White;
			AboutPage1.BackColor = System.Drawing.Color.White;

			byte[] MacAdd = new byte[6];
			string stMac;
			WlanControl1.GetNICMACAddress(MacAdd);
			stMac = String.Format("{0:X2} {1:X2} {2:X2} {3:X2} {4:X2} {5:X2}", MacAdd[0],
				MacAdd[1],MacAdd[2],MacAdd[3],MacAdd[4],MacAdd[5]);
			tbNicMac.Text = stMac;
			

			if(WlanControl1.GetWlanPwrStatus() != 0)
			{
				WlanControl1.SetWlanPwrOn();
			}
			timer1 = new Timer();
			timer1.Interval = 1000;
			timer1.Tick += new EventHandler(TimerOnTick);
			timer1.Enabled = true;



		}
		void GetInformation()
		{
			string stRssi,stBssi;
			int nRssi,nLnkSpd,nStatus;
			int nChannel;
            byte[] Bssid = new byte[6];
			char[] szAdapter = new char[256];
			char[] szSsid = new char[32];


			WlanControl1.GetAdapterName(szAdapter);
			tbAdapter.Text = new string(szAdapter);

			WlanControl1.GetBssid(Bssid);	
			stBssi = String.Format("{0:X2} {1:X2} {2:X2} {3:X2} {4:X2} {5:X2}", Bssid[0],
				  Bssid[1],Bssid[2],Bssid[3],Bssid[4],Bssid[5]);
			tbBssid.Text = stBssi;

			WlanControl1.GetSsidName(szSsid);
			tbSsid.Text = new string(szSsid);

			
            nRssi = WlanControl1.GetRssiValue();
			stRssi = Convert.ToString(nRssi);
            lbRssi.Text =String.Format("{0}dbm",stRssi);
            Setprogress(nRssi);

            nLnkSpd = WlanControl1.GetLinkSpeed();
			if( nLnkSpd == 10000)
			{
				tbLinkSpeed.Text = "1Mbps";
			} 
			else if( nLnkSpd == 20000)
			{
				tbLinkSpeed.Text = "2Mbps";
			} 
			else if( nLnkSpd == 55000)
			{
				tbLinkSpeed.Text = "5.5Mbps";
			} 
			else if( nLnkSpd == 110000)
			{
				tbLinkSpeed.Text = "11Mbps";
			} 
			else if( nLnkSpd == 220000)
			{
				tbLinkSpeed.Text = "22Mbps";
			} 
			else
			{	
				tbLinkSpeed.Text = String.Format("Error:{0}",nLnkSpd);
			}
            
			nChannel = WlanControl1.GetConfig_Channel();
			tbChannel.Text = GetChannelNam(nChannel);

			tbBeacon.Text = String.Format("{0}",WlanControl1.GetConfig_Beacon());
			tbAtim.Text = String.Format("{0}",WlanControl1.GetConfig_Atim());
			
			nStatus = WlanControl1.GetMediaConnStatus();
			switch(nStatus) 
			{
				case 1:
					tbState.Text= "DISCONNECTED";
					break;
				case 0:
					tbState.Text = "CONNECTED"; 
					break;
				case -1:
					tbState.Text = "UNKNOWN";
					break;
				default:
					tbState.Text = string.Format("Error:{0}",nStatus);
					break;
			}   
        	            
		}
		void Setprogress(int nRssi)
		{
			// 2006-01-20 AKAI  -95 to -45
			int nPos = 0;	
			nPos = ((95 + nRssi)*100)/50;
			if(nPos >= 100)
				nPos =100;
			if(nPos <= 0)
				nPos =0;
			progressBar1.Value = nPos;

			// 2006-01-20 AKAI zero config Msg
			if(nRssi < -90)
				lbZCMsg.Text = "No Signal";
			else if(nRssi < -81)
				lbZCMsg.Text = "Very Low";
			else if(nRssi < -71)
				lbZCMsg.Text = "Low";
			else if(nRssi < -67)
				lbZCMsg.Text = "Good";
			else if(nRssi < -57)
				lbZCMsg.Text = "Very Good";
			else
				lbZCMsg.Text = "Excellent";



		}

		string GetChannelNam(int lFrqcy)
		{
			string strRet;
			// 2006-01-20 AKAI  ex)2452MHz -> Channel 9
			if( lFrqcy == 2412000)
				strRet = "Channel 1";
			else if( lFrqcy == 2417000)
				strRet = "Channel 2";
			else if( lFrqcy == 2422000)
				strRet = "Channel 3";
			else if( lFrqcy == 2427000)
				strRet = "Channel 4";
			else if( lFrqcy == 2432000)
				strRet = "Channel 5";
			else if( lFrqcy == 2437000)
				strRet = "Channel 6";
			else if( lFrqcy == 2442000)
				strRet = "Channel 7";
			else if( lFrqcy == 2447000)
				strRet = "Channel 8";
			else if( lFrqcy == 2452000)
				strRet = "Channel 9";
			else if( lFrqcy == 2457000)
				strRet = "Channel 10";
			else if( lFrqcy == 2462000)
				strRet = "Channel 11";
			else if( lFrqcy == 2467000)
				strRet = "Channel 12";
			else if( lFrqcy == 2472000)
				strRet = "Channel 13";
			else
				strRet = String.Format("Error:{0}",lFrqcy);

			return strRet;
		}
		void TimerOnTick(object obj,EventArgs ea)
		{
			GetInformation();
		}
		/*unsafe public struct MC_WLAN_BSSID_LIST
		{
			public byte* MacAddress;// = new byte[6];
			public char* Ssid;// = new char[32];  
			public ulong Privacy;
			public long Rssi;
			public ulong BeaconPeriod;
			public ulong ATIMWindow;
			public ulong DSConfig;
			public uint  InfrastructureMode;
		};*/

		private void BssidListPage_EnabledChanged(object sender, System.EventArgs e)
		{
			
		}

		private void btnsearch_Click(object sender, System.EventArgs e)
		{
			int nCnt,nInf,i;
			string strtemp;
			lvBssid.Items.Clear();
			McBssidList[] BssidList = new McBssidList[20];
            
			Cursor.Current = Cursors.WaitCursor;
			
			WlanControl1.GetBssidList(out BssidList,out nCnt);

			Cursor.Current = Cursors.Default;


		

			for(i=0;i<nCnt;i++)
			{
				ListViewItem BsItem =new ListViewItem();
				BsItem.Text = BssidList[i].Ssid;
				BsItem.SubItems.Add(BssidList[i].MacAddress);
				BsItem.SubItems.Add(string.Format("{0:d}",BssidList[i].Rssi));
				BsItem.SubItems.Add(GetChannelNam(BssidList[i].DSConfig));
				BsItem.SubItems.Add(string.Format("{0:d}",BssidList[i].Privacy));
				nInf = BssidList[i].InfrastructureMode;
				if(nInf == 0)
						strtemp="Ad hoc";
					else if(nInf == 1)
						strtemp="Infrastructure";
					else if(nInf == 2)
						strtemp="automatic mode";
					else
						strtemp="InfrastructureMax ";
				BsItem.SubItems.Add(strtemp);

                
				lvBssid.Items.Add(BsItem);
		
			}

		}

		private void AboutPage1_EnabledChanged(object sender, System.EventArgs e)
		{		
		
		}


	}
}
