/*
 * OpenCL Deep Inspector
 * Compiled with: gcc opencl_deep_inspector.c -o opencl_inspector -lOpenCL
 */

#include <CL/cl.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_PLATFORMS 16
#define MAX_DEVICES 64
#define MAX_INFO 4096

// ============================================================================
// MODULE 1: Discovery Engine
// ============================================================================

typedef struct {
    cl_device_id id;
    char name[256];
    char vendor[256];
    cl_device_type type;
    cl_uint compute_units;
    cl_uint simd_width;
    cl_uint max_clock_freq;
    
    // Memory
    cl_ulong global_mem_size;
    cl_ulong local_mem_size;
    cl_ulong global_mem_cache_size;
    cl_device_local_mem_type local_mem_type;
    cl_bool has_unified_memory;
    
    // Vector widths
    cl_uint vector_width_char;
    cl_uint vector_width_short;
    cl_uint vector_width_int;
    cl_uint vector_width_long;
    cl_uint vector_width_float;
    cl_uint vector_width_double;
    cl_uint vector_width_half;
    
    // Limits
    size_t max_work_group_size;
    cl_uint max_work_item_dimensions;
    size_t max_work_item_sizes[3];
    size_t max_parameter_size;
    
    // Feature flags
    cl_bool fp16_support;
    cl_bool fp64_support;
    cl_bool int64_atomics;
    cl_bool subgroups;
    cl_bool svm;
    
    // Partition
    cl_uint partition_max_sub_devices;
    cl_device_partition_property partition_properties[16];
    
} DeviceInfo;

int discoverDevices(DeviceInfo* devices, int* count) {
    cl_platform_id platforms[MAX_PLATFORMS];
    cl_uint num_platforms = 0;
    
    clGetPlatformIDs(MAX_PLATFORMS, platforms, &num_platforms);
    printf("Found %d OpenCL platform(s)\n\n", num_platforms);
    
    int idx = 0;
    
    for (int p = 0; p < (int)num_platforms && idx < MAX_DEVICES; p++) {
        char platform_name[256];
        clGetPlatformInfo(platforms[p], CL_PLATFORM_NAME, sizeof(platform_name), platform_name, NULL);
        
        cl_device_id platform_devices[MAX_DEVICES];
        cl_uint num_devices = 0;
        
        clGetDeviceIDs(platforms[p], CL_DEVICE_TYPE_ALL, MAX_DEVICES, platform_devices, &num_devices);
        
        for (int d = 0; d < (int)num_devices && idx < MAX_DEVICES; d++) {
            DeviceInfo* dev = &devices[idx];
            memset(dev, 0, sizeof(DeviceInfo));
            dev->id = platform_devices[d];
            
            // Basic info
            clGetDeviceInfo(dev->id, CL_DEVICE_NAME, sizeof(dev->name), dev->name, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_VENDOR, sizeof(dev->vendor), dev->vendor, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_TYPE, sizeof(cl_device_type), &dev->type, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_COMPUTE_UNITS, sizeof(cl_uint), &dev->compute_units, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_CLOCK_FREQUENCY, sizeof(cl_uint), &dev->max_clock_freq, NULL);
            
            // SIMD Width (vendor-specific)
            cl_uint vendor_id;
            clGetDeviceInfo(dev->id, CL_DEVICE_VENDOR_ID, sizeof(cl_uint), &vendor_id, NULL);
            
            if (vendor_id == 0x10DE) {        // NVIDIA
                dev->simd_width = 32;  // Warp size
            } else if (vendor_id == 0x1002) { // AMD
                dev->simd_width = 64;  // Wavefront size
            } else if (vendor_id == 0x8086) { // Intel
                dev->simd_width = 16;  // Gen architecture
            } else {
                clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR, sizeof(cl_uint), &dev->simd_width, NULL);
            }
            
            // Memory architecture
            clGetDeviceInfo(dev->id, CL_DEVICE_GLOBAL_MEM_SIZE, sizeof(cl_ulong), &dev->global_mem_size, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_LOCAL_MEM_SIZE, sizeof(cl_ulong), &dev->local_mem_size, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_GLOBAL_MEM_CACHE_SIZE, sizeof(cl_ulong), &dev->global_mem_cache_size, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_LOCAL_MEM_TYPE, sizeof(cl_device_local_mem_type), &dev->local_mem_type, NULL);
            
            // Unified memory check
            char extensions[8192];
            clGetDeviceInfo(dev->id, CL_DEVICE_EXTENSIONS, sizeof(extensions), extensions, NULL);
            dev->has_unified_memory = (strstr(extensions, "cl_khr_unified_memory") != NULL);
            
            // Vector widths
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR, sizeof(cl_uint), &dev->vector_width_char, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_SHORT, sizeof(cl_uint), &dev->vector_width_short, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_INT, sizeof(cl_uint), &dev->vector_width_int, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_LONG, sizeof(cl_uint), &dev->vector_width_long, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_FLOAT, sizeof(cl_uint), &dev->vector_width_float, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_DOUBLE, sizeof(cl_uint), &dev->vector_width_double, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PREFERRED_VECTOR_WIDTH_HALF, sizeof(cl_uint), &dev->vector_width_half, NULL);
            
            // Limits
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_WORK_GROUP_SIZE, sizeof(size_t), &dev->max_work_group_size, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS, sizeof(cl_uint), &dev->max_work_item_dimensions, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_PARAMETER_SIZE, sizeof(size_t), &dev->max_parameter_size, NULL);
            
            // Clear work item sizes first
            for (int i = 0; i < 3; i++) dev->max_work_item_sizes[i] = 0;
            clGetDeviceInfo(dev->id, CL_DEVICE_MAX_WORK_ITEM_SIZES, sizeof(dev->max_work_item_sizes), dev->max_work_item_sizes, NULL);
            
            // Feature support
            dev->fp16_support = (strstr(extensions, "cl_khr_fp16") != NULL);
            dev->fp64_support = (strstr(extensions, "cl_khr_fp64") != NULL);
            dev->int64_atomics = (strstr(extensions, "cl_khr_int64_base_atomics") != NULL);
            dev->subgroups = (strstr(extensions, "cl_khr_subgroups") != NULL);
            dev->svm = (strstr(extensions, "cl_khr_svm") != NULL);
            
            // Partition
            clGetDeviceInfo(dev->id, CL_DEVICE_PARTITION_MAX_SUB_DEVICES, sizeof(cl_uint), &dev->partition_max_sub_devices, NULL);
            clGetDeviceInfo(dev->id, CL_DEVICE_PARTITION_PROPERTIES, sizeof(dev->partition_properties), dev->partition_properties, NULL);
            
            printf("[%d] %s (%s)\n", idx + 1, dev->name, platform_name);
            idx++;
        }
    }
    
    *count = idx;
    return 0;
}

// ============================================================================
// MODULE 2: Deep Profiler
// ============================================================================

double calculatePeakGFLOPs(DeviceInfo* dev, int precision) {
    // precision: 16 = FP16, 32 = FP32, 64 = FP64
    double clock_ghz = dev->max_clock_freq / 1000.0;
    
    int ops_per_cycle;
    if (dev->type & CL_DEVICE_TYPE_GPU) {
        ops_per_cycle = 2;  // FMA = 2 ops per cycle
    } else if (dev->type & CL_DEVICE_TYPE_CPU) {
        ops_per_cycle = 8;   // AVX-512
    } else {
        ops_per_cycle = 1;
    }
    
    int vector_width;
    if (precision == 16) vector_width = dev->vector_width_half;
    else if (precision == 32) vector_width = dev->vector_width_float;
    else if (precision == 64) vector_width = dev->vector_width_double;
    else vector_width = 1;
    
    double gflops = clock_ghz * dev->compute_units * ops_per_cycle * vector_width;
    return gflops;
}

void printDeviceProfile(DeviceInfo* dev, int index) {
    printf("\n");
    printf("================================================================================\n");
    printf("DEVICE %d: %s\n", index + 1, dev->name);
    printf("================================================================================\n");
    
    // Vendor and type
    printf("\n[ Hardware Topology ]\n");
    printf("  Vendor:       %s\n", dev->vendor);
    printf("  Type:         ");
    if (dev->type & CL_DEVICE_TYPE_GPU) printf("GPU\n");
    else if (dev->type & CL_DEVICE_TYPE_CPU) printf("CPU\n");
    else if (dev->type & CL_DEVICE_TYPE_ACCELERATOR) printf("FPGA/DSP/Accelerator\n");
    else printf("Unknown\n");
    
    printf("  Compute Units: %u\n", dev->compute_units);
    printf("  SIMD Width:    %u\n", dev->simd_width);
    printf("  Clock:         %u MHz\n", dev->max_clock_freq);
    
    // Partition info
    if (dev->partition_max_sub_devices > 1) {
        printf("  Partition:     %u sub-devices supported\n", dev->partition_max_sub_devices);
    }
    
    // Memory architecture
    printf("\n[ Memory Architecture ]\n");
    printf("  Global Memory:     %lu MB\n", dev->global_mem_size / (1024 * 1024));
    printf("  Local Memory:      %lu KB\n", dev->local_mem_size / 1024);
    printf("  Global Cache:      %lu KB\n", dev->global_mem_cache_size / 1024);
    printf("  Local Mem Type:   %s\n", dev->local_mem_type == CL_LOCAL ? "Dedicated Local" : 
                                         dev->local_mem_type == CL_GLOBAL ? "Global" : "None");
    printf("  Unified Memory:    %s\n", dev->has_unified_memory ? "YES (SVM)" : "No (Dedicated VRAM)");
    
    // Vector widths
    printf("\n[ Vector Widths ]\n");
    printf("  CHAR:  %u | SHORT: %u | INT: %u | LONG: %u\n",
           dev->vector_width_char, dev->vector_width_short, dev->vector_width_int, dev->vector_width_long);
    printf("  FLOAT: %u | DOUBLE: %u | HALF: %u\n",
           dev->vector_width_float, dev->vector_width_double, dev->vector_width_half);
    
    // Peak performance
    printf("\n[ Kernel Potential - Theoretical Peak ]\n");
    double fp16 = calculatePeakGFLOPs(dev, 16);
    double fp32 = calculatePeakGFLOPs(dev, 32);
    double fp64 = calculatePeakGFLOPs(dev, 64);
    printf("  FP16 (half):   %8.2f GFLOPS (%6.2f TFLOPS)\n", fp16, fp16 / 1000);
    printf("  FP32 (float):  %8.2f GFLOPS (%6.2f TFLOPS)\n", fp32, fp32 / 1000);
    printf("  FP64 (double): %8.2f GFLOPS (%6.2f TFLOPS)\n", fp64, fp64 / 1000);
    
    // Limits
    printf("\n[ Critical Limits ]\n");
    printf("  MAX_WORK_GROUP_SIZE:    %zu\n", dev->max_work_group_size);
    printf("  MAX_WORK_ITEM_DIMENSIONS: %u\n", dev->max_work_item_dimensions);
    printf("  MAX_WORK_ITEM_SIZES:    [%zu, %zu, %zu]\n", 
           dev->max_work_item_sizes[0], dev->max_work_item_sizes[1], dev->max_work_item_sizes[2]);
    printf("  MAX_PARAMETER_SIZE:     %zu bytes\n", dev->max_parameter_size);
    
    // Feature matrix
    printf("\n[ Feature Matrix ]\n");
    printf("  cl_khr_fp16:              %s\n", dev->fp16_support ? "SUPPORTED" : "NOT SUPPORTED");
    printf("  cl_khr_fp64:              %s\n", dev->fp64_support ? "SUPPORTED" : "NOT SUPPORTED");
    printf("  cl_khr_int64_base_atomics:%s\n", dev->int64_atomics ? "SUPPORTED" : "NOT SUPPORTED");
    printf("  cl_khr_subgroups:         %s\n", dev->subgroups ? "SUPPORTED" : "NOT SUPPORTED");
    printf("  cl_khr_svm:               %s\n", dev->svm ? "SUPPORTED" : "NOT SUPPORTED");
}

// ============================================================================
// MODULE 3: Optimization Planner
// ============================================================================

typedef enum {
    COMPUTE_BOUND,
    MEMORY_BOUND,
    MIXED,
    LATENCY_SENSITIVE
} WorkloadType;

const char* workloadNames[] = {"COMPUTE_BOUND", "MEMORY_BOUND", "MIXED", "LATENCY_SENSITIVE"};

size_t calculateOptimalLocalSize(DeviceInfo* dev) {
    if (dev->type & CL_DEVICE_TYPE_GPU) {
        // GPU: Target 75% occupancy, warp-aligned
        if (dev->simd_width == 32) return 256;  // NVIDIA warp
        if (dev->simd_width == 64) return 256;   // AMD wavefront
        return 128;  // Default
    }
    if (dev->type & CL_DEVICE_TYPE_CPU) {
        // CPU: Use core count * 4, max 64
        int optimal = dev->compute_units * 4;
        return optimal > 64 ? 64 : optimal;
    }
    return 1;  // FPGA/DSP
}

void recommendDevice(DeviceInfo* devices, int count, WorkloadType type) {
    printf("\n");
    printf("================================================================================\n");
    printf("OPTIMIZATION PLAN: %s\n", workloadNames[type]);
    printf("================================================================================\n\n");
    
    int best_idx = 0;
    double best_score = 0;
    
    for (int i = 0; i < count; i++) {
        DeviceInfo* dev = &devices[i];
        double score = 0;
        
        switch (type) {
            case COMPUTE_BOUND:
                score = calculatePeakGFLOPs(dev, 32) / 1000.0;
                break;
            case MEMORY_BOUND:
                score = dev->global_mem_size / (1024.0 * 1024.0 * 1024.0);  // GB
                break;
            case LATENCY_SENSITIVE:
                score = dev->max_clock_freq * dev->compute_units;
                break;
            default:
                score = (calculatePeakGFLOPs(dev, 32) / 1000.0 + dev->global_mem_size / (1024.0*1024.0*1024.0)) / 2;
        }
        
        if (score > best_score) {
            best_score = score;
            best_idx = i;
        }
    }
    
    DeviceInfo* best = &devices[best_idx];
    size_t optimal_local = calculateOptimalLocalSize(best);
    
    printf("  Recommended Device:   %s\n", best->name);
    printf("  Score:               %.2f\n", best_score);
    printf("  Optimal local_size:  %zu\n", optimal_local);
    
    // Hardware-specific advice
    cl_uint vendor_id;
    clGetDeviceInfo(best->id, CL_DEVICE_VENDOR_ID, sizeof(cl_uint), &vendor_id, NULL);
    
    printf("\n  Hardware-specific advice:\n");
    if (vendor_id == 0x10DE) {  // NVIDIA
        printf("    - NVIDIA: Warp size = 32, use local_size multiple of 32\n");
        printf("    - Max work group size: %zu\n", best->max_work_group_size);
        printf("    - Registers per thread affects occupancy\n");
    } else if (vendor_id == 0x1002) {  // AMD
        printf("    - AMD: Wavefront size = 64, use local_size multiple of 64\n");
        printf("    - LDS (Local Data Share) is fast, use for data reuse\n");
        printf("    - Avoid exceeding 256 work-items per group on GCN\n");
    } else if (vendor_id == 0x8086) {  // Intel
        printf("    - Intel Integrated: Beware EU saturation limits\n");
        printf("    - Gen8+ supports >= 16 wide SIMD\n");
        printf("    - Subgroups for vectorization help\n");
    }
    
    // Memory-bound specific
    if (type == MEMORY_BOUND) {
        printf("\n  Memory optimization:\n");
        if (best->has_unified_memory) {
            printf("    - SVM available: Use shared virtual memory\n");
            printf("    - Host-device transfers minimized\n");
        } else {
            printf("    - Dedicated VRAM: Minimize host-device transfers\n");
            printf("    - Use pinned memory for bulk transfers\n");
        }
        if (best->global_mem_cache_size > 0) {
            printf("    - L3 cache: %lu KB — exploit for data reuse\n", best->global_mem_cache_size / 1024);
        }
    }
    
    printf("\n  Mathematical optimization for local_work_size:\n");
    printf("    - Target: occupancy = (local_size * 4) / compute_units\n");
    printf("    - Optimal: %zu (based on %u CUs, SIMD=%u)\n", 
           optimal_local, best->compute_units, best->simd_width);
}

// ============================================================================
// MAIN
// ============================================================================

int main() {
    printf("\n");
    printf("################################################################################\n");
    printf("#                                                                              #\n");
    printf("#                        OpenCL Deep Inspector v1.0                           #\n");
    printf("#                   Heterogenes Computing - Hardware Analyse                  #\n");
    printf("#                                                                              #\n");
    printf("################################################################################\n\n");
    
    DeviceInfo devices[MAX_DEVICES];
    int count = 0;
    
    int err = discoverDevices(devices, &count);
    if (err || count == 0) {
        printf("No OpenCL devices found or error occurred.\n");
        return 1;
    }
    
    printf("\n%d device(s) discovered.\n\n", count);
    
    // Profile all devices
    for (int i = 0; i < count; i++) {
        printDeviceProfile(&devices[i], i);
    }
    
    // Generate optimization plans
    printf("\n\n");
    recommendDevice(devices, count, COMPUTE_BOUND);
    recommendDevice(devices, count, MEMORY_BOUND);
    recommendDevice(devices, count, LATENCY_SENSITIVE);
    
    printf("\n################################################################################\n");
    printf("#                           Analysis Complete                                 #\n");
    printf("################################################################################\n\n");
    
    return 0;
}