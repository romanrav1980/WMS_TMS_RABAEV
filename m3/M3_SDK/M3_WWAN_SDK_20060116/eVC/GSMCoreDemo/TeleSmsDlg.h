#if !defined(AFX_TELESMSDLG_H__5DFFFF7B_654E_4F5B_812F_CA8406C3421C__INCLUDED_)
#define AFX_TELESMSDLG_H__5DFFFF7B_654E_4F5B_812F_CA8406C3421C__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// TeleSmsDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CTeleSmsDlg dialog

class CTeleSmsDlg : public CDialog
{
// Construction
public:
	CTeleSmsDlg(CWnd* pParent = NULL);   // standard constructor

// Dialog Data
	//{{AFX_DATA(CTeleSmsDlg)
	enum { IDD = IDD_DLG_CALL_SMS };
	CString	m_szCallPhoneNum;
	CString	m_szDTMFString;
	CString	m_szSMSData;
	CString	m_szSMSPhoneNum;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CTeleSmsDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CTeleSmsDlg)
	afx_msg void OnMakeCall();
	afx_msg void OnEndCall();
	afx_msg void OnDtmfSend();
	afx_msg void OnSmsSend();
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_TELESMSDLG_H__5DFFFF7B_654E_4F5B_812F_CA8406C3421C__INCLUDED_)
