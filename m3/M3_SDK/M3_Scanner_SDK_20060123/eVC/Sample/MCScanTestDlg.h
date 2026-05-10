// MCScanTestDlg.h : header file
//

#if !defined(AFX_MCSCANTESTDLG_H__3B9BE872_4EF7_4A29_8D60_85DA6F392887__INCLUDED_)
#define AFX_MCSCANTESTDLG_H__3B9BE872_4EF7_4A29_8D60_85DA6F392887__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

/////////////////////////////////////////////////////////////////////////////
// CMCScanTestDlg dialog

class CMCScanTestDlg : public CDialog
{
// Construction
public:
	CMCScanTestDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CMCScanTestDlg)
	enum { IDD = IDD_MCSCANTEST_DIALOG };
	CListBox	m_ctrListBox;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCScanTestDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CMCScanTestDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnBtnRead();
	afx_msg void OnBtnCancel();
	afx_msg void OnBtnNewDlg();
	//}}AFX_MSG
	afx_msg void OnBarCodeRead(WPARAM,LPARAM);
	afx_msg void OnScanintiStart(WPARAM,LPARAM);
	afx_msg void OnScanintiEnd(WPARAM,LPARAM);
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCSCANTESTDLG_H__3B9BE872_4EF7_4A29_8D60_85DA6F392887__INCLUDED_)
