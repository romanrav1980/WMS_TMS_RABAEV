// NewDlg.cpp : implementation file
//

#include "stdafx.h"
#include "MCScanTest.h"
#include "NewDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CNewDlg dialog
#include "MCSSLib.h"
extern CMCSSLib* g_pMCScanner;

CNewDlg::CNewDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CNewDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CNewDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
}


void CNewDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CNewDlg)
	DDX_Control(pDX, IDC_LIST1, m_ctrBarList);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CNewDlg, CDialog)
	//{{AFX_MSG_MAP(CNewDlg)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CNewDlg message handlers

BOOL CNewDlg::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	// TODO: Add extra initialization here
	g_pMCScanner->RegisterWindow(this->m_hWnd);

	m_ctrBarList.InsertColumn(0,L"TYPE",LVCFMT_LEFT,100);
	m_ctrBarList.InsertColumn(1,L"DATA",LVCFMT_LEFT,300);
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

BOOL CNewDlg::PreTranslateMessage(MSG* pMsg) 
{
	// TODO: Add your specialized code here and/or call the base class
	TCHAR szBarData[2711];
	TCHAR szBarType[32];
	switch (pMsg->message) {

		case WM_SCAN_DATA : 
			SetDlgItemText(IDC_ST_MSG,L"Scanner Data Read");
			g_pMCScanner->GetScanDataWchar(szBarData,szBarType);
			
			m_ctrBarList.InsertItem(0,szBarType);
			m_ctrBarList.SetItemText(0,1,szBarData);
			break;
			// 2006-01-17 AKAI resume Event;
			// UseResumeWindow를 사용한다면 불필요
		case WM_SCANINIT_START:
			SetDlgItemText(IDC_ST_MSG,L"Scanner Initialize...");
			break;

		case WM_SCANINIT_END:
			SetDlgItemText(IDC_ST_MSG,L"Init Success");
			break;
			
	}
	return CDialog::PreTranslateMessage(pMsg);
}
