<html>
<body>
<pre>
<h1>Build Log</h1>
<h3>
--------------------Configuration: WlanSample - Win32 (WCE ARMV4I) Release--------------------
</h3>
<h3>Command Lines</h3>
Creating command line "rc.exe /l 0x409 /fo"ARMV4IRel/WlanSample.res" /d UNDER_CE=420 /d _WIN32_WCE=420 /d "UNICODE" /d "_UNICODE" /d "NDEBUG" /d "WCE_PLATFORM_MC6KS" /d "THUMB" /d "_THUMB_" /d "ARM" /d "_ARM_" /d "ARMV4I" /d "_AFXDLL" /r "E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\WlanSample.rc"" 
Creating temporary file "C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5BE.tmp" with contents
[
/nologo /W3 /D "ARM" /D "_ARM_" /D "ARMV4I" /D UNDER_CE=420 /D _WIN32_WCE=420 /D "WCE_PLATFORM_MC6KS" /D "UNICODE" /D "_UNICODE" /D "NDEBUG" /D "_AFXDLL" /FR"ARMV4IRel/" /Fp"ARMV4IRel/WlanSample.pch" /Yu"stdafx.h" /Fo"ARMV4IRel/" /QRarch4T /QRinterwork-return /O2 /MC /c 
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\AboutPage.cpp"
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\AssociatedPage.cpp"
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\BssidListPage.cpp"
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\WlanSample.cpp"
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\WlanSampleSheet.cpp"
]
Creating command line "clarm.exe @C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5BE.tmp" 
Creating temporary file "C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5BF.tmp" with contents
[
/nologo /W3 /D "ARM" /D "_ARM_" /D "ARMV4I" /D UNDER_CE=420 /D _WIN32_WCE=420 /D "WCE_PLATFORM_MC6KS" /D "UNICODE" /D "_UNICODE" /D "NDEBUG" /D "_AFXDLL" /FR"ARMV4IRel/" /Fp"ARMV4IRel/WlanSample.pch" /Yc"stdafx.h" /Fo"ARMV4IRel/" /QRarch4T /QRinterwork-return /O2 /MC /c 
"E:\SDK\Release\M3_Wlan_SDK_20060116\eVC\Sample\StdAfx.cpp"
]
Creating command line "clarm.exe @C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5BF.tmp" 
Creating temporary file "C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5C0.tmp" with contents
[
../Lib/WlanUtil.lib /nologo /base:"0x00010000" /stack:0x10000,0x1000 /entry:"wWinMainCRTStartup" /incremental:no /pdb:"ARMV4IRel/WlanSample.pdb" /out:"ARMV4IRel/WlanSample.exe" /subsystem:windowsce,4.20 /MACHINE:THUMB 
.\ARMV4IRel\AboutPage.obj
.\ARMV4IRel\AssociatedPage.obj
.\ARMV4IRel\BssidListPage.obj
.\ARMV4IRel\StdAfx.obj
.\ARMV4IRel\WlanSample.obj
.\ARMV4IRel\WlanSampleSheet.obj
.\ARMV4IRel\WlanSample.res
]
Creating command line "link.exe @C:\DOCUME~1\AKAI~1.SEG\LOCALS~1\Temp\RSP5C0.tmp"
<h3>Output Window</h3>
Compiling resources...
Compiling...
StdAfx.cpp
Compiling...
AboutPage.cpp
AssociatedPage.cpp
BssidListPage.cpp
WlanSample.cpp
WlanSampleSheet.cpp
Generating Code...
Linking...
Creating command line "bscmake.exe /nologo /o"ARMV4IRel/WlanSample.bsc"  .\ARMV4IRel\StdAfx.sbr .\ARMV4IRel\AboutPage.sbr .\ARMV4IRel\AssociatedPage.sbr .\ARMV4IRel\BssidListPage.sbr .\ARMV4IRel\WlanSample.sbr .\ARMV4IRel\WlanSampleSheet.sbr"
Creating browse info file...
<h3>Output Window</h3>




<h3>Results</h3>
WlanSample.exe - 0 error(s), 0 warning(s)
</pre>
</body>
</html>
