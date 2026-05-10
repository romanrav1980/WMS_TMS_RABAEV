// MCScanTest.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "MCScanTest.h"
#include "MCScanTestDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

#include "MCSSLib.h"
CMCSSLib* g_pMCScanner =NULL;


BOOL g_bFlag = FALSE;

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestApp

BEGIN_MESSAGE_MAP(CMCScanTestApp, CWinApp)
	//{{AFX_MSG_MAP(CMCScanTestApp)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestApp construction

CMCScanTestApp::CMCScanTestApp()
	: CWinApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CMCScanTestApp object

CMCScanTestApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestApp initialization

BOOL CMCScanTestApp::InitInstance()
{
	// Standard initialization
	// If you are not using these features and wish to reduce the size
	//  of your final executable, you should remove from the following
	//  the specific initialization routines you do not need.
	g_pMCScanner = new CMCSSLib;
	//AKAI 스케너를 활성화 합니다. 
	if(g_pMCScanner->InitScanner() != ERROR_NONE){
		AfxMessageBox(L"Scanner Init Fail...\r\nOTL");
		return FALSE;
	}	

	CMCScanTestDlg dlg;
	m_pMainWnd = &dlg;
	int nResponse = dlg.DoModal();
	if (nResponse == IDOK)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with OK
	}
	else if (nResponse == IDCANCEL)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with Cancel
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.

	//AKAI Scanner Close 를 잊지마세요~
	delete g_pMCScanner;
	g_pMCScanner->CloseScanner();

	return FALSE;
}

BOOL CMCScanTestApp::PreTranslateMessage(MSG* pMsg) 
{
	// TODO: Add your specialized code here and/or call the base class
	//펑션키를 사용하는 OS 버전에서  스케너 키값을 받고 싶다...라면
	//lParam의 값을 사용하지 마세요.
	//lParam 사용이유: VK_F22 의 repeat KeyDown Message 를 처리하기 위해서 입니다.

 	switch(pMsg->message){
	case WM_KEYDOWN :
		
		if(pMsg->wParam==VK_F22 && pMsg->lParam == 0x00810001){
			g_pMCScanner->Read();
		}
		break;
	case WM_KEYUP :
		if(pMsg->wParam==VK_F22)
		{
			g_pMCScanner->ReadCancel();
		}
		break;
	}

	return CWinApp::PreTranslateMessage(pMsg);
}
