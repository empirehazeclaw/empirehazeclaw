#pragma once
#define CL_HPP_ENABLE_EXCEPTIONS
#define CL_HPP_TARGET_OPENCL_VERSION 120
#define CL_HPP_MINIMUM_OPENCL_VERSION 120
#include <CL/cl2.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <map>

namespace OpenCLInspector {

// Hardware Topology Data
struct DeviceTopology {
    std::string name;
    std::string vendor;
    cl_device_type type;
    cl_uint compute_units;
    cl_uint simd_width;
    cl_uint max_clock_freq;
    
    // Partition properties
    std::vector<cl_device_partition_property> partition_properties;
    std::vector<cl_device_partition_property> partition_type;
    
    // Cache hierarchy
    cl_ulong global_mem_cache_size;
    cl_ulong global_mem_cache_type;  // Read-Only, Write-Only, or None
    cl_ulong local_mem_size;
    cl_device_local_mem_type local_mem_type;
    
    // Memory architecture
    cl_ulong global_mem_size;
    cl_ulong max_mem_alloc_size;
    bool has_unified_memory;
    
    // Compute capabilities
    cl_uint vector_width_float;
    cl_uint vector_width_double;
    cl_uint vector_width_half;
    
    // Peak performance
    double peak_gflops_fp16;
    double peak_gflops_fp32;
    double peak_gflops_fp64;
};

// Feature support matrix
struct FeatureMatrix {
    bool fp16_support;
    bool fp64_support;
    bool int64_atomics;
    bool subgroups;
    bool subgroup_intel;
    bool device_enqueue;
    bool pager_lock;
    bool svm;
    
    std::map<std::string, bool> extensions;
    std::map<std::string, size_t> limits;
};

// Device recommendation
enum class WorkloadType {
    COMPUTE_BOUND,
    MEMORY_BOUND,
    MIXED,
    LATENCY_SENSITIVE
};

struct DeviceRecommendation {
    std::string device_name;
    WorkloadType recommended_for;
    size_t optimal_local_size;
    double score;  // 0.0 - 1.0
    std::string reasoning;
};

} // namespace OpenCLInspector