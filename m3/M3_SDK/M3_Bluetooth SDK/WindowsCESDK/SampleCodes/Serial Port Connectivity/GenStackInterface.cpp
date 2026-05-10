

// GenStackInterface.cpp: implementation of the GenStackInterface class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "albtcore.h"
#include "albterrorcodes.h"
#include "GenStackInterface.h"

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif


/*
*
* FUNCTION NAME	:	GenStackInterface
*
* DESCRIPTION	:	Standard Constructor
*
* RETURNS		: VOID
*/
GenStackInterface::GenStackInterface()
{

}

/*
*
* FUNCTION NAME	:	Standard destructor
*
* DESCRIPTION	:	Constructor
*
* RETURNS		: VOID
*/
GenStackInterface::~GenStackInterface()
{

}

/*
*
* FUNCTION NAME	:	BTCardInitialize
*
* DESCRIPTION	:	Initializes the bluetooth hardware &software 
*					prior to use
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

BOOLEAN GenStackInterface::BTCardInitialize()
{

	INT8 port[]			= HCI_UART_Port;
	BOOLEAN retValue	= FALSE;

	iLogFile("# GenStackInterface :: BTCardInitialize - [enter] ");
	
	// Set the transport for the Bluetooth module
	retValue = BT_SetTransportLayer(BT_TRANSPORT);
	
	// If the above function succeeds or, if it is failed with the 
	// errorcode  BT_TRANSPORT_ALREADY_INITIALIZED, then proceed

	if(retValue || (BT_GetErrorCode() == BT_TRANSPORT_ALREADY_INITIALIZED))
	{
		retValue = FALSE;

		// Set the port parameters for the Bluetooth module

		if(BT_TRANSPORT == TL_H4)
		{
			retValue = BT_SetUARTDefaultPortParams(port, HCI_BAUDRATE); 
		}
		else if(BT_TRANSPORT == TL_BCSP)
		{
			retValue = BT_SetBCSPDefaultPortParams(port, HCI_BAUDRATE);
		}
		else
		{
			// Unsupported Transport
			iLogFile("# GenStackInterface :: BTCardInitialize - Unsupported Transport");
			return retValue;
		}

		// If the above function succeeds or, if it is failed with the 
		// errorcode  BT_TRANSPORT_ALREADY_INITIALIZED, then proceed

		if(retValue || (BT_GetErrorCode() == BT_TRANSPORT_ALREADY_INITIALIZED))		
		{
			if(BT_IsInitialized())
			{
				// Bluetooth stack already initialized; get an instance of the Stack
				if(BT_Open())
				{
					retValue = TRUE;
				}
				else
				{
					retValue = FALSE;
					iLogFile("# [error] - BT_Open - Status Fail");
				}		
			}
			else
			{
				// Bluetooth stack not initialized; Initialize it & get an instance
				if(BT_Init())
				{
					retValue = TRUE;
				}
				else
				{
					
					retValue = FALSE;
					iLogFile("# [error] - BT_Init - Status Fail");
				}		
			}
		}
		else
		{
			iLogFile("# [error] - BT_SetBCSPDefaultPortParams - Status Fail");
			retValue = FALSE;
		}	
	}
	else
	{
		iLogFile("# [error] - BT_SetTransportLayer - Status Fail");
	}

	if(retValue)
	{
		// Set connectable mode
		if(GAP_SetConnectableMode(TRUE))
		{				
			// Set discoverable mode
			if(GAP_SetDiscoverableMode(TRUE, NULL, 0))
			{				
				retValue = TRUE;
			}
			else
			{
				retValue =  FALSE;
				iLogFile("# [error] - GAP_SetConnectableMode - Status Fail");							
			}
		}
		else
		{
			retValue =  FALSE;
			iLogFile("# [error] - GAP_SetConnectableMode - Status Fail");						
		}
	}
	return retValue;
}		


/*
* FUNCTION NAME	:	BTCardDeInitialize
*
* DESCRIPTION	:	Resets and deinitialises the bluetooth module and SDK 
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

BOOLEAN GenStackInterface::BTCardDeInitialize()
{
	BOOLEAN retVal = FALSE;

	iLogFile("# GenStackInterface :: BTCardDeInitialize - [enter] ");

	// Release the stack instance

	if(BT_Close())
	{
		retVal = TRUE;	
	}
	else
	{
		iLogFile("# [error] - BT_Close - Status Fail");						
	}			
	
	// If this is the Control application, deInitialize the stack& reset 
	//	the card[Only control applications are expected to call  
	//	BT_DeInit()].

	if(BT_DeInit())
	{
		retVal = TRUE;
	}
	else
	{
		retVal = FALSE;
		iLogFile("# [error] - BT_DeInit - Satus Fail");			
	}
	
	iLogFile("# GenStackInterface :: BTCardDeInitialize - [leave] ");
	return retVal;
}

/*
*
* FUNCTION NAME	:	GapSetLocalDeviceName
*
* DESCRIPTION	:	Set the local device with the specified device name
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	name			DEVICE_NAME	I		Device name to set
*
* RETURNS		: VOID
*/

BOOLEAN GenStackInterface::GapSetLocalDeviceName(DEVICE_NAME name)
{
	BOOLEAN retVal = FALSE;
	
	iLogFile("# GenStackInterface :: GapSetLocalDeviceName - [leave] ");				
	GAP_SetLocalDeviceName(name);
	iLogFile("# GenStackInterface :: GapSetLocalDeviceName - [leave] ");			
	
	return retVal;
}

/*
*
* FUNCTION NAME	:	GapInquireAndRetrieveDevices
*
* DESCRIPTION	:	Perfoms inquiry and retreives the bluetooth devices in 
*					the vicinity 
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	accessCode		UINT32		I		Access code(Refer API doc)
*	duration		UINT8		I		Duration for the current inquiry
*	devices			BT_DEVICE[]	O		An array that receives the information
*										of the devices, found during inquiry 		
*	size			UINT8		I		Specifies the size of the array
*	retCount		PUINT8		O		Pointer to a UINT8 variable that 
*										receives the number of devices found
*										in the inquiry.
* RETURNS		: BOOLEAN, TRUE if success, FALSE otherwise
*/

BOOLEAN GenStackInterface::GapInquireAndRetrieveDevices(UINT32 accessCode,
										UINT8 duration, BT_DEVICE devices[], 
										UINT8 size, PUINT8 retCount)
{
	BOOLEAN retVal = FALSE;

	iLogFile("# GenStackInterface::GapInquireAndRetrieveDevices - [enter] ");
	
	if(GAP_InquireAndRetrieveDevices(accessCode, duration, devices, size, retCount) == TRUE)
	{
		retVal = TRUE;		
	}
	else
	{
		iLogFile("# [error] - GAP_InquireAndRetrieveDevices - Satus Fail ");
	}
	
	iLogFile("# GenStackInterface::GapInquireAndRetrieveDevices - [leave] ");
	return retVal;
}


/*
*
* FUNCTION NAME	:	GapGetLocalDeviceAddress
*
* DESCRIPTION	:	Retreives the device address of the local device 
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	bdAddress		BD_ADDRESS		I	Receives the bluetooth address of 
*										the local device

* RETURNS		: BOOLEAN, TRUE if success, FALSE otherwise
*/

BOOLEAN GenStackInterface::GapGetLocalDeviceAddress(BD_ADDRESS bdAddress)
{
	BOOLEAN retVal = FALSE;
	
	iLogFile("# GenStackInterface :: GapGetLocalDeviceAddress - [leave] ");			

	if(GAP_GetLocalDeviceAddress(bdAddress))
	{
		retVal = TRUE;
	}
	else
	{
		iLogFile("# [error] - GapGetLocalDeviceAddress - Satus Fail ");
	}
	iLogFile("# GenStackInterface :: GapGetLocalDeviceAddress - [leave] ");			
	
	return retVal;
}

/*
*
* FUNCTION NAME	:	SdapSearchRemoteServices
*
* DESCRIPTION	:	Retreives the service information registered in the 
*					specified device  
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	device			PBT_DEVICE	 I		Device information
*	sdpUuids		BT_UUID		 I		list of UUIDs used to locate matching 
*										services on the remote device.
*	uuidCount		UINT16		 I		size of sdpUuids array
*	services		BT_SERVICE[] O		Array that retreives the service 
*										information of the specified device
*	maxServicecount	UINT16		 I		Maximum number of services to retreive
*	numServices		PUINT16		 O		Number of services found 			

* RETURNS		: BOOLEAN, TRUE if success, FALSE otherwise
*/

BOOLEAN GenStackInterface::SdapSearchRemoteServices(PBT_DEVICE device, 
								BT_UUID sdpUuids[], UINT16  uuidCount, 
								BT_SERVICE services[], UINT16 maxServicecount, 
								PUINT16 numServices)
{
	BOOLEAN retValue = FALSE;	
	HANDLE sdpHandle = NULL;
	UINT16   tmpNumServices = 0;
	iLogFile("# GenStackInterface :: SdapSearchRemoteServices - [enter] ");
	
	sdpHandle		= SDAP_GetConnection(device);
	
	if(sdpHandle)
	{			
		*numServices = tmpNumServices;	
		retValue= SDAP_SearchRemoteServices(sdpHandle, sdpUuids, 1, 
		services, maxServicecount, &tmpNumServices);
	
		if(retValue)
		{
			*numServices = tmpNumServices;
			if(numServices)
			{
				UINT16 i = 0;
				for(i = 0; i < *numServices ; i ++)
				{
					services[i].protocolDescriptor = RFCOMM;
				}
			}
			else
			{
				iLogFile("# [status] - No Service Found");
			}
		}
		else
		{
			iLogFile("# [error] - SDAP_SearchRemoteServices - Satus Fail ");
		}
		
		if(SDAP_CloseConnection(sdpHandle) == FALSE)
		{
			iLogFile("# [error] - SDAP_CloseConnection - Satus Fail ");
		}
	}
	else
	{
		iLogFile("# [error] - SDAP_GetConnection - Satus Fail ");
	}	
	iLogFile("# GenStackInterface :: SdapSearchRemoteServices - [leave] ");

	return retValue;
}


//Using SPP Profile

/*
*
* FUNCTION NAME	:	SppConnect
*
* DESCRIPTION	:	Connects to the specified device for using the specified 
*					service on the remote device
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	device			PBT_DEVICE	 I		Device information
*	service		PBT_SERVICE	 I		Service information of the remote device
*	frameSize		PUINT16		 I,O		Frame size to be negotiated
*	secAttrib		PBT_SECURITY_ATTRIBUTE	I Security related information
*	portName		PINT8		I		name of the port to which the connection
*										is to be established

* RETURNS		: HANDLE, Returns a handle to the connection if the call is 
*success;Returns NULL if failed
*/
		
HANDLE GenStackInterface::SppConnect(PBT_DEVICE device, PBT_SERVICE service, 
									PUINT16 frameSize, 
									PBT_SECURITY_ATTRIBUTE secAttrib, 
									PINT8 portName)
{
	HANDLE sppConnection = NULL;
	iLogFile("# GenStackInterface :: SppConnect - [enter] ");		
	
	sppConnection = SPP_Connect(device, service, frameSize, secAttrib, portName);		
	if(sppConnection == NULL)
	{		
		iLogFile("# [error] - SPP_Connect - Satus Fail ");
	}	
	iLogFile("# GenStackInterface :: SppConnect - [leave] ");	
	
	return sppConnection;	
}

/*
*
* FUNCTION NAME	:	SppAccept
*
* DESCRIPTION	: Accepts connection request from remote devices for using the 
*					specified service registered previously
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	device			PBT_DEVICE	 I		Remote device information
*	services		PBT_SERVICE	 I		Contains the service information 
*										registered previously
*	frameSize		PUINT16		 I,O		Frame size to be negotiated
*	secAttrib		PBT_SECURITY_ATTRIBUTE	I Security related information
*	portName		PINT8		I		name of the port to which the connection
*										is to be established

* RETURNS		: HANDLE, Returns a handle to the connection if the call is 
*success;Returns NULL if failed
*/

HANDLE GenStackInterface::SppAccept(PBT_DEVICE device, PBT_SERVICE service, 
									PUINT16 frameSize, 
									PBT_SECURITY_ATTRIBUTE secAttrib, 
									PINT8 portName)
{
	HANDLE sppConnection = NULL;

	iLogFile("# GenStackInterface :: SppAccept - [enter] ");			
	sppConnection = SPP_Accept(device, service, frameSize, secAttrib, portName);	
	if(sppConnection == NULL)
	{
		iLogFile("# [error] - SPP_Accept - Satus Fail ");
	}	
	iLogFile("# GenStackInterface :: SppAccept - [leave] ");		
	
	return sppConnection;	
}

/*
*
* FUNCTION NAME	:	SppRegisterService
*
* DESCRIPTION	:	Registers the specified service to the SDK, So that other
*					devices can use the services.	
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*
*	services		PBT_SERVICE	 I		Contains the service information 
*										to be registered
*	uuid			PBT_UUID	 I		spevifies a UUID
*
*	serviceInfo		PBT_REGISTERSERVICE_INFO	I Service registration info
*
* RETURNS		: BOOLEAN , Returns TRUE if success
*/

BOOLEAN GenStackInterface::SppRegisterService(PBT_SERVICE service, PBT_UUID uuid, 
											PBT_REGISTERSERVICE_INFO serviceInfo)
{
	BOOLEAN retVal = FALSE;

	iLogFile("# GenStackInterface :: SppRegisterService - [enter] ");				
	
	if(SPP_RegisterService(service, uuid, serviceInfo))
	{
		retVal = TRUE;
	}
	else
	{
		iLogFile("# [error] - SPP_RegisterService - Satus Fail ");
	}

	iLogFile("# GenStackInterface :: SppRegisterService - [leave] ");			

	return retVal;
}

// Modified for ver1.004 Release

BOOLEAN GenStackInterface::SppDeleteService(PBT_REGISTERSERVICE_INFO serviceInfo)
{
	BOOLEAN retVal = FALSE;
	
	iLogFile("# GenStackInterface :: SppDeleteService - [enter] ");			
	if(SPP_DeleteService(serviceInfo))
	{
		retVal = TRUE;
	}
	else
	{
		iLogFile("# [error] - SPP_DeleteService - Status Fail ");
	}
	iLogFile("# GenStackInterface :: SppDeleteService - [leave] ");			
	
	return retVal;
}


BOOLEAN GenStackInterface::SppRemoveServer(BT_SERVICE service)
{
	BOOLEAN retVal = FALSE;

	iLogFile("# GenStackInterface :: SppRemoveServer - [leave] ");			
	
	if(SPP_CancelAccept(service))
	{
		retVal = TRUE;
	}
	else
	{
		iLogFile("# [error] - SPP_RemoveServer - Satus Fail ");
	}
	iLogFile("# GenStackInterface :: SppRemoveServer - [leave] ");			
	
	return retVal;
}


BOOLEAN GenStackInterface::SppClose(HANDLE handle)
{
	BOOLEAN retVal = FALSE;
	
	iLogFile("# GenStackInterface :: SppClose - [leave] ");			
	if(SPP_Close(handle))
	{
		retVal = TRUE;
	}
	else
	{
		iLogFile("# [error] - SppClose - Satus Fail ");
	}
	iLogFile("# GenStackInterface :: SppClose - [leave] ");			
	
	return retVal;
}


VOID iLogFile(char* msg)
{
#ifdef GSI_DEBUG_ENABLE

	FILE *fp = NULL;
	int i = 0,msgLen = 0;
	
	fp = _wfopen(L"packets.txt",L"a+");	
	msgLen = strlen(msg);	
	for(i=0;i<msgLen;++i)
	{
		fwprintf(fp, L"%c",msg[i]);
	}
	fwprintf(fp,L"\n");	
	fclose(fp);	
#endif
}
