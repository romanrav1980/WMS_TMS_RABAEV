#if !defined(AFX_NEWDLG_H__C1900A42_A506_42ED_A687_54CCEF29C843__INCLUDED_)
#define AFX_NEWDLG_H__C1900A42_A506_42ED_A687_54CCEF29C843__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// NewDlg.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CNewDlg dialog

class CNewDlg : public CDialog
{
// Construction
public:
	CNewDlg(CWnd* pParent = NULL);   // standard constructor

	
	// Dialog Data
	//{{AFX_DATA(CNewDlg)
	enum { IDD = IDD_DLG_TEST };
	CListCtrl	m_ctrBarList;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CNewDlg)
	public:
	virtual BOOL PreTranslateMessage(MSG* pMsg);
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(CNewDlg)
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_NEWDLG_H__C1900A42_A506_42ED_A687_54CCEF29C843__INCLUDED_)
