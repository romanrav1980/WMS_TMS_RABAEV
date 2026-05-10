// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the CAMCORE_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// CAMCORE_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
#ifdef CAMCORE_EXPORTS
#define CAMCORE_API __declspec(dllexport)
#else
#define CAMCORE_API __declspec(dllimport)
#endif

// User define Message
#define WM_CAM_STATE	WM_APP+200

// Error code
#define ERROR_NONE								0
#define ERROR_USB_PATH_OPEN						-1
#define ERROR_USB_PATH_GET						-2
#define ERROR_USB_PATH_ALREADY_CONNECT_CRADLE	-3
#define ERROR_USB_PATH_ENABLE_CAMERA			-4
#define ERROR_USB_PATH_DISABLE_CAMERA			-5
#define ERROR_USB_PORT_OPEN						-6
#define ERROR_USB_PORT_INIT						-7
#define ERROR_USB_PORT_CLOSE					-8
#define ERROR_UNKNOWN_CAPTURE_SIZE				-9
#define ERROR_UNKNOWN_BRIGHTNESS				-10
#define ERROR_UNKNOWN_COMPRESS_LEVEL			-11
#define ERROR_CREATE_PREVIEW_BUFFER				-12
#define ERROR_INVAILD_PREVIEW_HWND				-13
#define ERROR_OPEN_USB_EVENT					-14
#define ERROR_INVAILD_VALUE						-15
#define ERROR_USB_PATH_CHANGED_CREADLE			-16
#define ERROR_EMPTY_FILE_NAME					-17
#define ERROR_POWER_OFF							-18
#define ERROR_PREVIEW_OFF						-19
#define ERROR_CAPTURE_TIMEOUT					-20

// Camera capture size
#define CAM_API_CAPTURE_160_120		0
#define CAM_API_CAPTURE_320_240		1
#define CAM_API_CAPTURE_640_480		2

//Compress level
#define CAM_API_COMPRESS_LEVEL_07	0
#define CAM_API_COMPRESS_LEVEL_06	1
#define CAM_API_COMPRESS_LEVEL_05	2		 
#define CAM_API_COMPRESS_LEVEL_04	3 		
#define CAM_API_COMPRESS_LEVEL_03	4
#define CAM_API_COMPRESS_LEVEL_02	5
#define CAM_API_COMPRESS_LEVEL_01	6

// Camera State
#define CAM_API_STATE_POWER_OFF		0
#define CAM_API_STATE_POWER_ON		1
#define CAM_API_STATE_PREVIEW		2
#define CAM_API_STATE_CAPTURE		3

// This class is exported from the CamCore.dll
class CAMCORE_API CCamCore {
public:
	CCamCore(void);
	// TODO: add your methods here.
};

EXTERN_C CAMCORE_API int	MCCamPowerON (HWND hMainWnd);				// Power ON
EXTERN_C CAMCORE_API int	MCCamPowerOFF ();							// Power OFF
EXTERN_C CAMCORE_API int	MCCamGetState ();								// Camera state
EXTERN_C CAMCORE_API int	MCCamPreviewStart (HWND hPreviewControl);	// Preview start
EXTERN_C CAMCORE_API int	MCCamPreviewStop ();						// Prevview stop
EXTERN_C CAMCORE_API int	MCCamCapture (int nCompLev, int nSize, TCHAR *szFileName);	// Image capture
EXTERN_C CAMCORE_API void	MCCamGetError (int nErrorCode/*in*/, TCHAR* szErrorString/*out*/); // Error code to string

