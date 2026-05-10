/****************************************************************************
* FILE NAME: albtop.h										 				*
*																 		    *
* MODULE:    OBEX-based  Object Push Profile		    			        *
*																 		    *
* PURPOSE	: The header file containing common and exported structures in	*
*			  Object Push implementation	(For use with applications)	    *
*			  (c) Atinav Inc 2003								 		    *
*																			*
* INCLUDES : 											 	                *
*																 		    *
* DEVELOPMENT HISTORY											 		    *
*																		    *
*  Date         Author		MajorVer  MinorVer     Description Of Change	*
* --------   ------------	-------- ---------    ----------------------    *
* 04/12/03	  Atinav Inc	      1		001		  Release version  11.001	*
* 28/04/04    Atinav Inc          1     002       Release version  11.002   *
* 01/07/04    Atinav Inc          1     003       Release version  11.003   *
* 19/07/04    Atinav Inc          1     004       Release version  11.004   *
* 19/10/04    Atinav Inc          1     005       Release version  11.005   *
****************************************************************************/

#ifndef albtop_h
#define albtop_h

#ifdef __cplusplus
extern "C" {
#endif

#define OPP_DBG_ERROR			0x000000000100
#define OPP_DBG_WARNING			0x000000000200
#define OPP_DBG_IN_FLOW			0x000000000400
#define OPP_DBG_OUT_FLOW		0x000000000800
#define OPP_DBG_PKT1			0x000000001000
#define OPP_DBG_PKT2			0x000000002000
#define OPP_DBG_ALL				0x00000000FFFF
#define OPP_DBG_NONE			0x000000000000


// Target values
#define OPP_TARGET_CONSOLE		0x01
#define OPP_TARGET_FILE			0x02

#define VCARD21                0x01
#define VCARD30                0x02
#define VCALENDAR10            0x04
#define ICALENDAR20            0x08
#define VNOTE				   0x10
#define VMESSAGE			   0x20
#define GENERIC				   0xFF

typedef VOID    (*PSERVICESEARCHCOMPLETED)();
typedef VOID    (*PSESSIONSTARTED)();
typedef BOOLEAN (*PONPUSHREQUEST)   (HANDLE, PWCHAR); 
typedef BOOLEAN (*PONPULLREQUEST)   (HANDLE);
typedef VOID    (*PONOBJECTTRANSFERCOMPLETE)  (HANDLE, BOOLEAN, PWCHAR, BOOLEAN); 
typedef VOID    (*PONSESSIONCLOSE)  (HANDLE); 

typedef unsigned short WCHAR, *PWCHAR;

typedef struct _TRANSPORTCALLBACK /* User registered call back functions */
{		
	PSERVICESEARCHCOMPLETED serviceSearchCompleted;
	PSESSIONSTARTED sessionStarted;
}TRANSPORTCALLBACK, *PTRANSPORTCALLBACK;

typedef struct _OPERATIONSTATUS /* Status of the current operaion*/
{		
	UINT32 totalLength;
	UINT32 operationStatus;
	WCHAR objectName[255];	
}OPPOPERATIONSTATUS, *POPPOPERATIONSTATUS;

typedef struct _PUSHCALLBACK /* User registered call back functions to notify push and pull requests at the server side.*/
{		
	PONPUSHREQUEST onPushRequest;
	PONPULLREQUEST onPullRequest;	
	PONOBJECTTRANSFERCOMPLETE onObjectTransferComplete;
	PONSESSIONCLOSE onSessionClose;
} PUSHCALLBACK, *PPUSHCALLBACK;

/* Exported APIs of Server Module */
BOOLEAN OP_RegisterService(PBT_SERVICE,UINT8,PBT_REGISTERSERVICE_INFO);
HANDLE  OP_Accept(PBT_SERVICE, PBT_DEVICE);
BOOLEAN OP_SetOwnersBusinessCard(PWCHAR);
BOOLEAN OP_DeleteService(PBT_REGISTERSERVICE_INFO);
BOOLEAN OP_RegisterPushCallBack(PPUSHCALLBACK);
BOOLEAN OP_CancelAccept(BT_SERVICE);


/* Exported APIs of Client Module */
BOOLEAN OP_LocateDevices(UINT32, UINT8, UINT8, PBT_DEVICE, PUINT8);
VOID OP_SetTimeout(UINT32);
BOOLEAN OP_PushObject(PBT_DEVICE, PTRANSPORTCALLBACK, WCHAR**, UINT16, PUINT16);
BOOLEAN OP_PullBusinessCard(PBT_DEVICE, PTRANSPORTCALLBACK);
BOOLEAN OP_ExchangeBusinessCard(PBT_DEVICE, PTRANSPORTCALLBACK, PWCHAR);
BOOLEAN OP_CancelOperation();

/* Exported APIs of File Manipulation Module */
BOOLEAN OP_SetWorkingDirectory(PWCHAR);
BOOLEAN OP_GetStatus(POPPOPERATIONSTATUS);
BOOLEAN OP_Close(HANDLE);

VOID OP_SetDebugTarget(UINT8);
VOID OP_SetDebugLevel(INT64);

#ifdef __cplusplus
}
#endif 

#endif






