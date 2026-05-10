// GenStackInterface.h: interface for the GenStackInterface class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_GENSTACKINTERFACE_H__E9EEB4E0_BCF7_4A75_A7BB_16FC82434626__INCLUDED_)
#define AFX_GENSTACKINTERFACE_H__E9EEB4E0_BCF7_4A75_A7BB_16FC82434626__INCLUDED_


// If the target device is Mobile compia M3 device, define the following compiler 
// directive(M3_BUILTIN_BT) to set the specific Bluetooth parameters for the 
// built-in chip Bluetooth 

#define M3_BUILTIN_BT


#define BT_DEVICE_Name  "Atinav BlueCE-II" //Device name to set 

// The following two constants specifies the port in which the CF card is 
// listening and the baudrate of the CF card

// For getting the port, 
//	Plug in the CF card on to your windows ce device. 
//	Search all the subkeys of HKLM\Drivers\Active\. 
//	Select the "Name" field of the subkey with PnPId  of your Plugged CF card. 
//	(Usually it will be in the Last sub key of HKLM\Drivers\Active) 

// If you are using Builtin Bluetooth module,get the port and baudarate from
// vendor
 

#ifdef M3_BUILTIN_BT


//HCI port is COM7, baudrate : 921600, Transport : BCSP

// M3 Builtin Bluetooth HCI port
#define HCI_UART_Port	"COM7:"  // Port on which bluetooth card is listening


// M3 Builtin Bluetooth HCI port - baudrate

#define HCI_BAUDRATE	921600    // Baud rate of the bluetooth card


// This is the port emulated by atinav. Normally atinav sdk provides two emulated 
// port  in "COM"(If available). You can find the ports emulated  by atinav as follows,

//*** Select HKLM\Drivers\BuiltIn\AveBT1 or HKLM\Drivers\BuiltIn\AveBT2 registry keys
// The prefix and index values gives the emulated port.

// Emulated COM port by avelink Bluetooth SDK 
#define SPP_COM_Port	"COM6:"  //@@@@@@@  Modify 

// This is the transport used by your bluetooth module.
// If it is a BCSP card, set the value as TL_BCSP .
// If it is a UART card, set the value as TL_H4 .M3 module is BCSP.

#define BT_TRANSPORT TL_BCSP


#else

#define HCI_UART_Port	"COM0:"  // Port on which bluetooth card is listening


// For getting the baudrate, you should consult with card vendor.
// For brainboxes cards, the baudrate is 115200.

#define HCI_BAUDRATE	115200    // Baud rate of the bluetooth card


// This is the port emulated by atinav. Normally atinav sdk provides two emulated 
// port  in "COM"(If available). You can find the emulated by atinav as follows,

// Select HKLM\Drivers\BuiltIn\AveBT1 or HKLM\Drivers\BuiltIn\AveBT2 registry keys
// The prefix and index values gives the emulated port.

#define SPP_COM_Port	"COM6:"  // Emulated COM port by avelink Bluetooth SDK 

// This is the transport used by your bluetooth module.
// If it is a BCSP card, set the value as TL_BCSP .
// If it is a UART card, set the value as TL_H4 .

#define BT_TRANSPORT TL_BCSP // TL_H4


#endif // M3_BUILTIN_BT



// Uncomment the following line to enabling debug messages


//#define GSI_DEBUG_ENABLE

// End of Edit - Section
 


#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class GenStackInterface  
{
public:
	BOOLEAN GapSetLocalDeviceName(DEVICE_NAME name);
	BOOLEAN GapGetLocalDeviceAddress(BD_ADDRESS bdAddress);
	BOOLEAN SppClose(HANDLE handle);
	BOOLEAN BTCardDeInitialize();
	BOOLEAN SppRemoveServer(BT_SERVICE service);
//	BOOLEAN SppDeleteService(UINT32 recHndl);
	BOOLEAN SppDeleteService(PBT_REGISTERSERVICE_INFO serviceInfo);
//	BOOLEAN SppRegisterService(PBT_SERVICE service, PBT_UUID uuid, PUINT32 servRcdHandle);
	BOOLEAN SppRegisterService(PBT_SERVICE service, PBT_UUID uuid, PBT_REGISTERSERVICE_INFO serviceInfo);
	HANDLE  SppAccept(PBT_DEVICE device, PBT_SERVICE service,PUINT16 frameSize, PBT_SECURITY_ATTRIBUTE secAttrib,PINT8 portName);
	HANDLE  SppConnect(PBT_DEVICE device, PBT_SERVICE service,PUINT16 frameSize, PBT_SECURITY_ATTRIBUTE secAttrib,PINT8 portName);
	BOOLEAN SdapSearchRemoteServices(PBT_DEVICE device, BT_UUID sdpUuids[], UINT16  uuidCount, BT_SERVICE services[], UINT16 maxServicecount, PUINT16 numServices);
	BOOLEAN GapInquireAndRetrieveDevices(UINT32 accessCode, UINT8 duration, BT_DEVICE devices[], UINT8 size, PUINT8 retCount);
	BOOLEAN BTCardInitialize();
	GenStackInterface();
	virtual ~GenStackInterface();


};

	VOID iLogFile(char* msg);

#endif // !defined(AFX_GENSTACKINTERFACE_H__E9EEB4E0_BCF7_4A75_A7BB_16FC82434626__INCLUDED_)
