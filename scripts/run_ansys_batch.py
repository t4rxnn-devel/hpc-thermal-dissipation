#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC Multiphysics Pipeline Orchestrator - Enterprise Automation Edition
Handles JSON configuration parsing, dynamic APDL variable injection, real-time unbuffered 
stream logging, and advanced post-solve telemetry data verification scans.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

def parse_pipeline_arguments():
    """Builds a robust configuration and argument parsing infrastructure interface."""
    parser = argparse.ArgumentParser(description="HPC ThermoStress Master Automation Pipeline Launcher")
    parser.add_argument("--config", type=str, default="simulation/config.json", help="Path to external configuration override file")
    parser.add_argument("--h_coef", type=float, help="Override fluid convection coefficient (W/m^2*K)")
    parser.add_argument("--chip_l", type=float, help="Override structural chip footprint size (Meters)")
    return parser.parse_args()

def load_and_inject_config(config_path, apdl_deck_path, args_override):
    """Parses JSON parameters and injects variable definitions dynamically into the top of the APDL file."""
    default_config = {
        "COOL_H_BASE": 1200.0,
        "CHIP_L": 0.0400,
        "CHIP_W": 0.0400,
        "INLET_VEL": 0.45,
        "CORE_FLUX_BG": 400000.0
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"⚠️  [CONFIG] Parsing error on file {config_path}: {e}. Defaulting parameters.")
            
    if args_override.h_coef:
        default_config["COOL_H_BASE"] = args_override.h_coef
    if args_override.chip_l:
        default_config["CHIP_L"] = args_override.chip_l

    if not os.path.exists(apdl_deck_path):
        print(f"❌ [CONFIG] Target template APDL deck file '{apdl_deck_path}' not found.")
        return False

    with open(apdl_deck_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # Generate an explicit clean variable assignment header deck block block
    injection_block = []
    injection_block.append("! ============================================================================")
    injection_block.append("! DYNAMIC VARIABLES INJECTED NATIVELY VIA THE PYTHON AUTOMATION PIPELINE")
    injection_block.append("! ============================================================================")
    for key, val in default_config.items():
        injection_block.append(f"{key} = {val}")
    injection_block.append("! ============================================================================\n")
    
    # Strip any older automated injections to prevent variable duplication overrides
    if "! DYNAMIC VARIABLES INJECTED" in original_content:
        split_content = original_content.split("! ============================================================================\n")
        original_content = split_content[-1]

    with open(apdl_deck_path, "w", encoding="utf-8") as f:
        f.write("\n".join(injection_block) + original_content)
    print(f"✅ [CONFIG] Parametric configurations parsed and cleanly injected into {apdl_deck_path}")
    return True

def locate_ansys_executable():
    """Scans environmental system matrices to find valid MAPDL batch executables."""
    standard_paths = [
        r"C:\Program Files\ANSYS Inc\v261\ansys\bin\winx64\MAPDL.exe",
        r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\MAPDL.exe",
        r"C:\Program Files\ANSYS Inc\v242\ansys\bin\winx64\MAPDL.exe",
        r"D:\Program Files\ANSYS Inc\v261\ansys\bin\winx64\MAPDL.exe"
    ]
    for path in standard_paths:
        if os.path.exists(path):
            return path
    return None

def execute_solver_stream_logged(solver_bin, input_deck, output_log, console_dump_path):
    """Executes the solver headlessly, capturing unbuffered streams directly to local tracking records."""
    print(f"🚀 [SOLVER] Launching headless calculation thread matrix via: {solver_bin}")
    cmd = [solver_bin, "-b", "-i", input_deck, "-o", output_log]
    
    os.makedirs(os.path.dirname(console_dump_path), exist_ok=True)
    
    with open(console_dump_path, "w", encoding="utf-8") as logger:
        logger.write(f"=== HPC PIPELINE AUDIT TRACE STARTED: {datetime.now()} ===\n")
        
        # Open the sub-process using standard unbuffered environment stream captures
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Real-time stdout console relay engine
        while True:
            output_line = process.stdout.readline()
            if output_line == "" and process.poll() is not None:
                break
            if output_line:
                sanitized_line = f"[{datetime.now().strftime('%H:%M:%S')}] {output_line}"
                logger.write(sanitized_line)
                logger.flush()
                # Print live ticks to terminal window view interface
                print(f"  > {output_line.strip()}", flush=True)
                
        rc = process.poll()
        logger.write(f"=== HPC PIPELINE AUDIT TRACE ENDED WITH EXIT CODE {rc} AT: {datetime.now()} ===\n")
        return rc

def run_automated_results_post_check(solver_out_path, thermal_txt, stress_txt):
    """Scans file dumps and textual matrix patterns to catch numerical divergence or segmentation errors."""
    print("\n" + "="*75)
    print("🤖 RETROSPECTIVE INFRASTRUCTURE POST-CHECK AUTOMATION MATRIX")
    print("="*75)
    
    if not os.path.exists(solver_out_path):
        print("❌ [POST-CHECK] Fatal failure: Core solver log file was never dropped onto local disk.")
        return False
        
    # Critical textual error signature matches mapped from known MAPDL error dictionaries
    fatal_keywords = ["ERROR", "FATAL", "CORE DUMP", "SEGMENTATION FAULT", "ILLEGAL OPERATION"]
    divergence_keywords = ["SOLUTION NOT CONVERGED", "DIVERG", "FLOATING POINT EXCEPTION"]
    
    with open(solver_out_path, "r", encoding="utf-8", errors="ignore") as f:
        for num, line in enumerate(f, 1):
            upper_line = line.upper()
            for key in fatal_keywords:
                if key in upper_line:
                    print(f"❌ [POST-CHECK] Fatal core exception signature identified on row {num}: {line.strip()}")
                    return False
            for key in divergence_keywords:
                if key in upper_line:
                    print(f"❌ [POST-CHECK] Numerical divergence flag tripped on row {num}: {line.strip()}")
                    return False

    print("✅ [POST-CHECK] Zero structural fatal execution log signatures identified.")
    
    # Assert physical solution logs are compiled and filled with coordinates rows
    for tracking_file in [thermal_txt, stress_txt]:
        if not os.path.exists(tracking_file) or os.path.getsize(tracking_file) < 500:
            print(f"❌ [POST-CHECK] Target data matrix tracker file '{tracking_file}' is missing or malformed.")
            return False
            
    print("✅ [POST-CHECK] Solution metrics and telemetry matrix structures safely written.")
    return True

def main():
    # Enforce root folder navigation alignment patterns
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(project_root)

    args = parse_pipeline_arguments()
    
    apdl_input_deck = os.path.join("simulation", "run_simulation.dat")
    solver_raw_out  = os.path.join("simulation", "simulation_output.out")
    console_history = os.path.join("simulation", "pipeline_console_history.log")
    thermal_nodes   = os.path.join("simulation", "thermal_solution_nodes.txt")
    stress_nodes    = os.path.join("simulation", "structural_stress_nodes.txt")

    # 1. Parameter compilation step
    if not load_and_inject_config(args.config, apdl_input_deck, args):
        sys.exit(1)

    # 2. Executable verification step
    solver_bin_exe = locate_ansys_executable()
    if not solver_bin_exe:
        print("❌ [LAUNCHER] Aborting sequence: Compatible Ansys MAPDL workspace environment not detected.")
        sys.exit(1)
    print(f"🔍 [LAUNCHER] Verified system engine path anchor: {solver_bin_exe}")

    # 3. Stream-logged batch execution step
    status_flag = execute_solver_stream_logged(solver_bin_exe, apdl_input_deck, solver_raw_out, console_history)
    if status_flag != 0:
        print(f"❌ [LAUNCHER] Solver execution crashed cleanly back to shell with exit status: {status_flag}")
        sys.exit(status_flag)

    # 4. Result validation step
    pipeline_cleared = run_automated_results_post_check(solver_raw_out, thermal_nodes, stress_nodes)
    
    if pipeline_cleared:
        print("\n🏆 [PIPELINE] Multiphysics tracking runs successfully verified. Code 0 returned.")
        sys.exit(0)
    else:
        print("\n❌ [PIPELINE] Post-check validation failures reported. Code 1 returned.")
        sys.exit(1)

if __name__ == "__main__":
    main()
