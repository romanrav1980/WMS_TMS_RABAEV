// MCScanTest.h : main header file for the MCSCANTEST application

#if !defined(AFX_MCSCANTEST_H__2FDEFDA5_01D9_47FD_92EE_1227F74287EF__INCLUDED_)
#define AFX_MCSCANTEST_H__2FDEFDA5_01D9_47FD_92EE_1227F74287EF__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestApp:
// See MCScanTest.cpp for the implementation of this class
//

class CMCScanTestApp : public CWinApp
{
public:
	CMCScanTestApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCScanTestApp)
	public:
	virtual BOOL InitInstance();
	virtual BOOL PreTranslateMessage(MSG* pMsg);
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CMCScanTestApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCSCANTEST_H__2FDEFDA5_01D9_47FD_92EE_1227F74287EF__INCLUDED_)
