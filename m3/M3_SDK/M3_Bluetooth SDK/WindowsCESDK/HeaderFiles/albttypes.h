/****************************************************************************
* FILE NAME: albttypes.h										 			*
*																 		    *
* MODULE	  : aveLink BT SDK For Windows CE 							    *
*																 		    *
* PURPOSE	: The header file defining datatypes used in					*
*			  core stack implementation	(For use with applications)			*
*			  (c) Atinav										 		    *
*																			*
****************************************************************************/
#ifndef _ALBTTYPES_H
#define _ALBTTYPES_H


#ifndef _INC_WINDOWS  
#include <windows.h>
#define _INC_WINDOWS  
#endif        

#ifdef __cplusplus
extern "C" {
#endif


typedef signed char		INT8, *PINT8;
typedef unsigned char	UINT8, *PUINT8;

typedef signed short	INT16, *PINT16;
typedef unsigned short	UINT16, *PUINT16;
	
//typedef signed long	INT32, *PINT32;	//Already defined for windows(basetsd.h)
//typedef unsigned long	UINT32, *PUINT32;	//Already defined for windows(basetsd.h)

//typedef INT64 has beend defined already in windows
//typedef unsigned char BOOLEAN, *PBOOLEAN; //Already defined for windows(winnt.h)

//typedef void *HANDLE;// Already defined for windows
//typedef void VOID; // Already defined for windows

typedef HANDLE					PBT_EVENT;
typedef FILE                    BT_FILE, *PBT_FILE;

typedef CRITICAL_SECTION		BT_CSECTION, *PBT_CSECTION;

typedef HANDLE					PBT_THREAD;
typedef LPTHREAD_START_ROUTINE	PBT_THREAD_ROUTINE;


#ifndef TRUE
#define TRUE  1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#ifndef NULL
#define NULL 0
#endif



#ifdef __cplusplus
}
#endif 

#endif
