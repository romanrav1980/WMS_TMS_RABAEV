<html>
<body>
<pre>
<h1>Build Log</h1>
<h3>
--------------------Configuration: CamCoreDemo - Win32 (WCE ARMV4I) Release--------------------
</h3>
<h3>Command Lines</h3>
Creating command line "rc.exe /l 0x409 /fo"ARMV4IRel/CamCoreDemo.res" /d UNDER_CE=420 /d _WIN32_WCE=420 /d "UNICODE" /d "_UNICODE" /d "NDEBUG" /d "WCE_PLATFORM_MC6KS" /d "THUMB" /d "_THUMB_" /d "ARM" /d "_ARM_" /d "ARMV4I" /d "_AFXDLL" /r "D:\Project\DevLib\M3\CamaraSource\SDK\Build\eVC\Sample\CamCoreDemo.rc"" 
Creating temporary file "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSP9E.tmp" with contents
[
/nologo /W3 /I "..\Include" /D "ARM" /D "_ARM_" /D "ARMV4I" /D UNDER_CE=420 /D _WIN32_WCE=420 /D "WCE_PLATFORM_MC6KS" /D "UNICODE" /D "_UNICODE" /D "NDEBUG" /D "_AFXDLL" /Fo"ARMV4IRel/" /QRarch4T /QRinterwork-return /O2 /MC /c 
"D:\Project\DevLib\M3\CamaraSource\SDK\Build\eVC\Sample\CamCoreDemo.cpp"
"D:\Project\DevLib\M3\CamaraSource\SDK\Build\eVC\Sample\CamCoreDemoDlg.cpp"
]
Creating command line "clarm.exe @C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSP9E.tmp" 
Creating temporary file "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSP9F.tmp" with contents
[
/nologo /W3 /I "..\Include" /D "ARM" /D "_ARM_" /D "ARMV4I" /D UNDER_CE=420 /D _WIN32_WCE=420 /D "WCE_PLATFORM_MC6KS" /D "UNICODE" /D "_UNICODE" /D "NDEBUG" /D "_AFXDLL" /Fp"ARMV4IRel/CamCoreDemo.pch" /Yc"stdafx.h" /Fo"ARMV4IRel/" /QRarch4T /QRinterwork-return /O2 /MC /c 
"D:\Project\DevLib\M3\CamaraSource\SDK\Build\eVC\Sample\StdAfx.cpp"
]
Creating command line "clarm.exe @C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSP9F.tmp" 
Creating temporary file "C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSPA0.tmp" with contents
[
CamCore.lib /nologo /base:"0x00010000" /stack:0x10000,0x1000 /entry:"wWinMainCRTStartup" /incremental:no /pdb:"ARMV4IRel/CamCoreDemo.pdb" /out:"ARMV4IRel/CamCoreDemo.exe" /libpath:"..\Lib" /subsystem:windowsce,4.20 /MACHINE:THUMB 
.\ARMV4IRel\CamCoreDemo.obj
.\ARMV4IRel\CamCoreDemoDlg.obj
.\ARMV4IRel\StdAfx.obj
.\ARMV4IRel\CamCoreDemo.res
]
Creating command line "link.exe @C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\RSPA0.tmp"
<h3>Output Window</h3>
Compiling resources...
Compiling...
StdAfx.cpp
Compiling...
CamCoreDemo.cpp
CamCoreDemoDlg.cpp
Generating Code...
Linking...




<h3>Results</h3>
CamCoreDemo.exe - 0 error(s), 0 warning(s)
</pre>
</body>
</html>
