// BT Serial.h : main header file for the BT SERIAL application
//

#if !defined(AFX_BTSERIAL_H__ED63C409_C857_4ECE_96EB_35564980F967__INCLUDED_)
#define AFX_BTSERIAL_H__ED63C409_C857_4ECE_96EB_35564980F967__INCLUDED_


#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CBTSerialApp:
// See BT Serial.cpp for the implementation of this class
//

class CBTSerialApp : public CWinApp
{
public:
	CBTSerialApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CBTSerialApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CBTSerialApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_BTSERIAL_H__ED63C409_C857_4ECE_96EB_35564980F967__INCLUDED_)
