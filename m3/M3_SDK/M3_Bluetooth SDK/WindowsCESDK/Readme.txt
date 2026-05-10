-------------------------------------------------------------------------------
                       aveLinkBT SDK for Windows CE
				  
              (c) 1997-2005 Atinav LLC.  100 Franklin Square Drive
		        Suite # 304, Somerset, NJ 08873., USA
-------------------------------------------------------------------------------


        Abstarct
-------------------------------------------

 			Congratulations!  You have obtained the aveLinkBT SDK for Windows CE. 

The purpose of the aveLinkBT SDK is to provide an easy to use programming interface for developing Bluetooth software.
The SDK provides a high-level abstraction of the Bluetooth Core specifications.Using the SDK, bluetooth 
applications can be written without the knowledge of original Bluetooth specifications.Some of the functions 
provided by the API are identical to the functions described in the Bluetooth Core specifications, others provide
enhanced functionality and still others provide completely new functionality.The API provides a layer of abstraction,
which separates the programmer from the technical details of the Bluetooth stack and the hardware on which it runs.




        Index
-------------------------------------------
  1. Installation/Uninstallation instructions
  2. Version Information	
  3. Installed Components
  4. Other components
  5. Usage
  6. profile Support
  7. Programing Mobile compia Built-in Bluetooth
  8. Errors
  9. Contact
  10. Copyright

1. 	Installation/Uninstallation instructions
------------------------------------------------

Installation
------------

aveLinkBT SDK can be installed using the aveLinkBT setup program. To install, first Connect the PocketPC to your 
personal computer using its craddle and execute the installation file from the Personal Computer.The installation
wizard will pop up and guide you through the installation.

Uninstallation
--------------
Installed components in the desktop PC can be removed from 'Start –> programs –> aveLinkBT -> WindowsCESDK-> UnInstallation' which will uninstall the SDK components from the desktop system.

Installed components in the windows CE device can be removed using RemovePrograms in StartMenu-->Settings-->System  of Windows CE device

2. 	Version Information
----------------------------

Version 2.1.05-CS11017 Build 05DEC01CE-MOBILECOMPIA-BUILTIN-FULL

3.       Installed Components
-------------------------------------------------

The following SDK components will get installed in the windows ce device during the installation process,

   a) The bluetooth SDK interface - albtcore.dll 
   b) Generic object exchange Profile interface  - albtgoep.dll
   c) Lap & Dun profile interface - albtnetprofiles.dll
   d) Lap/Dun utility library - albtconnmgr.dll	
   e) File transfer profile interface - albtftp.dll
   f) Object push profile interface - albtgoep.dll 

 The utility program REGEDIT.exe will be installed in "My Device\aveLinkBT\WindowsCESDK" directory of the windows ce device.


4.       Other components
-------------------------------------------
 API documentation, samplecodes, user libraries and header files that are helpful for SDK progrmming will get installed in the installation folder specified in desktop computer.


5.       Usage
-------------------------------------------
 a) For SDK documentation please refer the APIreferenceguide.chm in the installation directory of the desktop system.
 
 b) For deatils on usage of libraries please refer "getting started"  section in the APIreferenceguide.chm.

  

6.       profile Support
-------------------------------------------

 The SDK supports following core profiles
 
   a) GAP
   b) SDAP
   c) SPP 
   d) Security Manager

 In addition to the core profiles, the SDK also supports the following bluetooth profiles,
   
   a) GOEP
   b) LAP,DUN
   c) FTP
   d) Object Push	    	


7.  Programing Mobile compia Built-in Bluetooth
---------------------------------------------
   
 The following values are relevant for M3 builtin Bluetooth,
 
 HCI UART Port 	: "COM7:"
 HCI TRANSPORT		: TL_BCSP
 HCI BAUDRATE		:	921600
  
 
8.	Errors
---------------------------------------------
 In any case of abnormality, reset the windows CE device and try again.



9.	Contact
---------------------------------------------
	100 FRANKLIN SQUARE DRIVE, 
	SUITE # 304, SOMERSET, 
	NEW JERSEY 08873 
	PHONE: 732.412.3000 
	FAX: 732.412.2145 

Email : support@atinav.com


10.	Copyright
---------------------------------------------

(c) 2003-2004 Atinav LLC.  100 Franklin Square Drive, Suite # 304, Somerset, NJ 08873., USA



 



