
// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the WLANUTIL_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// WLANUTIL_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
#ifndef WLANUTIL_EXPORTS_DEF
#define WLANUTIL_EXPORTS_DEF

#ifdef WLANUTIL_EXPORTS
#define WLANUTIL_API __declspec(dllexport)
#else
#define WLANUTIL_API __declspec(dllimport)
#endif

typedef struct _MC_WLAN_BSSID_LIST
{	
    UCHAR                     MacAddress[6];         // BSSID
    TCHAR                     Ssid[32];               // SSID
    int                       Privacy;            // WEP encryption requirement
    int                       Rssi;               // receive signal strength in dBm
    int                       BeaconPeriod;
    int                       ATIMWindow;
    int			    		  DSConfig;
	int                       InfrastructureMode;
} MC_WLAN_BSSID_LIST, *PMC_WLAN_BSSID_LIST;

typedef struct _MC_INT_BSSID_LIST
{
    int                       Privacy;            // WEP encryption requirement
    int                       Rssi;               // receive signal strength in dBm
    int                       BeaconPeriod;
    int                       ATIMWindow;
    int			    		  DSConfig;
	int                       InfrastructureMode;
} MC_INT_BSSID_LIST, *PMC_INT_BSSID_LIST;





// Error code
#define ERROR_QUERY_RSSI                        1
#define ERROR_NONE								0
#define ERROR_CREATE_HANDLE					   -1
#define ERROR_MEDIA_STATUS                     -3
#define ERROR_BSSID_SCAN                       -4

//function code
#define FN_CONFIG_ATIM                             101
#define FN_CONFIG_CHANNEL                          102
#define FN_CONFIG_BEACON                           103

// This class is exported from the WlanUtil.dll
class WLANUTIL_API CWlanUtil {
public:
	CWlanUtil(void);
	// TODO: add your methods here.
};
BOOL CreateFile_UIO0();
BOOL CreateFile_NDS1();
int CheckRequired();
extern WLANUTIL_API int nWlanUtil;
WLANUTIL_API int fnWlanUtil(void);


//Return zero is "WLAN on", not zero is "WLAN off"
EXTERN_C WLANUTIL_API int   MCGetWlanPwrStatus();
EXTERN_C WLANUTIL_API BOOL  MCSetWlanPwrOn();
EXTERN_C WLANUTIL_API BOOL  MCSetWlanPwrOff();
EXTERN_C WLANUTIL_API int   MCGetAdapterName(TCHAR *szAdapter);
EXTERN_C WLANUTIL_API int   MCGetRssiValue();
EXTERN_C WLANUTIL_API int   MCGetMediaConnStatus();
EXTERN_C WLANUTIL_API int   MCGetSsidName(TCHAR* szSsid);
EXTERN_C WLANUTIL_API int   MCGetBssid(UCHAR *uszBssid);
EXTERN_C WLANUTIL_API int   MCGetLinkSpeed();
EXTERN_C WLANUTIL_API int MCGetConfiguration(int nSelect);
EXTERN_C WLANUTIL_API int   MCGetBssidList(PMC_WLAN_BSSID_LIST pBssidList,int* pnCnt);
EXTERN_C WLANUTIL_API BOOL  MCSetBssidListScan();
EXTERN_C WLANUTIL_API int MCGetNICMACAddress(UCHAR *uszBssid);
EXTERN_C WLANUTIL_API int MCGetApCntNSetgBssid();
EXTERN_C WLANUTIL_API int MCGetBSListcf(UCHAR *uszBssid,TCHAR* szSsid,
										int* nAti,int* nBeacon,int* nDsCfg,int* nInfra,int* nPri,int* nRssi,
										int nRequire);
EXTERN_C WLANUTIL_API int MCDelBSListcf();

#endif
