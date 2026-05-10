/****************************************************************************
* FILE NAME	:	albtnetprofiles.h									 		*
*																 		    *
* MODULE	:	LAP & DUN Profiles											*
*																 		    *
* PURPOSE	:	The header file contains structures in						*
*				Net Profiles implementation	(For use with applications)		*
*				(c) Atinav								 					*
****************************************************************************/

#ifndef ALBTNETPROFILES_H
#define ALBTNETPROFILES_H

typedef VOID EventNotifyProc(HANDLE handle, UINT32 event);

#ifdef __cplusplus
extern "C" {
#endif


 BOOLEAN DUN_LocateDevices(UINT32 accessCode, 
						UINT8 duration, PBT_DEVICE remoteDevices, 
						UINT8 maxNumDevices, PUINT8 numDevices);

 BOOLEAN LAP_LocateDevices(UINT32 accessCode, 
						UINT8 duration, PBT_DEVICE remoteDevices, 
						UINT8 maxNumDevices, PUINT8 numDevices);

 BOOLEAN DUN_GetRemoteServices(PBT_DEVICE device,
						PBT_SERVICE services, UINT16 maxServiceCount,
						PUINT16 numServices);
 BOOLEAN DUN_SetEventNotifyProc(HANDLE dunHandle,
						EventNotifyProc * upperCallbackProc);

 BOOLEAN LAP_GetRemoteServices(PBT_DEVICE device, 
						PBT_SERVICE services, UINT16 maxServiceCount,
						PUINT16 numServices);
 BOOLEAN LAP_SetEventNotifyProc(HANDLE lapHandle,
		              EventNotifyProc * upperCallbackProc);

 HANDLE DUN_Connect(PBT_DEVICE device,PBT_SERVICE service,
						PUINT16 frameSize , PBT_SECURITY_ATTRIBUTE attrib , 
						PINT8 portName);
 BOOLEAN DUN_PPPConnect(PWCHAR entryName, 
						PWCHAR userName, PWCHAR  password);

 BOOLEAN DUN_PPPDisconnect(PWCHAR entryName);
 BOOLEAN DUN_Disconnect(HANDLE dunHandle);
 HANDLE LAP_Connect(PBT_DEVICE device, PBT_SERVICE service,
						PUINT16 frameSize, PBT_SECURITY_ATTRIBUTE attrib , 
						PINT8 portName);
 BOOLEAN LAP_PPPConnect(PWCHAR entryName, PWCHAR userName, 
							PWCHAR  password); 
 BOOLEAN LAP_Disconnect(HANDLE lapHandle);
 BOOLEAN LAP_PPPDisconnect(PWCHAR entryName);
 BOOLEAN DUN_Disconnect(HANDLE dunHandle);
 BOOLEAN DUN_CancelConnect(PBT_DEVICE device, PBT_SERVICE service);
 BOOLEAN LAP_CancelConnect(PBT_DEVICE device, PBT_SERVICE service);
 BOOLEAN DUN_CreateRasEntry (PWCHAR  entryName, PWCHAR  login, 
 								PWCHAR  password, PWCHAR  phoneNumber);
 BOOLEAN LAP_CreateRasEntry(PWCHAR  entryName, PWCHAR  login, 
 								PWCHAR  password, PWCHAR  phoneNumber);
 BOOLEAN DUN_DeleteRasEntry(PWCHAR entryName);
 BOOLEAN LAP_DeleteRasEntry(PWCHAR entryName);

 BOOLEAN LAP_CreateSettings(PWCHAR strEntryName);
 BOOLEAN DUN_CreateSettings(PWCHAR strEntryName);

 
#ifdef __cplusplus
}
#endif 


#endif