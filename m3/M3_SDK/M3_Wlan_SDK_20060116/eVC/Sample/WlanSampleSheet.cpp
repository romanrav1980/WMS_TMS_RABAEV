// WlanSampleSheet.cpp : implementation file
//

#include "stdafx.h"
#include "WlanSample.h"
#include "WlanSampleSheet.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CWlanSampleSheet

IMPLEMENT_DYNAMIC(CWlanSampleSheet, CPropertySheet)

CWlanSampleSheet::CWlanSampleSheet(UINT nIDCaption, CWnd* pParentWnd, UINT iSelectPage)
	:CPropertySheet(nIDCaption, pParentWnd, iSelectPage)
{	
	AddPage(&m_AssociatedPage);
	AddPage(&m_BssidListPage);
	AddPage(&m_AboutPage);
	
}

CWlanSampleSheet::CWlanSampleSheet(LPCTSTR pszCaption, CWnd* pParentWnd, UINT iSelectPage)
	:CPropertySheet(pszCaption, pParentWnd, iSelectPage)
{	
	
	AddPage(&m_AssociatedPage);
	AddPage(&m_BssidListPage);
	AddPage(&m_AboutPage);
	
}

CWlanSampleSheet::~CWlanSampleSheet()
{
}


BEGIN_MESSAGE_MAP(CWlanSampleSheet, CPropertySheet)
	//{{AFX_MSG_MAP(CWlanSampleSheet)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CWlanSampleSheet message handlers


BOOL CWlanSampleSheet::OnInitDialog() 
{
	BOOL bResult = CPropertySheet::OnInitDialog();
	
	// TODO: Add your specialized code here
	MoveWindow(0, -1, 240, 300);

	
	if(MCGetWlanPwrStatus())
	{
		if(MessageBox(L"Wireless LAN Power ON?",L"",MB_YESNO) == IDNO){
			OnClose();
		}
	}
	MCSetWlanPwrOn();
	return bResult;
}
