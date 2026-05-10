// CamCoreDemoDlg.h : header file
//

#if !defined(AFX_CAMCOREDEMODLG_H__26826DAF_5EC4_48FB_9E41_05268BA64173__INCLUDED_)
#define AFX_CAMCOREDEMODLG_H__26826DAF_5EC4_48FB_9E41_05268BA64173__INCLUDED_

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

/////////////////////////////////////////////////////////////////////////////
// CCamCoreDemoDlg dialog

class CCamCoreDemoDlg : public CDialog
{
protected:
	void ErrorMsgBox (int nError);
	void InitControl();

// Construction
public:
	CCamCoreDemoDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CCamCoreDemoDlg)
	enum { IDD = IDD_CAMCOREDEMO_DIALOG };
	CComboBox	m_comboSize;
	CComboBox	m_comboCompress;
	CButton	m_btnPreviewStop;
	CButton	m_btnPreviewStart;
	CButton	m_btnCapture;
	CStatic	m_ctlPreview;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CCamCoreDemoDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CCamCoreDemoDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnBtnPreviewStart();
	afx_msg void OnBtnPreviewStop();
	afx_msg void OnBtnCapture();
	afx_msg void OnDestroy();
	//}}AFX_MSG
	afx_msg void OnCameraError (WPARAM wParam, LPARAM lParam);
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CAMCOREDEMODLG_H__26826DAF_5EC4_48FB_9E41_05268BA64173__INCLUDED_)
