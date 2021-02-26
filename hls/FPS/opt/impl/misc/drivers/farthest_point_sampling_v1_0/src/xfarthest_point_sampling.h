// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2020.1 (64-bit)
// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef XFARTHEST_POINT_SAMPLING_H
#define XFARTHEST_POINT_SAMPLING_H

#ifdef __cplusplus
extern "C" {
#endif

/***************************** Include Files *********************************/
#ifndef __linux__
#include "xil_types.h"
#include "xil_assert.h"
#include "xstatus.h"
#include "xil_io.h"
#else
#include <stdint.h>
#include <assert.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stddef.h>
#endif
#include "xfarthest_point_sampling_hw.h"

/**************************** Type Definitions ******************************/
#ifdef __linux__
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
#else
typedef struct {
    u16 DeviceId;
    u32 Control_BaseAddress;
} XFarthest_point_sampling_Config;
#endif

typedef struct {
    u32 Control_BaseAddress;
    u32 IsReady;
} XFarthest_point_sampling;

typedef u32 word_type;

/***************** Macros (Inline Functions) Definitions *********************/
#ifndef __linux__
#define XFarthest_point_sampling_WriteReg(BaseAddress, RegOffset, Data) \
    Xil_Out32((BaseAddress) + (RegOffset), (u32)(Data))
#define XFarthest_point_sampling_ReadReg(BaseAddress, RegOffset) \
    Xil_In32((BaseAddress) + (RegOffset))
#else
#define XFarthest_point_sampling_WriteReg(BaseAddress, RegOffset, Data) \
    *(volatile u32*)((BaseAddress) + (RegOffset)) = (u32)(Data)
#define XFarthest_point_sampling_ReadReg(BaseAddress, RegOffset) \
    *(volatile u32*)((BaseAddress) + (RegOffset))

#define Xil_AssertVoid(expr)    assert(expr)
#define Xil_AssertNonvoid(expr) assert(expr)

#define XST_SUCCESS             0
#define XST_DEVICE_NOT_FOUND    2
#define XST_OPEN_DEVICE_FAILED  3
#define XIL_COMPONENT_IS_READY  1
#endif

/************************** Function Prototypes *****************************/
#ifndef __linux__
int XFarthest_point_sampling_Initialize(XFarthest_point_sampling *InstancePtr, u16 DeviceId);
XFarthest_point_sampling_Config* XFarthest_point_sampling_LookupConfig(u16 DeviceId);
int XFarthest_point_sampling_CfgInitialize(XFarthest_point_sampling *InstancePtr, XFarthest_point_sampling_Config *ConfigPtr);
#else
int XFarthest_point_sampling_Initialize(XFarthest_point_sampling *InstancePtr, const char* InstanceName);
int XFarthest_point_sampling_Release(XFarthest_point_sampling *InstancePtr);
#endif

void XFarthest_point_sampling_Start(XFarthest_point_sampling *InstancePtr);
u32 XFarthest_point_sampling_IsDone(XFarthest_point_sampling *InstancePtr);
u32 XFarthest_point_sampling_IsIdle(XFarthest_point_sampling *InstancePtr);
u32 XFarthest_point_sampling_IsReady(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_Continue(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_EnableAutoRestart(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_DisableAutoRestart(XFarthest_point_sampling *InstancePtr);

void XFarthest_point_sampling_Set_in_r(XFarthest_point_sampling *InstancePtr, u64 Data);
u64 XFarthest_point_sampling_Get_in_r(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_Set_out_r(XFarthest_point_sampling *InstancePtr, u64 Data);
u64 XFarthest_point_sampling_Get_out_r(XFarthest_point_sampling *InstancePtr);

void XFarthest_point_sampling_InterruptGlobalEnable(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_InterruptGlobalDisable(XFarthest_point_sampling *InstancePtr);
void XFarthest_point_sampling_InterruptEnable(XFarthest_point_sampling *InstancePtr, u32 Mask);
void XFarthest_point_sampling_InterruptDisable(XFarthest_point_sampling *InstancePtr, u32 Mask);
void XFarthest_point_sampling_InterruptClear(XFarthest_point_sampling *InstancePtr, u32 Mask);
u32 XFarthest_point_sampling_InterruptGetEnabled(XFarthest_point_sampling *InstancePtr);
u32 XFarthest_point_sampling_InterruptGetStatus(XFarthest_point_sampling *InstancePtr);

#ifdef __cplusplus
}
#endif

#endif
