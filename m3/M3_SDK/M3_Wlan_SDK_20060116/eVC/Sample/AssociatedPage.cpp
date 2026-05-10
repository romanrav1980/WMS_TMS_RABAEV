// AssociatedPage.cpp : implementation file
//

#include "stdafx.h"
#include "WlanSample.h"
#include "AssociatedPage.h"




#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAssociatedPage property page

IMPLEMENT_DYNCREATE(CAssociatedPage, CPropertyPage)

CAssociatedPage::CAssociatedPage() : CPropertyPage(CAssociatedPage::IDD)
{
	//{{AFX_DATA_INIT(CAssociatedPage)
	m_strAtim = _T("");
	m_strBeacon = _T("");
	m_strBssId = _T("");
	m_strChannel = _T("");
	m_strLinkSpeed = _T("");
	m_strSsid = _T("");
	m_strState = _T("");
	m_strAdaper = _T("");
	//}}AFX_DATA_INIT
}

CAssociatedPage::~CAssociatedPage()
{
}

void CAssociatedPage::DoDataExchange(CDataExchange* pDX)
{
	CPropertyPage::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAssociatedPage)
	DDX_Control(pDX, IDC_PROGRESS, m_ProgressBar);
	DDX_Text(pDX, IDC_ED_ATIM, m_strAtim);
	DDX_Text(pDX, IDC_ED_BEACON, m_strBeacon);
	DDX_Text(pDX, IDC_ED_BSSID, m_strBssId);
	DDX_Text(pDX, IDC_ED_CHANNEL, m_strChannel);
	DDX_Text(pDX, IDC_ED_LINK_SPEED, m_strLinkSpeed);
	DDX_Text(pDX, IDC_ED_SSID, m_strSsid);
	DDX_Text(pDX, IDC_ED_STATE, m_strState);
	DDX_Text(pDX, IDC_ED_ADAPTER, m_strAdaper);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CAssociatedPage, CPropertyPage)
	//{{AFX_MSG_MAP(CAssociatedPage)
	ON_WM_TIMER()
	ON_WM_CLOSE()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAssociatedPage message handlers

BOOL CAssociatedPage::OnInitDialog() 
{
	CPropertyPage::OnInitDialog();
	
	// TODO: Add extra initialization here
	TCHAR szName[256];
	MCGetAdapterName(szName);
	SetDlgItemText(IDC_ED_ADAPTER,(LPCTSTR)szName);

	m_ProgressBar.SetRange(0,100);
	
	SetTimer(1001,1000,NULL);
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void CAssociatedPage::OnTimer(UINT nIDEvent) 
{
	// TODO: Add your message handler code here and/or call default
	GetInformation();
	CPropertyPage::OnTimer(nIDEvent);
}

void CAssociatedPage::GetInformation()
{
	CString		strMsg;
	int       ulconfig= 0;
	int			nRssi,nStatus,nLinkSpeed;
	TCHAR		szSsid[32]={0,};
	UCHAR		uszBssid[6]={0,};
	TCHAR       szName[256];

	MCGetAdapterName(szName);
	m_strAdaper = (LPCTSTR)szName;

	nRssi= MCGetRssiValue();
	SetProgBar(nRssi);
	strMsg.Format(L"%d dbm",nRssi);
	SetDlgItemText(IDC_ST_RSSI,strMsg);

	nStatus = MCGetMediaConnStatus();
	switch(nStatus) {
	case 1:
		m_strState = _T("DISCONNECTED");
		break;
	case 0:
		m_strState = _T("CONNECTED"); 
		break;
	case -1:
		m_strState = _T("UNKNOWN");
	default:
		m_strState.Format(_T("Err: %d"),nStatus);
		break;
	}
	
	MCGetSsidName(szSsid);
//	SetDlgItemText(IDC_ED_SSID,(LPCTSTR)szSsid);
	m_strSsid = (LPCTSTR)szSsid;

	MCGetBssid(uszBssid);
	m_strBssId.Format(_T("%02X %02X %02X %02X %02X %02X"),uszBssid[0],uszBssid[1],
		uszBssid[2],uszBssid[3], uszBssid[4],uszBssid[5]);
	
	nLinkSpeed = MCGetLinkSpeed();	
	if( nLinkSpeed == 10000)
	{
		m_strLinkSpeed = _T("1Mbps");
	} else if( nLinkSpeed == 20000)
	{
		m_strLinkSpeed = _T("2Mbps");
	} else if( nLinkSpeed == 55000)
	{
		m_strLinkSpeed = _T("5.5Mbps");
	} else if( nLinkSpeed == 110000)
	{
		m_strLinkSpeed = _T("11Mbps");
	} else if( nLinkSpeed == 220000)
	{
		m_strLinkSpeed = _T("22Mbps");
	} else
	{	
		m_strLinkSpeed.Format(_T("Err: %d"),nLinkSpeed);
	}
	ulconfig = MCGetConfiguration(FN_CONFIG_CHANNEL);
	GetChannelNam(ulconfig);

	ulconfig = MCGetConfiguration(FN_CONFIG_BEACON);
	m_strBeacon.Format(_T("%d"),ulconfig);
	ulconfig = MCGetConfiguration(FN_CONFIG_ATIM);

	m_strAtim.Format(_T("%d"),ulconfig);
	
	UpdateData(FALSE);
}

void CAssociatedPage::SetProgBar(int nRssi)
{
	// 2006-01-04 AKAI  -95 to -45
	int nPos = 0;	
	nPos = ((95 + nRssi)*100)/50;
	m_ProgressBar.SetPos(nPos);

	// 2006-01-04 AKAI  zero config Msg
	if(nRssi < -90)
	   	SetDlgItemText(IDC_ST_ZC,_T("No Signal"));
	else if(nRssi < -81)
		SetDlgItemText(IDC_ST_ZC,_T("Very Low"));
	else if(nRssi < -71)
		SetDlgItemText(IDC_ST_ZC,_T("Low"));
	else if(nRssi < -67)
		SetDlgItemText(IDC_ST_ZC,_T("Good"));
	else if(nRssi < -57)
		SetDlgItemText(IDC_ST_ZC,_T("Very Good"));
	else
		SetDlgItemText(IDC_ST_ZC,_T("Excellent"));

}

void CAssociatedPage::GetChannelNam(ULONG ulFrqcy)
{
	// 2006-01-04 AKAI  ex)2452MHz -> Channel 9
	if( ulFrqcy == 2412000)
		m_strChannel = _T("Channel 1");
	else if( ulFrqcy == 2417000)
		m_strChannel = _T("Channel 2");
    else if( ulFrqcy == 2422000)
		m_strChannel = _T("Channel 3");
	else if( ulFrqcy == 2427000)
		m_strChannel = _T("Channel 4");
    else if( ulFrqcy == 2432000)
		m_strChannel = _T("Channel 5");
	else if( ulFrqcy == 2437000)
		m_strChannel = _T("Channel 6");
	else if( ulFrqcy == 2442000)
		m_strChannel = _T("Channel 7");
	else if( ulFrqcy == 2447000)
		m_strChannel = _T("Channel 8");
	else if( ulFrqcy == 2452000)
		m_strChannel = _T("Channel 9");
	else if( ulFrqcy == 2457000)
		m_strChannel = _T("Channel 10");
	else if( ulFrqcy == 2462000)
		m_strChannel = _T("Channel 11");
	else if( ulFrqcy == 2467000)
		m_strChannel = _T("Channel 12");
	else if( ulFrqcy == 2472000)
		m_strChannel = _T("Channel 13");
	else
		m_strChannel.Format(_T("%d"),ulFrqcy);
	return;
}

void CAssociatedPage::OnClose() 
{
	// TODO: Add your message handler code here and/or call default
	KillTimer(1001);
	CPropertyPage::OnClose();
}
