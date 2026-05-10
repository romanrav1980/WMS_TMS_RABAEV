// CamCoreDemo.h : main header file for the CAMCOREDEMO application
//

#if !defined(AFX_CAMCOREDEMO_H__0A0111B3_38CC_420B_B762_C09EB56B0FB2__INCLUDED_)
#define AFX_CAMCOREDEMO_H__0A0111B3_38CC_420B_B762_C09EB56B0FB2__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CCamCoreDemoApp:
// See CamCoreDemo.cpp for the implementation of this class
//

class CCamCoreDemoApp : public CWinApp
{
public:
	CCamCoreDemoApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCamCoreDemoApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CCamCoreDemoApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CAMCOREDEMO_H__0A0111B3_38CC_420B_B762_C09EB56B0FB2__INCLUDED_)
