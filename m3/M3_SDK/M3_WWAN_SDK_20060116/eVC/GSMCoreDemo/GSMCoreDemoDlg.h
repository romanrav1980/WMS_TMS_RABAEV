// GSMCoreDemoDlg.h : header file
//

#if !defined(AFX_GSMCOREDEMODLG_H__389F0108_A58B_4270_8F50_832AED657784__INCLUDED_)
#define AFX_GSMCOREDEMODLG_H__389F0108_A58B_4270_8F50_832AED657784__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

/////////////////////////////////////////////////////////////////////////////
// CGSMCoreDemoDlg dialog

class CGSMCoreDemoDlg : public CDialog
{
// Construction
public:
	CGSMCoreDemoDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CGSMCoreDemoDlg)
	enum { IDD = IDD_GSMCOREDEMO_DIALOG };
	CString	m_szRSSI;
	CString	m_szTime;
	CString	m_szIMEI;
	CString	m_szSIMState;
	CString	m_szSIMPIN;
	CString	m_szSIMPUK;
	CString	m_szNewPIN;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CGSMCoreDemoDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CGSMCoreDemoDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnBtnGsmTime();
	afx_msg void OnBtnGetRssi();
	afx_msg void OnBtnImei();
	afx_msg void OnDestroy();
	afx_msg void OnBtnCallSms();
	afx_msg void OnBtnRasPb();
	afx_msg void OnBtnSimState();
	afx_msg void OnBtnEnterSim();
	afx_msg void OnBtnEnterPuk();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_GSMCOREDEMODLG_H__389F0108_A58B_4270_8F50_832AED657784__INCLUDED_)
