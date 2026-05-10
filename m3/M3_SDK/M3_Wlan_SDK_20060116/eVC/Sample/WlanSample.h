// WlanSample.h : main header file for the WLANSAMPLE application
//

#if !defined(AFX_WLANSAMPLE_H__9CB2F1BD_1A95_4AF2_AFA0_763C5350CF40__INCLUDED_)
#define AFX_WLANSAMPLE_H__9CB2F1BD_1A95_4AF2_AFA0_763C5350CF40__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CWlanSampleApp:
// See WlanSample.cpp for the implementation of this class
//

class CWlanSampleApp : public CWinApp
{
public:
	CWlanSampleApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CWlanSampleApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CWlanSampleApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_WLANSAMPLE_H__9CB2F1BD_1A95_4AF2_AFA0_763C5350CF40__INCLUDED_)
