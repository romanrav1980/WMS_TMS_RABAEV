/*============================================================================
//  KoamTac Scan Module SDK Include File
//
//  (C) Copyright KoamTac, Inc. 2004
//  http://barcode.koamtac.com/
//
//  Title:   KScanBar.h
//  Version: 3.20
//  Date:    February 1, 2005
//----------------------------------------------------------------------------
//  Change log:
//  DATE        REV  DESCRIPTION
//  ----------- ---- ---------------------------------------------------------
//  Feb 16 2004 1.45 Created
//  Mar 30 2004 2.07 Preliminary Release
//  Apr 15 2004 3.20 PDF417 and Code35 added
//============================================================================
*/

#if !defined(__API_KSCANBAR_H__)
#define __API_KSCANBAR_H__

#ifdef __cplusplus
extern "C" {
#endif
//#pragma comment(lib, "KScanBar.lib")

#if !defined( PASCAL )
#define PASCAL  __pascal
#endif
#if !defined( WINAPI )
#define WINAPI	PASCAL
#endif
#if !defined( KSCANAPI )
#define KSCANAPI	WINAPI
#endif
#define KSCAN_API __declspec(dllimport)

typedef int (KSCANAPI * KS_FN_CALLBACK)(LPVOID);

typedef struct tagKSCANREAD {
	int             nSize;
	unsigned        nTimeInSeconds;
	unsigned long   dwFlags;
	unsigned long   dwReadType;
	int             nMinLength;
	int             nSecurity;
	KS_FN_CALLBACK  fnCallBack;
	LPVOID          pUserData;
	LPVOID          pReadEx;
	int             out_Status;
	int             out_Type;
	char            out_Barcode[2711];
} KSCANREAD;
typedef KSCANREAD *	PKSCANREAD;


#define KSCAN_READ_TYPE_EAN_13        0x00000001L
#define KSCAN_READ_TYPE_EAN_8         0x00000002L
#define KSCAN_READ_TYPE_UPCA          0x00000004L
#define KSCAN_READ_TYPE_UPCE          0x00000008L
#define KSCAN_READ_TYPE_CODE_39       0x00000010L
#define KSCAN_READ_TYPE_ITF_14        0x00000020L	// In Decoder 6.00 or later
#define KSCAN_READ_TYPE_CODE_128      0x00000040L
#define KSCAN_READ_TYPE_CODE_I25      0x00000080L
#define KSCAN_READ_TYPE_CODA_BAR      0x00000100L
#define KSCAN_READ_TYPE_UCCEAN_128    0x00000200L
#define KSCAN_READ_TYPE_CODE_93       0x00000400L
#define KSCAN_READ_TYPE_CODE_35       0x00000800L

#define KSCAN_READ_TYPE_BOOKLAND      0x00001000L	// New in Decoder 6.10
#define KSCAN_READ_TYPE_EAN_13_ADDON  0x00002000L	// New in Decoder 6.10
#define KSCAN_READ_TYPE_EAN_8_ADDON   0x00004000L	// New in Decoder 6.10
#define KSCAN_READ_TYPE_UPCA_ADDON    0x00008000L	// New in Decoder 6.10
#define KSCAN_READ_TYPE_UPCE_ADDON    0x00010000L	// New in Decoder 6.10

#define KSCAN_READ_TYPE_PDF417        0x80000000L
#define KSCAN_READ_TYPE_ALL           0xFFFFFFFFL


#define KSCAN_RET_TYPE_EAN_13				0
#define KSCAN_RET_TYPE_EAN_8				1
#define KSCAN_RET_TYPE_UPCA					2
#define KSCAN_RET_TYPE_UPCE					3
#define KSCAN_RET_TYPE_CODE_39				4
#define KSCAN_RET_TYPE_ITF_14				5	// In Decoder 6.00 or later
#define KSCAN_RET_TYPE_CODE_128				6
#define KSCAN_RET_TYPE_CODE_I25				7
#define KSCAN_RET_TYPE_CODA_BAR				8
#define KSCAN_RET_TYPE_UCCEAN_128			9
#define KSCAN_RET_TYPE_CODE_93				10
#define KSCAN_RET_TYPE_CODE_35				11
#define KSCAN_RET_TYPE_PDF417				12
#define KSCAN_RET_TYPE_MACRO_PDF417			13 // All segments have been read OR unbuffered mode
#define KSCAN_RET_TYPE_BOOKLAND				14 // New in Decoder 6.10
#define KSCAN_RET_TYPE_MACRO_PDF417_INC		18 // Not all segments have been read.
#define KSCAN_RET_TYPE_MACRO_PDF417_ERROR	19 // Error in the control block; data block OK
#define KSCAN_RET_TYPE_UNKNOWN				0xFF

//
// Flags - Scanner parameters & UPC/EAN options
//
#define KSCAN_FLAG_REVERSEDIRECTION     0x00000010
#define KSCAN_FLAG_RETURNCHECK          0x00001000 // More fine-grained control is available in Decoder 6.04 (see below)
#define KSCAN_FLAG_ERRORCHECK           0x00002000 // More fine-grained control is available in Decoder 6.04 (see below)
#define KSCAN_FLAG_WIDESCANANGLE        0x00004000
#define KSCAN_FLAG_HIGHFILTERMODE       0x00008000
//
// Only available in Decoder 6.00 or later
//
#define KSCAN_FLAG_UPCE_AS_UPCA         0x00000200 
#define KSCAN_FLAG_EAN8_AS_EAN13        0x00000400
#define KSCAN_FLAG_UPCE_AS_EAN13        0x00000800
#define KSCAN_FLAG_UPCA_AS_EAN13		0x00080000
//
// Only available in Decoder 6.04 or later
//
#define KSCAN_FLAG_VERIFYCHECK          0x00002000 // A name change only - same value as KSCAN_FLAG_ERRORCHECK
#define KSCAN_FLAG_I2OF5_VERIFYCHECK    0x00400000
#define KSCAN_FLAG_CODE39_VERIFYCHECK   0x00800000

#define KSCAN_FLAG_CODABAR_NOSTARTSTOP  0x00000001

#define KSCAN_FLAG_I2OF5_RETURNCHECK	0x04000000
#define KSCAN_FLAG_CODE39_RETURNCHECK   0x08000000
#define KSCAN_FLAG_UPCE_RETURNCHECK     0x10000000
#define KSCAN_FLAG_UPCA_RETURNCHECK     0x20000000
#define KSCAN_FLAG_EAN8_RETURNCHECK     0x40000000
#define KSCAN_FLAG_EAN13_RETURNCHECK    0x80000000
/*
// Following flags are no longer used.
#define KSCAN_FLAG_PARTIALSOK           0x00000002	// No longer used.
#define KSCAN_FLAG_NOQUIETZONE          0x00000100	// No longer used.
#define KSCAN_FLAG_QUIET_START			0x00020000	// No longer used.
#define KSCAN_FLAG_QUIET_END			0x00040000	// No longer used.
*/

//
// PDF417 related constants that must be exposed top the application
//
const short KSCAN_CONST_PDF417_MIN_TILT = 2;
const short KSCAN_CONST_PDF417_MAX_TILT = 6;
const short KSCAN_CONST_PDF417_MAX_QUALITY = 4;
const short KSCAN_FLAG_START_SYMB_REQ = 1;
const short KSCAN_FLAG_STOP_SYMB_REQ  = 2;
const short KSCAN_FLAG_START_AND_STOP_SYMB_REQ = 3;
const short KSCAN_FLAG_START_OR_STOP_SYMB_REQ  = 4;
//
// Return values from Read
//
// Both blocking & non-blocking
#define KSCAN_RET_NORMAL                        0 // Barcode found
#define KSCAN_RET_USER_CANCEL                   2 // User initiated cancel of read operation
#define KSCAN_RET_TIMEOUT                       3 // Time-out: barcode not found
// Only for non-blocking
#define KSCAN_RET_BAR_NOTFOUND                  4 // Barcode not found till now
#define KSCAN_RET_NORMAL_SWEEP                  5 // Barcode found, but the security criteria has not been met
//
// Error codes (values are usually >= 10)
// DO NOT EXPLICITLY USE THESE CONSTANTS IN THE CODE AS THEY ARE LIKELY TO CHANGE.
// Call GetLastErrorMsg() to obtain the error messages.
//
#define KSCAN_RET_ERR_READ_ALREADYINPROGRESS   14
#define	KSCAN_RET_ERR_NOTHINGTOCANCEL          15
#define KSCAN_RET_ERR_READCANCEL_INPROGRESS    16

#define KSCAN_RET_ERR_COMM_NOTOPENED           20
#define KSCAN_RET_ERR_COMM_ALREADY_OPEN        21
#define KSCAN_RET_ERR_COMM_PORT_OUTOFRANGE     22
#define KSCAN_RET_ERR_COMM_PURGEFAILED         24
#define KSCAN_RET_ERR_COMM_CLOSEHANDLEFAILED   25
#define KSCAN_RET_ERR_COMM_SETCOMMSTATEFAILED  26
#define KSCAN_RET_ERR_COMM_READWRITEFAILED     27

#define KSCAN_RET_ERR_HW_NOTFOUND              30
#define KSCAN_RET_ERR_HW_RESPONSETIMEOUT       31
#define KSCAN_RET_ERR_HW_INVALIDRESP           32
#define KSCAN_RET_ERR_HW_CMDEXECUTIONFAILED    33
#define KSCAN_RET_ERR_THREAD_CREATIONFAILED    35
#define KSCAN_RET_ERR_EVENT_CREATION_FAILED    36
#define KSCAN_RET_ERR_READ_NOTTERMINATED       37

#define KSCAN_RET_ERR_SERIALNUMBER_READ_FAILED 40
#define KSCAN_RET_ERR_FWVERSION_READ_FAILED    41
#define KSCAN_RET_ERR_FWBUILD_READ_FAILED      42
#define KSCAN_RET_ERR_ALLVERSION_READ_FAILED   43
#define KSCAN_RET_ERR_SYMBOLOGY_READ_FAILED    44
#define KSCAN_RET_ERR_FW_TOO_OLD               45
#define KSCAN_RET_ERR_SCANNERTYPE_READ_FAILED  46

#define KSCAN_RET_ERR_PDF417_INSUFFICIENT_DATA 50

/*
// Following return values are no longer used.
#define KSCAN_RET_CHECKERROR                    1 // No longer used
#define KSCAN_RET_CHECKERROR_SWEEP              6 // No longer used
#define KSCAN_RET_ERR_UNKNOWN                  10 // No longer used
#define KSCAN_RET_ERR_DECODING                 11 // No longer used
#define KSCAN_RET_ERR_NOTSUPPORTED             12 // No longer used
#define KSCAN_RET_ERR_INVALID_FLAGS            13 // No longer used
#define KSCAN_RET_ERR_SWEEP_DATA               17 // No longer used
#define KSCAN_RET_ERR_COMM_CHKSUM              23 // No longer used
#define KSCAN_RET_ERR_HW_NOTSUPPORTED          34 // No longer used
*/

#ifdef __cplusplus
}
#endif


#define _C_INTERFACE

#ifdef __cplusplus

class KSCAN_API CKScan {
public:
	CKScan(void);
	~CKScan(void);
	BOOL Open(int CommNumber, BOOL CommDetect, DWORD BaudRate, BOOL BaudDetect, DWORD ExFlags);
	BOOL Close();
	BOOL Read(PKSCANREAD pRead);
	BOOL ReadForever(PKSCANREAD pRead);
	BOOL ReadCancel();
	BOOL Sleep();
	BOOL Wakeup();
	BOOL Reset();
	int GetCommNumber();
	LPCTSTR GetCommName();
	HANDLE GetCommHandle();
	LPCTSTR GetLastErrorMsg();
	LPCTSTR GetVersionInfo();
	DWORD GetSymbologyInfo();
};
#endif	// __cplusplus

#if defined(_C_INTERFACE)

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

KSCAN_API BOOL KSCANAPI KScanOpen(int CommNumber, BOOL CommDetect, DWORD BaudRate, BOOL BaudDetect, DWORD ExFlags);
KSCAN_API BOOL KSCANAPI KScanClose();
KSCAN_API BOOL KSCANAPI KScanRead(PKSCANREAD pRead);
KSCAN_API BOOL KSCANAPI KScanReadCancel();
KSCAN_API BOOL KSCANAPI KScanSleep();
KSCAN_API BOOL KSCANAPI KScanWakeup();
KSCAN_API BOOL KSCANAPI KScanReset();
KSCAN_API int KSCANAPI KScanGetCommNumber();
KSCAN_API LPCTSTR KSCANAPI KScanGetCommName();
KSCAN_API LPCTSTR KSCANAPI KScanGetLastErrorMsg();
KSCAN_API LPCTSTR KSCANAPI KScanGetVersionInfo();

KSCAN_API DWORD KSCANAPI KScanGetSymbologyInfo();
//
// PDF417 Parameters
//
KSCAN_API void  KSCANAPI GetPDF417Text(char str[]);
KSCAN_API short KSCANAPI GetPDF417Quality(void);
KSCAN_API void  KSCANAPI SetPDF417Quality(short Quality);
KSCAN_API short KSCANAPI GetPDF417Tilt(void);
KSCAN_API void  KSCANAPI SetPDF417Tilt(short nRows);
KSCAN_API short KSCANAPI GetPDF417StartStop(void);
KSCAN_API void  KSCANAPI SetPDF417StartStop(short flag);

#ifdef __cplusplus
}
#endif // __cplusplus

#endif // defined(_C_INTERFACE)


#endif // !defined(__API_KSCANBAR_H__)
// End of file "KScanBar.h"
