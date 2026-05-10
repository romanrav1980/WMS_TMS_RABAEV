
// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the GSMCORE_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// GSMCORE_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
#ifdef GSMCORE_EXPORTS
#define GSMCORE_API __declspec(dllexport)
#else
#define GSMCORE_API __declspec(dllimport)
#endif

typedef enum _tagPINFlag{
	TYPE_SIM_READY,
	TYPE_SIM_PIN,
	TYPE_SIM_PUK,
	TYPE_SIM_PIN2,
	TYPE_SIM_PUK2,
	TYPE_PH_SIM_PIN,
	TYPE_PH_SIM_PUK,
	TYPE_PH_FSIM_PIN,
	TYPE_PH_FSIM_PUK,
	TYPE_PH_NET_PIN,
	TYPE_PH_NET_PUK,
	TYPE_PH_NS_PIN,
	TYPE_PH_NS_PUK,
	TYPE_PH_SP_PIN,
	TYPE_PH_SP_PUK,
	TYPE_PH_C_PIN,
	TYPE_PH_C_PUK
} PINTYPE;

#define ERROR_NONE				0		// No error occurred 
#define ERROR_NAK				1		// Invalid command 
#define ERROR_GSM_NORESPONSE	2		// No response from GSM Module
#define ERROR_NAK_PARAM			3		// Command is valid but GSM Module can not process that. 
#define ERROR_SLOT_EMPTY		4		// Failed to read the processing result of command
#define ERROR_BUFFER_READ		5		// Failed to read the processing result of command
#define ERROR_REG_READ			6		// Register read fail
#define ERROR_RAS_BUFFER		7		// Insufficient Memory error when creating RAS Entry
#define ERROR_NOTFIND_RASENTRY	8		// Can not found RAS Entry
#define ERROR_DUPLICATE_SIM_PB	9		// Duplicate SIM Phone Book Index
#define ERROR_PHONE_OFF			10		// Phone Power Off
#define ERROR_SIM_PIN_LENGTH	11		// Invalid SIM Pin
#define ERROR_RAS_BASE			600		// RAS Error Refer to MSDN

// Initialize
EXTERN_C GSMCORE_API int	MCInitGSMLibW (LPCTSTR lpWindowName);
// Initialize
EXTERN_C GSMCORE_API int	MCInitGSMLib (HWND hNotiTaker);
// Uninitialize
EXTERN_C GSMCORE_API void	MCUninitGSMLib ();

// Read RSSI from GSM module
EXTERN_C GSMCORE_API int	MCGetRSSI (int* pRssi/*out*/);
// Read DateTime from GSM module
EXTERN_C GSMCORE_API int	MCGetGSMTime (WCHAR* pszDateTime/*out*/);
// Read IMEI from GSM module
EXTERN_C GSMCORE_API int	MCGetIMEI (WCHAR* pszIMEI/*out*/);
// Get error code to error string
EXTERN_C GSMCORE_API void	MCGetErrMsg (int nErrCode/*in*/, WCHAR* pszErrString/*out*/);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PhoneBook Features
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Write a Phone Book Entry to the SIM Card
EXTERN_C GSMCORE_API int	MCWritePhoneBookEntry (int nLocation/*in*/, WCHAR* pszPhoneNumber/*in*/, WCHAR* pszName/*in*/);
// Read a Phone Book Entry to the SIM Card
EXTERN_C GSMCORE_API int	MCReadPhoneBookEntry (int nLocation/*in*/, WCHAR* pszPhoneNumber/*out*/, WCHAR* pszName/*out*/);
// Delete a Phone Book Entry to the SIM Card
EXTERN_C GSMCORE_API int	MCDeletePhoneBookEntry (int nLocation/*in*/);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SIM Card Security
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Check if the SIM Card Requires a PIN
EXTERN_C GSMCORE_API int	MCCheckSIMPin (int* pState/*out*/);
// Enter the PIN for a SIM Card
EXTERN_C GSMCORE_API int	MCEnterSIMPin (WCHAR* pszPinNumber/*in*/);
// Enter the PUK for a SIM Card
EXTERN_C GSMCORE_API int	MCEnterPUKNumber (WCHAR* pszPuk, WCHAR* pszNewPin);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SMS Related Features
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Send SMS
EXTERN_C GSMCORE_API int	MCSendSMS (WCHAR* pszPhoneNum/*in*/, WCHAR* pszSMSData/*in*/);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Telephony Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Hang Up a Telephone Call
EXTERN_C GSMCORE_API int	MCEndCall ();
// Make a Voice Telephone Call
EXTERN_C GSMCORE_API int	MCMakeCall (WCHAR* pszPhoneNum/*in*/);
// Send DTMF Tones During Active Voice Calls
EXTERN_C GSMCORE_API int	MCDTMFSend (WCHAR* pszDTMFString);
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Connectivity Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Create a RAS Entry
EXTERN_C GSMCORE_API int MCCreateRasEntry	(LPCTSTR lpszEntry, int nBaudRate,
											LPCTSTR lpszPhoneNo, LPCTSTR lpszExtraCmds,
											LPCTSTR lpszUserName, LPCTSTR lpszPassword,
											LPCTSTR lpszDomain, LPCTSTR lpszIPAddr,
											LPCTSTR lpszDNS, LPCTSTR lpszDNSAlt,
											LPCTSTR lpszWINS, LPCTSTR lpszWINSAlt );
// Delete a RAS Entry
EXTERN_C GSMCORE_API int MCDeleteRasEntry(LPCTSTR lpszEntry/*in*/ );
// Use RAS To Make a WWAN Connection
EXTERN_C GSMCORE_API int MCDoRASConnect(LPCTSTR ConnectionName/*in*/);
// Terminate a RAS Connection
EXTERN_C GSMCORE_API int MCDoRASHangup();
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// This class is exported from the GSMCore.dll
class GSMCORE_API CGSMCore 
{
public:
	int		Initialize (HWND hNotiTaker/*in*/);
	void	Uninitalize ();
	int		GetRSSI (int* pRssi/*out*/);
	int		GetGSMTime (WCHAR* pszDateTime/*out*/);
	int		GetIMEI (WCHAR* pszIMEI/*out*/);
	int		SendSMS (WCHAR* pszPhoneNum/*in*/, WCHAR* pszSMSData/*in*/);
	int		EndCall ();
	int		MakeCall (WCHAR* pszPhoneNum/*in*/);
	int		CreateRasEntry	(LPCTSTR lpszEntry, int nBaudRate,
								LPCTSTR lpszPhoneNo, LPCTSTR lpszExtraCmds,
								LPCTSTR lpszUserName, LPCTSTR lpszPassword,
								LPCTSTR lpszDomain, LPCTSTR lpszIPAddr,
								LPCTSTR lpszDNS, LPCTSTR lpszDNSAlt,
								LPCTSTR lpszWINS, LPCTSTR lpszWINSAlt );
	int		DeleteRasEntry(LPCTSTR lpszEntry );
	int		DoRASConnect(LPCTSTR ConnectionName);
	int		DoRASHangup();
	int		WritePhoneBookEntry (int nLocation/*in*/, WCHAR* pszPhoneNumber/*in*/, WCHAR* pszName/*in*/);
	int		ReadPhoneBookEntry (int nLocation/*in*/, WCHAR* pszPhoneNumber/*out*/, WCHAR* pszName/*out*/);
	int		DeletePhoneBookEntry (int nLocation/*in*/);
	int		CheckSIMPin (int* pState/*out*/);
	int		EnterSIMPin (WCHAR* pszPinNumber/*in*/);
	int		EnterPUKNumber (WCHAR* pszPuk, WCHAR* pszNewPin);
	int		DTMFSend (WCHAR* pszDTMFString);

public:
	CGSMCore(void);
};

