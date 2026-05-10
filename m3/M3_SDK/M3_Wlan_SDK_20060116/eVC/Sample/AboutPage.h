#if !defined(AFX_ABOUTPAGE_H__BDDEA532_3D52_4850_8AB8_CFB3AB23149F__INCLUDED_)
#define AFX_ABOUTPAGE_H__BDDEA532_3D52_4850_8AB8_CFB3AB23149F__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// AboutPage.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CAboutPage dialog

class CAboutPage : public CPropertyPage
{
	DECLARE_DYNCREATE(CAboutPage)

// Construction
public:
	CAboutPage();
	~CAboutPage();

// Dialog Data
	//{{AFX_DATA(CAboutPage)
	enum { IDD = IDD_ABOUT_PAGE };
	CString	m_strMAc;
	//}}AFX_DATA


// Overrides
	// ClassWizard generate virtual function overrides
	//{{AFX_VIRTUAL(CAboutPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	// Generated message map functions
	//{{AFX_MSG(CAboutPage)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ABOUTPAGE_H__BDDEA532_3D52_4850_8AB8_CFB3AB23149F__INCLUDED_)
