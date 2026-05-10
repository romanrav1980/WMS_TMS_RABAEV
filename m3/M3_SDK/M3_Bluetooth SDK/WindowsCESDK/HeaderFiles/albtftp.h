/****************************************************************************
* FILE NAME: albtftp.h										 				*
*																 		    *
* MODULE:    OBEX-based  File Transfer Profile		    			        *
*																 		    *
* PURPOSE	: The header file containing common and exported structures in	*
*			  FTP implementation	(For use with applications)			    *
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
* 19/10/04    Atinav Inc          1     004       Release version  11.004   *
****************************************************************************/


#ifndef albtftp_h
#define albtftp_h

#ifdef __cplusplus
extern "C" {
#endif
#define AUTHENTICATE_NONE 0
#define AUTHENTICATE_CONNECT 1
#define AUTHENTICATE_PUSH 2
#define AUTHENTICATE_PULL 4
#define AUTHENTICATE_DELETE 8
#define AUTHENTICATE_NEWFOLDER 16
#define AUTHENTICATE_ALL 31

#define FTP_DBG_ERROR			0x000000000001
#define FTP_DBG_WARNING			0x000000000002
#define FTP_DBG_IN_FLOW			0x000000000004
#define FTP_DBG_OUT_FLOW		0x000000000008
#define FTP_DBG_PKT1			0x000000000010
#define FTP_DBG_PKT2			0x000000000020
#define FTP_DBG_ALL				0x0000000000FF
#define FTP_DBG_NONE			0x000000000000


// Target values
#define FTP_TARGET_CONSOLE		0x01
#define FTP_TARGET_FILE			0x02




typedef struct _OBJECTPROPERTIES
{
	WCHAR		objectName[255];
	UINT32		size;
	WCHAR		accessPermission[5];
	WCHAR		mimeType[20];
	BOOLEAN		isFolder;
	SYSTEMTIME  createdTime;
	SYSTEMTIME  modifiedTime;	

}OBJECTPROPERTIES, *POBJECTPROPERTIES;

typedef   struct StatusOfOperation
{
  WCHAR	  objectName[255] ;       //name of the object 
  UINT32  totalSizeOfObj ;      //total size of the object
  UINT32  currentStatus;       //Number of bytes transferred
}FTPOPERATIONSTATUS,*PFTPOPERATIONSTATUS;

typedef VOID    (*PONSESSIONCLOSE)     (HANDLE); 


/*FTP server call back functions*/
typedef struct _FTPSERVERCALLBACK
{	
	PONSESSIONCLOSE sessionClose; /*Notifies when the session is closed*/

}FTPSERVERCALLBACK, *PFTPSERVERCALLBACK;


typedef BOOLEAN (*PGETUSERDETAILS)(PAUTHDETAILS authDet, UINT16 count, PUINT8 userName, PUINT16 userLength, PUINT8 password, PUINT16 passLength, PUINT16 index); /*Username and password are output parameters*/
typedef BOOLEAN (*PGETUSERPASSWORD)(PUINT8 userName,UINT16 userLength, PUINT8 realm, UINT16 realmLength, PUINT8 password, PUINT16 passLength); /*Here Username is input parameter and password is output parameter*/

typedef struct _FTPAUTHCALLBACKS /* User registered call back functions for authenticateion*/
{		
	PGETUSERDETAILS getUserDetails;
	PGETUSERPASSWORD getUserPassword;
}FTPAUTHCALLBACKS, *PFTPAUTHCALLBACKS;

//Exported APIs
//Server Functions
BOOLEAN FTP_RegisterService(PBT_SERVICE,PBT_REGISTERSERVICE_INFO);
BOOLEAN FTP_DeleteService(PBT_REGISTERSERVICE_INFO);

VOID    FTP_RegisterServerCallback(PFTPSERVERCALLBACK);
BOOLEAN FTP_SetInbox(PWCHAR, BOOLEAN);
HANDLE  FTP_AcceptConnection(PBT_SERVICE, PBT_DEVICE);
BOOLEAN FTP_CancelAccept(BT_SERVICE);

//Client Functions
BOOLEAN FTP_LocateDevices(UINT32, UINT8, UINT8, PBT_DEVICE, PUINT8);
BOOLEAN FTP_GetRemoteServices(PBT_DEVICE, UINT16, PBT_SERVICE, PUINT16 servCount);
HANDLE  FTP_OpenConnection(PBT_DEVICE,  PBT_SERVICE);
BOOLEAN FTP_CancelOpen(PBT_DEVICE, PBT_SERVICE);
BOOLEAN FTP_Connect(HANDLE, PUINT32);
BOOLEAN FTP_GetFolderList(HANDLE, UINT32,  POBJECTPROPERTIES*, PUINT16);
BOOLEAN FTP_FreeFolderListObject(POBJECTPROPERTIES);
BOOLEAN FTP_SetCurrentDirectory(HANDLE, UINT32, PWCHAR, BOOLEAN);
BOOLEAN FTP_CreateFolder(HANDLE, UINT32, PWCHAR);
BOOLEAN FTP_DeleteObject(HANDLE, UINT32, PWCHAR);
BOOLEAN	FTP_PushObject(HANDLE, UINT32, PWCHAR, PWCHAR);
BOOLEAN FTP_PullObject(HANDLE, UINT32, PWCHAR, PWCHAR);
BOOLEAN FTP_CancelOperation(HANDLE);
BOOLEAN FTP_GetStatus(HANDLE, PFTPOPERATIONSTATUS);
BOOLEAN FTP_Disconnect(HANDLE, UINT32);
BOOLEAN FTP_SetTimeout(HANDLE,  UINT32);



BOOLEAN FTP_CloseConnection(HANDLE);

//Security Functions
VOID    FTP_RegisterAuthCallbacks(PFTPAUTHCALLBACKS);
BOOLEAN FTP_SetAuthentication(PAUTHDETAILS, UINT16, UINT8);

VOID FTP_SetDebugLevel(INT64);
VOID FTP_SetDebugTarget(UINT8);

#ifdef __cplusplus
}
#endif 

#endif