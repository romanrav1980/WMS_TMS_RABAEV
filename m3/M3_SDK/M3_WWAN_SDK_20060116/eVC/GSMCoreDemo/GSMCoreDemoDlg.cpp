// GSMCoreDemoDlg.cpp : implementation file
//

#include "stdafx.h"
#include "GSMCoreDemo.h"
#include "GSMCoreDemoDlg.h"
#include "RasPbDlg.h"
#include "TeleSmsDlg.h"

#include "GSMCore.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CGSMCoreDemoDlg dialog

CGSMCoreDemoDlg::CGSMCoreDemoDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CGSMCoreDemoDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CGSMCoreDemoDlg)
	m_szRSSI = _T("");
	m_szTime = _T("");
	m_szIMEI = _T("");
	m_szSIMState = _T("");
	m_szSIMPIN = _T("");
	m_szSIMPUK = _T("");
	m_szNewPIN = _T("");
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CGSMCoreDemoDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CGSMCoreDemoDlg)
	DDX_Text(pDX, IDC_STATIC_RSSI, m_szRSSI);
	DDX_Text(pDX, IDC_STATIC_TIME, m_szTime);
	DDX_Text(pDX, IDC_STATIC_IMEI, m_szIMEI);
	DDX_Text(pDX, IDC_STATIC_SIM_STATE, m_szSIMState);
	DDX_Text(pDX, IDC_EDIT_SIM_PIN, m_szSIMPIN);
	DDV_MaxChars(pDX, m_szSIMPIN, 8);
	DDX_Text(pDX, IDC_EDIT_SIM_PUK, m_szSIMPUK);
	DDV_MaxChars(pDX, m_szSIMPUK, 8);
	DDX_Text(pDX, IDC_EDIT_NEW_PIN, m_szNewPIN);
	DDV_MaxChars(pDX, m_szNewPIN, 8);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CGSMCoreDemoDlg, CDialog)
	//{{AFX_MSG_MAP(CGSMCoreDemoDlg)
	ON_BN_CLICKED(IDC_BTN_GSM_TIME, OnBtnGsmTime)
	ON_BN_CLICKED(IDC_BTN_GET_RSSI, OnBtnGetRssi)
	ON_BN_CLICKED(IDC_BTN_IMEI, OnBtnImei)
	ON_WM_DESTROY()
	ON_BN_CLICKED(IDC_BTN_CALL_SMS, OnBtnCallSms)
	ON_BN_CLICKED(IDC_BTN_RAS_PB, OnBtnRasPb)
	ON_BN_CLICKED(IDC_BTN_SIM_STATE, OnBtnSimState)
	ON_BN_CLICKED(IDC_BTN_ENTER_SIM, OnBtnEnterSim)
	ON_BN_CLICKED(IDC_BTN_ENTER_PUK, OnBtnEnterPuk)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CGSMCoreDemoDlg message handlers

BOOL CGSMCoreDemoDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	CenterWindow(GetDesktopWindow());	// center to the hpc screen

	ShowWindow(SW_SHOWMAXIMIZED);

	// GSM Lib Initalize
	MCInitGSMLib (this->m_hWnd);

	return TRUE;  // return TRUE  unless you set the focus to a control
}



void CGSMCoreDemoDlg::OnBtnGsmTime() 
{
	WCHAR szData[256] = {NULL,};


	// Getting DateTime from Phone
	int nRet = MCGetGSMTime (szData);

	m_szTime = CString(szData);

	UpdateData(FALSE);	
}

void CGSMCoreDemoDlg::OnBtnGetRssi() 
{
	int	nRssi = 0;

	// Getting DateTime from Phone
	int nRet = MCGetRSSI (&nRssi);

	m_szRSSI.Format(L"%d", nRssi);

	UpdateData(FALSE);		
}

void CGSMCoreDemoDlg::OnBtnImei() 
{
	WCHAR szData[256] = {NULL,};

	// Getting IMEI from Phone
	int nRet = MCGetIMEI (szData);

	m_szIMEI = CString(szData);

	UpdateData(FALSE);			
}

void CGSMCoreDemoDlg::OnDestroy() 
{
	CDialog::OnDestroy();
	
	MCUninitGSMLib();
	
}

void CGSMCoreDemoDlg::OnBtnSimState() 
{
	int nSIMState = TYPE_SIM_READY;
	int nRet = MCCheckSIMPin (&nSIMState);
	if (nRet == ERROR_NONE)
	{
		switch(nSIMState) 
		{
		case TYPE_SIM_READY:
			m_szSIMState = L"SIM Ready";
			break;
		case TYPE_SIM_PIN:
			m_szSIMState = L"SIM PIN";
			break;
		case TYPE_SIM_PUK:
			m_szSIMState = L"SIM PUK";
			break;
		case TYPE_SIM_PUK2:
			m_szSIMState = L"SIM PUK2";
			break;
		default:
			m_szSIMState = L"....";
			break;
		}
	}

	UpdateData (FALSE);
}


void CGSMCoreDemoDlg::OnBtnEnterSim() 
{
	UpdateData ();

	if (m_szSIMPIN.GetLength() < 4) return;

	int nRet = MCEnterSIMPin (m_szSIMPIN.GetBuffer(0));
	if (nRet == ERROR_NONE)
	{
		AfxMessageBox (L"Success MCEnterSIMPin");
	}
	
}

void CGSMCoreDemoDlg::OnBtnEnterPuk() 
{
	UpdateData ();

	if (m_szSIMPUK.GetLength() < 4) return;
	if (m_szNewPIN.GetLength() < 4) return;

	int nRet = MCEnterPUKNumber (m_szSIMPUK.GetBuffer(0), m_szNewPIN.GetBuffer(0));
	if (nRet == ERROR_NONE)
	{
		AfxMessageBox (L"Success MCEnterPUKNumber");
	}
}

void CGSMCoreDemoDlg::OnBtnCallSms() 
{
	CTeleSmsDlg Dlg;
	Dlg.DoModal();
}

void CGSMCoreDemoDlg::OnBtnRasPb() 
{
	CRasPbDlg Dlg;
	Dlg.DoModal();
}



