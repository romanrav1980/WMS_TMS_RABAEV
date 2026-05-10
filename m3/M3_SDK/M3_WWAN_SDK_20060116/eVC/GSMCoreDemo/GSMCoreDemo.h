// GSMCoreDemo.h : main header file for the GSMCOREDEMO application
//

#if !defined(AFX_GSMCOREDEMO_H__334EDED9_FF10_419C_8FBA_51B8F2876281__INCLUDED_)
#define AFX_GSMCOREDEMO_H__334EDED9_FF10_419C_8FBA_51B8F2876281__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CGSMCoreDemoApp:
// See GSMCoreDemo.cpp for the implementation of this class
//

class CGSMCoreDemoApp : public CWinApp
{
public:
	CGSMCoreDemoApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CGSMCoreDemoApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CGSMCoreDemoApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_GSMCOREDEMO_H__334EDED9_FF10_419C_8FBA_51B8F2876281__INCLUDED_)
