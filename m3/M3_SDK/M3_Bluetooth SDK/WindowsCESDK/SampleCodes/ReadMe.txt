-------------------------------------------------------------------------------
      Serial Blutooth Applications using aveLink Bluetooth SDK for Windows CE
				         BT Serial.exe
                   (c) 2003-2004 Atinav LLC.  100 Franklin Square Drive
		        Suite # 304, Somerset, NJ 08873., USA

-------------------------------------------------------------------------------

Abstarct
 Congratulations!  You have obtained source code of a sample Bluetooth Serial application.
 This is to enable serial connectivity using Bluetooth technology. Any legacy application running 
 over serial ports can run over the emulated COM port connectivity obtained by BT Serial.exe

==========================================
Index
==========================================
1.	Installation/Uninstallation instructions
2.	Installed Components
3.	Usage
4.	Errors
5.	Contact
6.	Copyright
==========================================


1.	Installation/Uninstallation instructions
----------------------------------------------
 	BT Serial appication source code get copied in to the installation directory (aveLinkBT\WindowsCESDK\SampleCodes) of the desktop PC when the installation program is executed.

2.	Installed Components
----------------------------------------------
 	The sample code is provided as an embedded VC++ project.It uses the the library file albtcore.lib to interface with the avelink Bluetooth SDK for Windows CE.The header file albtcore.h lists the functions exported by avelink Bluetooth SDK.

3.	Usage
-----------------------------------------------
 	3.1.	How to Compile BT Serial.exe
	----------------------------------

  	1. Open "BT Serial.vcw" in Embedded Vc++.
   
  	2. Include albtcore.h to the project
	
  	3. Link albtcore.lib to the project

	4. Build the application		

 	3.2	Customizations
	----------------------------------
	
	Open "GenStackInterface.h" in Embedded Vc++ IDE,  Search for section containig the following lines

 	// Edit - Section For User
 	#define SPP_COM_Port	"COM6:"   // Emulated COM port by avelink Bluetooth SDK 
  	
	#define HCI_UART_Port	"COM0:"   // Port on which the bluetooth card is listening
  	#define HCI_BAUDRATE	115200    // Baud rate of the bluetooth Card
  	
	#define BT_DEVICE_Name  "Atinav BlueCE II" // Local Device Name
	
	#define BT_TRANSPORT TL_BCSP 
  	
	// End of Edit - Section

  	Customise the Portnames, Baudrate and Device Name, specific to your BT Radio Module.

  	In the windows ce device, run RegEdit.exe present in "\\My Device\aveLinkBT\WindowsCESDK" directory and 
	find these values.

  	SPP_COM_Port  - Its given in the 'Index' field of HKLM\Drivers\BuiltIn\AveBT1 or HKLM\Drivers\BuiltIn\AveBT2. 
  		Since the serial ports are installed based on the avaialbility of them at the time of 
		installation, it can vary from installation to installation.

	HCI_UART_Port - Plug in the CF card on to your windows ce device. Search all the subkeys of HKLM\Drivers\Active\. 
                Select the "Name" field of the subkey with PnPId  of your Plugged CF card. Usually it will be 
                 in the Last sub key of HKLM\Drivers\Active.

  	BT_TRANSPORT  - Transport supported by the bluetooth module.If it is a UART card, set it as TL_H4.If it is
		a BCSP card, set the value TL_BCSP.	
	
	Edit the HCI_BAUDRATE, and BT_DEVICE_Name if necessary 
	Save it and Compile. 
  
  NOTE : Inorder to work with Ipaq6315 Builtin Bluetooth, you must replace the above constants with the following
  values,
  
  HCI_UART_Port 	: "COM8:"
  BT_TRANSPORT		: TL_H4
  HCI_BAUDRATE		:	115200
  SPP_COM_Port 		: Select the value from the registry as described above.
  
  You must also use the following APIs specified in albtradio.h to power-up/power-down the builin Bluetooth module.
  
  1) BOOL BTRadioOn()	- Power-up the Builtin chip.This has to be invoked before initializing the Bluetooth stack
  (see sample).
  2) BOOL BTRadioOff()- Power-down the Builtin chip.This has to be invoked after stopping the Bluetooth stack
  (see sample).
   
	3.3	How to execute BT Serial.exe
	-------------------------------------
  	Copy BT Serial.exe to your windowsce device & execute.(Before running BT Serial.exe, you need to install 
	avelinkBT SDK for Windows CE.)

4.	Errors
---------------------------------------------
 	In any case of abnormality, reset the windows ce device and try again.

5.	Contact
---------------------------------------------
	100 FRANKLIN SQUARE DRIVE, 
	SUITE # 304, SOMERSET, 
	NEW JERSEY 08873 
	PHONE: 732.412.3000 
	FAX: 732.412.2145 

Email : support@atinav.com

6.	Copyright
---------------------------------------------

(c) 2003-2004 Atinav LLC.  100 Franklin Square Drive, Suite # 304, Somerset, NJ 08873., USA

