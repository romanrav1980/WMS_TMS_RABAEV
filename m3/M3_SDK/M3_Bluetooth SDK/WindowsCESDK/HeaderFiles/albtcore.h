/****************************************************************************
* FILE NAME	:	albtcore.h									 				*
*																 		    *
* MODULE	:	aveLink BT SDK For Windows CE 								*
*																 		    *
* PURPOSE	:	The header file containing common and exported structures in*
*				core stack implementation	(For use with applications)		*
*				(c) Atinav Inc 2003								 		    *
****************************************************************************/
#ifndef _ALBTCORE_H
#define _ALBTCORE_H


#ifndef _ALBTTYPES_H
#include "albttypes.h"
#define _ALBTTYPES_H
#endif

#ifdef __cplusplus
extern "C" {
#endif


typedef UINT8 BD_ADDRESS[6];
typedef UINT8 DEVICE_NAME[249];
typedef UINT8 SERVICE_NAME[200];
typedef UINT8 PSM[2];
typedef UINT8 LINK_KEY[16];
typedef UINT8 IAC_LAP[3];
typedef INT8 PROFILE_CONTEXT[256];

typedef struct _BT_DEVICE /* BT Device structure */	
{
    BD_ADDRESS  bdAddress;				//Address of the devcie
    UINT8		pageScanRepetitionMode; //Page scan repetetion mode
    UINT8		pageScanPeriodMode;		//Page scan period mode
    UINT8		pageScanMode;			//Page scan mode
	UINT16		serviceClass;			//Service class field
	UINT8		majorDeviceClass;		//Device class(Major) feild
	UINT8		minorDeviceClass;		//Device class(Minor) feild
    UINT8		clockOffset[2];			//Clock offset
}BT_DEVICE, *PBT_DEVICE;

typedef struct _LMP_VERSION_INFO /* LMP version info */
{
	UINT8		hciVer;		  //HCI version
    UINT16		hciRev;		  //HCI revesion
    UINT8		lmpVer;		  //LMP version
    UINT16		manufacturer; //Manufacturer info
    UINT16		lmpSubVer;    //LMP sub version
}LMP_VERSION_INFO, *PLMP_VERSION_INFO;



typedef struct _LMP_SUPPORTED_FEATURES /* LMP supported features */
{
	UINT8 pkt3Slot:1;     	// 3-slot packets
	UINT8 pkt5Slot:1;     	// 5-slot packets
	UINT8 encryption:1;    	// encryption
	UINT8 slotOffset:1;    	// slot offset
	UINT8 timingAccuracy:1;	// timing accuracy
	UINT8 roleSwitch:1;    	// switch
	UINT8 holdMode:1;      	// hold mode
	UINT8 sniffMode:1;     	// sniff mode

	UINT8 parkMode:1;      	// park mode
	UINT8 rssi:1;          	// RSSI
	UINT8 dataRate:1;      	// channel quality driven data rate
	UINT8 scoLink:1;       	// SCO link
	UINT8 pktHV2:1;     	// HV2 packets
	UINT8 pktHV3:1;     	// HV3 packets
	UINT8 u_law:1;         	// u-law log
	UINT8 a_law:1;         	// A-law log

	UINT8 cvsd:1;          	// cvsd
	UINT8 paging:1;        	// paging scheme
	UINT8 power:1;         	// power control
	UINT8 transparentSCO:1;	// transparent SCO data
	UINT8 fcLag0:1;        	// Flow control lag (bit0)
	UINT8 fcLag1:1;        	// Flow control lag (bit1)
	UINT8 fcLag2:1;	      	// Flow control lag (bit2)
	UINT8 :1;
} LMP_SUPPORTED_FEATURES, *PLMP_SUPPORTED_FEATURES;

typedef struct _BT_VOICE_SETTING /* Voice setting for all SCO connections */
{
	UINT16	inputCoding;		// Input coding format
	UINT16	inputData;			// Input data format
	UINT16	inputSampleSize;	// Input sample size
	UINT8	pcmBitPos;			// Linear PCM Bit Position
	UINT16	airCoding;			// Air coding format
} BT_VOICE_SETTING, *PBT_VOICE_SETTING;

typedef struct _BT_SERVICE /* BT Service structure */
{
	UINT8		protocolDescriptor; //Protocol descriptor specifying the protocol
	UINT8		profileDescriptor; //Profile descriptor specifying the profile over which the service is registerd
	UINT16		identifier;			//Protocol specific identifier[OUT]
	UINT8		serviceName[255];	//Service name ,if a name was registered
}BT_SERVICE, *PBT_SERVICE;


typedef struct _BT_CONNECTION /* Information on an active connection */
{
	BT_DEVICE    btDevice;	//Device information
	BT_SERVICE	 btService; //Service information
	DEVICE_NAME  name;      //Device name
	UINT8		 initiator; //Initiator of the connection
	PROFILE_CONTEXT	profileContext; // profile specific additional information if there is any
}BT_CONNECTION, *PBT_CONNECTION;

typedef struct _BT_QOS /* The structure that stores all the QOS parameters of an L2CAP channel */
{
	UINT8 code;			// configuration option type ; 0x03 for qos
	UINT8 length;       // length of the rest of the struct; value is 22
	UINT8 flags;        // reserved for future use and must be set to 0
	UINT8 serviceType;	// level of service required.
	UINT8 tokenRate[4]; // rate at which traffic credits are granted
						// in bytes per second.
	UINT8 bucketSize[4]; // size of the token bucket in bytes.
	UINT8 bandWidth[4]; // rate of data transfer in bytes per second
	UINT8 latency[4];   // maximum acceptable delay between 
						// transmission of a bit by the sender
						// and its initial transmission over the air,
						// expressed in microseconds.
	UINT8 delay[4];     // difference, in microseconds, between 
						// the maximum and minimum possible delay 
						// that a packet will experience.
}BT_QOS, *PBT_QOS;

typedef struct _BT_UUID /* SDP UUID */
{
	UINT8 uuid[16];	//UUID bytes
	UINT8 length;   //length of UUID
}BT_UUID, *PBT_UUID;

typedef struct BT_ATTRIBUTE_ID /* SDP ATTRIBUTE ID */
{
	UINT32	attributeID;	//Attribute ID
	BOOLEAN	range;			//Range	
}BT_ATTRIBUTE_ID, *PBT_ATTRIBUTE_ID;


typedef struct _BT_COMM_PARAMS /* RFCOMM RPN PARAMETERS */
{ 
	UINT8			baudRate;	 //Baudrate
	UINT8			dataBits:2;  //Data bits
	UINT8			stopBit:1;   //Stope bits
	UINT8			parityBit:1; //Parity bit	
	UINT8			parityType:2;//Parity type 
	UINT8			res1:2;		 //Reserved
	UINT8			flowCtrl:6;	 //Flowcontrol type
	UINT8			res2:2;		 //reserved
	UINT8			xon;		 //XON character
	UINT8			xoff;		 //XOFF character	
}BT_COMM_PARAMS, *PBT_COMM_PARAMS;


typedef struct _BT_COMM_STATUS /* SPP COMM STATUS */
{
	UINT8		flags;		  //flag consisting of communication status
    UINT32		inQueueSize;  //No:of bytes in the receive queue
    UINT32		outQueueSize; //No of bytes in the transmit queue*/
}BT_COMM_STATUS,*PBT_COMM_STATUS;

typedef struct _BT_SECURITY_ATTRIBUTE /* structure for Service level Security information */
{  
	UINT8   authenticate: 1;		//enable /disable authentication
	UINT8   authorize: 1;			//enable /disable Authorization
	UINT8   encrypt: 1;				//enable /disable Encryption
	UINT8   incomingConnection: 1;  //incoming/outgoing connection
	UINT8   allowConnectionless: 1; // Enable / disable connection less security 
	UINT8   broadcast: 1;			// broadcast allowed or not
	UINT8   reserved: 2;			// reserved	
} BT_SECURITY_ATTRIBUTE, *PBT_SECURITY_ATTRIBUTE;
typedef struct _BT_RFC
{
	UINT8 	 Mode;
	UINT8 	 length;
	UINT8 	 TxWindowsize;
	UINT8 	 MaxTransmit;
	UINT16	 RetransmissionTimeout;
	UINT16   MonitorTimeout;
	UINT16 	 MaximumPDUSize; 
}BT_RFC,*PBT_RFC;

typedef struct _L2CAPW_CONFIG 
{ 
	UINT8			configFlag;
   	UINT16			mtu;	            // Maximum transmission unit
	UINT16			flushTimeout;       // flush timeout
	PBT_QOS			qos; 	            // qos options that are to be negotiated
	PBT_RFC			rfc; 	            // rfc options for flow control & RT		
 
}L2CAPW_CONFIG, *PL2CAPW_CONFIG;

typedef struct _BT_REGISTERSERVICE_INFO /*Structure  which returns Service and Record Handles(used in Profiles for Service Registeration)*/
{

	HANDLE  serviceHandle;         // handle to the Service record created.
	UINT32  recordHandle;         // handle to the Service record added in the SDP Database.

}BT_REGISTERSERVICE_INFO,*PBT_REGISTERSERVICE_INFO;

typedef VOID SPP_EventInd(HANDLE sppHandle,UINT32 event);			//SPP notification prototype
typedef VOID InquiryNotifyProc(PBT_DEVICE btDevice, UINT8 responseType);    			//Inquiry notification prototype
typedef VOID SecurityNotifyProc(UINT8 type, BT_DEVICE btDevice, PBT_SERVICE service);   //Security notification prototype
typedef VOID ActiveConnectionNotifyProc(UINT8 code, PBT_CONNECTION connection);         //Active Connection notification prototype
typedef VOID ResetNotifyProc();//Reset Notification Prototype
typedef VOID SCO_ConnectionNotifyProc(BD_ADDRESS bdAddress, 
									  UINT8 connIdentifier, UINT8 status);//SCO connection notification proc
typedef VOID SCO_DisconnectionNotifyProc(UINT8 connIdentifier, UINT8 status);//SCO disconnection notify proc


/*Debug Constants*/

// Level values 


#define BT_DBG_ERROR		   0x0100000000				
#define BT_DBG_WARNING		   0x0200000000	
#define BT_DBG_NONE			   0x0000000000
#define BT_DBG_ALL			   0xFFFFFFFFFF
#define BT_DBG_IN_FLOW		   0x0311111111
#define BT_DBG_OUT_FLOW		   0x0322222222
#define BT_DBG_PKT1			   0x0344444444
#define BT_DBG_PKT2			   0x0388888888	


#define HCI_DBG_IN_FLOW		   0x0000000001	
#define HCI_DBG_OUT_FLOW	   0x0000000002	
#define HCI_DBG_PKT1		   0x0000000004	
#define HCI_DBG_PKT2		   0x0000000008	


#define L2C_DBG_IN_FLOW		   0x0000000010	
#define L2C_DBG_OUT_FLOW	   0x0000000020	
#define L2C_DBG_PKT1		   0x0000000040	
#define L2C_DBG_PKT2		   0x0000000080	

#define SDP_DBG_IN_FLOW		   0x0000000100	
#define SDP_DBG_OUT_FLOW	   0x0000000200	
#define SDP_DBG_PKT1		   0x0000000400
#define SDP_DBG_PKT2		   0x0000000800


#define RFC_DBG_IN_FLOW		   0x0000001000	
#define RFC_DBG_OUT_FLOW	   0x0000002000	
#define RFC_DBG_PKT1		   0x0000004000
#define RFC_DBG_PKT2		   0x0000008000	


#define TCS_DBG_IN_FLOW		   0x0000010000	
#define TCS_DBG_OUT_FLOW	   0x0000020000	
#define TCS_DBG_PKT1		   0x0000040000
#define TCS_DBG_PKT2		   0x0000080000	


#define GEN_DBG_IN_FLOW		   0x0000100000	
#define GEN_DBG_OUT_FLOW	   0x0000200000	
#define GEN_DBG_PKT1		   0x0000400000
#define GEN_DBG_PKT2		   0x0000800000


							   
#define TL_DBG_IN_FLOW		   0x0001000000	
#define TL_DBG_OUT_FLOW	   	   0x0002000000	
#define TL_DBG_PKT1		   	   0x0004000000
#define TL_DBG_PKT2			   0x0008000000


#define SEC_DBG_IN_FLOW		   0x0010000000	
#define SEC_DBG_OUT_FLOW	   0x0020000000		
#define SEC_DBG_PKT1		   0x0040000000	
#define SEC_DBG_PKT2		   0x0080000000	


// Debug Target values
#define BT_TARGET_CONSOLE		0x01
#define BT_TARGET_FILE			0x02


/* SDAP Data types */
#define SDP_NULL		0x00
#define SDP_UINT1		0x01
#define SDP_UINT2		0x02
#define SDP_UINT4		0x03
#define SDP_UINT8		0x04
#define SDP_UINT16		0x05
#define SDP_INT1		0x06
#define SDP_INT2		0x07
#define SDP_INT4		0x08
#define SDP_INT8		0x09
#define SDP_INT16		0x0A
#define SDP_UUID		0x0B
#define SDP_STRING		0x0C
#define SDP_BOOL		0x0D
#define SDP_DES			0x0E
#define SDP_DEA			0x0F
#define SDP_URL			0x10

/*Protocol specifiers*/
#define	HCI			0x01
#define	L2CAP		0x02
#define	SDP			0x03
#define	RFCOMM		0x04
#define	TCS			0x05
#define	SPP			0x06
#define	OBEX		0x07
#define FTP			0x08
#define OPP			0x09
#define LAP			0x10
#define DUN			0x11
#define HS			0x12
#define AVDTP		0x13 
#define A2DP		0x14  

#define	UNSPECIFIED	0x20 


/*Constants related with GAP*/

/*Discoverable modes*/
#define BT_NON_DISCOVERABLE     0x00
#define BT_LIAC                 0x9E8B00
#define BT_GIAC                 0x9E8B33

/* Service class Flags */
#define	BT_SC_UNSPECIFIED					0x0000
#define	BT_SC_LIMITED_DISCOVERABLE_MODE		0x0001
#define	BT_SC_NETWORKING					0x0010
#define	BT_SC_RENDERING						0x0020
#define	BT_SC_CAPTURING						0x0040
#define	BT_SC_OBJECT_TRANSFER				0x0080
#define	BT_SC_AUDIO							0x0100
#define	BT_SC_TELEPHONY						0x0200
#define	BT_SC_INFORMATION					0x0400

/* Major device class values */
#define	BT_MAJOR_MISC						0x00
#define	BT_MAJOR_COMPUTER					0x01
#define	BT_MAJOR_PHONE						0x02
#define	BT_MAJOR_LAP						0x03
#define	BT_MAJOR_AUDIO						0x04
#define	BT_MAJOR_PERIPHERAL					0x05

/* Minor device class values */
/* Computer Major Class */
#define	BT_MINOR_UNCLASSIFIED				0x00
#define	BT_MINOR_DESKTOP					0x01
#define	BT_MINOR_SERVER						0x02
#define	BT_MINOR_LAPTOP						0x03
#define	BT_MINOR_HANDHELD					0x04
#define	BT_MINOR_PALM						0x05

/* Phone Major Class */
#define	BT_MINOR_UNCLASSIFIED				0x00
#define	BT_MINOR_CELLULAR					0x01
#define	BT_MINOR_CORDLESS					0x02
#define	BT_MINOR_SMARTPHONE					0x03
#define	BT_MINOR_WIREDMODEM					0x04
#define	BT_MINOR_PALM						0x05

/* LAN Access Point Major Class */
#define	BT_MINOR_FULLY_AVAILABLE			0x00
#define	BT_MINOR_17							0x08
#define	BT_MINOR_33							0x10
#define	BT_MINOR_50							0x18
#define	BT_MINOR_67							0x20
#define	BT_MINOR_83							0x28
#define	BT_MINOR_99							0x30
#define	BT_MINOR_NO_SERVICE					0x38

/* Audio Major Class */
#define	BT_MINOR_UNCLASSIFIED				0x00
#define	BT_MINOR_HS_PROFILE					0x01

/*Events for SPP/L2CAP Wrapper*/
#define	EVENT_RECEIVED		0x00001 
#define	EVENT_TRANSMIT		0x00002
#define	EVENT_COMMEVENT		0x00004
#define	EVENT_DISCONNECT	0x01000
#define EVENT_QOS_VIOLATION 0x02000

#define EVENT_COM_OPENED	0x0020000
#define	EVENT_COM_CLOSED	0x0040000

/*Security manager constants*/
#define AUTHENTICATE		0x01
#define AUTHORIZE			0x02
#define PAIRING_SUCCESS		0x03
#define PAIRING_FAILED      0x04

/*Loopback mode Constants*/
#define LPM_DISABLED			0x00
#define LPM_LOCAL				0x01
#define LPM_REMOTE				0x02


/*Role constants*/
#define ROLE_MASTER				0x00
#define ROLE_SLAVE				0x01

/*Encryption constants*/
#define ENCRYPTION_DISABLED			0x00
#define ENCRYPTION_POINT2POINT		0x01
#define ENCRYPTION_BOTH				0x02

/* constants*/
#define PSRM_R0						0x00
#define PSRM_R1						0x01
#define PSRM_R2						0x02

/* constants*/
#define PSPM_P0						0x00
#define PSPM_P1						0x01
#define PSPM_P2						0x02	

/* constants*/
#define PSM_MANDATORY				0x00
#define PSM_OPTIONAL_I				0x01
#define PSM_OPTIONAL_II				0x02
#define PSM_OPTIONAL_III			0x03

/* constants*/
#define LPS_DISABLE_ALL				0x0000 //Disable All LM Modes Default.
#define LPS_MS_SWITCH				0x0001 //Enable Master Slave Switch.
#define LPS_HM						0x0002 //Enable Hold Mode.
#define LPS_SM						0x0004 //Enable Sniff Mode.
#define LPS_PM						0x0008 //Enable Park Mode.00 

// Service type for QoS
/* constants*/
#define ST_NO_TRAFFIC				0x00	// No traffic
#define	ST_BEST_EFFORT				0x01	// Best effort	
#define ST_GUARANTEED				0x02	// Guaranteed

// Trnasport layer constants
#define TL_H2		0x02
#define TL_H3		0x03
#define TL_H4		0x04
#define TL_BCSP		0x05

//Flush timeout constants
#define FLUSHTO_DEFAULT			0x0000;
#define FLUSHTO_NO_RETRANS      0x0001;
#define FLUSHTO_RETRANS			0xFFFF;

//Info type constants
#define INFO_TYPE_CLMTU			0x0001
#define INFO_TYPE_SUCCESS		0x0000	
#define INFO_TYPE_NOT_SUPPORTED 0x0001
#define INFO_TYPE_REJECTED		0x0002
#define INFO_TYPE_TIMEOUT		0x0003

// Inquiry response type values
#define BT_IRT_INQUIRY_RESULT			0x01
#define BT_IRT_INQUIRY_COMPLETED		0x02



// Voice setting

// Input coding format
#define VS_IC_LINEAR			0x000 //Input coding : linear
#define VS_IC_MLOW				0x100 //Input coding : µ-law
#define VS_IC_ALOW				0x200 //Input coding : A-law

//Input data format
#define VS_ID_1COMPLEMENT		0x000 //Input data format : 1's complement
#define VS_ID_2COMPLEMENT		0x040 //Input data format : 2 's complement
#define VS_ID_SIGN_MAGNITUDE	0x080 //Input data format : Sign magnitude

// Input sample size
#define VS_IS_8					0x000 //Input sample size : 8bit (only  for Linear PCM)
#define VS_IS_16				0x020 //Input sample size : 16bit (only  for Linear PCM)

//To do	
// Air coding format
#define VS_AC_CVSD				0x000 //Air coding format : CVSD
#define VS_AC_MLOW				0x001 //Air coding format : µ-law
#define VS_AC_ALOW				0x002 //Air coding format : A-law

#define HMA_CURRENT_STATE		0x00 //Maintain current power level.
#define HMA_PAGE_SCAN			0x01 //Suspend page scan.
#define HMA_INQUIRY_SCAN		0x02 //Suspend Inquiry scan.
#define HMA_PERIODIC_INQUIRY	0x04 //Suspend periodic inquiries.

// Page scan mode
#define PSM_MANDATORY			0x00 //Mandatory Page Scan Mode.
#define PSM_OPTIONAL_I			0x01 //Optional page scan mode I
#define PSM_OPTIONAL_II			0x02 //Optional page scan mode II
#define PSM_OPTIONAL_III 		0x03 //Optional page scan mode III

// Encryption mode
#define ENCRYPTION_DISABLED		0x00 //	Encryption disabled
#define ENCRYPTION_POINT2POINT	0x01 //Encryption only for Point-to-Point packets
#define ENCRYPTION_BOTH			0x02 //Encryption for both Point-to-Point and Broadcast packets

// Country code
#define CC_NA					0x00 //North america, Japan and countries in Europe other  than France.
#define CC_FR					0x01 //France

// Master link key values
#define MLK_SEMI_PERMANENT 		0x00 //	Use semi-permanent link keys.
#define MLK_TEMPORARY			0x01 //Use temporary link key of the master.

// Transmit power level types
#define TPL_CURRENT				0x00 //Current Transmit Power Level.
#define TPL_MAXIMUM				0x01 //Maximum Transmit Power Level


// Packet types
// ACL packet type
#define PT_DM1					0x0008
#define PT_DH1					0x0010
#define PT_DM3					0x0400
#define PT_DH3					0x0800
#define PT_DM5					0x4000
#define PT_DH5					0x8000

// SCO packet type
#define PT_HV1					0x0020 
#define PT_HV2					0x0040
#define PT_HV3					0x0080

// Manufacturer of Bluetooth hardware
#define MFG_ERICSSON_MOBILE_COMMUNICATIONS	0x0000
#define MFG_NOKIA_MOBILE_PHONES 			0x0001
#define MFG_INTEL_CORP 						0x0002
#define MFG_IBM_CORP 						0x0003
#define MFG_TOSHIBA_CORP 					0x0004
#define MFG_3COM							0x0005
#define MFG_MICROSOFT 						0x0006
#define MFG_LUCENT 							0x0007
#define MFG_MOTOROLA 						0x0008
#define MFG_INFINEON_TECHNOLOGIES_AG 		0x0009
#define MFG_CAMBRIDGE_SILICON_RADIO 		0x000A
#define MFG_SILICON_WAVE 					0x000B
#define MFG_DIGIANSWER 						0x000C

// HCI Version
#define HCI_VERSION_1_0			0x01
#define HCI_VERSION_1_1         0x01

// The Link Manger Version Parameter
#define LMP_VERSION_1_0         0x00
#define LMP_VERSION_1_1         0x00

// Default connectable mode and discoverable mode.
#define BT_DEFAULT_DISCOVERABLE_MODE		FALSE
#define BT_DEFAULT_CONNECTABLE_MODE			FALSE

//Constants for Active connections type
#define BT_CONNECTION_ARRIVAL		 1
#define BT_CONNECTION_REMOVAL		 2


//Exported functions

//GENERAL
BOOLEAN BT_SetTransportLayer(UINT8 transport);
BOOLEAN BT_SetUARTDefaultPortParams(INT8 portname[], UINT32 baud);
BOOLEAN BT_SetBCSPDefaultPortParams(INT8 portname[], UINT32 baud);
BOOLEAN BT_DeInit();
BOOLEAN BT_Init();
BOOLEAN BT_SetResetNotifyProc(ResetNotifyProc *proc);
UINT32  BT_GetErrorCode();
VOID    BT_SetDebugLevel(INT64 debugLevel);
VOID    BT_SetDebugTarget(UINT8 target);


//Active Connection Management
BOOLEAN BT_GetActiveConnections(BT_CONNECTION connections[], INT32 count, PINT32 retCount);
BOOLEAN BT_SetActiveConnectionNotifyProc(ActiveConnectionNotifyProc *proc);

//GAP

BOOLEAN GAP_ClearAllEventFilters();
BOOLEAN GAP_SetCODFilterForConnSetup(UINT16 serviceClass, UINT8 majorDevClass, 
									 UINT8 minorDevClass);
BOOLEAN GAP_SetCODFilterForInquiryResult(UINT16 serviceClass, 
										 UINT8 majorDevClass, 
										 UINT8 minorDevClass);
BOOLEAN GAP_SetConnectableMode(BOOLEAN connectableMode);
BOOLEAN GAP_SetDeviceFilterForConnSetup(BD_ADDRESS bdAddress);
BOOLEAN GAP_SetDeviceFilterForInquiryResult(BD_ADDRESS bdAddress);

BOOLEAN GAP_SetDiscoverableMode(BOOLEAN discoverableMode, 
										  UINT32 iacLap[], INT8 count);
BOOLEAN GAP_SetEncryptionMode(UINT8 mode);
BOOLEAN GAP_SetInquiryScanActivity(UINT16 inqScanInterval, 
								   UINT16 inqScanWindow);					   
BOOLEAN GAP_SetLocalClassOfDevice(UINT16 serviceClass, UINT8 majorDevClass, 
								  UINT8 minorDevClass);
BOOLEAN GAP_SetLocalDeviceName(DEVICE_NAME name);

BOOLEAN GAP_SetPageScanActivity(UINT16 pageScanInterval, UINT16 pageScanWindow);
BOOLEAN GAP_SetPageScanMode(UINT8 psm);
BOOLEAN GAP_SetPageScanPeriodMode(UINT8 pspm);
BOOLEAN GAP_SetPageTimeout(UINT16 timeout);
BOOLEAN GAP_SetPairingMode(BOOLEAN enable);
BOOLEAN GAP_SetPinType(BOOLEAN variablePin);
BOOLEAN GAP_RemovePairedDevice(BD_ADDRESS bdAddress);

// Functions for retreiving Host Controller parameters
BOOLEAN GAP_GetConnectableMode(PBOOLEAN connectableMode);
BOOLEAN GAP_GetCountryCode(PUINT8 countryCode);
BOOLEAN GAP_GetDiscoverableMode(PBOOLEAN discoverableMode, 
										  UINT32 iacLap[], UINT8 count, 
										  PUINT8 retCount);
BOOLEAN GAP_GetEncryptionMode(PUINT8 mode);

BOOLEAN GAP_GetInquiryScanActivity(PUINT16 inqScanInterval, 
    							   PUINT16 inqScanWindow);
BOOLEAN GAP_GetLocalClassOfDevice(PUINT16 serviceClass, PUINT8 majorDevClass, 
								  PUINT8 minorDevClass);
BOOLEAN GAP_GetLocalDeviceAddress(BD_ADDRESS bdAddress);
BOOLEAN GAP_GetLocalDeviceName(DEVICE_NAME name);
BOOLEAN GAP_GetLocalSupportedFeatures(PLMP_SUPPORTED_FEATURES lmpFeatures);
BOOLEAN GAP_GetLocalVersionInformation(PLMP_VERSION_INFO versionInfo);

BOOLEAN GAP_GetNumberOfCurrentIAC(PUINT8 numStoredIAC);
BOOLEAN GAP_GetNumberOfSupportedIAC(PUINT8 numSupportedIAC);
BOOLEAN GAP_GetPageScanActivity(PUINT16 pageScanInterval, 
								PUINT16 pageScanWindow);
BOOLEAN GAP_GetPageScanMode(PUINT8 psm);
BOOLEAN GAP_GetPageScanPeriodMode(PUINT8 pspm);
BOOLEAN GAP_GetPageTimeout(PUINT16 timeout);
BOOLEAN GAP_GetPairingMode(PBOOLEAN enable);
BOOLEAN GAP_GetPinType(PBOOLEAN variablePin);

// Inquiry procedures
BOOLEAN GAP_CancelInquiry();
BOOLEAN GAP_CancelPeriodicInquiry();
BOOLEAN GAP_InquireAndRetrieveDevices(UINT32 accessCode, UINT8 duration, 
									 BT_DEVICE devices[], UINT8 size, PUINT8 retCount);
BOOLEAN GAP_StartInquiry(UINT32 accessCode, UINT8 duration, 
						 UINT8 nbrOfResponse, InquiryNotifyProc *proc);

BOOLEAN GAP_StartPeriodicInquiry(UINT32 accessCode, UINT16 minTime, 
									 UINT16 maxTime, UINT8 duration, 
									 UINT8 nbrOfResponse, 
									 InquiryNotifyProc *proc);
									 
// Functions for retrieving remote device Parameters
BOOLEAN GAP_GetRemoteDeviceName(PBT_DEVICE btDevice, DEVICE_NAME name);
BOOLEAN GAP_GetRemoteSupportedFeatures(BD_ADDRESS bdAddress, 
									   PLMP_SUPPORTED_FEATURES lmpFeatures);
BOOLEAN GAP_GetRemoteVersionInformation(BD_ADDRESS bdAddress, 
										PLMP_VERSION_INFO versionInfo);
										
// Security management functions
BOOLEAN GAP_AcceptAuthorizeReq(BD_ADDRESS bdAddress, PBT_SERVICE btService);
BOOLEAN GAP_AcceptPasskeyReq(BD_ADDRESS bdAddress, UINT8 passkey[], INT8 length, 
     						 BOOLEAN addToList);
BOOLEAN GAP_AuthenticateConnection(BD_ADDRESS bdAddress);
BOOLEAN GAP_ChangeConnectionLinkKey(BD_ADDRESS bdAddress);
BOOLEAN GAP_DeleteAllStoredLinkKeys(PUINT16 numKeysDeleted);
BOOLEAN GAP_DeleteStoredLinkKey(BD_ADDRESS bdAddress);

BOOLEAN GAP_GetStoredLinkKeys(BD_ADDRESS bdAddress[], LINK_KEY linkKey[], 
							  UINT16 count, PUINT16 retCount);

BOOLEAN GAP_GetStoredLinkKeysCount(PUINT16 count);
BOOLEAN GAP_IsAuthenticated(BD_ADDRESS bdAddress);
BOOLEAN GAP_IsEncrypted(BD_ADDRESS bdAddress);
BOOLEAN GAP_MasterLinkKey(UINT8 keyFlag);
BOOLEAN GAP_PrePairDevice(PBT_DEVICE btDevice);
BOOLEAN GAP_RejectAuthorizeReq(BD_ADDRESS bdAddress, PBT_SERVICE btService);
BOOLEAN GAP_RejectPasskeyReq(BD_ADDRESS bdAddress);
BOOLEAN GAP_SetSecurityNotifyProc(SecurityNotifyProc *proc);
BOOLEAN GAP_WriteStoredLinkKeys(BD_ADDRESS bdAddress[], LINK_KEY linkKeys[], 
							   UINT8 numKeys, PUINT8 linkKeysWritten);
BOOLEAN GAP_SetConnectionEncryption ( BD_ADDRESS bdAddress,BOOLEAN  enable); 
BOOLEAN GAP_GetPairedDevices(BD_ADDRESS address[],UINT8  count,PUINT8 retrievdCount);
 
// Connection management functions
BOOLEAN GAP_GetLinkPolicySetting(BD_ADDRESS bdAddress, PUINT16 linkPolicy);
BOOLEAN GAP_GetLinkQuality(BD_ADDRESS bdAddress, PUINT8 linkQuality);
BOOLEAN GAP_GetLinkSupervisionTimeout(BD_ADDRESS bdAddress, PUINT16 timeout);
BOOLEAN GAP_GetRole(BD_ADDRESS bdAddress, PUINT8 role);
BOOLEAN GAP_GetRSSI(BD_ADDRESS bdAddress, PUINT8 rssi);

BOOLEAN GAP_GetTransmitPowerLevel(BD_ADDRESS bdAddress, UINT8 type, 
								  PINT8 powerLevel);
BOOLEAN GAP_SetLinkPolicySetting(BD_ADDRESS bdAddress, UINT16 linkPolicy);
BOOLEAN GAP_SetLinkSupervisionTimeout(BD_ADDRESS bdAddress, UINT16 timeout);

BOOLEAN GAP_SwitchRole(BD_ADDRESS bdAddress, UINT8 role);
//API's for SCO Manager
BOOLEAN SCO_SetConnectionNotifyProc(BD_ADDRESS bdAddress, 
										SCO_ConnectionNotifyProc appConnCallback);
BOOLEAN SCO_SetDisconnectionNotifyProc(UINT8 connIdentifier, 
										  SCO_DisconnectionNotifyProc appDiscCallback);
BOOLEAN SCO_Connect(BD_ADDRESS bdAddress, UINT16 packetType, 
								PUINT8 connIdentifier);
BOOLEAN SCO_Disconnect(UINT8 connIdentifier);
BOOLEAN SCO_GetConnectionHandle(BD_ADDRESS bdAddress, PUINT8 connIdentifier);
BOOLEAN SCO_Write(UINT8 connIdentifier, PUINT8 buffer, UINT8 numberOfBytesToWrite, 
				  PUINT8 numberOfBytesWritten);
BOOLEAN SCO_Read(UINT8 connIdentifier, PUINT8 buffer, UINT8 numberOfBytesToRead, 
				  PUINT8 numberOfBytesRead);
BOOLEAN SCO_ReadBufferSize(PUINT8 bufferSize);
BOOLEAN SCO_SetVoiceSetting(PBT_VOICE_SETTING voiceSetting);
BOOLEAN SCO_GetVoiceSetting(PBT_VOICE_SETTING voiceSetting);

//APIs for Connection Management 
HANDLE  SDAP_GetConnection(PBT_DEVICE btDevice);
BOOLEAN SDAP_CloseConnection(HANDLE handle);


//APIs to retrieve PSM & Serv. Channel 
UINT16 SDAP_GetPSMValue(); 
UINT8  SDAP_GetServerChannel();
 
//ResultSet accessor APIs
BOOLEAN SDAP_FirstAttribute(HANDLE handle);
BOOLEAN SDAP_NextAttribute(HANDLE handle);
BOOLEAN SDAP_PreviousAttribute(HANDLE handle);
BOOLEAN SDAP_GetAttributeID(HANDLE handle,PUINT16 attributeID);
BOOLEAN SDAP_GetAttributeType(HANDLE handle,PUINT16 attributeType);
BOOLEAN SDAP_GetIntegerAttribute(HANDLE handle,PINT32 intValue);
BOOLEAN SDAP_GetByteArrayAttribute(HANDLE handle, INT8 byteArray[]);
BOOLEAN SDAP_GetUUIDAttribute(HANDLE handle,PBT_UUID uuidValue);
BOOLEAN SDAP_GetStringLength(HANDLE handle, PUINT32 stringLength);
BOOLEAN SDAP_GetStringAttribute(HANDLE handle, INT8 stringValue[], UINT32 stringLength);
BOOLEAN SDAP_GetBooleanAttribute(HANDLE handle,PBOOLEAN boolValue);
BOOLEAN SDAP_GetDESAttribute(HANDLE handle,HANDLE* returnHandle);
BOOLEAN SDAP_GetDEAAttribute(HANDLE handle, HANDLE* returnHandle);
BOOLEAN SDAP_GetURLLength(HANDLE handle, PUINT32 urlLength);
BOOLEAN SDAP_GetURLAttribute(HANDLE handle, INT8 urlValue[], UINT32 urlLength);
BOOLEAN SDAP_GetAllAttributeIDs(HANDLE handle, UINT16 attributeIDs[], UINT16 size, PUINT16 retSize);
BOOLEAN SDAP_GetAttribute(HANDLE handle, UINT16 attributeID);
BOOLEAN SDAP_FreeResults(HANDLE handle);

//Service related information accessor APIs
BOOLEAN SDAP_GetServiceRecord(UINT32 recordHandle,HANDLE* result);
BOOLEAN SDAP_GetAllServices(HANDLE* results, UINT16 size, PUINT16 retSize);
BOOLEAN SDAP_GetNumOfServicesRegistered(PUINT16 retSize);
//Service Search Transaction APIs
BOOLEAN SDAP_ServiceSearchRequest(HANDLE handle,BT_UUID uuids[],UINT16 uuidCount,UINT32 recordHandles[],UINT16 maxServiceRecordCount, PUINT16 retSize );
BOOLEAN SDAP_ServiceAttributeRequest(HANDLE handle,UINT32 recordHandle, BT_ATTRIBUTE_ID attributes[],UINT16 attributeCount, HANDLE* result);
BOOLEAN SDAP_ServiceSearchAttributeRequest(HANDLE handle,BT_UUID uuids[],UINT16 uuidCount,BT_ATTRIBUTE_ID attributes[],UINT16 attributeCount,HANDLE result[],UINT16 size, PUINT16 retSize);

//DB manipulation APIs
BOOLEAN SDAP_AddToDB(HANDLE serviceHandle, PUINT32 recordHandle);
BOOLEAN SDAP_RemoveFromDB(UINT32 recordHandle);
BOOLEAN SDAP_CreateService(BT_UUID uuids[], UINT16 uuidCount, HANDLE* serviceHandle);
BOOLEAN SDAP_DeleteService(HANDLE serviceHandle);
BOOLEAN SDAP_MakeAttribute(UINT16 attributeType,PVOID attributeValue, HANDLE* attributeHandle);
BOOLEAN SDAP_MakeAttributeSequence(HANDLE handles[],UINT16 size, UINT16 attributeType, HANDLE* attributeSeqHandle);
BOOLEAN SDAP_AddAttribute(HANDLE serviceHandle, HANDLE attributeHandle, UINT16 attributeID);
BOOLEAN SDAP_ModifyAttribute(HANDLE serviceHandle, HANDLE attributeHandle, UINT16 attributeID);
BOOLEAN SDAP_DeleteAttribute(HANDLE serviceHandle, UINT16 attributeID);

//SPP API's
HANDLE SPP_Connect(PBT_DEVICE device, PBT_SERVICE service,PUINT16 frameSize, PBT_SECURITY_ATTRIBUTE secAttrib,PINT8 portName);
HANDLE SPP_Accept(PBT_DEVICE device, PBT_SERVICE service,PUINT16 frameSize, PBT_SECURITY_ATTRIBUTE secAttrib,PINT8 portName);
BOOLEAN SPP_SetEventNotifyProc(HANDLE sppHandle,SPP_EventInd* appCallback);
BOOLEAN SPP_Close(HANDLE handle);
BOOLEAN SPP_GetLocalServices(PBT_UUID uuid, BT_SERVICE services[], INT16 count, PINT16 numServices);
BOOLEAN SPP_GetRemoteServices(PBT_DEVICE device, PBT_UUID uuid,BT_SERVICE services[], INT16 count, PINT16 numServices);
BOOLEAN SPP_RegisterService(PBT_SERVICE service, PBT_UUID uuid, PBT_REGISTERSERVICE_INFO regInfo); 
BOOLEAN SPP_DeleteService( PBT_REGISTERSERVICE_INFO regInfo);
BOOLEAN SPP_CancelConnect(BD_ADDRESS bdAddress, UINT8 serverChannel);
BOOLEAN SPP_CancelAccept(BT_SERVICE service);

//Undocumented API's
BOOLEAN  SDAP_Cancel(BD_ADDRESS bdAddress);
void     BT_SetErrorCode(UINT32 error);
BOOLEAN  SDAP_Register(BT_UUID uuids[], UINT16  uuidCount, PBT_SERVICE service, HANDLE* serviceHandle);
BOOLEAN  SDAP_SearchLocalServices(BT_UUID uuids[], UINT16  uuidCount, BT_SERVICE services[], UINT16 size, PUINT16 retSize);
BOOLEAN  SDAP_SearchRemoteServices(HANDLE handle,BT_UUID uuids[], UINT16  uuidCount ,BT_SERVICE services[], UINT16 size, PUINT16 retSize);
BOOLEAN  BT_IsInitialized();
BOOLEAN  BT_Close();
BOOLEAN  BT_Open();



#ifdef __cplusplus
}
#endif 

#endif


