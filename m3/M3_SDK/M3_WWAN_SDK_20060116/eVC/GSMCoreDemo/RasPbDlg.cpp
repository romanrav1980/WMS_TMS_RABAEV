// RasPbDlg.cpp : implementation file
//

#include "stdafx.h"
#include "GSMCoreDemo.h"
#include "RasPbDlg.h"

#include "GSMCore.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CRasPbDlg dialog


CRasPbDlg::CRasPbDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CRasPbDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CRasPbDlg)
	m_szIndex = _T("");
	m_szName = _T("");
	m_szPhoneNum = _T("");
	m_szResult = _T("");
	//}}AFX_DATA_INIT
}


void CRasPbDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CRasPbDlg)
	DDX_Text(pDX, IDC_EDIT_INDEX, m_szIndex);
	DDX_Text(pDX, IDC_EDIT_NAME, m_szName);
	DDX_Text(pDX, IDC_EDIT_PHONE_NUM, m_szPhoneNum);
	DDX_Text(pDX, IDC_STATIC_RESULT, m_szResult);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(CRasPbDlg, CDialog)
	//{{AFX_MSG_MAP(CRasPbDlg)
	ON_BN_CLICKED(IDC_BTN_CREATE_RAS_ENTRY, OnBtnCreateRasEntry)
	ON_BN_CLICKED(IDC_BTN_RAS_CONNECT, OnBtnRasConnect)
	ON_BN_CLICKED(IDC_BTN_RAS_HANG_UP, OnBtnRasHangUp)
	ON_BN_CLICKED(IDC_BTN_WRITE, OnBtnPBWrite)
	ON_BN_CLICKED(IDC_BTN_READ, OnBtnPBRead)
	ON_BN_CLICKED(IDC_BTN_DEL, OnBtnPBDel)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CRasPbDlg message handlers

void CRasPbDlg::OnBtnCreateRasEntry() 
{
	int nRet = MCCreateRasEntry (L"My GPRS", 115200, L"*99***1#", L"+CGDCONT=1,\"IP\",\"kipa\"", L"", L"", L" ", L"", L"", L"", L"", L"" );	

	if (nRet == ERROR_NONE)
	{
		m_szResult = L"Success MCCreateRasEntry";
	}

	UpdateData(FALSE);	
}

void CRasPbDlg::OnBtnRasConnect() 
{
	int nRet = MCDoRASConnect (L"My GPRS");
	if (nRet == ERROR_NONE)
	{
		m_szResult = L"Success MCDoRASConnect";
	}

	UpdateData(FALSE);	
}

void CRasPbDlg::OnBtnRasHangUp() 
{
	int nRet = MCDoRASHangup ();
	if (nRet == ERROR_NONE)
	{
		m_szResult = L"Success MCDoRASHangup";
	}

	UpdateData(FALSE);			
}

void CRasPbDlg::OnBtnPBWrite() 
{
	UpdateData();

	int		nIndex = _wtoi(m_szIndex.GetBuffer(0));
	int		nRet = ERROR_NONE;
	WCHAR	szErrorString[256] = {NULL,};

	if (nIndex < 1) return ;

	nRet = MCWritePhoneBookEntry (nIndex, m_szPhoneNum.GetBuffer(0), m_szName.GetBuffer(0));
	if (nRet != ERROR_NONE)
	{
		MCGetErrMsg(nRet, szErrorString);
		m_szResult = szErrorString;
	}
	else
	{
		m_szResult = L"MCWritePhoneBookEntry Success";
	}

	UpdateData(FALSE);
}

void CRasPbDlg::OnBtnPBRead() 
{
	UpdateData();

	int		nIndex = _wtoi(m_szIndex.GetBuffer(0));
	int		nRet = ERROR_NONE;
	WCHAR	szPhoneNumber[128] = {NULL,};
	WCHAR	szName[128] = {NULL,};
	WCHAR	szErrorString[256] = {NULL,};

	if (nIndex < 1) return ;

	nRet = MCReadPhoneBookEntry (nIndex, szPhoneNumber, szName);
	if (nRet != ERROR_NONE)
	{
		MCGetErrMsg(nRet, szErrorString);
		m_szResult = szErrorString;
	}
	else
	{
		m_szPhoneNum = szPhoneNumber;
		m_szName = szName;
		m_szResult = L"MCReadPhoneBookEntry Success";
	}

	UpdateData(FALSE);
	
}

void CRasPbDlg::OnBtnPBDel() 
{
	UpdateData();

	int		nIndex = _wtoi(m_szIndex.GetBuffer(0));
	int		nRet = ERROR_NONE;
	WCHAR	szErrorString[256] = {NULL,};

	if (nIndex < 1) return ;

	nRet = MCDeletePhoneBookEntry (nIndex);
	if (nRet != ERROR_NONE)
	{
		MCGetErrMsg(nRet, szErrorString);
		m_szResult = szErrorString;
	}
	else
	{
		m_szResult = L"MCDeletePhoneBookEntry Success";
	}

	UpdateData(FALSE);
}

BOOL CRasPbDlg::OnInitDialog() 
{
	CDialog::OnInitDialog();
	
	ShowWindow(SW_SHOWMAXIMIZED);
	
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}
