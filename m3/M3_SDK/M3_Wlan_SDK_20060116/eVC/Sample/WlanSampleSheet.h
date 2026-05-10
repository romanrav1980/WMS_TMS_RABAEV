#if !defined(AFX_WLANSAMPLESHEET_H__C5DC6F16_39B4_4D77_9F27_0A9419944644__INCLUDED_)
#define AFX_WLANSAMPLESHEET_H__C5DC6F16_39B4_4D77_9F27_0A9419944644__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// WlanSampleSheet.h : header file
//

#include "AboutPage.h"
#include "AssociatedPage.h"
#include "BssidListPage.h"

#include "..\\Include\\WlanUtil.h"

/////////////////////////////////////////////////////////////////////////////
// CWlanSampleSheet

class CWlanSampleSheet : public CPropertySheet
{
	DECLARE_DYNAMIC(CWlanSampleSheet)

// Construction
public:
	CWlanSampleSheet(UINT nIDCaption, CWnd* pParentWnd = NULL, UINT iSelectPage = 0);
	CWlanSampleSheet(LPCTSTR pszCaption, CWnd* pParentWnd = NULL, UINT iSelectPage = 0);

// Attributes
public:
	CAboutPage		m_AboutPage;
	CAssociatedPage m_AssociatedPage;
	CBssidListPage  m_BssidListPage;
	

// Operations
public:

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CWlanSampleSheet)
	public:
	virtual BOOL OnInitDialog();
	//}}AFX_VIRTUAL





	//}}AFX_VIRTUAL
// Implementation
public:
	virtual ~CWlanSampleSheet();

	// Generated message map functions
protected:
	//{{AFX_MSG(CWlanSampleSheet)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_WLANSAMPLESHEET_H__C5DC6F16_39B4_4D77_9F27_0A9419944644__INCLUDED_)
