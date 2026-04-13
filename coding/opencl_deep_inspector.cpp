#include "opencl_deep_inspector.hpp"
#include <algorithm>
#include <cmath>
#include <iomanip>

namespace OpenCLInspector {

// ============================================================================
// MODULE 1: Discovery Engine
// ============================================================================

class DiscoveryEngine {
public:
    static std::vector<DeviceTopology> discoverAllDevices() {
        std::vector<DeviceTopology> devices;
        
        try {
            std::vector<cl::Platform> platforms;
            cl::Platform::get(&platforms);
            
            for (const auto& platform : platforms) {
                std::vector<cl::Device> platformDevices;
                platform.getDevices(CL_DEVICE_TYPE_ALL, &platformDevices);
                
                for (const auto& device : platformDevices) {
                    DeviceTopology topo = extractTopology(device);
                    topo.platform_name = platform.getInfo<CL_PLATFORM_NAME>();
                    devices.push_back(topo);
                }
            }
        } catch (const cl::Error& e) {
            std::cerr << "OpenCL Error: " << e.what() << std::endl;
        }
        
        return devices;
    }
    
private:
    static DeviceTopology extractTopology(const cl::Device& device) {
        DeviceTopology topo;
        
        topo.name = device.getInfo<CL_DEVICE_NAME>();
        topo.vendor = device.getInfo<CL_DEVICE_VENDOR>();
        topo.type = device.getInfo<CL_DEVICE_TYPE>();
        topo.compute_units = device.getInfo<CL_DEVICE_MAX_COMPUTE_UNITS>();
        topo.max_clock_freq = device.getInfo<CL_DEVICE_MAX_CLOCK_FREQUENCY>();
        
        // SIMD width detection (vendor-specific)
        topo.simd_width = detectSIMDWidth(device);
        
        // Partition properties
        std::vector<cl_device_partition_property> props;
        try {
            device.getInfo(CL_DEVICE_PARTITION_PROPERTIES, &props);
            topo.partition_properties = props;
        } catch (...) {}
        
        // Cache hierarchy
        topo.global_mem_cache_size = device.getInfo<CL_DEVICE_GLOBAL_MEM_CACHE_SIZE>();
        topo.global_mem_cache_type = device.getInfo<CL_DEVICE_GLOBAL_MEM_CACHE_TYPE>();
        
        // Local memory
        topo.local_mem_size = device.getInfo<CL_DEVICE_LOCAL_MEM_SIZE>();
        topo.local_mem_type = device.getInfo<CL_DEVICE_LOCAL_MEM_TYPE>();
        
        // Memory architecture
        topo.global_mem_size = device.getInfo<CL_DEVICE_GLOBAL_MEM_SIZE>();
        topo.max_mem_alloc_size = device.getInfo<CL_DEVICE_MAX_MEM_ALLOC_SIZE>();
        topo.has_unified_memory = detectUnifiedMemory(device);
        
        // Vector widths
        topo.vector_width_float = detectVectorWidth(device, CL_NATIVE_FLOAT);
        topo.vector_width_double = detectVectorWidth(device, CL_DOUBLE);
        topo.vector_width_half = detectVectorWidth(device, CL_HALF);
        
        return topo;
    }
    
    static cl_uint detectSIMDWidth(const cl::Device& device) {
        // NVIDIA: Warp size is 32
        if (device.getInfo<CL_DEVICE_VENDOR_ID>() == 0x10DE) {
            return 32;
        }
        
        // AMD: Wavefront size is 64
        if (device.getInfo<CL_DEVICE_VENDOR_ID>() == 0x1002) {
            return 64;
        }
        
        // Intel: VLM based on device
        if (device.getInfo<CL_DEVICE_VENDOR_ID>() == 0x8086) {
            // Integrated GPUs typically have SIMD8 or SIMD16
            return 16;  // Gen architecture
        }
        
        // FPGA: Usually SIMD1
        if (device.getInfo<CL_DEVICE_TYPE>() == CL_DEVICE_TYPE_ACCELERATOR) {
            return 1;
        }
        
        // Default
        return device.getInfo<CL_DEVICE_PREFERRED_VECTOR_WIDTH_CHAR>();
    }
    
    static bool detectUnifiedMemory(const cl::Device& device) {
        try {
            auto extensions = device.getInfo<CL_DEVICE_EXTENSIONS>();
            return extensions.find("cl_khr_unified_memory") != std::string::npos;
        } catch (...) {
            return false;
        }
    }
    
    static cl_uint detectVectorWidth(const cl::Device& device, cl_uint type) {
        try {
            return device.getInfo<CL_DEVICE_PREFERRED_VECTOR_WIDTH>();
        } catch (...) {
            return 0;
        }
    }
};

// ============================================================================
// MODULE 2: Deep Profiler
// ============================================================================

class DeepProfiler {
public:
    static FeatureMatrix profileDevice(const cl::Device& device) {
        FeatureMatrix matrix;
        
        // FP16 support
        matrix.fp16_support = checkExtension(device, "cl_khr_fp16");
        
        // FP64 support  
        matrix.fp64_support = checkExtension(device, "cl_khr_fp64");
        
        // Atomics
        matrix.int64_atomics = checkExtension(device, "cl_khr_int64_base_atomics");
        
        // Subgroups
        matrix.subgroups = checkExtension(device, "cl_khr_subgroups");
        matrix.subgroup_intel = checkExtension(device, "cl_intel_subgroups");
        
        // Device enqueue
        matrix.device_enqueue = checkExtension(device, "cl_khr_device_enqueue_local_arg_types");
        
        // Pager lock
        matrix.pager_lock = checkExtension(device, "cl_khr_pager_lock");
        
        // SVM (Shared Virtual Memory)
        matrix.svm = checkExtension(device, "cl_khr_svm");
        
        // Critical limits
        matrix.limits["MAX_PARAMETER_SIZE"] = device.getInfo<CL_DEVICE_MAX_PARAMETER_SIZE>();
        matrix.limits["MAX_WORK_GROUP_SIZE"] = device.getInfo<CL_DEVICE_MAX_WORK_GROUP_SIZE>();
        matrix.limits["MAX_WORK_ITEM_DIMENSIONS"] = device.getInfo<CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS>();
        matrix.limits["MAX_CLOCK_FREQUENCY"] = device.getInfo<CL_DEVICE_MAX_CLOCK_FREQUENCY>();
        matrix.limits["GLOBAL_MEM_SIZE"] = device.getInfo<CL_DEVICE_GLOBAL_MEM_SIZE>();
        matrix.limits["LOCAL_MEM_SIZE"] = device.getInfo<CL_DEVICE_LOCAL_MEM_SIZE>();
        
        return matrix;
    }
    
    // Calculate theoretical peak GFLOPS
    static double calculatePeakGFLOPs(const DeviceTopology& topo, int precision) {
        // precision: 16 = FP16, 32 = FP32, 64 = FP64
        double clock_ghz = topo.max_clock_freq / 1000.0;
        
        int simd_units;
        int ops_per_cycle;
        
        // Estimate based on device type
        if (topo.type & CL_DEVICE_TYPE_GPU) {
            simd_units = topo.compute_units;
            ops_per_cycle = 2;  // FMA = 2 ops per cycle
        } else if (topo.type & CL_DEVICE_TYPE_CPU) {
            simd_units = topo.compute_units;
            ops_per_cycle = 8;  // AVX-512 = 8 ops per cycle
        } else {
            simd_units = topo.compute_units;
            ops_per_cycle = 1;
        }
        
        if (precision == 16) return clock_ghz * simd_units * ops_per_cycle * topo.vector_width_half;
        if (precision == 32) return clock_ghz * simd_units * ops_per_cycle * topo.vector_width_float;
        if (precision == 64) return clock_ghz * simd_units * ops_per_cycle * topo.vector_width_double;
        
        return 0.0;
    }
    
private:
    static bool checkExtension(const cl::Device& device, const std::string& ext) {
        try {
            auto extensions = device.getInfo<CL_DEVICE_EXTENSIONS>();
            return extensions.find(ext) != std::string::npos;
        } catch (...) {
            return false;
        }
    }
};

// ============================================================================
// MODULE 3: Optimization Planner
// ============================================================================

class OptimizationPlanner {
public:
    static DeviceRecommendation recommendDevice(
        const std::vector<DeviceTopology>& devices,
        WorkloadType workload) {
        
        DeviceRecommendation rec;
        
        double best_score = 0.0;
        for (const auto& dev : devices) {
            double score = calculateScore(dev, workload);
            if (score > best_score) {
                best_score = score;
                rec.device_name = dev.name;
                rec.recommended_for = workload;
                rec.score = score;
                rec.optimal_local_size = calculateOptimalLocalSize(dev);
                rec.reasoning = generateReasoning(dev, workload, score);
            }
        }
        
        return rec;
    }
    
    static size_t calculateOptimalLocalSize(const DeviceTopology& topo) {
        // For GPUs: Use occupancy formula
        if (topo.type & CL_DEVICE_TYPE_GPU) {
            // Target 75% occupancy
            size_t max_wg = topo.compute_units * 4;  // 4 waves per CU
            
            // Warp-aligned
            if (topo.simd_width == 32) return 256;  // NVIDIA warp
            if (topo.simd_width == 64) return 256;   // AMD wavefront
            
            return std::min<size_t>(max_wg, 256);
        }
        
        // For CPUs: Use core count
        if (topo.type & CL_DEVICE_TYPE_CPU) {
            return std::min<size_t>(topo.compute_units * 4, 64);
        }
        
        // FPGA: Usually 1
        return 1;
    }
    
private:
    static double calculateScore(const DeviceTopology& dev, WorkloadType workload) {
        double score = 0.0;
        
        switch (workload) {
            case WorkloadType::COMPUTE_BOUND:
                score = dev.peak_gflops_fp32 / 1e6;  // Normalize
                break;
            case WorkloadType::MEMORY_BOUND:
                score = dev.global_mem_size / 1e9;  // More memory = better
                break;
            case WorkloadType::LATENCY_SENSITIVE:
                score = dev.max_clock_freq * dev.compute_units;
                break;
            default:
                score = (dev.peak_gflops_fp32 + dev.global_mem_size / 1e9) / 2;
        }
        
        // Normalize to 0-1 range
        return std::min(score / 10.0, 1.0);
    }
    
    static std::string generateReasoning(const DeviceTopology& dev, 
                                         WorkloadType workload, double score) {
        std::string reason;
        
        if (workload == WorkloadType::COMPUTE_BOUND) {
            reason = "Best for compute-bound: " + std::to_string(dev.peak_gflops_fp32) + 
                     " GFLOPS, " + std::to_string(dev.compute_units) + " CUs";
        } else if (workload == WorkloadType::MEMORY_BOUND) {
            reason = "Best for memory-bound: " + std::to_string(dev.global_mem_size / 1e9) +
                     " GB, " + (dev.has_unified_memory ? "Unified" : "Dedicated") + " memory";
        }
        
        return reason;
    }
};

// ============================================================================
// Main Inspector Class
// ============================================================================

class OpenCLDeepInspector {
public:
    void runFullAnalysis() {
        std::cout << "========================================\n";
        std::cout << "  OpenCL Deep Inspector v1.0\n";
        std::cout << "========================================\n\n";
        
        // Discover all devices
        auto devices = DiscoveryEngine::discoverAllDevices();
        
        std::cout << "Found " << devices.size() << " OpenCL device(s)\n\n";
        
        for (size_t i = 0; i < devices.size(); ++i) {
            std::cout << "--- Device " << (i + 1) << " ---\n";
            analyzeDevice(devices[i]);
            std::cout << "\n";
        }
        
        // Generate recommendations
        std::cout << "=== RECOMMENDATIONS ===\n";
        auto rec_compute = OptimizationPlanner::recommendDevice(devices, WorkloadType::COMPUTE_BOUND);
        auto rec_memory = OptimizationPlanner::recommendDevice(devices, WorkloadType::MEMORY_BOUND);
        
        std::cout << "For COMPUTE_BOUND: " << rec_compute.device_name << "\n";
        std::cout << "  Optimal local size: " << rec_compute.optimal_local_size << "\n";
        std::cout << "  Reasoning: " << rec_compute.reasoning << "\n\n";
        
        std::cout << "For MEMORY_BOUND: " << rec_memory.device_name << "\n";
        std::cout << "  Optimal local size: " << rec_memory.optimal_local_size << "\n";
        std::cout << "  Reasoning: " << rec_memory.reasoning << "\n";
    }
    
private:
    void analyzeDevice(const DeviceTopology& dev) {
        // Hardware topology
        std::cout << "Name: " << dev.name << "\n";
        std::cout << "Vendor: " << dev.vendor << "\n";
        std::cout << "Type: " << getDeviceTypeString(dev.type) << "\n";
        std::cout << "Compute Units: " << dev.compute_units << "\n";
        std::cout << "SIMD Width: " << dev.simd_width << "\n";
        std::cout << "Clock: " << dev.max_clock_freq << " MHz\n";
        
        // Memory
        std::cout << "\nMemory Architecture:\n";
        std::cout << "  Global: " << (dev.global_mem_size / 1e9) << " GB\n";
        std::cout << "  Local: " << (dev.local_mem_size / 1e3) << " KB\n";
        std::cout << "  Cache: " << (dev.global_mem_cache_size / 1e3) << " KB\n";
        std::cout << "  Unified Memory: " << (dev.has_unified_memory ? "Yes" : "No") << "\n";
        std::cout << "  Local Mem Type: " << getLocalMemTypeString(dev.local_mem_type) << "\n";
        
        // Peak performance
        std::cout << "\nTheoretical Peak Performance:\n";
        std::cout << "  FP16: " << std::fixed << std::setprecision(2) 
                  << (dev.peak_gflops_fp16 / 1e3) << " TFLOPS\n";
        std::cout << "  FP32: " << (dev.peak_gflops_fp32 / 1e3) << " TFLOPS\n";
        std::cout << "  FP64: " << (dev.peak_gflops_fp64 / 1e3) << " TFLOPS\n";
    }
    
    std::string getDeviceTypeString(cl_device_type type) {
        if (type & CL_DEVICE_TYPE_GPU) return "GPU";
        if (type & CL_DEVICE_TYPE_CPU) return "CPU";
        if (type & CL_DEVICE_TYPE_ACCELERATOR) return "FPGA/DSP";
        return "Unknown";
    }
    
    std::string getLocalMemTypeString(cl_device_local_mem_type type) {
        if (type == CL_LOCAL) return "Dedicated Local";
        if (type == CL_GLOBAL) return "Global";
        return "None";
    }
};

} // namespace OpenCLInspector