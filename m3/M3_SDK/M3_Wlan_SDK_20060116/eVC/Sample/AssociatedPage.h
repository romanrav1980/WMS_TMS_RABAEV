#if !defined(AFX_ASSOCIATEDPAGE_H__0BE6108F_AE6C_4870_88AA_05AD93974BD2__INCLUDED_)
#define AFX_ASSOCIATEDPAGE_H__0BE6108F_AE6C_4870_88AA_05AD93974BD2__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// AssociatedPage.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CAssociatedPage dialog


class CAssociatedPage : public CPropertyPage
{
	DECLARE_DYNCREATE(CAssociatedPage)

// Construction
public:
	void GetChannelNam(ULONG ulFrqcy);
	void SetProgBar(int nPos);
	void GetInformation();
	CAssociatedPage();
	~CAssociatedPage();

// Dialog Data
	//{{AFX_DATA(CAssociatedPage)
	enum { IDD = IDD_ASSOCIATED_PAGE };
	CProgressCtrl	m_ProgressBar;
	CString	m_strAtim;
	CString	m_strBeacon;
	CString	m_strBssId;
	CString	m_strChannel;
	CString	m_strLinkSpeed;
	CString	m_strSsid;
	CString	m_strState;
	CString	m_strAdaper;
	//}}AFX_DATA


// Overrides
	// ClassWizard generate virtual function overrides
	//{{AFX_VIRTUAL(CAssociatedPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	// Generated message map functions
	//{{AFX_MSG(CAssociatedPage)
	virtual BOOL OnInitDialog();
	afx_msg void OnTimer(UINT nIDEvent);
	afx_msg void OnClose();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ASSOCIATEDPAGE_H__0BE6108F_AE6C_4870_88AA_05AD93974BD2__INCLUDED_)
