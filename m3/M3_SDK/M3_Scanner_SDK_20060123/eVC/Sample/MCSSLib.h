
// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the MCSSLIB_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// MCSSLIB_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
//#include "KScanBar.h"	// Added by ClassView
#ifdef MCSSLIB_EXPORTS
#define MCSSLIB_API __declspec(dllexport)
#else
#define MCSSLIB_API __declspec(dllimport)
#endif


//ERROR CORD
#define ERROR_NONE			 0
#define POWER_ON_ERROR      -1
#define POWER_OFF_ERROR     -2
#define PORT_OPEN_ERROR     -3
#define PORT_CLOSE_ERROR    -4
#define READ_ERROR          -5
#define READ_CANCEL_ERROR   -6

#define WM_SCAN_DATA		WM_USER+100
#define WM_SCANINIT_START	WM_USER+101
#define WM_SCANINIT_END     WM_USER+102


typedef struct _MCBarCodeType
{	
	BYTE bMC_EAN_13;	
	BYTE bMC_CODA_BAR;	
	BYTE bMC_CODE_128;	
	BYTE bMC_CODE_39;	
	BYTE bMC_CODE_35;	
	BYTE bMC_CODE_93;	
	BYTE bMC_CODE_I25;	
	BYTE bMC_EAN_8;	
	BYTE bMC_PDF417;	
	BYTE bMC_UCCEAN_128;	
	BYTE bMC_UPCA;	
	BYTE bMC_UPCE;	
	BYTE bMC_UPCE_ADDON;	
	BYTE bMC_UPCA_ADDON;	
	BYTE bMC_BOOKLAND;		
	BYTE bMC_EAN_13_ADDON;	
	BYTE bMC_EAN_8_ADDON;	
	// 2006-01-16 AKAI  17개
/*	BOOL bMC_EAN_13;	
	BOOL bMC_CODA_BAR;	
	BOOL bMC_CODE_128;	
	BOOL bMC_CODE_39;	
	BOOL bMC_CODE_35;	
	BOOL bMC_CODE_93;	
	BOOL bMC_CODE_I25;	
	BOOL bMC_EAN_8;	
	BOOL bMC_PDF417;	
	BOOL bMC_UCCEAN_128;	
	BOOL bMC_UPCA;	
	BOOL bMC_UPCE;	
	BOOL bMC_UPCE_ADDON;	
	BOOL bMC_UPCA_ADDON;	
	BOOL bMC_BOOKLAND;		
	BOOL bMC_EAN_13_ADDON;	
	BOOL bMC_EAN_8_ADDON;	*/

}MCBarCodeType,* PMCBarCodeType;

typedef struct _MCReadOption
{
	BYTE bMC_WIDESCANANGLE;
	BYTE bMC_RETURNCHECK;
	BYTE bMC_ERRORCHECK;
	BYTE bMC_HIGHFILTERMODE;

}MCReadOption,* PMCReadOption;

typedef struct _MCModuleOption
{
	int nMC_TimeOutSec;
	int nMC_MinLen;
	int nMC_SecurityLevel;

}MCModuleOption,* PMCModuleOption;

typedef struct _MCPDF417Option
{
	int nMC_Quality;
	int nMC_Tilt;
	int nMC_SnSSymbol; //start and stop symbols
	
/*const short KSCAN_CONST_PDF417_MIN_TILT = 2;
const short KSCAN_CONST_PDF417_MAX_TILT = 6;
const short KSCAN_CONST_PDF417_MAX_QUALITY = 4;
const short KSCAN_FLAG_START_SYMB_REQ = 1;
const short KSCAN_FLAG_STOP_SYMB_REQ  = 2;
const short KSCAN_FLAG_START_AND_STOP_SYMB_REQ = 3;
const short KSCAN_FLAG_START_OR_STOP_SYMB_REQ  = 4;*/
}MCPDF417Option,* PMCPDF417Option;

// This class is exported from the MCSSLib.dll
class MCSSLIB_API CMCSSLib {
	
public:
	void UseResumeWindow(BOOL bRwin);
	void UseDefaultSound(BOOL bWSound);
	void RegisterWindow(HWND hWnd);
	void SetDefaultOption();
	void GetScanDataWchar(TCHAR *szBarData,TCHAR *szBarType);
	void GetScanDataByte(BYTE * sBarData, BYTE * sBarType);
	void GetScanDataChar(char *szBarData, char *szBarType);
	void SetBarCodeTypeToString(int nType);
	void SetPDF417Option(PMCPDF417Option pPDF);
	void SetModuleOption(PMCModuleOption pMDO);
	void SetReadOption(PMCReadOption pRDO);
	void SetBarCodeType(PMCBarCodeType pBCT);
	int ReadCancel();
	int Read();
//	void SetReadStruct(KSCANREAD &kRead);
	int CloseScanner();
	int ResumeProcess();
	void GetBarCodeType(PMCBarCodeType pBCT);
	void GetReadOption(PMCReadOption pRDO);
	void GetModuleOption(PMCModuleOption pMDO);
	void GetPDF417Option(PMCPDF417Option pPDF);
	char        m_BarData[2711];
	char        m_BarType[32];
	int         m_nBarType;

//	CKScan KScan;
	MCBarCodeType stBarType;
	MCReadOption  stRdOption;
	MCModuleOption stMdOption;
	MCPDF417Option stPDFOption;
	CMCSSLib(void);
	// TODO: add your methods here.
	int InitScanner();
};

extern MCSSLIB_API int nMCSSLib;

MCSSLIB_API int fnMCSSLib(void);
EXTERN_C MCSSLIB_API int MCScanInit();
EXTERN_C MCSSLIB_API int MCScanClose();
EXTERN_C MCSSLIB_API int MCScanRead();
EXTERN_C MCSSLIB_API int MCScanReadCancel();
EXTERN_C MCSSLIB_API void MCRegisterWindow(HWND hWnd);
EXTERN_C MCSSLIB_API void MCGetScanDataByte(BYTE* sBarData, BYTE* sBarType);
EXTERN_C MCSSLIB_API void MCGetScanDataWchar(TCHAR* sBarData, TCHAR* sBarType);
EXTERN_C MCSSLIB_API void MCGetScanDataChar(char *szBarData, char *szBarType);
// 2006-01-16 AKAI  옵션에 대한 구조체를 Set!!
EXTERN_C MCSSLIB_API void MCSetBarCodeType(PMCBarCodeType pBCT);
EXTERN_C MCSSLIB_API void MCSetReadOption(PMCReadOption pRDO);
EXTERN_C MCSSLIB_API void MCSetModuleOption(PMCModuleOption pMDO);
EXTERN_C MCSSLIB_API void MCSetPDF417Option(PMCPDF417Option pPDF);
// 2006-01-16 AKAI  옵션에 대한 구조체를 Get!!
EXTERN_C MCSSLIB_API void MCGetBarCodeType(PMCBarCodeType pBCT);
EXTERN_C MCSSLIB_API void MCGetReadOption(PMCReadOption pRDO);
EXTERN_C MCSSLIB_API void MCGetModuleOption(PMCModuleOption pMDO);
EXTERN_C MCSSLIB_API void MCGetPDF417Option(PMCPDF417Option pPDF);
EXTERN_C MCSSLIB_API void MCUseDefaultSound(BOOL bWSound);
EXTERN_C MCSSLIB_API void MCUseResumeWindow(BOOL bWSound);
