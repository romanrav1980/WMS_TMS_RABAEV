// BT SerialDlg.h : header file
//

#if !defined(AFX_BTSERIALDLG_H__905C0570_8B24_4267_BFEE_F48C79769224__INCLUDED_)
#define AFX_BTSERIALDLG_H__905C0570_8B24_4267_BFEE_F48C79769224__INCLUDED_
#include "Vector.h"	// Added by ClassView
#include "albtcore.h"
#include "GenStackInterface.h"	// Added by ClassView

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000


#define SERVER_CONNECTED 1
#define SERVER_WAITING   0

/////////////////////////////////////////////////////////////////////////////
// CBTSerialDlg dialog
typedef struct _DUN_SERVICE_HEAD
{
	BT_DEVICE  btDevice;
	BT_SERVICE btService;
}DUN_SERVICE_HEAD,*PDUN_SERVICE_HEAD;

class CBTSerialDlg : public CDialog
{
// Construction
public:
	GenStackInterface genStackInterface;
	Vector *mpVector;
	CImageList ImageList;
	CBTSerialDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CBTSerialDlg)
	enum { IDD = IDD_BTSERIAL_DIALOG };
	CListCtrl	m_devlistBt;
	CButton	m_ServerMode;
	CButton	m_rfconnectBt;
	CButton	m_sdpBt;
	CButton	m_devBt;
	CButton	m_initBt;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CBTSerialDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CBTSerialDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnBluetoothON();
	afx_msg void OnServiceSearch();
	afx_msg void OnBTDeviceSearch();
	afx_msg void OnSppConnect();
	afx_msg void OnClickList1(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnSppServer();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
public:
	void OnOK();
	
	static CBTSerialDlg* pBTSInstance;
};

VOID appSppEventCallback(HANDLE sppHandle,UINT32 event);
VOID StartSppServer();


//{{AFX_INSERT_LOCATION}}
// Microsoft eMbedded Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_BTSERIALDLG_H__905C0570_8B24_4267_BFEE_F48C79769224__INCLUDED_)
