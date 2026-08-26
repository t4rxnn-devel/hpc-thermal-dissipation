#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC Multiphysics Pipeline Orchestrator - Anisotropic Transient Edition
Handles dynamic sweep routing, background transient APDL solving, and tensor safety audits.
"""

import os
import sys
import subprocess
import pandas as pd
import numpy as np

def find_system_ansys_core():
    """Systematically maps OS environment pathways to locate the MAPDL batch solver."""
    supported_releases = ["v261", "v252", "v242", "v232", "v222"]
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

def verify_transient_anisotropic_logs(t_path, s_path, max_temp=85.0, max_stress_mpa=150.0):
    """Parses advanced multi-axial node tables using vectorized matrix analytics."""
    print("\n" + "="*75)
    print("📋 ANISOTROPIC TRANSIENT DESIGN COMPLIANCE & SAFETY AUDIT")
    print("="*75)
    
    for path in [t_path, s_path]:
        if not os.path.exists(path):
            print(f"❌ PIPELINE ERROR: Mandatory simulation log file [{path}] is missing.")
            return False

    try:
        # Ingest space-delimited structural nodes arrays
        t_data = pd.read_csv(t_path, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Value'])
        s_data = pd.read_csv(s_path, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Value'])
        
        # Eliminate empty cells or alphanumeric headers dropped by the MAPDL page-break formatter
        t_data = t_data[pd.to_numeric(t_data['Value'], errors='coerce').notnull()]
        s_data = s_data[pd.to_numeric(s_data['Value'], errors='coerce').notnull()]
        
        peak_temp = np.max(t_data['Value'].astype(float))
        peak_stress_mpa = np.max(s_data['Value'].astype(float)) / 1e6
        
        print(f"🌡️  Peak Transient Thermal Node: {peak_temp:.2f}°C / Limit: {max_temp}°C")
        print(f"💪 Peak Anisotropic Von Mises Tensor: {peak_stress_mpa:.2f} MPa / Limit: {max_stress_mpa} MPa")
        print("-" * 75)
        
        if peak_temp > max_temp:
            print("❌ RISK ALERTS DETECTED: Thermal runaway recorded during pulsed cycles.")
            return False
        if peak_stress_mpa > max_stress_mpa:
            print("❌ RISK ALERTS DETECTED: Anisotropic shear matrices exceeded material yield points.")
            return False
            
        print("✅ STABILITY VERIFIED: Structural nodes match design compliance guidelines.")
        return True
    except Exception as err:
        print(f"❌ PIPELINE ERROR: Analytics engine failed to parse log data: {err}")
        return False

def main():
    # Enforce strict path binding to the repository workspace root folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(workspace_root)

    apdl_deck = os.path.join("simulation", "run_simulation.dat")
    thermal_log = os.path.join("simulation", "thermal_solution_nodes.txt")
    stress_log = os.path.join("simulation", "structural_stress_nodes.txt")
    solver_dump = os.path.join("simulation", "simulation_output.out")

    print("[PIPELINE] Initializing Advanced Multi-Physics Orchestrator Framework...")
    
    if not os.path.exists(apdl_deck):
        print(f"❌ CONFIGURATION ERROR: The execution deck '{apdl_deck}' is missing.")
        sys.exit(1)

    solver_exe = find_system_ansys_core()
    if not solver_exe:
        print("❌ DEPLOYMENT ERROR: No active local Ansys MAPDL environment detected.")
        sys.exit(1)
    print(f"🔍 Pipeline Link Established: {solver_exe}")

    print("🚀 Launching Headless Transient Solver Loop (This may take up to 2 minutes)...")
    cmd_args = [solver_exe, "-b", "-i", apdl_deck, "-o", solver_dump]
    
    try:
        # Pass control to MAPDL execution layer with extended timeout monitoring buffers
        subprocess.run(cmd_args, check=True, timeout=300)
        print("🏁 Multi-step transient calculation tasks completed.")
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT ERROR: Solver thread hung or exceeded maximum execution allowance.")
        sys.exit(1)
    except subprocess.CalledProcessError as fail:
        print(f"❌ SOLVER EXCEPTION: Engine aborted prematurely with status code {fail.returncode}")
        sys.exit(1)

    qa_clearance = verify_transient_anisotropic_logs(thermal_log, stress_log)
    sys.exit(0 if qa_clearance else 1)

if __name__ == "__main__":
    main()
