/****************************************************************************
* FILE NAME: albterrorcodes.h										 		*
*																 		    *
* MODULE	  : aveLink BT SDK For Windows CE								*
*																 		    *
* PURPOSE	: The header file containing all the error code constants used	*
*			  in the SDK			 								 		*
*																			*
****************************************************************************/
#ifndef _ALBTERRORCODES_H
#define _ALBTERRORCODES_H

/*
	A 32-bit integer is used to represent the error code. This 16 bit integer
contains different sub-fields which is explained in the below figure.

 ___________________________________________________________________________
|	version	 	  |		severity 	  |	 Layer	 	 	|					|
|_________________|____|____|____|____|_________________|___________________|
31			   		27 	 26   25   24 				  16				   0

The most significant four bits are kept for version information.

       The next four bits are used to indicate the severity of the error. 
Five different values are defined now. The 27th bit, which is the most 
significant of these four bits, is hence kept reserved and set to zero. 
The defined values for the severity field are those given below. 

       000 - Success
       001 - Informative
       002 - Warning - If the failure doesn’t prevent user from further 
			actions and can be  Ignored.
       003 - Error - If the failure cannot be ignored.
       004 - Fatal- If the failure requires the user to re initialize the 
			whole stack. 

       The next eight bits are used to specify the layer or area of the stack
that generated the error. The values defined currently for different sections
of the stack are those given below.

       0x01    - TRANSPORT
       0x02    - HCI
       0x03    - GAP
       0x04    - L2CAP
       0x05    - L2CAP WRAPPER
       0x06    - SDP
       0x07    - SDAP
       0x08    - RFCOMM
       0x09    - SPP
       0x0A    - TCS
       0x0B    - CTP
       0x0C    - SECURITY
       0x0D    - OAL
       0x0E    - SCO
       0x0F    - GENERAL
       0x10    - TLH4
       0x11    - TLH2
       0x12    - TLH3
       0x13    - BCSP

       0x20    - GOEP 
	   0x21    - OPP

	   0x22-0x25 - Reserved 

	   0x26    -  DUN
	   0x27    -  LAP
	   0x28	   -  HP
	   0x29-0x30 - Reserved.
	   0x31	   -  HIDP

	   0x32	   -  AVDTP
	   0x33	   -  GAVDP
       0x34	   -  A2DP
	   0x35	   -  Reserved

The next sixteen bits represent the error that occurred. 
 
*/

//
//Code Id  : BT_NO_ERROR
//Code Text: No error has occured
//
#define  BT_NO_ERROR					   	 0x0000000
//
//Code Id  : BT_INVALID_PARAMETER
//Code Text: A parameter that was passed to the API was invalid
//
#define  BT_INVALID_PARAMETER			   	 0x30F0001
//
//Code Id  : BT_INSUFFICIENT_RESOURCES
//Code Text: Insufficient system resources to complete the API
//
#define  BT_INSUFFICIENT_RESOURCES			 0x30F0002
//
//Code Id  : BT_INVALID_HANDLE
//Code Text: The handle that was passed to the API was invalid
//
#define  BT_INVALID_HANDLE					 0x30F0003
//
//Code Id  : BT_NOT_INITIALIZED
//Code Text: The bluetooth stack and hardware module has not been
//  initialised
//
#define  BT_NOT_INITIALIZED				     0x30F0004
//
//Code Id  : BT_REQUEST_CANCELED
//Code Text: The request has been canceled.
//
#define  BT_REQUEST_CANCELED				 0x30F0005
//
//Code Id  : BT_USER_DE_INITIALIZED
//Code Text: The user initiated deinitialisation.
//
#define  BT_USER_DE_INITIALIZED				 0x10F0006
//
//Code Id  : BT_NOT_OPENED
//Code Text: The bluetooth stack was not Opened for use
//
#define  BT_NOT_OPENED					     0x30F0007 
//
//Code Id  : BT_TRIAL_PERIOD_EXPIRED
//Code Text:  trial period expired 
//
#define  BT_TRIAL_PERIOD_EXPIRED			0x30F0008 
//
//Code Id  : BT_ALREADY_INITIALIZED
//Code Text: The bluetooth stack is already initialized
//
#define  BT_ALREADY_INITIALIZED						0x20F0009 
//
//Code Id  : BT_TRANSPORT_ALREADY_INITIALIZED
//Code Text: The transport layer already initialized.
//
#define  BT_TRANSPORT_ALREADY_INITIALIZED 	 0x2010001
//
//Code Id  : BT_TRANSPORT_NOT_INITIALIZED
//Code Text:Transport layer not initialized.
//
#define  BT_TRANSPORT_NOT_INITIALIZED	 0x3010007
//
//Code Id  : BT_TRANSPORT_H2_DEVICE_NOT_READY
//Code Text:Attept to retreive device information failed.
//
#define  BT_TRANSPORT_H2_DEVICE_NOT_READY	0x3110001
//
//Code Id : BT_TRANSPORT_H2_COMPONENT_MISSING
//Code Text :Component requiered for the usb transport missing
//

#define  BT_TRANSPORT_H2_COMPONENT_MISSING	0x3110002
//
//Code Id  : BT_TRANSPORT_H2_READ_FAILURE
//Code Text:Attempt to read from the device failed.
//
#define  BT_TRANSPORT_H2_READ_FAILURE				0x4110003
//
//Code Id  : BT_TRANSPORT_H2_INVALID_PACKET_ERROR
//Code Text:Invalid bluetooth packet.
//
#define  BT_TRANSPORT_H2_INVALID_PACKET_ERROR		0x4110004		
//
//Code Id  : BT_TRANSPORT_H2_WRITE_FAILED
//Code Text: Attempt to write to the device failed
//
#define  BT_TRANSPORT_H2_WRITE_FAILED				0x4110005


//Code Id  : BT_TRANSPORT_H4_BAD_PORT
//Code Text:Port with the specified name doesnot exist.
//
#define  BT_TRANSPORT_H4_BAD_PORT					0x3100001
//
//Code Id  : BT_TRANSPORT_H4_PORT_IN_USE
//Code Text:Specified port is currently in use.
//
#define  BT_TRANSPORT_H4_PORT_IN_USE 				0x3100002
//
//Code Id  : BT_TRANSPORT_H4_UNSUPPORTED_PARAMETERS
//Code Text:Specified parameters not supported by the transport layer.
//
#define  BT_TRANSPORT_H4_UNSUPPORTED_PARAMETERS		0x3100003
//
//Code Id  : BT_TRANSPORT_H4_PARAMETERS_ERROR
//Code Text: Invalid commaunication parameter(Port parameters)
//
#define  BT_TRANSPORT_H4_PARAMETERS_ERROR			0x3100005
//
//Code Id  : BT_TRANSPORT_H4_READ_FAILURE 
//Code Text: Attempt to read from the device failed.
//
#define  BT_TRANSPORT_H4_READ_FAILURE				0x4100006	   			
//
//Code Id  : BT_TRANSPORT_H4_INVALID_PACKET_ERROR
//Code Text: Invalid bluetooth packet.
//
#define  BT_TRANSPORT_H4_INVALID_PACKET_ERROR		0x4100007		
//
//Code Id  : BT_TRANSPORT_H4_WRITE_FAILED
//Code Text: Attempt to write to the device failed
//
#define  BT_TRANSPORT_H4_WRITE_FAILED				0x4100008
//
//Code Id  : BT_TRANSPORT_BCSP_BAD_PORT
//Code Text:Port with the specified name does not exist.
//
#define  BT_TRANSPORT_BCSP_BAD_PORT					0x3130001 
//
//Code Id  : BT_TRANSPORT_BCSP_PORT_IN_USE
//Code Text:Specified port is currently in use.
//
#define  BT_TRANSPORT_BCSP_PORT_IN_USE 				0x3130002 
//
//Code Id  : BT_TRANSPORT_BCSP_UNSUPPORTED_PARAMETERS
//Code Text:Specified parameters not supported by the transport layer.
//
#define  BT_TRANSPORT_BCSP_UNSUPPORTED_PARAMETERS	0x3130003 
//
//Code Id  : BT_TRANSPORT_BCSP_LINK_SETUP_FAILED
//Code Text: BCSP link set up between host and host controller failed.
//
#define  BT_TRANSPORT_BCSP_LINK_SETUP_FAILED		0x3130005 
//
//Code Id  : BT_TRANSPORT_BCSP_READ_FAILURE 
//Code Text: Attempt to read from the device failed.
//
#define  BT_TRANSPORT_BCSP_READ_FAILURE				0x4130006	   			
//
//Code Id  : BT_TRANSPORT_BCSP_INVALID_PACKET_ERROR
//Code Text: Invalid bluetooth packet.
//
#define  BT_TRANSPORT_BCSP_INVALID_PACKET_ERROR		0x4130007		
//
//Code Id  : BT_TRANSPORT_BCSP_WRITE_FAILED
//Code Text: Attempt to write to the device failed
//
#define  BT_TRANSPORT_BCSP_WRITE_FAILED				0x4130008

//Error codes corresponding to that described in Spec 

//
//Code Id  : BT_HCI_UNKNOWN_COMMAND
//Code Text:Unknown hci command
//
#define  BT_HCI_UNKNOWN_COMMAND						0x3020001            
//
//Code Id  : BT_HCI_NO_EXISTING_CONNECTION
//Code Text:Host has issued a command which requires an
//existing connection and there is currently no connection 
//corresponding to the specified device Address.
//
#define  BT_HCI_NO_EXISTING_CONNECTION 				0x3020002            
//
//Code Id  : BT_HCI_HARDWARE_FAILURE
//Code Text:command can not be executed because of a hardware 
//failure.
//
#define  BT_HCI_HARDWARE_FAILURE					0x3020003            
//
//Code Id  : BT_HCI_PAGE_TIMEOUT
//Code Text:Page timeout occured during connection attempt.
//
#define  BT_HCI_PAGE_TIMEOUT						0x3020004            
//
//Code Id  : BT_HCI_AUTHENTICATION_FAILURE
//Code Text:pairing or authentication failed due to  incorrect 
//PIN code or link key.
//
#define  BT_HCI_AUTHENTICATION_FAILURE				0x3020005            
//
//Code Id  : BT_HCI_KEY_MISSING
//Code Text: PIN code(s) missing.
//
#define  BT_HCI_KEY_MISSING							0x3020006            
//
//Code Id  : BT_HCI_MEMORY_FULL
//Code Text:Host Controller does not have memory capacity to 
//store additional parameters
//
#define  BT_HCI_MEMORY_FULL							0x3020007            
//
//Code Id  : BT_HCI_CONNECTION_TIMEOUT
//Code Text:Connection timeout.
//
#define  BT_HCI_CONNECTION_TIMEOUT					0x3020008            
//
//Code Id  : BT_HCI_MAX_NO_OF_CONNECTIONS
//Code Text:Maximum number of connections established.
//
#define  BT_HCI_MAX_NO_OF_CONNECTIONS				0x3020009            
//
//Code Id  : BT_HCI_MAX_NO_OF_SCO_CONNECTIONS
//Code Text:Maximum number of SCO connections established.
//
#define  BT_HCI_MAX_NO_OF_SCO_CONNECTIONS			0x302000A            
//
//Code Id  : BT_HCI_ACL_CONNECTION_ALREADY_EXISTS
//Code Text:An ACL connection to the device already exists.
//
#define  BT_HCI_ACL_CONNECTION_ALREADY_EXISTS		0x302000B
//
//Code Id  : BT_HCI_COMMAND_DISALLOWED
//Code Text:Command disallowed.
//
#define  BT_HCI_COMMAND_DISALLOWED					0x302000C
//
//Code Id  : BT_HCI_HOST_REJECTED_LIMITED_RESOURCES
//Code Text: Host rejected the incoming connection request due to 
//limited resources.
//
#define  BT_HCI_HOST_REJECTED_LIMITED_RESOURCES		0x302000D
//
//Code Id  : BT_HCI_HOST_REJECTED_SECURITY_REASONS
//Code Text:Host rejected the incoming connection request due to 
//security reasons.
//
#define  BT_HCI_HOST_REJECTED_SECURITY_REASONS		0x302000E
//
//Code Id  : BT_HCI_HOST_REJECTED_PERSONAL_DEVICE
//Code Text:Host Rejected the incoming connection request due to 
//remote device is only a personal device.
//
#define  BT_HCI_HOST_REJECTED_PERSONAL_DEVICE		0x302000F
//
//Code Id  : BT_HCI_HOST_TIMEOUT
//Code Text:Host timeout occured before responding to an incoming 
//connection request
//
#define  BT_HCI_HOST_TIMEOUT						0x3020010
//
//Code Id  : BT_HCI_UNSUPPORTED_FEATURE_OR_PARAMETER
//Code Text:One or more specified parameter(s) not supported by 
//the hardware
#define  BT_HCI_UNSUPPORTED_FEATURE_OR_PARAMETER	0x3020011
//
//Code Id  : BT_HCI_INVALID_COMMAND_PARAMETER
//Code Text:One or more specified parameter values not conform 
//to the bluetooth specification
//
#define  BT_HCI_INVALID_COMMAND_PARAMETER			0x3020012
//
//Code Id  : BT_HCI_OTHER_END_TERMINATED_USER_ENDED_CONNECTION
//Code Text: Connection terminated by user at the other end.
//
#define  BT_HCI_OTHER_END_TERMINATED_USER_ENDED_CONNECTION	 0x3020013
//
//Code Id  : BT_HCI_OTHER_END_TERMINATED_LOW_RESOURCES
//Code Text: Connection terminated by the other end due to low resources.
//
#define  BT_HCI_OTHER_END_TERMINATED_LOW_RESOURCES			 0x3020014
//
//Code Id  : BT_HCI_OTHER_END_TERMINATED_POWER_OFF
//Code Text: Other End Terminated Connection: About to Power Off.
//
#define  BT_HCI_OTHER_END_TERMINATED_POWER_OFF				 0x3020015
//
//Code Id  : BT_HCI_CONNECTION_TERMINATED_LOCAL_HOST
//Code Text: Connection terminated by the local host.
//
#define  BT_HCI_CONNECTION_TERMINATED_LOCAL_HOST			 0x3020016
//
//Code Id  : BT_HCI_REPEATED_ATTEMPTS
//Code Text: Device not allowed authentication\pairing because too 
//little time has elapsed since an unsuccessful authentication\pairing 
//attempt.
//
#define  BT_HCI_REPEATED_ATTEMPTS							 0x3020017
//
//Code Id  : BT_HCI_PAIRING_NOT_ALLOWED
//Code Text: Device not allowed pairing due to some reason.
//
#define  BT_HCI_PAIRING_NOT_ALLOWED					0x3020018    
//
//Code Id  : BT_HCI_UNKNOWN_LMP_PDU
//Code Text: Unknown LMP PDU.
//
#define  BT_HCI_UNKNOWN_LMP_PDU						0x3020019    
//
//Code Id  : BT_HCI_UNSUPPORTED_REMOTE_FEATURE
//Code Text: Remote device doesnot support the feature associated with 
//the issued command. 
//
#define  BT_HCI_UNSUPPORTED_REMOTE_FEATURE			0x302001A    
//
//Code Id  : BT_HCI_SCO_OFFSET_REJECTED
//Code Text: SCO offset rejected.
//
#define  BT_HCI_SCO_OFFSET_REJECTED					0x302001B    
//
//Code Id  : BT_HCI_SCO_INTERVAL_REJECTED
//Code Text: SCO interval rejected.
//
#define  BT_HCI_SCO_INTERVAL_REJECTED				0x302001C    
//
//Code Id  : BT_HCI_SCO_AIR_MODE_REJECTED
//Code Text: SCO air mode rejected.
//
#define  BT_HCI_SCO_AIR_MODE_REJECTED				0x302001D    
//
//Code Id  : BT_HCI_INVALID_LMP_PARAMETERS
//Code Text: Invalid LMP parameters.
//
#define  BT_HCI_INVALID_LMP_PARAMETERS				0x302001E    
//
//Code Id  : BT_HCI_UNSPECIFIED_ERROR
//Code Text: This error code is used when no other error code 
//is appropriate
//
#define  BT_HCI_UNSPECIFIED_ERROR					0x302001F    
//
//Code Id  : BT_HCI_UNSUPPORTED_LMP_PARAMETER
//Code Text: Unsupported LMP parameters.
//
#define  BT_HCI_UNSUPPORTED_LMP_PARAMETER			0x3020020    
//
//Code Id  : BT_HCI_ROLE_CHANGE_NOT_ALLOWED
//Code Text: Role change not allowed.
//
#define  BT_HCI_ROLE_CHANGE_NOT_ALLOWED				0x3020021    
//
//Code Id  : BT_HCI_LMP_RESPONSE_TIMEOUT
//Code Text: LMP response timeout.
//
#define  BT_HCI_LMP_RESPONSE_TIMEOUT				0x3020022    
//
//Code Id  : BT_HCI_LMP_ERROR_TRANSACTION_COLLISION
//Code Text: LMP error transaction collision
//
#define  BT_HCI_LMP_ERROR_TRANSACTION_COLLISION		0x3020023    
//
//Code Id  : BT_HCI_LMP_PDU_NOT_ALLOWED
//Code Text: LMP PDU not allowed.
//
#define  BT_HCI_LMP_PDU_NOT_ALLOWED					0x3020024    
//
//Code Id  : BT_HCI_ENCRYPTION_MODE_NOT_ACCEPTABLE
//Code Text: Couldnt negotiate for which encryption mode 
//to use.
//
#define  BT_HCI_ENCRYPTION_MODE_NOT_ACCEPTABLE		0x3020025    
//
//Code Id  : BT_HCI_UNIT_KEY_USED
//Code Text: Link key for the specified connection cannot be 
//changed since it is a UNIT key.
//
#define  BT_HCI_UNIT_KEY_USED						0x3020026    
//
//Code Id  : BT_HCI_QOS_NOT_SUPPORTED
//Code Text: Requested quality of service is not supported.
//
#define  BT_HCI_QOS_NOT_SUPPORTED					0x3020027    
//
//Code Id  : BT_HCI_INSTANT_PASSED
//Code Text: The instant at which the specifed operation shall done 
//is in the past.
//
#define  BT_HCI_INSTANT_PASSED						0x3020028    
//
//Code Id  : BT_HCI_PAIRING_WITH_UNIT_KEY_NOT_SUPPORTED
//Code Text: Pairing with unit key not supported.
//
#define  BT_HCI_PAIRING_WITH_UNIT_KEY_NOT_SUPPORTED	0x3020029
//
//Code Id  : BT_HCI_NOT_INITIALIZED
//Code Text: Hci not initialized.
//
#define  BT_HCI_NOT_INITIALIZED			 0x3020054
//
//Code Id  : BT_HCI_INQUIRY_IN_PROGRESS
//Code Text: Device inquiry is in progress.
//
#define  BT_HCI_INQUIRY_IN_PROGRESS		 0x3020055
//
//Code Id  : BT_HCI_PERIODIC_INQUIRY_IN_PROGRESS
//Code Text: Periodic device inquiry is in progress.
//
#define  BT_HCI_PERIODIC_INQUIRY_IN_PROGRESS 0x3020056
//
//Code Id  : BT_HCI_WRITE_FAILED
//Code Text: Attempt to write to the device failed. 
//
#define  BT_HCI_WRITE_FAILED				 0x4020058
//
//Code Id  : BT_HCI_COMMAND_NOT_ALLOWED
//Code Text: The specified command is not allowed.
//
#define  BT_HCI_COMMAND_NOT_ALLOWED			 0x3020059
//
//Code Id  : BT_HCI_TIMEOUT
//Code Text: Timeout occured while waiting for the hci command respose.
//
#define  BT_HCI_TIMEOUT					     0x302005A
//
//Code Id  : BT_HCI_NO_ACL_BUFFER
//Code Text: No ACL buffer free in  host controller.
#define  BT_HCI_NO_ACL_BUFFER				 0x302005B
//
//Code Id  : BT_HCI_NO_SCO_BUFFER
//Code Text: No SCO buffer free in  host controller.
#define  BT_HCI_NO_SCO_BUFFER				 0x302005C
//
//Code Id  : BT_HCI_REMOVE_PENDING
//Code Text: hci connection object being removed 	  	
//
#define  BT_HCI_REMOVE_PENDING				 0x302005D
//
//Code Id  : BT_SCO_NOT_INITIALIZED
//Code Text: sco layer not initialized
#define  BT_SCO_NOT_INITIALIZED						0x30E0001 
//
//Code Id  : BT_SCO_REMOVE_PENDING
//Code Text: sco list being removed
//
#define  BT_SCO_REMOVE_PENDING						0x30E0002            
//
//Code Id  : BT_SCO_NO_EXISTING_ACL_CONNECTION
//Code Text: no ACL connection exists with the remote device with which
//			 sco connection is to be made
//
#define  BT_SCO_NO_EXISTING_ACL_CONNECTION			0x30E0003    
//
//Code Id  : BT_SCO_NO_EXISTING_SCO_CONNECTION
//Code Text: no SCO connection exists with the remote device
//
#define  BT_SCO_NO_EXISTING_SCO_CONNECTION			0x30E0004  
//
//Code Id  : BT_SCO_MAX_NO_OF_SCO_CONNECTIONS
//Code Text: maximum number of sco connections(three) already made
//
#define  BT_SCO_MAX_NO_OF_SCO_CONNECTIONS			0x30E0005          
//
//Code Id  : BT_SCO_TIMEOUT
//Code Text: request timed out
//
#define  BT_SCO_TIMEOUT								0x30E0006
                                      
//
//Code Id  : BT_L2CAP_TIMEOUT_CONNECT_REQ
//Code Text: The wait for connect response timed out 
//
#define  BT_L2CAP_TIMEOUT_CONNECT_REQ				0x3040001
//
//Code Id  : BT_L2CAP_TIMEOUT_CONFIG_REQ
//Code Text: The wait for config response timed out 
//
#define  BT_L2CAP_TIMEOUT_CONFIG_REQ				0x3040002    
//
//Code Id  : BT_L2CAP_TIMEOUT_DISC_REQ
//Code Text: The wait for disconnect response timed out 
//
#define  BT_L2CAP_TIMEOUT_DISC_REQ					0x3040003  
//
//Code Id  : BT_L2CAP_TIMEOUT_ECHO_REQ
//Code Text: The wait for echo response timed out 
//      
#define  BT_L2CAP_TIMEOUT_ECHO_REQ					0x3040004  
//
//Code Id  : BT_L2CAP_TIMEOUT_INFO_REQ
//Code Text: The wait for info response timed out 
//       
#define  BT_L2CAP_TIMEOUT_INFO_REQ					0x3040005   
				//
//Code Id  : BT_L2CAP_TIMEOUT_CONNECT_CFM_FROM_HCI
//Code Text: The wait for ACL connect confirm from HCI timed out 
//      
#define  BT_L2CAP_TIMEOUT_CONNECT_CFM_FROM_HCI		0x3040006
//
//Code Id  : BT_L2CAP_TIMEOUT_DISCONNECT_RSP_FROM_HCI
//Code Text: The wait for ACL diconnect response from HCI timed out 
//
#define  BT_L2CAP_TIMEOUT_DISCONNECT_RSP_FROM_HCI	0x3040007

//
//Code Id  : BT_L2CAP_INVALID_STATE
//Code Text: The current L2CAP state is invalid
//      
#define  BT_L2CAP_INVALID_STATE						0x3040008
//
//Code Id  : BT_L2CAP_ACL_CLOSE_PENDING
//Code Text: hci connection being closed	
//
#define  BT_L2CAP_ACL_CLOSE_PENDING					0x3040009  
//
//Code Id  : BT_L2CAP_ACL_CONNECTION_PENDING
//Code Text: currently processing another hci_connectReq to the same device 	
//  
#define  BT_L2CAP_ACL_CONNECTION_PENDING			0x304000A   

//
//Code Id  : BT_L2CAP_INVALID_GROUP
//Code Text: no such l2cap group present	
// 
#define  BT_L2CAP_INVALID_GROUP						0x304000D
//
//Code Id  : BT_L2CAP_INVALID_GROUP_MEMBER
//Code Text: device not a member of the group  	
//
#define  BT_L2CAP_INVALID_GROUP_MEMBER				0x304000E
//
//Code Id  : BT_L2CAP_REMOVE_PENDING
//Code Text: l2cap connection object being removed 	  	
//
#define  BT_L2CAP_REMOVE_PENDING					0x3040010
//
//Code Id  : BT_L2CAP_CONNECTION_ALREADY_EXIST
//Code Text: l2cap connection already exists  	  	
//
#define  BT_L2CAP_CONNECTION_ALREADY_EXIST			0x3040011
//
//Code Id  : BT_L2CAP_UNKNOWN_OPTIONS
//Code Text: channel configuration failed 
//
#define  BT_L2CAP_UNKNOWN_OPTIONS					0x3040014
//
//Code Id  : BT_L2CAP_CONNECTION_REFUSED
//Code Text: L2CAP connection refused by remote machine 
//
#define  BT_L2CAP_CONNECTION_REFUSED				0x3040016
//
//Code Id  : BT_L2CAP_BUSY_STATE
//Code Text: A connection to the specified device and PSM is in progress 
//
#define  BT_L2CAP_BUSY_STATE						0x3040017 
//
//Code Id  : BT_SDP_REQUEST_TIMEOUT
//Code Text: Service search/service attribute/service search attribute requests timed out 
//                                                 
#define  BT_SDP_REQUEST_TIMEOUT						0x3060001
//
//Code Id  : BT_SDP_UNSUPPORTED_SDP_VERSION
//Code Text: sdp version not supported
//
#define  BT_SDP_UNSUPPORTED_SDP_VERSION				0x3060004
//
//Code Id  : BT_SDP_REMOVE_PENDING
//Code Text: sdp connection object being removed 	  	
//
#define  BT_SDP_REMOVE_PENDING					0x3060005
//
//Code Id  : BT_SDP_INSUFFICIENT_RESOURCE
//Code Text: Insufficient Resources to satisfy Request.
//
#define  BT_SDP_INSUFFICIENT_RESOURCE				0x3060006

//Code Id  : BT_SDP_ATTRIBUTE_ALREADY_EXISTS
//Code Text: Occurs when user tries to add an existing attribute.
//
#define  BT_SDP_ATTRIBUTE_ALREADY_EXISTS			0x3060007  

//
//Code Id  : BT_SDP_L2CAP_CONNECTION_FAILED
//Code Text: Failed to establish l2cap connection
//
#define  BT_SDP_L2CAP_CONNECTION_FAILED				0x3060008

//
//Code Id  : BT_SDP_L2CAP_IN_CLOSING_STATE
//Code Text: Occurs when l2cap is in closing state 
//
#define  BT_SDP_L2CAP_IN_CLOSING_STATE				0x3060009

//
//Code Id  : BT_SDP_SERVICE_ALREADY_EXISTS
//Code Text: service already exists 
//
#define  BT_SDP_SERVICE_ALREADY_EXISTS				0x306000E

//
//Code Id  : BT_SDP_RESULTSET_OVERFLOW
//Code Text: when we try to access the element after cursor position (cursor count)
//
#define  BT_SDP_RESULTSET_OVERFLOW					0x3060014        
//
//Code Id  : BT_SDP_RESULTSET_UNDERFLOW
//Code Text: occurs when we try to access the element before the starting position of the  list.
//
#define  BT_SDP_RESULTSET_UNDERFLOW					0x3060015  
//
//Code Id  : BT_SDP_INVALID_CURSOR_POSITION
//Code Text: occurs when the cursor position is not valid(ie before the start of the list)
//
#define  BT_SDP_INVALID_CURSOR_POSITION				0x3060016

//
//Code Id  : BT_RFCOMM_TIMEOUT_TEST_REQ
//Code Text: Test request timed out.
//
#define  BT_RFCOMM_TIMEOUT_TEST_REQ 				0x3080001     
//
//Code Id  : BT_RFCOMM_TIMEOUT_SABM_REQ
//Code Text: Sabm request timed out.
//
#define  BT_RFCOMM_TIMEOUT_SABM_REQ 				0x3080002     
//
//Code Id  : BT_RFCOMM_TIMEOUT_PN_REQ
//Code Text: PN request timed out.
//
#define  BT_RFCOMM_TIMEOUT_PN_REQ 					0x3080003     
//
//Code Id  : BT_RFCOMM_TIMEOUT_MSC_REQ
//Code Text: MSC request timed out.
//
#define  BT_RFCOMM_TIMEOUT_MSC_REQ 					0x3080004     
//
//Code Id  : BT_RFCOMM_TIMEOUT_FCON_REQ
//Code Text: FCON request timed out.
//
#define  BT_RFCOMM_TIMEOUT_FCON_REQ 				0x3080005     
//
//Code Id  : BT_RFCOMM_TIMEOUT_FCOFF_REQ
//Code Text: FCOFF request timed out.
//
#define  BT_RFCOMM_TIMEOUT_FCOFF_REQ 				0x3080006     
//
//Code Id  : BT_RFCOMM_TIMEOUT_RPN_REQ
//Code Text: RPN request timed out.
//
#define  BT_RFCOMM_TIMEOUT_RPN_REQ 					0x3080007     
//
//Code Id  : BT_RFCOMM_TIMEOUT_RLS_REQ
//Code Text: RLS request timed out.
//
#define  BT_RFCOMM_TIMEOUT_RLS_REQ	 				0x3080008     
                                               
//
//Code Id  : BT_RFCOMM_BAUDRATE_NOT_SUPPORTED
//Code Text: Baud rate not suppoted.
//
#define  BT_RFCOMM_BAUDRATE_NOT_SUPPORTED 			0x3080009	
//
//Code Id  : BT_RFCOMM_DATABITS_NOT_SUPPORTED
//Code Text: Data bit not supported.
//
#define  BT_RFCOMM_DATABITS_NOT_SUPPORTED 			0x308000A	
//
//Code Id  : BT_RFCOMM_STOPBIT_NOT_SUPPORTED
//Code Text: Stop bit not supported.
//
#define  BT_RFCOMM_STOPBIT_NOT_SUPPORTED 			0x308000B	
//
//Code Id  : BT_RFCOMM_PARITYBIT_NOT_SUPPORTED
//Code Text: Parity bit not supported.
//
#define  BT_RFCOMM_PARITYBIT_NOT_SUPPORTED 			0x308000C
//
//Code Id  : BT_RFCOMM_PARITYTYPE_NOT_SUPPORTED
//Code Text: Parity type not supported
//
#define  BT_RFCOMM_PARITYTYPE_NOT_SUPPORTED 		0x308000D
//
//Code Id  : BT_RFCOMM_FLOWCONTROL_NOT_SUPPORTED
//Code Text: Flowcontrol not supported.
//
#define  BT_RFCOMM_FLOWCONTROL_NOT_SUPPORTED 		0x308000E
//
//Code Id  : BT_RFCOMM_XONCHAR_NOT_SUPPORTED
//Code Text: xon character not supported.
//
#define  BT_RFCOMM_XONCHAR_NOT_SUPPORTED 			0x308000F	
//
//Code Id  : BT_RFCOMM_XOFFCHAR_NOT_SUPPORTED
//Code Text: xoff character not supported.
//
#define  BT_RFCOMM_XOFFCHAR_NOT_SUPPORTED 			0x3080010	
                                               
//
//Code Id  : BT_RFCOMM_NO_UPPERLAYER_REGISTERED
//Code Text: No upper layer registered.
//
#define  BT_RFCOMM_NO_UPPERLAYER_REGISTERED			0x3080011
//
//Code Id  : BT_RFCOMM_SESSION_NOT_CONNECTED
//Code Text: Session not in connected state.
//
#define  BT_RFCOMM_SESSION_NOT_CONNECTED			0x3080012
//
//Code Id  : BT_RFCOMM_CONNECTION_ALREADY_EXISTS
//Code Text: The connection already excists to this channel
//
#define  BT_RFCOMM_CONNECTION_ALREADY_EXISTS		0x3080013
//
//Code Id  : BT_RFCOMM_DLCI_NOT_CONNECTED
//Code Text: DLCI not in connected state.
//
#define  BT_RFCOMM_DLCI_NOT_CONNECTED				0x3080014
//
//Code Id  : BT_RFCOMM_TEST_DATA_MISMATCH
//Code Text: Received test data mismatch.
//
#define  BT_RFCOMM_TEST_DATA_MISMATCH				0x3080015
//
//Code Id  : BT_RFCOMM_NO_SESSION
//Code Text: Seession does not excist.
//
#define  BT_RFCOMM_NO_SESSION						0x3080016
//
//Code Id  : BT_RFCOMM_FCS_MISMATCH
//Code Text: FCS mismatch occourred.
//
#define  BT_RFCOMM_FCS_MISMATCH						0x3080017
//
//Code Id  : BT_RFCOMM_MAX_NO_OF_SESSIONS
//Code Text: Already reached maximum number of allowable sessions.
//
#define  BT_RFCOMM_MAX_NO_OF_SESSIONS				0x3080018
//
//Code Id  : BT_RFCOMM_REMOVE_PENDING
//Code Text: An object referenced is going to be removed.
//
#define  BT_RFCOMM_REMOVE_PENDING					0x3080019
//
//Code Id  : BT_RFCOMM_SERVER_ALREADY_WAITING
//Code Text: A server is already waiting in the given server channel.
//
#define  BT_RFCOMM_SERVER_ALREADY_WAITING			0x3080020
//
//Code Id  : BT_SPP_PORT_ACCESS_DENIED
//Code Text: The specified port is already bounded with an SPP connection 
// or in the process of binding.
//
#define  BT_SPP_PORT_ACCESS_DENIED					0x3090001
//
//Code Id  : BT_SPP_PORT_NOT_FOUND
//Code Text: The specified port may not be installed in the system or its 
// installation may not be proper.
//
#define  BT_SPP_PORT_NOT_FOUND						0x3090002
//
//Code Id  : BT_SPP_SERVICE_IN_USE
//Code Text: The specified service cannot be deleted as it is in use
//
#define  BT_SPP_SERVICE_IN_USE						0x3090003
//
//Code Id  : BT_SECURITY_ACCESS_DENIED
//Code Text: When a  request is reject bcause of security failure.
//
#define  BT_SECURITY_ACCESS_DENIED                  0x30C0001
//
//Code Id  : BT_SECURITY_THREAD_CREATION_FAILED
//Code Text: When creating a thread is failed.
//
#define  BT_SECURITY_THREAD_CREATION_FAILED         0x30C0002
//
//Code Id  : BT_SECURITY_REGISTRY_OPERATION_FAILED
//Code Text: When registry operation is failed.
//
#define  BT_SECURITY_REGISTRY_OPERATION_FAILED      0x30C0003
//
//Code Id  : BT_SECURITY_CALLBACK_ALREADY_REGISTERED
//Code Text: When callback is tried to set multiple times.
//
#define  BT_SECURITY_CALLBACK_ALREADY_REGISTERED    0x30C0004 



/*					 profile error codes 						*/


//
//Code Id  : BT_GOEP_CONNECTION_TERMINATED 
//Code Text: The transport connection has been terminated.
//
#define  BT_GOEP_CONNECTION_TERMINATED					0x3200001
//
//Code Id  : BT_GOEP_REQUEST_TIMEDOUT 
//Code Text: The request has been timed out.
//
#define  BT_GOEP_REQUEST_TIMEDOUT						0x3200002
//
//Code Id  : BT_GOEP_OPERATION_IN_PROGRESS 
//Code Text: An operation is already in progress.
//
#define  BT_GOEP_OPERATION_IN_PROGRESS					0x3200003
//
//Code Id  : BT_GOEP_ AUTHENTICATION_FAILED 
//Code Text: Server could not authenticate the client.
//
#define  BT_GOEP_AUTHENTICATION_FAILED					0x3200004
		 		 //
//Code Id  : BT_GOEP_INVALID_RESPONSE 
//Code Text: The response from the server is invalid.
//
#define  BT_GOEP_INVALID_RESPONSE						0x3200005
//
//Code Id  : BT_GOEP_UNAUTHORIZED_SERVER 
//Code Text: Client could not authenticate the server.
//
#define  BT_GOEP_UNAUTHORIZED_SERVER					0x3200006
//
//Code Id  : BT_GOEP_OPERATION_ABORTED 
//Code Text: The operation is aborted.
//
#define  BT_GOEP_OPERATION_ABORTED						0x3200007
//
//Code Id  : BT_GOEP_INVALID_HEADER_ID 
//Code Text: Header is is invalid.
//
#define  BT_GOEP_INVALID_HEADER_ID						0x3200008
//
//Code Id  : BT_GOEP_INVALID_HANDLE 
//Code Text: Given handle is invalid.
//			 Handle can be sessionhandle, 
//			 operation handle or headersethandle
//
#define BT_GOEP_INVALID_HANDLE							0x3200009
//
//Code Id  : BT_GOEP_SERVICE_NOT_AVAILABLE
//Code Text: The specified service is not available,
//			 at the server
//
#define BT_GOEP_SERVICE_NOT_AVAILABLE					0x3200010
//
//Code Id  : BT_GOEP_ATTRIBUTE_NOT_FOUND
//Code Text: The specified attribute is not available,
//			 in the SDDB of the server
//
#define BT_GOEP_ATTRIBUTE_NOT_FOUND 					0x3200011
//
//Code Id  : BT_GOEP_WORKING_DIRECTORY_REQUIRED
//Code Text: The working directory should be set prior,
//			 to the call of the function
//
#define BT_GOEP_WORKING_DIRECTORY_REQUIRED				0x3200012
//
//Code Id  : BT_GOEP_FILE_NOT_FOUND
//Code Text: The speciifed file not found in the given,
//			 directory
//
#define BT_GOEP_FILE_NOT_FOUND							0x3200013
//
//Code Id  : BT_GOEP_INVALID_PARAMETER
//Code Text: A parameter that was passed to the API,
//			 was invalid
//
#define BT_GOEP_INVALID_PARAMETER						0x3200014
//
//Code Id  : BT_GOEP_OBEXCONNECTION_FAILED
//Code Text: GOEP connection failed to establish
//
#define BT_GOEP_OBEXCONNECTION_FAILED					0x3200015
//
//Code Id  : BT_GOEP_INVALID_TYPE
//Code Text: Object is of an invalid type
//
#define BT_GOEP_INVALID_TYPE							0x3200016
//
//Code Id  : BT_GOEP_OPERATION_DISALLOWED
//Code Text: Operation is disallowed
//
#define BT_GOEP_OPERATION_DISALLOWED					0x3200017
//
//Code Id  : BT_GOEP_NO_OPERATION_IN_PROGRESS
//Code Text: There are push or pull operation in progress
//
#define BT_GOEP_NO_OPERATION_IN_PROGRESS				0x3200018
//
//Code Id  : BT_OPP_BUSINESSCARD_PUSH_FAILED
//Code Text: Pushing business card failed
//
#define BT_OPP_BUSINESSCARD_PUSH_FAILED					0x3210001
//
//Code Id  : BT_OPP_BUSINESSCARD_PULL_FAILED
//Code Text: Pulling business card failed
//
#define BT_OPP_BUSINESSCARD_PULL_FAILED					0x3210002
//
//Code Id  : BT_DUN_ALREADY_CONNECTED
//Code Text: The DUN connection is already established
//
#define BT_DUN_ALREADY_CONNECTED						0x3260001
//
//Code Id  : BT_LAP_ALREADY_CONNECTED
//Code Text:  The LAP connection is already established
//
#define BT_LAP_ALREADY_CONNECTED						0x3270001
//
//Code Id  : BT_HP_NOT_INITIALIZED
//Code Text: HP has not been initialized
//
#define BT_HP_NOT_INITIALIZED							0x3280001
//
//Code Id  : BT_HP_MAX_NO_OF_SESSIONS
//Code Text: Number of possible sessions Exceeds Maximum Limit
//
#define BT_HP_MAX_NO_OF_SESSIONS						0x3280002

//
//Code Id  : BT_HIDP_ALREADY_INITIALIZED
//Code Text: The HID profile already initialized
//
#define BT_HIDP_ALREADY_INITIALIZED   		3310001
//
//Code Id  : BT_HIDP_NOT_INITIALIZED
//Code Text: The HID profile has not been initialized
//
#define BT_HIDP_NOT_INITIALIZED             		3310002
//
//Code Id  : BT_HIDP_REQUEST_PENDING
//Code Text: The HID profile request to the device is pending 
//
#define BT_HIDP_REQUEST_PENDING         		3310003 
//
//Code Id  : BT_HIDP_COMMAND_TIMEOUT
//Code Text: HID command to device timedout
//
#define BT_HIDP_COMMAND_TIMEOUT      			3310004
//
//Code Id  : BT_HIDP_DEVICE_NOT_READY
//Code Text: The HID device is not ready
//
#define BT_HIDP_DEVICE_NOT_READY     			3310005
//
//Code Id  : BT_HIDP_INVALID_REPORT_ID
//Code Text: Invalid data from the HID device
//
#define BT_HIDP_INVALID_REPORT_ID      			3310006
//
//Code Id  : BT_HIDP_UNSUPPORTED_REQUEST
//Code Text: Unsupported HID request
//
#define BT_HIDP_UNSUPPORTED_REQUEST  			3310007
//
//Code Id  : BT_HIDP_INVALID_PARAMETER
//Code Text: Invalid Parameter
//
#define BT_HIDP_INVALID_PARAMETER         	 	3310008
//
//Code Id  : BT_HIDP_ERR_UNKNOWN
//Code Text: Unknown error
//
#define BT_HIDP_ERR_UNKNOWN                		3310009
//
//Code Id  : BT_HIDP_ERR_FATAL
//Code Text: Fatal error
//
#define BT_HIDP_ERR_FATAL		 				331000A

//
//Code Id  : BT_AVDTP_L2CAP_REGISTRATION_FAILED
//Code Text: Failed to register the L2cap Callbacks
//
// 
#define BT_AVDTP_L2CAP_REGISTRATION_FAILED			0x3320001
//
//Code Id  : BT_AVDTP_STREAM_CONTEXT_EMPTY
//Code Text: The stream Context is Empty
//
// 
#define BT_AVDTP_STREAM_CONTEXT_EMPTY				0x3320002
//
//Code Id  : BT_AVDTP_INVALID_SEID
//Code Text: The given SEID is invalid
//
// 
#define BT_AVDTP_INVALID_SEID						0x3320003
//
//Code Id  : BT_AVDTP_INVALID_STREAM_STATE
//Code Text: The present State of the Stream is Invalid
//
// 
#define BT_AVDTP_INVALID_STREAM_STATE				0x3320004
//
// Code Id	:BT_AVDTP_NO_CHANNEL
//Code Text	:No L2cap channel exists
//
#define BT_AVDTP_NO_CHANNEL							0x3320005
//
//Code Id  : BT_GAVDP_LOCAL_SEID_MISMATCH
//Code Text: A mismatch has occurred between the 
//			 Seids maintained locally.
//
// Code Id :BT_AVDTP_REQUEST_TIMEDOUT
//Code Text :AVDTP request has timed out
//
#define BT_AVDTP_REQUEST_TIMEDOUT 					0x3320006
//
// 
#define BT_GAVDP_LOCAL_SEID_MISMATCH				0x3330001
//
//Code Id  : BT_GAVDP_MEDIA_CODEC_NOT_SUPPORTED
//Code Text: Media Codec is not supported
//
// 
#define BT_GAVDP_MEDIA_CODEC_NOT_SUPPORTED			0x3330002
//
//Code Id  : BT_GAVDP_CAPABILITY_REGISTRATION_VIOLATION
//Code Text: An attempt to register more than one capability 
//			 of a particular category
//
// 
#define BT_GAVDP_CAPABILITY_REGISTRATION_VIOLATION	0x3330003
//
//Code Id  : BT_GAVDP_ACCEPT_TIMEOUT
//Code Text:  GAVDP_Accept request timed out.
//
//
#define BT_GAVDP_ACCEPT_TIMEOUT						0x3330004
//
//Code Id  : BT_GAVDP_SIGNALING_CHANNEL_ALREADY_EXISTS
//Code Text: Presently supporting only connection between 2 devices
//
// 
#define BT_GAVDP_SIGNALING_CHANNEL_ALREADY_EXISTS	0x3330005
//
// Code Id :BT_GAVDP_REQUEST_TIMEDOUT
//Code Text :GAVDP request has timed out
//
#define BT_GAVDP_REQUEST_TIMEDOUT     				0x3330006
//
//Code Id  : BT_A2DP_NOT_INITIALIZED
//Code Text: A2D profile not initialized properly
//
// 
#define BT_A2DP_NOT_INITIALIZED						0x3340001
//
//Code Id  : BT_A2DP_SEPTYPE_NOT_SET
//Code Text: A2DP -Local SEP Type not set
//
// 
#define BT_A2DP_SEPTYPE_NOT_SET						0x3340002
//
//Code Id  : BT_A2DP_INVALID_SEPTYPE
//Code Text: A2DP -Local SEP Type is invalid
//
// 
#define BT_A2DP_INVALID_SEPTYPE						0x3340003
//
// Code Id : BT_A2DP_REQUEST_TIMEDOUT
//Code Text: A2DP request has timed out
//
#define BT_A2DP_REQUEST_TIMEDOUT				    0x3340004

#endif //_ALBTERRORCODES_H
