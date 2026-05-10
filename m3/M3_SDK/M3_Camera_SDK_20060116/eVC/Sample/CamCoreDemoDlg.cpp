// CamCoreDemoDlg.cpp : implementation file
//

#include "stdafx.h"
#include "CamCoreDemo.h"
#include "CamCoreDemoDlg.h"
#include "CamCore.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CCamCoreDemoDlg dialog

CCamCoreDemoDlg::CCamCoreDemoDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CCamCoreDemoDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CCamCoreDemoDlg)
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CCamCoreDemoDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CCamCoreDemoDlg)
	DDX_Control(pDX, IDC_COMBO_SIZE, m_comboSize);
	DDX_Control(pDX, IDC_COMBO_COMPRESS, m_comboCompress);
	DDX_Control(pDX, IDC_BTN_PREVIEW_STOP, m_btnPreviewStop);
	DDX_Control(pDX, IDC_BTN_PREVIEW_START, m_btnPreviewStart);
	DDX_Control(pDX, IDC_BTN_CAPTURE, m_btnCapture);
	DDX_Control(pDX, IDC_STATIC_PREVIEW, m_ctlPreview);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CCamCoreDemoDlg, CDialog)
	//{{AFX_MSG_MAP(CCamCoreDemoDlg)
	ON_BN_CLICKED(IDC_BTN_PREVIEW_START, OnBtnPreviewStart)
	ON_BN_CLICKED(IDC_BTN_PREVIEW_STOP, OnBtnPreviewStop)
	ON_BN_CLICKED(IDC_BTN_CAPTURE, OnBtnCapture)
	ON_WM_DESTROY()
	//}}AFX_MSG_MAP
	ON_MESSAGE (WM_CAM_STATE, OnCameraError)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CCamCoreDemoDlg message handlers

BOOL CCamCoreDemoDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	CenterWindow(GetDesktopWindow());	// center to the hpc screen

	InitControl ();
	
	return TRUE;  // return TRUE  unless you set the focus to a control
}

// 미리보기 상태에서 카메라 동작에 관한 상태나 에러를 처리한다
// Message	: WM_CAM_STATE
// wParam	: 상태나 에러코드
void CCamCoreDemoDlg::OnCameraError (WPARAM wParam, LPARAM lParam)
{
	int nRet = (int)wParam;

	switch (nRet) 
	{
	case ERROR_OPEN_USB_EVENT:
		AfxMessageBox (L"Can not open USB Event");
		break;
	case ERROR_USB_PATH_GET:
		AfxMessageBox (L"Can not connect USB Path");
		break;
	case ERROR_USB_PATH_CHANGED_CREADLE:
		m_ctlPreview.SetWindowText(L"Camera can not be used while on the cradle.");

		m_btnPreviewStart.EnableWindow(TRUE);
		m_btnPreviewStop.EnableWindow(FALSE);
		m_btnCapture.EnableWindow(FALSE);
		break;
	default:
		break;
	}
}

void CCamCoreDemoDlg::OnBtnPreviewStart() 
{
	int nRet = ERROR_NONE;

	m_ctlPreview.SetWindowText(L"Preview Image");
	m_btnPreviewStart.EnableWindow(FALSE);
	m_btnPreviewStop.EnableWindow(TRUE);

	// 카메라에 전원을 인가한다.
	nRet = MCCamPowerON (this->m_hWnd);
	if (nRet != ERROR_NONE)
	{
		m_btnPreviewStart.EnableWindow(TRUE);
		m_btnPreviewStop.EnableWindow(FALSE);

		ErrorMsgBox(nRet);

		return;
	}

	// 미리보기를 시작한다.
	nRet = MCCamPreviewStart (m_ctlPreview.m_hWnd);
	if (nRet != ERROR_NONE)
	{
		ErrorMsgBox(nRet);
		return;
	}

	m_btnCapture.EnableWindow(TRUE);
}

void CCamCoreDemoDlg::OnBtnPreviewStop() 
{
	int nRet = ERROR_NONE;

	// 미리보기를 멈춘다.
	nRet = MCCamPreviewStop ();
	if (nRet != ERROR_NONE)
	{
		ErrorMsgBox(nRet);
	}

	// 카메라 전원을 내린다.
	nRet = MCCamPowerOFF ();
	if (nRet != ERROR_NONE)
	{
		ErrorMsgBox(nRet);
	}	
	
	m_btnPreviewStart.EnableWindow(TRUE);
	m_btnPreviewStop.EnableWindow(FALSE);

	m_btnCapture.EnableWindow(FALSE);
}

void CCamCoreDemoDlg::OnBtnCapture() 
{
	TCHAR	szFileName[]	= L".\\Capture.jpg";				// Capture image를 저장할 경로를 포함한 파일명
	int		nCompressLevel	= m_comboCompress.GetCurSel();	// Image 압축 레벨 (1 ~7)
	int		nCaptureSize	= m_comboSize.GetCurSel();		// Image 해상동 (160X120, 320X240, 640X480)
	int		nRet			= ERROR_NONE;					// 리턴 코드

	// 현재 미리보기 화면을 Capture한다.
	nRet = MCCamCapture (nCompressLevel, nCaptureSize, szFileName);
	if (nRet != ERROR_NONE)
	{
		ErrorMsgBox(nRet);
	}
}

void CCamCoreDemoDlg::OnDestroy() 
{
	CDialog::OnDestroy();
	
	int	nRet = ERROR_NONE;

	// 현재 카메라 상태가 Power off가 아니면 Power Off후 종료한다
	if (MCCamGetState() != CAM_API_STATE_POWER_OFF)
	{
		// Camera Power off 한다
		// 만일 프리뷰모드이면 자동으로 프리뷰를 멈춘후 Power Off 작동을 수행한다.
		nRet = MCCamPowerOFF ();
		if (nRet != ERROR_NONE)
		{
			ErrorMsgBox(nRet);
		}	
	}
}

void CCamCoreDemoDlg::InitControl()
{
	ShowWindow(SW_SHOWMAXIMIZED);

	m_comboCompress.SetCurSel(CAM_API_COMPRESS_LEVEL_06);
	m_comboSize.SetCurSel(CAM_API_CAPTURE_160_120);
}

void CCamCoreDemoDlg::ErrorMsgBox(int nError)
{
	TCHAR szErrorString[256] = {NULL,};

	// 에러코드에 대한 에러내용을 얻어온다.
	MCCamGetError(nError, szErrorString);

	AfxMessageBox(szErrorString);
}


