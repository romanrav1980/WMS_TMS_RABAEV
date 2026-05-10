// AboutPage.cpp : implementation file
//

#include "stdafx.h"
#include "WlanSample.h"
#include "AboutPage.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAboutPage property page

IMPLEMENT_DYNCREATE(CAboutPage, CPropertyPage)

CAboutPage::CAboutPage() : CPropertyPage(CAboutPage::IDD)
{
	//{{AFX_DATA_INIT(CAboutPage)
	m_strMAc = _T("");
	//}}AFX_DATA_INIT
}

CAboutPage::~CAboutPage()
{
}

void CAboutPage::DoDataExchange(CDataExchange* pDX)
{
	CPropertyPage::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutPage)
	DDX_Text(pDX, IDC_ED_MAC, m_strMAc);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CAboutPage, CPropertyPage)
	//{{AFX_MSG_MAP(CAboutPage)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CAboutPage message handlers

BOOL CAboutPage::OnInitDialog() 
{
	CPropertyPage::OnInitDialog();
	
	// TODO: Add extra initialization here
	UCHAR		uszMacAddress[6]={0,};
	MCGetNICMACAddress(uszMacAddress);
	m_strMAc.Format(_T("%02X %02X %02X %02X %02X %02X"),uszMacAddress[0],uszMacAddress[1],
		uszMacAddress[2],uszMacAddress[3], uszMacAddress[4],uszMacAddress[5]);
	
	UpdateData(FALSE);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
