// MCScanTestDlg.cpp : implementation file
//

#include "stdafx.h"
#include "MCScanTest.h"
#include "MCScanTestDlg.h"
#include "NewDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestDlg dialog

#include "MCSSLib.h"
extern CMCSSLib* g_pMCScanner;

CMCScanTestDlg::CMCScanTestDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CMCScanTestDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CMCScanTestDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CMCScanTestDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMCScanTestDlg)
	DDX_Control(pDX, IDC_LT_DATA, m_ctrListBox);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CMCScanTestDlg, CDialog)
	//{{AFX_MSG_MAP(CMCScanTestDlg)
	ON_BN_CLICKED(IDC_BTN_READ, OnBtnRead)
	ON_BN_CLICKED(IDC_BTN_CANCEL, OnBtnCancel)
	ON_MESSAGE(WM_SCAN_DATA,OnBarCodeRead)
	ON_MESSAGE(WM_SCANINIT_START,OnScanintiStart)
	ON_MESSAGE(WM_SCANINIT_END,OnScanintiEnd)
	ON_BN_CLICKED(IDC_BTN_NEW_DLG, OnBtnNewDlg)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestDlg message handlers

BOOL CMCScanTestDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	CenterWindow(GetDesktopWindow());	// center to the hpc screen

	// TODO: Add extra initialization here

	// 2006-01-16 AKAI  OnBarCodeRead를 받을 window 지정,기본 사운드 사용,Resume시 원도우 사용 
	g_pMCScanner->RegisterWindow(this->m_hWnd);
	g_pMCScanner->UseDefaultSound(TRUE);
	g_pMCScanner->UseResumeWindow(TRUE);

	
	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CMCScanTestDlg::OnBtnRead() 
{
	// TODO: Add your control notification handler code here
	g_pMCScanner->Read();
}
//AKAI BarCode Reading을 success 했을 경우 받는 Message
void CMCScanTestDlg::OnBarCodeRead(WPARAM wParam,LPARAM lParam)
{	
	TCHAR szBarData[2711];  //요거는 PDF417 땜에 2711로 설정 했습니다. 사용하는 barcode 에 따라 적정하게 하셔도 무방합니다.
	TCHAR szBarType[32];
	SetDlgItemText(IDC_ED_MSG,L"Scanner Data Read...");
	g_pMCScanner->GetScanDataWchar(szBarData,szBarType);
	SetDlgItemText(IDC_ED_TYPE,(LPCTSTR)szBarType);
	m_ctrListBox.AddString((LPCTSTR)szBarData);
	m_ctrListBox.SetCurSel(m_ctrListBox.GetCount()-1);
}

void CMCScanTestDlg::OnBtnCancel() 
{
	// TODO: Add your control notification handler code here
	g_pMCScanner->ReadCancel();
}

void CMCScanTestDlg::OnBtnNewDlg() 
{
	// TODO: Add your control notification handler code here
	CNewDlg dlg;
	dlg.DoModal();
	//AKAI Dialog 가 종료된후 OnBarCodeRead 받을 window 지정 
	g_pMCScanner->RegisterWindow(this->m_hWnd);
	
}

// 2006-01-21 AKAI  Resume Event 에 대한 message 을 받아서 처리할때 사용
// 이때 Scanner에 대한 init나 Close를 사용하지마세요.
// UseResumeWindow를 사용한다면 불필요하나,
// OnScanintiStart는 프로그램에서 PDA의 Rusume 상태를 알고 싶을때 사용 하셔도 될듯...
void CMCScanTestDlg::OnScanintiStart(WPARAM wParam,LPARAM lParam)
{	
	SetDlgItemText(IDC_ED_MSG,L"Scanner Initialize...");
}

void CMCScanTestDlg::OnScanintiEnd(WPARAM wParam,LPARAM lParam)
{
	SetDlgItemText(IDC_ED_MSG,L"Init Success");	
}
