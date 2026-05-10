#if !defined(AFX_BSSIDLISTPAGE_H__42375ED5_1F6D_4F51_ADB2_3ABEDF5125E3__INCLUDED_)
#define AFX_BSSIDLISTPAGE_H__42375ED5_1F6D_4F51_ADB2_3ABEDF5125E3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// BssidListPage.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// CBssidListPage dialog

class CBssidListPage : public CPropertyPage
{
	DECLARE_DYNCREATE(CBssidListPage)

// Construction
public:
	CString m_strChannel;
	CBssidListPage();
	~CBssidListPage();

	void GetChannelNam(ULONG ulFrqcy);

// Dialog Data
	//{{AFX_DATA(CBssidListPage)
	enum { IDD = IDD_BSSID_LIST_PAGE };
	CListCtrl	m_ctrListBssid;
	//}}AFX_DATA


// Overrides
	// ClassWizard generate virtual function overrides
	//{{AFX_VIRTUAL(CBssidListPage)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	// Generated message map functions
	//{{AFX_MSG(CBssidListPage)
	afx_msg void OnBtnBssidList();
	afx_msg void OnBtnScan();
	virtual BOOL OnInitDialog();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_BSSIDLISTPAGE_H__42375ED5_1F6D_4F51_ADB2_3ABEDF5125E3__INCLUDED_)
