// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2020.1 (64-bit)
// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// ==============================================================
/***************************** Include Files *********************************/
#include "xfarthest_point_sampling.h"

/************************** Function Implementation *************************/
#ifndef __linux__
int XFarthest_point_sampling_CfgInitialize(XFarthest_point_sampling *InstancePtr, XFarthest_point_sampling_Config *ConfigPtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(ConfigPtr != NULL);

    InstancePtr->Control_BaseAddress = ConfigPtr->Control_BaseAddress;
    InstancePtr->IsReady = XIL_COMPONENT_IS_READY;

    return XST_SUCCESS;
}
#endif

void XFarthest_point_sampling_Start(XFarthest_point_sampling *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL) & 0x80;
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL, Data | 0x01);
}

u32 XFarthest_point_sampling_IsDone(XFarthest_point_sampling *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL);
    return (Data >> 1) & 0x1;
}

u32 XFarthest_point_sampling_IsIdle(XFarthest_point_sampling *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL);
    return (Data >> 2) & 0x1;
}

u32 XFarthest_point_sampling_IsReady(XFarthest_point_sampling *InstancePtr) {
    u32 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL);
    // check ap_start to see if the pcore is ready for next input
    return !(Data & 0x1);
}

void XFarthest_point_sampling_Continue(XFarthest_point_sampling *InstancePtr) {
    u32 Data;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL) & 0x80;
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL, Data | 0x10);
}

void XFarthest_point_sampling_EnableAutoRestart(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL, 0x80);
}

void XFarthest_point_sampling_DisableAutoRestart(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_AP_CTRL, 0);
}

void XFarthest_point_sampling_Set_in_r(XFarthest_point_sampling *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IN_R_DATA, (u32)(Data));
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IN_R_DATA + 4, (u32)(Data >> 32));
}

u64 XFarthest_point_sampling_Get_in_r(XFarthest_point_sampling *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IN_R_DATA);
    Data += (u64)XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IN_R_DATA + 4) << 32;
    return Data;
}

void XFarthest_point_sampling_Set_out_r(XFarthest_point_sampling *InstancePtr, u64 Data) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_OUT_R_DATA, (u32)(Data));
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_OUT_R_DATA + 4, (u32)(Data >> 32));
}

u64 XFarthest_point_sampling_Get_out_r(XFarthest_point_sampling *InstancePtr) {
    u64 Data;

    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Data = XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_OUT_R_DATA);
    Data += (u64)XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_OUT_R_DATA + 4) << 32;
    return Data;
}

void XFarthest_point_sampling_InterruptGlobalEnable(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_GIE, 1);
}

void XFarthest_point_sampling_InterruptGlobalDisable(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_GIE, 0);
}

void XFarthest_point_sampling_InterruptEnable(XFarthest_point_sampling *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IER);
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IER, Register | Mask);
}

void XFarthest_point_sampling_InterruptDisable(XFarthest_point_sampling *InstancePtr, u32 Mask) {
    u32 Register;

    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    Register =  XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IER);
    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IER, Register & (~Mask));
}

void XFarthest_point_sampling_InterruptClear(XFarthest_point_sampling *InstancePtr, u32 Mask) {
    Xil_AssertVoid(InstancePtr != NULL);
    Xil_AssertVoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    XFarthest_point_sampling_WriteReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_ISR, Mask);
}

u32 XFarthest_point_sampling_InterruptGetEnabled(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_IER);
}

u32 XFarthest_point_sampling_InterruptGetStatus(XFarthest_point_sampling *InstancePtr) {
    Xil_AssertNonvoid(InstancePtr != NULL);
    Xil_AssertNonvoid(InstancePtr->IsReady == XIL_COMPONENT_IS_READY);

    return XFarthest_point_sampling_ReadReg(InstancePtr->Control_BaseAddress, XFARTHEST_POINT_SAMPLING_CONTROL_ADDR_ISR);
}

