#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC Multiphysics Pipeline Orchestrator - Industrial Grade Edition
Includes Ansys page-break sanitation, layout throttling, and robust exception catching.
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np

def find_system_ansys_core():
    """Scans and maps recent platform paths to lock down the active MAPDL engine."""
    supported_releases = ["v271", "v262", "v261", "v252", "v242", "v232", "v212"]
    base_paths = [
        r"C:\Program Files\ANSYS Inc",
        r"D:\Program Files\ANSYS Inc",
        r"C:\Program Files\AnsysEM"
    ]
    for base in base_paths:
        for release in supported_releases:
            target_bin = os.path.join(base, release, "ansys", "bin", "winx64", "MAPDL.exe")
            if os.path.exists(target_bin):
                return target_bin
    return None

def sanitize_and_parse_ansys_report(file_path):
    """
    Strips away Ansys's custom text headers, page-breaks, and tabular formatting.
    Ensures Pandas only reads clean, isolated numeric coordinate rows.
    """
    clean_rows = []
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            # Ansys coordinate rows always start with a numeric Node ID integer
            if len(parts) >= 2 and parts[0].isdigit():
                try:
                    node_id = int(parts[0])
                    # Extract the final field value (Temperature or Stress scalar value)
                    value = float(parts[-1])
                    clean_rows.append([node_id, value])
                except ValueError:
                    continue # Skip raw page-break header remnants safely
                    
    if not clean_rows:
        return None
    return pd.DataFrame(clean_rows, columns=['NodeID', 'Value'])

def verify_transient_anisotropic_logs(t_path, s_path, max_temp=85.0, max_stress_mpa=150.0):
    """Executes vectorized QA evaluations over sanitized engineering logs."""
    print("\n" + "="*75)
    print("📋 ANISOTROPIC TRANSIENT DESIGN COMPLIANCE & SAFETY AUDIT")
    print("="*75)
    
    t_data = sanitize_and_parse_ansys_report(t_path)
    s_data = sanitize_and_parse_ansys_report(s_path)
    
    if t_data is None or s_data is None:
        print("❌ PIPELINE ERROR: Structural solution logs are corrupt, empty, or unreadable.")
        return False

    peak_temp = t_data['Value'].max()
    peak_stress_mpa = s_data['Value'].max() / 1e6
    
    print(f"       Peak System Temperature: {peak_temp:.2f}°C / Limit: {max_temp}°C")
    print(f"  Peak Von Mises Tensile Stress: {peak_stress_mpa:.2f} MPa / Limit: {max_stress_mpa} MPa")
    print("-"*75)
    
    if peak_temp > max_temp:
        print("❌ DESIGN VIOLATION: Thermal threshold breached during pulsed load steps.")
        return False
    if peak_stress_mpa > max_stress_mpa:
        print("❌ DESIGN VIOLATION: Anisotropic mechanical tension exceeded local yielding limits.")
        return False
        
    print("✅ VERIFICATION SUCCESS: All fields conform to technical compliance matrices.")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(workspace_root)

    os.makedirs("simulation", exist_ok=True)
    
    apdl_deck = os.path.join("simulation", "run_simulation.dat")
    thermal_log = os.path.join("simulation", "thermal_solution_nodes.txt")
    stress_log = os.path.join("simulation", "structural_stress_nodes.txt")
    solver_dump = os.path.join("simulation", "simulation_output.out")

    print("[SYSTEM] Booting Advanced Multi-Physics Processing Core...")
    
    solver_exe = find_system_ansys_core()
    if not solver_exe:
        print("❌ DEPLOYMENT ERROR: Ansys MAPDL local core installation folder was not detected.")
        sys.exit(1)
    print(f"🔍 Located Verification Link: {solver_exe}")

    # Safety Layer: Detect student license limits and warn user if mesh capacity might bottleneck
    if "student" in solver_exe.lower():
        print("⚠️  NOTICE: Student installation identified. If mesh limits breach tier capacities,")
        print("   manually adjust 'S_PITCH_X/Y' variables to 0.005 inside simulation/run_simulation.dat")

    print("🚀 Transmitting instruction macros to headless solver (Processing fields)...")
    cmd_args = [solver_exe, "-b", "-i", apdl_deck, "-o", solver_dump]
    
    try:
        # Pass control loop directly to core executable engine
        subprocess.run(cmd_args, check=True, timeout=180)
        print("🏁 Computational loops concluded successfully.")
    except subprocess.TimeoutExpired:
        print("❌ EXCEPTION: Process timed out. Mesh configuration is too large for current engine license.")
        sys.exit(1)
    except subprocess.CalledProcessError as err:
        print(f"❌ EXCEPTION: Simulation engine aborted with error status flag: {err.returncode}")
        sys.exit(1)

    qa_clearance = verify_transient_anisotropic_logs(thermal_log, stress_log)
    sys.exit(0 if qa_clearance else 1)

if __name__ == "__main__":
    main()
