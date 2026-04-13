#!/usr/bin/env python3
"""
OpenCL Deep Inspector v1.0
Heterogenes Computing - Hardware Analyse Tool

Erstellt von Sir HazeClaw für HPC/OpenCL System-Analyse.
Kompiliert mit Python + pyopencl für maximale Portabilität.

Usage:
    python3 opencl_deep_inspector.py
"""

import sys
import os

# Add virtual environment to path
VENV_PATH = "/home/clawbot/opencl_env"
if os.path.exists(VENV_PATH):
    sys.path.insert(0, os.path.join(VENV_PATH, "lib", "python3.12", "site-packages"))

import pyopencl as cl
import json
from typing import List, Dict, Tuple

# ============================================================================
# MODULE 1: Discovery Engine
# ============================================================================

class DiscoveryEngine:
    """Entdeckt alle OpenCL Plattformen und Devices."""
    
    @staticmethod
    def discoverAllDevices() -> List[Dict]:
        """Iteriert alle Plattformen und extrahiert maximale Info."""
        devices = []
        
        try:
            platforms = cl.get_platforms()
            print(f"Found {len(platforms)} OpenCL platform(s)\n")
            
            for platform_idx, platform in enumerate(platforms):
                platform_name = platform.name
                try:
                    platform_devices = platform.get_devices()
                except:
                    continue
                
                for device_idx, device in enumerate(platform_devices):
                    device_info = DiscoveryEngine._extractDeviceInfo(device, platform_name)
                    device_info['platform_index'] = platform_idx
                    device_info['device_index'] = device_idx
                    devices.append(device_info)
                    
        except Exception as e:
            print(f"Error during discovery: {e}")
        
        return devices
    
    @staticmethod
    def _extractDeviceInfo(device, platform_name: str) -> Dict:
        """Extrahiert alle verfügbaren Device-Informationen."""
        info = {
            'name': device.name,
            'vendor': device.vendor,
            'platform': platform_name,
            'type': str(device.type),
        }
        
        # Basic hardware
        info['compute_units'] = device.max_compute_units
        info['max_clock_frequency'] = device.max_clock_frequency
        
        # SIMD Width detection (vendor-specific)
        info['simd_width'] = DiscoveryEngine._detectSIMDWidth(device)
        
        # Partition properties
        try:
            info['partition_properties'] = list(device.partition_properties)
            info['partition_max_sub_devices'] = device.partition_max_sub_devices
        except:
            info['partition_properties'] = []
            info['partition_max_sub_devices'] = 0
        
        # Cache hierarchy
        info['global_mem_cache_size'] = device.global_mem_cache_size
        info['global_mem_cache_type'] = str(device.global_mem_cache_type)
        
        # Local memory
        info['local_mem_size'] = device.local_mem_size
        info['local_mem_type'] = str(device.local_mem_type)
        
        # Memory architecture
        info['global_mem_size'] = device.global_mem_size
        info['max_mem_alloc_size'] = device.max_mem_alloc_size
        info['has_unified_memory'] = 'cl_khr_unified_memory' in device.extensions
        
        # Vector widths
        info['vector_width_char'] = device.preferred_vector_width_char
        info['vector_width_short'] = device.preferred_vector_width_short
        info['vector_width_int'] = device.preferred_vector_width_int
        info['vector_width_long'] = device.preferred_vector_width_long
        info['vector_width_float'] = device.preferred_vector_width_float
        info['vector_width_double'] = device.preferred_vector_width_double
        info['vector_width_half'] = device.preferred_vector_width_half
        
        # Limits
        info['max_work_group_size'] = device.max_work_group_size
        info['max_work_item_dimensions'] = device.max_work_item_dimensions
        info['max_work_item_sizes'] = list(device.max_work_item_sizes)
        info['max_parameter_size'] = device.max_parameter_size
        
        # Feature matrix
        exts = device.extensions
        info['fp16_support'] = 'cl_khr_fp16' in exts
        info['fp64_support'] = 'cl_khr_fp64' in exts
        info['int64_atomics'] = 'cl_khr_int64_base_atomics' in exts
        info['subgroups'] = 'cl_khr_subgroups' in exts
        info['svm'] = 'cl_khr_svm' in exts
        info['extensions'] = exts.split()
        
        return info
    
    @staticmethod
    def _detectSIMDWidth(device) -> int:
        """Erkennt SIMD-Breite basierend auf Vendor."""
        vendor_id = device.vendor_id
        
        # NVIDIA: Warp size = 32
        if vendor_id == 0x10DE:
            return 32
        # AMD: Wavefront size = 64
        if vendor_id == 0x1002:
            return 64
        # Intel: Gen architecture typically 16
        if vendor_id == 0x8086:
            return 16
        # FPGA/DSP: Usually 1
        if 'Accelerator' in str(device.type) or 'Custom' in str(device.type):
            return 1
        
        # Fallback: use preferred vector width
        return device.preferred_vector_width_char

# ============================================================================
# MODULE 2: Deep Profiler
# ============================================================================

class DeepProfiler:
    """Analysiert spezifische Limits und Feature-Support."""
    
    @staticmethod
    def profileDevice(device_info: Dict) -> Dict:
        """Erstellt vollständige Feature-Matrix."""
        profile = {
            'limits': {},
            'features': {},
            'peak_gflops': {}
        }
        
        # Critical limits
        profile['limits']['MAX_WORK_GROUP_SIZE'] = device_info['max_work_group_size']
        profile['limits']['MAX_WORK_ITEM_DIMENSIONS'] = device_info['max_work_item_dimensions']
        profile['limits']['MAX_WORK_ITEM_SIZES'] = device_info['max_work_item_sizes']
        profile['limits']['MAX_PARAMETER_SIZE'] = device_info['max_parameter_size']
        profile['limits']['MAX_CLOCK_FREQUENCY'] = device_info['max_clock_frequency']
        profile['limits']['GLOBAL_MEM_SIZE_BYTES'] = device_info['global_mem_size']
        profile['limits']['LOCAL_MEM_SIZE_BYTES'] = device_info['local_mem_size']
        
        # Features
        profile['features']['fp16'] = device_info['fp16_support']
        profile['features']['fp64'] = device_info['fp64_support']
        profile['features']['int64_atomics'] = device_info['int64_atomics']
        profile['features']['subgroups'] = device_info['subgroups']
        profile['features']['svm_unified_memory'] = device_info['svm']
        
        # Peak GFLOPS
        profile['peak_gflops'] = DeepProfiler.calculatePeakGFLOPs(device_info)
        
        return profile
    
    @staticmethod
    def calculatePeakGFLOPs(device_info: Dict) -> Dict:
        """Berechnet theoretische Peak-Performance für FP16/FP32/FP64."""
        clock_ghz = device_info['max_clock_frequency'] / 1000.0
        compute_units = device_info['compute_units']
        device_type = device_info['type']
        
        # Ops per cycle: FMA = 2 ops
        if 'GPU' in device_type:
            ops_per_cycle = 2
        elif 'CPU' in device_type:
            ops_per_cycle = 8  # AVX-512
        else:
            ops_per_cycle = 1
        
        gflops = {}
        
        # FP16
        fp16_width = device_info['vector_width_half']
        if fp16_width == 0:
            fp16_width = device_info['vector_width_float']  # Fallback
        gflops['fp16'] = clock_ghz * compute_units * ops_per_cycle * fp16_width
        
        # FP32
        fp32_width = device_info['vector_width_float']
        gflops['fp32'] = clock_ghz * compute_units * ops_per_cycle * fp32_width
        
        # FP64
        fp64_width = device_info['vector_width_double']
        gflops['fp64'] = clock_ghz * compute_units * ops_per_cycle * fp64_width
        
        return gflops

# ============================================================================
# MODULE 3: Optimization Planner
# ============================================================================

class OptimizationPlanner:
    """Erstellt Optimierungs-Plan basierend auf Device-Capabilities."""
    
    # Workload types
    COMPUTE_BOUND = "compute_bound"
    MEMORY_BOUND = "memory_bound"
    MIXED = "mixed"
    LATENCY_SENSITIVE = "latency_sensitive"
    
    @staticmethod
    def recommendDevice(devices: List[Dict], workload: str) -> Dict:
        """Empfehle bestes Device für Workload."""
        recommendations = []
        
        for dev in devices:
            score = OptimizationPlanner._calculateScore(dev, workload)
            optimal_local = OptimizationPlanner.calculateOptimalLocalSize(dev)
            
            recommendations.append({
                'device': dev['name'],
                'score': score,
                'optimal_local_size': optimal_local,
                'reasoning': OptimizationPlanner._generateReasoning(dev, workload, score),
                'vendor': dev['vendor']
            })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[0] if recommendations else None
    
    @staticmethod
    def calculateOptimalLocalSize(device: Dict) -> int:
        """Berechnet optimale local_work_size."""
        device_type = device['type']
        compute_units = device['compute_units']
        simd_width = device['simd_width']
        max_wg_size = device['max_work_group_size']
        
        if 'GPU' in device_type:
            # GPU: Target 75% occupancy, warp-aligned
            if simd_width == 32:
                return min(256, max_wg_size)  # NVIDIA warp
            elif simd_width == 64:
                return min(256, max_wg_size)  # AMD wavefront
            else:
                return min(128, max_wg_size)
        elif 'CPU' in device_type:
            # CPU: core_count * 4, max 64
            optimal = compute_units * 4
            return min(optimal, 64)
        else:
            # FPGA/DSP: Usually 1
            return 1
    
    @staticmethod
    def _calculateScore(device: Dict, workload: str) -> float:
        """Berechnet Score für Device + Workload."""
        if workload == OptimizationPlanner.COMPUTE_BOUND:
            profile = DeepProfiler.profileDevice(device)
            return profile['peak_gflops']['fp32'] / 1000.0
        elif workload == OptimizationPlanner.MEMORY_BOUND:
            gb = device['global_mem_size'] / (1024**3)
            return gb
        elif workload == OptimizationPlanner.LATENCY_SENSITIVE:
            return device['max_clock_frequency'] * device['compute_units']
        else:  # MIXED
            profile = DeepProfiler.profileDevice(device)
            fp32_gflops = profile['peak_gflops']['fp32'] / 1000.0
            gb = device['global_mem_size'] / (1024**3)
            return (fp32_gflops + gb) / 2
    
    @staticmethod
    def _generateReasoning(device: Dict, workload: str, score: float) -> str:
        """Generiert Begründung für Empfehlung."""
        reasons = []
        device_type = device['type']
        
        if workload == OptimizationPlanner.COMPUTE_BOUND:
            profile = DeepProfiler.profileDevice(device)
            reasons.append(f"Peak FP32: {profile['peak_gflops']['fp32']:.2f} GFLOPS")
            reasons.append(f"{device['compute_units']} Compute Units @ {device['max_clock_frequency']} MHz")
        elif workload == OptimizationPlanner.MEMORY_BOUND:
            gb = device['global_mem_size'] / (1024**3)
            reasons.append(f"Global Memory: {gb:.2f} GB")
            if device['has_unified_memory']:
                reasons.append("Unified Memory (SVM) available")
            else:
                reasons.append("Dedicated VRAM")
        
        # Hardware-specific advice
        vendor_id = device.get('vendor_id', 0)
        if vendor_id == 0x10DE:
            reasons.append("NVIDIA: Use warp-aligned local_size (multiple of 32)")
        elif vendor_id == 0x1002:
            reasons.append("AMD: Use wavefront-aligned local_size (multiple of 64)")
        elif vendor_id == 0x8086:
            reasons.append("Intel: Beware EU saturation limits")
        
        return "; ".join(reasons)

# ============================================================================
# Output Formatter
# ============================================================================

class OutputFormatter:
    """Formatiert Output für Terminal."""
    
    SEPARATOR = "=" * 80
    
    @staticmethod
    def printDeviceAnalysis(device_info: Dict, profile: Dict):
        """Gibt vollständige Device-Analyse aus."""
        print(f"\n{OutputFormatter.SEPARATOR}")
        print(f"DEVICE: {device_info['name']}")
        print(f"{OutputFormatter.SEPARATOR}")
        
        # Hardware Topology
        print(f"\n[ Hardware Topology ]")
        print(f"  Vendor:                 {device_info['vendor']}")
        print(f"  Platform:               {device_info['platform']}")
        print(f"  Type:                   {device_info['type']}")
        print(f"  Compute Units:          {device_info['compute_units']}")
        print(f"  SIMD Width:             {device_info['simd_width']}")
        print(f"  Clock Frequency:       {device_info['max_clock_frequency']} MHz")
        
        if device_info['partition_max_sub_devices'] > 1:
            print(f"  Partition Support:     {device_info['partition_max_sub_devices']} sub-devices")
        
        # Memory Architecture
        print(f"\n[ Memory Architecture ]")
        gb = device_info['global_mem_size'] / (1024**3)
        print(f"  Global Memory:          {gb:.2f} GB")
        print(f"  Max Mem Alloc:         {device_info['max_mem_alloc_size'] / (1024**3):.2f} GB")
        print(f"  Local Memory:           {device_info['local_mem_size'] / 1024:.2f} KB")
        print(f"  Global Cache:           {device_info['global_mem_cache_size'] / 1024:.2f} KB")
        print(f"  Local Mem Type:         {device_info['local_mem_type']}")
        print(f"  Unified Memory (SVM):   {'YES' if device_info['has_unified_memory'] else 'NO'}")
        
        # Vector widths
        print(f"\n[ Vector Widths ]")
        v = device_info
        print(f"  CHAR:  {v['vector_width_char']:2d} | SHORT: {v['vector_width_short']:2d} | INT: {v['vector_width_int']:2d} | LONG: {v['vector_width_long']:2d}")
        print(f"  FLOAT: {v['vector_width_float']:2d} | DOUBLE: {v['vector_width_double']:2d} | HALF: {v['vector_width_half']:2d}")
        
        # Peak Performance
        print(f"\n[ Kernel Potential - Theoretical Peak Performance ]")
        pf = profile['peak_gflops']
        print(f"  FP16 (half):   {pf['fp16']:12.2f} GFLOPS ({pf['fp16']/1000:6.2f} TFLOPS)")
        print(f"  FP32 (float):  {pf['fp32']:12.2f} GFLOPS ({pf['fp32']/1000:6.2f} TFLOPS)")
        print(f"  FP64 (double): {pf['fp64']:12.2f} GFLOPS ({pf['fp64']/1000:6.2f} TFLOPS)")
        
        # Limits
        print(f"\n[ Critical Limits ]")
        lim = profile['limits']
        print(f"  MAX_WORK_GROUP_SIZE:       {lim['MAX_WORK_GROUP_SIZE']:,}")
        print(f"  MAX_WORK_ITEM_DIMENSIONS: {lim['MAX_WORK_ITEM_DIMENSIONS']}")
        sizes = lim['MAX_WORK_ITEM_SIZES']
        print(f"  MAX_WORK_ITEM_SIZES:        [{sizes[0]:,}, {sizes[1]:,}, {sizes[2]:,}]")
        print(f"  MAX_PARAMETER_SIZE:        {lim['MAX_PARAMETER_SIZE']:,} bytes")
        
        # Feature Matrix
        print(f"\n[ Feature Matrix ]")
        feat = profile['features']
        def support_str(s): return "✅ SUPPORTED" if s else "❌ NOT SUPPORTED"
        print(f"  cl_khr_fp16:               {support_str(feat['fp16'])}")
        print(f"  cl_khr_fp64:               {support_str(feat['fp64'])}")
        print(f"  cl_khr_int64_base_atomics: {support_str(feat['int64_atomics'])}")
        print(f"  cl_khr_subgroups:          {support_str(feat['subgroups'])}")
        print(f"  cl_khr_svm:                {support_str(feat['svm_unified_memory'])}")
    
    @staticmethod
    def printRecommendations(devices: List[Dict]):
        """Gibt Optimierungs-Empfehlungen aus."""
        print(f"\n\n{OutputFormatter.SEPARATOR}")
        print("OPTIMIZATION PLAN")
        print(f"{OutputFormatter.SEPARATOR}")
        
        for workload, name in [
            (OptimizationPlanner.COMPUTE_BOUND, "COMPUTE_BOUND"),
            (OptimizationPlanner.MEMORY_BOUND, "MEMORY_BOUND"),
            (OptimizationPlanner.LATENCY_SENSITIVE, "LATENCY_SENSITIVE")
        ]:
            rec = OptimizationPlanner.recommendDevice(devices, workload)
            if rec:
                print(f"\n  [{name}]")
                print(f"    Device:              {rec['device']}")
                print(f"    Score:               {rec['score']:.2f}")
                print(f"    Optimal local_size:  {rec['optimal_local_size']}")
                print(f"    Reasoning:           {rec['reasoning']}")
        
        # Global advice
        print(f"\n  [Hardcoded Fallstricke - GPU-spezifisch]")
        print(f"    NVIDIA: max_work_group_size typically 1024, use multiple of warp (32)")
        print(f"    AMD:     max_work_group_size typically 256, use multiple of wavefront (64)")
        print(f"    Intel:   Integrated GPUs brauchen EU-aware scheduling, subgroups helfen")
        print(f"    FPGA:    Usually 1, partitionieren für parallelism")

# ============================================================================
# Main
# ============================================================================

def main():
    print(f"""
################################################################################
#                                                                              #
#                        OpenCL Deep Inspector v1.0                           #
#                   Heterogenes Computing - Hardware Analyse                  #
#                                                                              #
################################################################################
""")
    
    # Discover
    print("[1/3] Discovering OpenCL devices...")
    devices = DiscoveryEngine.discoverAllDevices()
    
    if not devices:
        print("\n❌ No OpenCL devices found.")
        print("   Install OpenCL runtime:")
        print("   - Ubuntu/Debian: sudo apt install pocl-opencl-icd")
        print("   - NVIDIA:         sudo apt install nvidia-opencl-icd")
        print("   - AMD:            sudo apt install rocm-opencl-runtime")
        return 1
    
    print(f"   Found {len(devices)} device(s)\n")
    
    # Profile each device
    print("[2/3] Profiling devices...")
    profiles = []
    for i, dev in enumerate(devices):
        profile = DeepProfiler.profileDevice(dev)
        profiles.append(profile)
        OutputFormatter.printDeviceAnalysis(dev, profile)
    
    # Optimization
    print("\n[3/3] Generating optimization plan...")
    OutputFormatter.printRecommendations(devices)
    
    print(f"""
################################################################################
#                           Analysis Complete                                  #
################################################################################
""")
    
    # JSON output option
    if '--json' in sys.argv:
        output = {
            'devices': devices,
            'profiles': profiles
        }
        print("\nJSON Output:")
        print(json.dumps(output, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())