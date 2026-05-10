/****************************************************************************
* FILE NAME: albtgoep.h										 				*
*																 		    *
*																			*
* MODULE:    Generic Object Exchange Profile						        *
*																 		    *
* PURPOSE:   The header file containing common and exported structures in	*
*			 GOEP implementation	(For use with applications)			    *
*			 (c) Atinav Inc 2003								 		    *			        
*																			*
* INCLUDES :             											 	    *
*																 		    *
* DEVELOPMENT HISTORY											 		    *
*																		    *
*  Date         Author		MajorVer  MinorVer     Description Of Change	*
* --------   ------------	-------- ---------    ----------------------    *
* 16/09/03	  Atinav Inc	      1		001		  Release version  11.001	*
* 31/10/03    Atinav Inc          1     002       Release version  11.002   *
* 28/04/04    Atinav Inc          1     003       Release version  11.003   *
* 10/06/04    Atinav Inc		  1     004b      Release version  11.004b  *
* 01/07/04    Atinav Inc		  1     005       Release version  11.005   *
* 19/10/04    Atinav Inc		  1     006       Release version  11.006   *
****************************************************************************/

#ifndef albtgoep_h
#define albtgoep_h

#ifdef __cplusplus
extern "C" {
#endif

#define GOEP_DBG_ERROR			0x000000000001
#define GOEP_DBG_WARNING		0x000000000002
#define GOEP_DBG_IN_FLOW		0x000000000004
#define GOEP_DBG_OUT_FLOW		0x000000000008
#define GOEP_DBG_PKT1			0x000000000010
#define GOEP_DBG_PKT2			0x000000000020
#define GOEP_DBG_ALL			0x0000000000FF
#define GOEP_DBG_NONE			0x000000000000


/*OBEX Headers*/
#define COUNT			0xC0
#define NAME			0x01
#define TYPE			0x42
#define LENGTH			0xC3
#define TIME_ISO_8601	0x44
#define TIME_4_BYTES	0xC4
#define DESCRIPTION		0x05
#define TARGET			0x46
#define HTTP			0x47
#define WHO				0x4A
#define CONNECTIONID	0xCB
#define APP_PARAM		0x4C
#define OBJECT_CLASS	0x4F

/*OBEX Response Codes*/
#define OBEX_SUCCESS                  0xA0
#define OBEX_CREATED				  0xA1
#define OBEX_ACCEPTED                 0xA2
#define OBEX_NON_AUTHORITATIVE	      0xA3
#define OBEX_NO_CONTENT				  0xA4
#define OBEX_RESET_CONTENT			  0xA5
#define OBEX_PARTIAL_CONTENT		  0xA6
#define OBEX_MULTIPLE_CHOICES         0xB0
#define OBEX_MOVED_PERMANENTLY        0xB1
#define OBEX_MOVED_TEMPORARILY		  0xB2
#define OBEX_SEE_OTHER                0xB3
#define OBEX_NOT_MODIFIED             0xB4
#define OBEX_USE_PROXY				  0xB5
#define OBEX_BAD_REQUEST              0xC0
#define OBEX_UNAUTHORIZED             0xC1
#define OBEX_PAYMENT_REQUIRED         0xC2
#define OBEX_FORBIDDEN	              0xC3
#define OBEX_NOT_FOUND                0xC4
#define OBEX_METHOD_NOT_ALLOWED		  0xC5
#define OBEX_NOT_ACCEPTABLE			  0xC6
#define OBEX_PROXY_AUTH_REQUIRED	  0xC7
#define OBEX_REQUEST_TIME_OUT         0xC8
#define OBEX_CONFLICT	              0xC9
#define OBEX_GONE			          0xCA
#define OBEX_LENGTH_REQUIRED          0xCB
#define OBEX_PRECONDITION_FAILED	  0xCC
#define OBEX_REQUESTED_ENTITY_LARGE	  0xCD
#define OBEX_REQUEST_URL_LARGE		  0xCE
#define OBEX_UNSUPPORTED_MEDIA_TYPE	  0xCF
#define OBEX_INTERNAL_SERVER_ERROR    0xD0
#define OBEX_NOT_IMPLEMENTED		  0xD1
#define OBEX_BAD_GATEWAY			  0xD2
#define OBEX_SERVICE_UNAVAILABLE      0xD3
#define OBEX_GATEWAY_TIMEOUT		  0xD4
#define OBEX_HTTP_VER_NOT_SUPPORTED	  0xD5
#define OBEX_DATABASE_FULL			  0xE0
#define OBEX_DATABASE_LOCKED		  0xE1


typedef struct _AUTHDETAILS /*Authentication Details for user interaction*/
{
	BOOLEAN userIDRequired;
	BOOLEAN access;
	UINT8   hashingAlgo;
	UINT8   realmLength;
	PUINT8  realm;		
	
}AUTHDETAILS,*PAUTHDETAILS;

typedef BOOLEAN (*PONAUTHENTICATECHALLENGE)(HANDLE sessionHandle, PAUTHDETAILS authDet, UINT16 count, PUINT8 userName, PUINT16 userLength, PUINT8 password, PUINT16 passLength, PUINT16 index); /*Username and password are output parameters*/
typedef BOOLEAN (*PONAUTHENTICATERESPONSE)(HANDLE sessionHandle, PUINT8 userName,UINT16 userLength, PUINT8 realm, UINT16 realmLength, PUINT8 password, PUINT16 passLength); /*Here Username is input parameter and password is output parameter*/

typedef	UINT8 (*PONCONNECT)   (HANDLE sessionHandle, HANDLE requestHandle, BOOLEAN authenticatedClient, HANDLE responseHandle);
typedef	UINT8 (*PONDISCONNECT)(HANDLE sessionHandle, HANDLE requestHandle, HANDLE responseHandle);
typedef	UINT8 (*PONPUT)       (HANDLE sessionHandle, HANDLE requestHandle, BOOLEAN authenticatedClient, HANDLE opHandle);
typedef	UINT8 (*PONGET)       (HANDLE sessionHandle, HANDLE requestHandle, BOOLEAN authenticatedClient, HANDLE opHandle);
typedef	UINT8 (*PONDELETE)    (HANDLE sessionHandle, HANDLE requestHandle, BOOLEAN authenticatedClient, HANDLE responseHandle);
typedef	UINT8 (*PONSETPATH)   (HANDLE sessionHandle, HANDLE requestHandle, BOOLEAN authenticatedClient, BOOLEAN backup, BOOLEAN create, HANDLE responseHandle);
typedef	VOID (*PONSESSIONCLOSE)	  (HANDLE sessionHandle);


typedef VOID (*PONHEADERRECEIVE)(HANDLE headerSetHandle);


typedef struct _AUTHCALLBACK /* User registered call back functions for authenticateion*/
{		
	PONAUTHENTICATECHALLENGE onAuthenticateChallenge;
	PONAUTHENTICATERESPONSE onAuthenticateResponse;

}AUTHCALLBACK, *PAUTHCALLBACK;	

typedef struct _SERVERCALLBACK	/* User registered call back functions for OBEX Operations*/
{		
		PONCONNECT onConnect;
		PONDISCONNECT onDisconnect;
		PONPUT onPut;
		PONGET onGet;
		PONDELETE onDelete;
		PONSETPATH onSetpath;
		PONSESSIONCLOSE onSessionClose;
}SERVERCALLBACK, *PSERVERCALLBACK;

typedef struct _HEADERCALLBACK
{
	PONHEADERRECEIVE onHeaderReceive;

}HEADERCALLBACK, *PHEADERCALLBACK;

/* Exported APIs of Server Module */
HANDLE GOEP_Accept(PBT_SERVICE, PSERVERCALLBACK, PAUTHCALLBACK, PBT_DEVICE);
//HANDLE GOEP_RegisterService(PBT_SERVICE, PBT_UUID, PHANDLE, PUINT32);
//HANDLE GOEP_RegisterService(PBT_SERVICE, PBT_UUID);
BOOLEAN GOEP_RegisterService(PBT_SERVICE,
		PBT_UUID, PBT_REGISTERSERVICE_INFO);

BOOLEAN GOEP_DeleteService(PBT_REGISTERSERVICE_INFO);

//BOOLEAN GOEP_DeleteService(HANDLE);
BOOLEAN GOEP_CancelAccept(BT_SERVICE);


/* Exported APIs of Client Module */
BOOLEAN GOEP_LocateDevices(UINT32,UINT8,UINT8,PBT_DEVICE,PUINT8);
BOOLEAN GOEP_GetRemoteServices(PBT_DEVICE, PBT_UUID, UINT16, PBT_SERVICE, UINT16, PUINT16);
BOOLEAN GOEP_Connect(HANDLE, HANDLE, PUINT8, HANDLE);
BOOLEAN GOEP_Disconnect(HANDLE, HANDLE, PUINT8, HANDLE);
BOOLEAN GOEP_SetPath(HANDLE, HANDLE, BOOLEAN, BOOLEAN, PUINT8, HANDLE);
BOOLEAN GOEP_Delete(HANDLE, HANDLE, PUINT8, HANDLE);
BOOLEAN GOEP_CancelOpen(PBT_DEVICE, PBT_SERVICE);
HANDLE  GOEP_Open(PBT_DEVICE,PBT_SERVICE,PAUTHCALLBACK);
HANDLE  GOEP_Put(HANDLE, HANDLE, PUINT8, HANDLE);
HANDLE  GOEP_Get(HANDLE, HANDLE, PUINT8, HANDLE);

/* Exported APIs of Security Module */
BOOLEAN GOEP_SetAuthenticationChallenge(HANDLE, PAUTHDETAILS, UINT16);

/* Exported APIs of Packet Processing Module */
HANDLE  GOEP_CreateHeaderSet();
BOOLEAN GOEP_SetHeader(HANDLE, UINT8, PVOID, UINT16);
BOOLEAN GOEP_FreeHeaderSet(HANDLE);
BOOLEAN GOEP_GetNumberOfHeaders(HANDLE, PUINT16);
BOOLEAN GOEP_GetHeaderIds(HANDLE, PUINT8);
BOOLEAN GOEP_GetValueLength(HANDLE, UINT8, PUINT16);
BOOLEAN GOEP_GetValue(HANDLE, UINT8, PVOID);

/* Exported APIs of Stream Module */
BOOLEAN GOEP_RegisterHeaderCallBack(HANDLE, PHEADERCALLBACK);
BOOLEAN GOEP_ReadData (HANDLE, UINT16, PUINT8, PINT32);
BOOLEAN GOEP_WriteData(HANDLE, PUINT8, UINT16, PUINT16);
BOOLEAN GOEP_SetOperationHeader(HANDLE, HANDLE);
BOOLEAN GOEP_Available(HANDLE,PUINT16);
VOID GOEP_StreamClose(HANDLE);
BOOLEAN GOEP_Abort(HANDLE, HANDLE, PUINT8, HANDLE);

/* Exported APIs of Transport Module */
BOOLEAN GOEP_SetTimeOut(HANDLE , UINT32);

/* General */
BOOLEAN GOEP_Close(HANDLE);
VOID GOEP_SetDebugTarget(UINT8);
VOID GOEP_SetDebugLevel(INT64);


#ifdef __cplusplus
}
#endif 

#endif