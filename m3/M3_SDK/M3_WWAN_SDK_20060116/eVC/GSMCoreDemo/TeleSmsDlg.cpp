// TeleSmsDlg.cpp : implementation file
//

#include "stdafx.h"
#include "GSMCoreDemo.h"
#include "TeleSmsDlg.h"

#include "GSMCore.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CTeleSmsDlg dialog


CTeleSmsDlg::CTeleSmsDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CTeleSmsDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CTeleSmsDlg)
	m_szCallPhoneNum = _T("");
	m_szDTMFString = _T("");
	m_szSMSData = _T("");
	m_szSMSPhoneNum = _T("");
	//}}AFX_DATA_INIT
}


void CTeleSmsDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CTeleSmsDlg)
	DDX_Text(pDX, IDC_EDIT_CALL_PHONE_NUM, m_szCallPhoneNum);
	DDX_Text(pDX, IDC_EDIT_DTMF_STRING, m_szDTMFString);
	DDX_Text(pDX, IDC_EDIT_SMS_DATA, m_szSMSData);
	DDX_Text(pDX, IDC_EDIT_SMS_PHONE_NUM, m_szSMSPhoneNum);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CTeleSmsDlg, CDialog)
	//{{AFX_MSG_MAP(CTeleSmsDlg)
	ON_BN_CLICKED(IDC_MAKE_CALL, OnMakeCall)
	ON_BN_CLICKED(IDC_END_CALL, OnEndCall)
	ON_BN_CLICKED(IDC_DTMF_SEND, OnDtmfSend)
	ON_BN_CLICKED(IDC_SMS_SEND, OnSmsSend)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CTeleSmsDlg message handlers

void CTeleSmsDlg::OnMakeCall() 
{
	UpdateData();

	MCMakeCall(m_szCallPhoneNum.GetBuffer(0));		
}

void CTeleSmsDlg::OnEndCall() 
{
	MCEndCall();
}

void CTeleSmsDlg::OnDtmfSend() 
{
	UpdateData();
	MCDTMFSend(m_szDTMFString.GetBuffer(0));	
}

void CTeleSmsDlg::OnSmsSend() 
{
	UpdateData();

	MCSendSMS(m_szSMSPhoneNum.GetBuffer(0), m_szSMSData.GetBuffer(0));
}

BOOL CTeleSmsDlg::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	ShowWindow(SW_SHOWMAXIMIZED);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
