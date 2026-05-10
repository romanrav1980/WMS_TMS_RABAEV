// BssidListPage.cpp : implementation file
//

#include "stdafx.h"
#include "WlanSample.h"
#include "BssidListPage.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CBssidListPage property page

IMPLEMENT_DYNCREATE(CBssidListPage, CPropertyPage)

CBssidListPage::CBssidListPage() : CPropertyPage(CBssidListPage::IDD)
{
	//{{AFX_DATA_INIT(CBssidListPage)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}

CBssidListPage::~CBssidListPage()
{
}

void CBssidListPage::DoDataExchange(CDataExchange* pDX)
{
	CPropertyPage::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CBssidListPage)
	DDX_Control(pDX, IDC_LIST_BSSID, m_ctrListBssid);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CBssidListPage, CPropertyPage)
	//{{AFX_MSG_MAP(CBssidListPage)
	ON_BN_CLICKED(IDC_BTN_BSSID_LIST, OnBtnBssidList)
	ON_BN_CLICKED(IDC_BTN_SCAN, OnBtnScan)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CBssidListPage message handlers

void CBssidListPage::OnBtnBssidList() 
{
	// TODO: Add your control notification handler code here
	

	CString strTemp;
	int nCount,nInf;
	MC_WLAN_BSSID_LIST BssidList[20];

	m_ctrListBssid.DeleteAllItems();
	MCGetBssidList(BssidList,&nCount);

	
	int i;
	
	for(i=0; i < nCount;i++)
	{
		strTemp.Format(L"%s",BssidList[i].Ssid);
		m_ctrListBssid.InsertItem(i,strTemp,0);

		strTemp.Format(_T("%02X %02X %02X %02X %02X %02X"),BssidList[i].MacAddress[0],BssidList[i].MacAddress[1],
		BssidList[i].MacAddress[2],BssidList[i].MacAddress[3], BssidList[i].MacAddress[4],BssidList[i].MacAddress[5]);
		m_ctrListBssid.SetItemText(i,1,strTemp);

		strTemp.Format(L"%d",BssidList[i].Rssi);
		m_ctrListBssid.SetItemText(i,2,strTemp);

		GetChannelNam(BssidList[i].DSConfig);
		m_ctrListBssid.SetItemText(i,3,m_strChannel);

		strTemp.Format(L"%d",BssidList[i].Privacy);
		m_ctrListBssid.SetItemText(i,4,strTemp);

		nInf = BssidList[i].InfrastructureMode;
		if(nInf == 0)
	   		m_ctrListBssid.SetItemText(i,5,_T("Ad hoc"));
		else if(nInf == 1)
			m_ctrListBssid.SetItemText(i,5,_T("Infrastructure"));
		else if(nInf == 2)
			m_ctrListBssid.SetItemText(i,5,_T("automatic mode"));
		else
			m_ctrListBssid.SetItemText(i,5,_T("InfrastructureMax "));
			
	

		
	}

//	m_ctrListBssid.InsertItem(i,strMsg,0);

}

void CBssidListPage::OnBtnScan() 
{
	// TODO: Add your control notification handler code here
	MCSetBssidListScan();
}

BOOL CBssidListPage::OnInitDialog() 
{
	CPropertyPage::OnInitDialog();
	
	// TODO: Add extra initialization here
	m_ctrListBssid.InsertColumn(0,L"SSID",LVCFMT_LEFT,50);
	m_ctrListBssid.InsertColumn(1,L"BSSID",LVCFMT_LEFT,102);
	m_ctrListBssid.InsertColumn(2,L"RSSI",LVCFMT_LEFT,28);
	m_ctrListBssid.InsertColumn(3,L"Ch",LVCFMT_LEFT,25);
	m_ctrListBssid.InsertColumn(4,L"Privacy",LVCFMT_LEFT,20);
	m_ctrListBssid.InsertColumn(5,L"Infrastructure",LVCFMT_LEFT,40);

	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
void CBssidListPage::GetChannelNam(ULONG ulFrqcy)
{
	// 2006-01-04 AKAI  ex)2452MHz -> Channel 9
	if( ulFrqcy == 2412000)
		m_strChannel = _T("1");
	else if( ulFrqcy == 2417000)
		m_strChannel = _T("2");
    else if( ulFrqcy == 2422000)
		m_strChannel = _T("3");
	else if( ulFrqcy == 2427000)
		m_strChannel = _T("4");
    else if( ulFrqcy == 2432000)
		m_strChannel = _T("5");
	else if( ulFrqcy == 2437000)
		m_strChannel = _T("6");
	else if( ulFrqcy == 2442000)
		m_strChannel = _T("7");
	else if( ulFrqcy == 2447000)
		m_strChannel = _T("8");
	else if( ulFrqcy == 2452000)
		m_strChannel = _T("9");
	else if( ulFrqcy == 2457000)
		m_strChannel = _T("10");
	else if( ulFrqcy == 2462000)
		m_strChannel = _T("11");
	else if( ulFrqcy == 2467000)
		m_strChannel = _T("12");
	else if( ulFrqcy == 2472000)
		m_strChannel = _T("13");
	else
		m_strChannel.Format(_T("%d"),ulFrqcy);
	return;
}
