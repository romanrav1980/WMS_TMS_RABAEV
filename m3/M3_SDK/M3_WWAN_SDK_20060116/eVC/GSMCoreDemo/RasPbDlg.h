#if !defined(AFX_RASPBDLG_H__24C2A789_D6CF_452A_A480_5D8A5ACB5198__INCLUDED_)
#define AFX_RASPBDLG_H__24C2A789_D6CF_452A_A480_5D8A5ACB5198__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// RasPbDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CRasPbDlg dialog

class CRasPbDlg : public CDialog
{
// Construction
public:
	CRasPbDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CRasPbDlg)
	enum { IDD = IDD_DLG_RAS_PB };
	CString	m_szIndex;
	CString	m_szName;
	CString	m_szPhoneNum;
	CString	m_szResult;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CRasPbDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CRasPbDlg)
	afx_msg void OnBtnCreateRasEntry();
	afx_msg void OnBtnRasConnect();
	afx_msg void OnBtnRasHangUp();
	afx_msg void OnBtnPBWrite();
	afx_msg void OnBtnPBRead();
	afx_msg void OnBtnPBDel();
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_RASPBDLG_H__24C2A789_D6CF_452A_A480_5D8A5ACB5198__INCLUDED_)
