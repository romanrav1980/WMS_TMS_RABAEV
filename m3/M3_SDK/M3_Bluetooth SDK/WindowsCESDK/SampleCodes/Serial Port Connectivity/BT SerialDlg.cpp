//  : implementation file
/****************************************************************************
*																			
* FILENAME	:	BT SerialDlg.cpp
*																			
* MODULE	:	Bluetoth serial connectivity sample						
*																			
* PURPOSE	:	Implementation of the user interface
*			
* DEVELOPMENT HISTORY: 													
****************************************************************************/

#include "stdafx.h"
#include "BT Serial.h"
#include "BT SerialDlg.h"
#include "GenStackInterface.h"
#include "Vector.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CBTSerialDlg dialog

HANDLE sppClient		= NULL; // Handle for Serial port client connection
HANDLE sppServer		= NULL; // Handle for Serial port Server connection
INT    serverStatus		= 0;	// Server status
BT_REGISTERSERVICE_INFO serviceRegInfo = {0}; //Bluetooth Service 
											//registration information
INT    gServerChannel   = 0;	// Server channel for the remote service
HANDLE hThread			= NULL;	// Handle to the thread
BOOLEAN bCardStatus		= FALSE; // Status of the bluetooth module	
CBTSerialDlg* CBTSerialDlg::pBTSInstance = NULL; // Static pointer to the one 
										//and only instance of CBTSerialDlg

/*
*
* FUNCTION NAME	:	CBTSerialDlg
*
* DESCRIPTION	:	Constructor
*
*/

CBTSerialDlg::CBTSerialDlg(CWnd* pParent /*=NULL*/)
: CDialog(CBTSerialDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CBTSerialDlg)
	// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CBTSerialDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CBTSerialDlg)
	DDX_Control(pDX, IDC_LIST1, m_devlistBt);
	DDX_Control(pDX, IDC_CHECK1, m_ServerMode);
	DDX_Control(pDX, IDC_BUTTON4, m_rfconnectBt);
	DDX_Control(pDX, IDC_BUTTON3, m_sdpBt);
	DDX_Control(pDX, IDC_BUTTON2, m_devBt);
	DDX_Control(pDX, IDC_BUTTON1, m_initBt);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CBTSerialDlg, CDialog)
	//{{AFX_MSG_MAP(CBTSerialDlg)
	ON_BN_CLICKED(IDC_BUTTON1, OnBluetoothON)
	ON_BN_CLICKED(IDC_BUTTON3, OnServiceSearch)
	ON_BN_CLICKED(IDC_BUTTON2, OnBTDeviceSearch)
	ON_BN_CLICKED(IDC_BUTTON4, OnSppConnect)
	ON_NOTIFY(NM_CLICK, IDC_LIST1, OnClickList1)
	ON_BN_CLICKED(IDC_CHECK1, OnSppServer)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CBTSerialDlg message handlers


/*
*
* FUNCTION NAME	:	OnInitDialog
*
* DESCRIPTION	:	Initialization member function for the dialog
*/

BOOL CBTSerialDlg::OnInitDialog()
{
	CDialog::OnInitDialog();
	
	//  Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	CenterWindow(GetDesktopWindow());	// center to the hpc screen
	
	bCardStatus =  FALSE;
	GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Stack Not Initialized"));	
	
	// Create a vector to hold the remote device information for later use
	mpVector = create();	
	
	//Create imagelist
	ImageList.Create(32,32,ILC_MASK | ILC_COLORDDB, 10, 2);
	
	ImageList.Add(AfxGetApp()->LoadIcon(IDI_ICON1));
	ImageList.SetBkColor(ILD_TRANSPARENT);
	
	m_devlistBt.SetImageList(&ImageList,LVSIL_NORMAL);
	m_devlistBt.InsertColumn(0,TEXT("Device Address"),LVCFMT_LEFT,115);
	m_devlistBt.InsertColumn(1,TEXT("Service"),LVCFMT_LEFT,115);

	pBTSInstance = this;
	
	return TRUE;  
}

/*
*
* FUNCTION NAME	:	OnBluetoothON
*
* DESCRIPTION	:	(message handlers) Controls the bluetooth stack states.
*					Ie: Initializes\de-initializes the bluetooth SDK
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

void CBTSerialDlg::OnBluetoothON() 
{
	CString bdAddres;
	DEVICE_NAME devName;
	if(bCardStatus == FALSE)
	{
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Card Initializing"));			

		
		// Initilaize the bluetooth SDK
#ifdef M3_BUILTIN_BT		
		
		// We need to power-up builtin-in Bluetooth starting.
		// Power-up the module either using the utility program BT_ON_OFF from
		// \Flash Disk\Bluetooth\ or using the functions provided by 
		// Mobile compia

#endif
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Card Initializing"));
		if(genStackInterface.BTCardInitialize())
		{
			bCardStatus = TRUE;
			strcpy((char*)devName,(char*)BT_DEVICE_Name);
			// Set the device name for the local device
			genStackInterface.GapSetLocalDeviceName(devName);
			m_initBt.SetWindowText(TEXT("Bluetooth OFF"));							
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Bluetooth Initialized"));			
		}
		else
		{
#ifdef M3_BUILTIN_BT		
		
			// like power-up, we have to power-down the builtin-in Bluetooth after
			// the use		
#endif
			bCardStatus = FALSE;
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Bluetooth Not Initialized"));
		}
	}
	else
	{
		genStackInterface.BTCardDeInitialize();	

#ifdef M3_BUILTIN_BT		
		
			// like power-up, we have to power-down builtin-in Bluetooth after
			// the use			
#endif

		bCardStatus = FALSE;
		m_initBt.SetWindowText(TEXT("Bluetooth ON"));			
		m_rfconnectBt.SetWindowText(TEXT("SPP  Connect"));
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Bluetooth Not Initialized"));			
	}	
}

/*
*
* FUNCTION NAME	:	OnBTDeviceSearch
*
* DESCRIPTION	:	(message handler) Performs the device iquiry and lists the 
*					results in the correspoding listbox.
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

void CBTSerialDlg::OnBTDeviceSearch() 
{
	BT_DEVICE devices[15]	= {0};				
	UINT8 retCount			= 0;
	INT i					= 0;
	
	if(bCardStatus == TRUE)
	{		
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Device Searching"));	
		
		m_devlistBt.DeleteAllItems();

		// Remove previous vector entries ...

		while(!isEmpty(mpVector))
		{
			removeElementAt(mpVector, 0);
		}

		Sleep(10);	
		if(genStackInterface.GapInquireAndRetrieveDevices(BT_GIAC,6,devices,10,&retCount))
		{
			CString cstrDevAddress;
			INT iListIndex = 0;
			
			if(retCount)
			{
				for(i=0;i<retCount;i++)
				{
					cstrDevAddress.Format(TEXT("%.2X:%.2X:%.2X:%.2X:%.2X:%.2X"),\
						devices[i].bdAddress[0],devices[i].bdAddress[1],devices[i].bdAddress[2],\
						devices[i].bdAddress[3],devices[i].bdAddress[4],devices[i].bdAddress[5]);
					iListIndex = m_devlistBt.InsertItem(i,cstrDevAddress,i); 
					m_devlistBt.SetItemData(iListIndex,i);
					
					{
						DUN_SERVICE_HEAD *deviceNode = new DUN_SERVICE_HEAD;												
						memset(&deviceNode->btService,0,sizeof(BT_SERVICE)); 
						memcpy(deviceNode->btDevice.bdAddress,devices[i].bdAddress,6);
						memcpy(deviceNode->btDevice.clockOffset,devices[i].clockOffset,2);
						deviceNode->btDevice.majorDeviceClass		= devices[i].majorDeviceClass;
						deviceNode->btDevice.minorDeviceClass		= devices[i].minorDeviceClass;
						deviceNode->btDevice.pageScanMode			= devices[i].pageScanMode;
						deviceNode->btDevice.pageScanPeriodMode		= devices[i].pageScanPeriodMode;
						deviceNode->btDevice.pageScanRepetitionMode	= devices[i].pageScanRepetitionMode;
						deviceNode->btDevice.serviceClass			= devices[i].serviceClass;
						addElement(mpVector,(void*)deviceNode);
					}					
				}			
				CString strMsg;
				strMsg.Format(TEXT("%d Devices found"),retCount);
				GetDlgItem(IDC_STATUS)->SetWindowText(strMsg);
			}
			else
			{
				GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("No Device Found."));
			}			
		}
		else
		{
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Device Search - Fail"));	
		}
	}
	else
	{
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Card Not InitializeD"));	
	}	
}

/*
*
* FUNCTION NAME	:	OnServiceSearch
*
* DESCRIPTION	:	(message handler) Performs the service search to find out 
*					the services offered by the specified device
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

void CBTSerialDlg::OnServiceSearch() 
{
	BT_DEVICE device			= {0};
	PDUN_SERVICE_HEAD  dunHead	= NULL;
	BT_UUID uuid				= {{0x11, 0x01},2};
	BT_SERVICE services[10]		= {0};
	UINT16 numServices			= 0;
	INT i =0 , j = 0;
	
	if(bCardStatus)
	{		
		if(m_devlistBt.GetSelectedCount())		
		{
			INT index = m_devlistBt.GetSelectionMark();
			if(index != -1)
			{
				CString FavString = m_devlistBt.GetItemText(index,0);
				FavString += TEXT("    Searching");
				GetDlgItem(IDC_STATUS)->SetWindowText(FavString);
				
				dunHead = (PDUN_SERVICE_HEAD)elementAt(mpVector,index);				 
				device  = (BT_DEVICE)dunHead->btDevice;
				
				if(genStackInterface.SdapSearchRemoteServices(&device, &uuid, 1, services, 5, &numServices))
				{
					if(numServices)
					{
						//for(i=0;i<numServices;i++)
						{
							CString strItemText = services[0].serviceName;
							m_devlistBt.SetItemText(index,1,strItemText);
							dunHead->btService.identifier = services[0].identifier;
							dunHead->btService.profileDescriptor = services[0].profileDescriptor;
							dunHead->btService.protocolDescriptor = services[0].protocolDescriptor;
							strcpy((char*)dunHead->btService.serviceName,(char*)services[0].serviceName);
							GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Service found."));
						}
					}
					else
					{
						GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("No Service Found."));
						m_devlistBt.SetItemText(index,1,L"No Service found");					
					}
				}
				else
				{
					GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Service Search - Fail "));	
				}		
			}
		}
		else
		{
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("No Device Selected "));	
		}
	}
	else
	{
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Turn Bluetooth ON"));	
	}
}

/*
*
* FUNCTION NAME	:	OnSppConnect
*
* DESCRIPTION	:	(message handler) Establishes/Removes connection to the 
*					specifed device
*					 
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/


void CBTSerialDlg::OnSppConnect() 
{
	PDUN_SERVICE_HEAD  dunHead	= NULL;
	BT_DEVICE device			= {0};
	BT_SERVICE service			= {0};
	UINT16 frameSize				= 1500;
	PINT8 portName				= (PINT8) SPP_COM_Port;
	TCHAR ctrlCaption[100]		= {0};

	if(bCardStatus)
	{
		if(m_devlistBt.GetSelectedCount())		
		{
			INT index = m_devlistBt.GetSelectionMark();
			if(index != -1)
			{			
				dunHead = (PDUN_SERVICE_HEAD)elementAt(mpVector,index);					
				device  = (BT_DEVICE)dunHead->btDevice;
				service = (BT_SERVICE)dunHead->btService;
				
				if(dunHead)
				{	
					m_rfconnectBt.GetWindowText(ctrlCaption,25);

					// The request is to connect to the specified device
					if(wcscmp(ctrlCaption,TEXT("SPP  Connect")) == 0)
					{
						CString FavString = m_devlistBt.GetItemText(index,0);
						FavString += TEXT("    Connecting");
						GetDlgItem(IDC_STATUS)->SetWindowText(FavString);
						
						sppClient = genStackInterface.SppConnect(&device, &service, &frameSize, NULL,portName);
						if(sppClient == NULL)
						{
							GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("SPP_Connect - Fail"));	
						}
						else
						{
							GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("SPP_Connect - Success"));	
							m_rfconnectBt.SetWindowText(TEXT("SPP  Disconnect"));
							SPP_SetEventNotifyProc(sppClient, appSppEventCallback);

						}
					}
					// The request is to remove the connection 
					else if(wcscmp(ctrlCaption,TEXT("SPP  Disconnect")) == 0)
					{
						if(genStackInterface.SppClose(sppClient))
						{
							GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("SPP_Disconnect - Success"));	
							m_rfconnectBt.SetWindowText(TEXT("SPP  Connect"));
						}
						else
						{
							GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("SPP_Disconnect - Fail"));	
						}
					}
					else
					{
						GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Invaid Operation.- Close"));	
					}
				}
				else
				{
					GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Couldnot Connect "));		
				}
			}
			else
			{
				GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("No Device Selected "));	
			}			
		}
		else
		{
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("No Device Selected "));	
		}
	}
	else
	{
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Turn Bluetooth ON"));	
	}	
}


/*
*
* FUNCTION NAME	:	OnSppServer
*
* DESCRIPTION	:	(message handler) Starts/Stops the local service(s).
*					 
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/

void CBTSerialDlg::OnSppServer() 
{
	BT_SERVICE service;
	if(bCardStatus)
	{
		service.identifier			= gServerChannel;
		service.profileDescriptor	= SPP;
		service.protocolDescriptor	= RFCOMM;
		strcpy((char*)service.serviceName, "SPP Test Server");

		// Request fot starting the serial service 
		if(m_ServerMode.GetCheck()==BST_CHECKED)
		{			
			hThread = CreateThread(NULL,0,
									(LPTHREAD_START_ROUTINE)StartSppServer,
									(LPVOID)(NULL),0,NULL);
			if(!hThread)
			{
				GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Can't Start Server"));						
			}
		}
		// Request fot terminate the serial service 
		else	
		{	
			GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Server Stopped"));									
			
			if(serverStatus == SERVER_CONNECTED )
			{
				genStackInterface.SppDeleteService(&serviceRegInfo);
				genStackInterface.SppClose(sppServer);						
			}
			else
			{										
				genStackInterface.SppRemoveServer(service);
			}
			
			if(hThread)
				CloseHandle(hThread);
		}
	}
	else
	{
		GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Turn Bluetooth ON"));	
		m_ServerMode.SetCheck(BST_UNCHECKED);
	}
}


/*
*
* FUNCTION NAME	:	StartSppServer
*
* DESCRIPTION	:	Thread procedure for the local  service
*					 
*
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	NIL			
*
* RETURNS		: VOID
*/
VOID StartSppServer()
{
	
	BT_UUID uuid			= {0};
	BT_DEVICE device		= {0};
	UINT16 frameSize			= 1500;
	PINT8 portName			= (PINT8)SPP_COM_Port;
	PBT_SECURITY_ATTRIBUTE secAttrib = NULL;
	BT_SERVICE service		= {0};
	CBTSerialDlg* pBTS = CBTSerialDlg::pBTSInstance;

	
	service.identifier			= gServerChannel;
	service.profileDescriptor	= SPP;
	service.protocolDescriptor	= RFCOMM;
	strcpy((char*)service.serviceName,"SPP Test Server");
	
	uuid.length		= 2;
	uuid.uuid[0]	= 0x11;
	uuid.uuid[1]	= 0x01;	

	
	pBTS->genStackInterface.SppRegisterService(&service,&uuid,&serviceRegInfo);	
	gServerChannel  = service.identifier;
	pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Server Waiting"));	
	
	serverStatus	= SERVER_WAITING;
	sppServer       = NULL;
	sppServer		= pBTS->genStackInterface.SppAccept(&device, &service,&frameSize, secAttrib,portName );
	
	if(sppServer)
	{
		serverStatus = SERVER_CONNECTED;		
		pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Server Connected"));	

		SPP_SetEventNotifyProc(sppServer, appSppEventCallback);
	}
	else
	{
		pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Server Connection Failed"));	
		pBTS->genStackInterface.SppDeleteService(&serviceRegInfo);		
		(pBTS->m_ServerMode).SetCheck(BST_UNCHECKED);
	}	
}

/*
*
* FUNCTION NAME	:	appSppEventCallback
*
* DESCRIPTION	:	User registered callback function for handling SPP 
*					notifications
*					 
*	ARGUMENT		TYPE		I/O		DESCRIPTION
*	--------		----		----	-------------
*	sppHandle		HANDLE		I		Handle to the previously established 
*										SPP connection 
*	event			UINT32		I		SPP event
*
* RETURNS		: VOID
*/

VOID appSppEventCallback(HANDLE sppHandle,UINT32 event)
{
	CBTSerialDlg* pBTS = CBTSerialDlg::pBTSInstance;
	
	
	switch(event)
	{
		case EVENT_COM_CLOSED :

			pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Port closed"));
			break;
			
		case EVENT_DISCONNECT :
			
			if(sppHandle == sppClient)
			{				
				pBTS->m_rfconnectBt.SetWindowText(TEXT("SPP  Connect"));
				pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Connection lost"));
			}
			else if(sppHandle == sppServer)
			{		
				serverStatus	= SERVER_WAITING;
				(pBTS->m_ServerMode).SetCheck(BST_UNCHECKED);
				pBTS->genStackInterface.SppDeleteService(&serviceRegInfo);
				pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Server Stopped"));
			}
			else
			{
				pBTS->GetDlgItem(IDC_STATUS)->SetWindowText(TEXT("Got SPP Disconnect"));
			}
			break;	
		
		default :
			
			break;
	}
}


void CBTSerialDlg::OnClickList1(NMHDR* pNMHDR, LRESULT* pResult)
{
	*pResult = 0;
}


void CBTSerialDlg::OnOK()
{
	INT status =MessageBox(L"Do you want to Quit",L"   BT Serial   ",MB_OKCANCEL);
	if(status == IDOK)
	{
		genStackInterface.BTCardDeInitialize();

		if(hThread)
			CloseHandle(hThread);
		
		if(mpVector)
			deleteVector(mpVector);

#ifdef M3_BUILTIN_BT		
			
			// like power-up, we have to power-down builtin-in Bluetooth after
			// the use	
	#endif
		
		CDialog::OnOK();
	}

}

