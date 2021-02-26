// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2020.1 (64-bit)
// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// ==============================================================
#ifndef __linux__

#include "xstatus.h"
#include "xparameters.h"
#include "xfarthest_point_sampling.h"

extern XFarthest_point_sampling_Config XFarthest_point_sampling_ConfigTable[];

XFarthest_point_sampling_Config *XFarthest_point_sampling_LookupConfig(u16 DeviceId) {
	XFarthest_point_sampling_Config *ConfigPtr = NULL;

	int Index;

	for (Index = 0; Index < XPAR_XFARTHEST_POINT_SAMPLING_NUM_INSTANCES; Index++) {
		if (XFarthest_point_sampling_ConfigTable[Index].DeviceId == DeviceId) {
			ConfigPtr = &XFarthest_point_sampling_ConfigTable[Index];
			break;
		}
	}

	return ConfigPtr;
}

int XFarthest_point_sampling_Initialize(XFarthest_point_sampling *InstancePtr, u16 DeviceId) {
	XFarthest_point_sampling_Config *ConfigPtr;

	Xil_AssertNonvoid(InstancePtr != NULL);

	ConfigPtr = XFarthest_point_sampling_LookupConfig(DeviceId);
	if (ConfigPtr == NULL) {
		InstancePtr->IsReady = 0;
		return (XST_DEVICE_NOT_FOUND);
	}

	return XFarthest_point_sampling_CfgInitialize(InstancePtr, ConfigPtr);
}

#endif

