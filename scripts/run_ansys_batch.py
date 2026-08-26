#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC Multiphysics Pipeline Orchestrator
Automates: Native Geometric Array Construction -> Headless MAPDL Solve -> Nodal Analysis
"""

import os
import sys
import subprocess
import pandas as pd

def locate_ansys_executable():
    """Dynamically sweeps standard installation trees to isolate the MAPDL core executable."""
    standard_paths = [
        r"C:\Program Files\ANSYS Inc\v261\ansys\bin\winx64\MAPDL.exe",
        r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\MAPDL.exe",
        r"C:\Program Files\ANSYS Inc\v242\ansys\bin\winx64\MAPDL.exe",
    ]
    for path in standard_paths:
        if os.path.exists(path):
            return path
    return None

def write_advanced_apdl_input(file_path):
    """
    Generates the complete, mathematically stable multiphysics APDL macro script.
    Bypasses text-to-STEP conversion by driving Ansys's internal solid modeler geometry engine.
    """
    apdl_template = """! ============================================================================
! ADVANCED MULTIPHYSICS PIPELINE: THERMAL GRID & MECHANICAL STRESS
! ============================================================================
/BATCH                              ! Headless non-interactive processing mode
/CLEAR,NOSTART                      ! Clear engine memory maps

! ----------------------------------------------------------------------------
! STEP 1: COMPREHENSIVE MATERIAL STRUCTURAL DATA DEFINITIONS
! ----------------------------------------------------------------------------
/PREP7

! Material 1: Oxygen-Free Electronic Copper (C10100) - Fin Arrays
MP,DENS,1,8920                      
MP,KXX,1,391                        
MP,C,1,385                          
MP,ALPX,1,1.7e-5                    
MP,EX,1,1.15e11                     
MP,PRXY,1,0.33                      

! Material 5: Silicon Carbide (SiC) - High Stress Chip Die Substrate
MP,DENS,5,3210                      
MP,KXX,5,120                        
MP,C,5,750                          
MP,ALPX,5,4.0e-6                    
MP,EX,5,4.1e11                      
MP,PRXY,5,0.14

! ----------------------------------------------------------------------------
! STEP 2: NATIVE APDL PROCEDURAL PARAMETRIC GEOMETRY ARRAY ENGINE
! ----------------------------------------------------------------------------
DIE_W   = 0.024                     ! Chip Die Width (24mm)
DIE_L   = 0.024                     ! Chip Die Length (24mm)
DIE_H   = 0.001                     ! Chip Substrate Thickness (1mm)
SINK_H  = 0.003                     ! Solid Heatsink Base Thickness (3mm)
FIN_H   = 0.005                     ! Target Micro-channel Fin Height (5mm)
FIN_W   = 0.0015                    ! Width of individual dissipation fins (1.5mm)
GAP_W   = 0.0015                    ! Channel flow gap width (1.5mm)
NUM_FINS = 8                        ! Expanded High-Density Fin Count Array

! Volume 1: Build Core Component Die Substrate
BLOCK, 0, DIE_W, 0, DIE_L, 0, DIE_H                  

! Volume 2: Build Base Plate Interface Layout
BLOCK, 0, DIE_W, 0, DIE_L, DIE_H, DIE_H+SINK_H        

! Procedural Loop: Iteratively map micro-channels relative to calculated pitches
*DO,i,0,NUM_FINS-1
    X_START = i * (FIN_W + GAP_W)
    *IF, X_START+FIN_W, LE, DIE_W, THEN
        BLOCK, X_START, X_START+FIN_W, 0, DIE_L, DIE_H+SINK_H, DIE_H+SINK_H+FIN_H
    *ENDIF
*ENDDO

VGLUE, ALL                          ! Execute Boolean Glue to enforce perfect mesh conformal boundary nodes
/FACET,WIRE                         ! Optimize system graphics memory
FINISH

! ----------------------------------------------------------------------------
! STEP 3: MESH CONFIGURATION AND MATHEMATICAL ELEMENT ASSIGNMENTS
! ----------------------------------------------------------------------------
/PREP7
ET,1,SOLID70                        ! Instantiate 3D 8-Node Thermal Solid Elements

VSEL,S,VOLU,,1                      ! Select Substrate Die Volume
VATT,5,,1                           ! Map Silicon Carbide (Material 5) properties

VSEL,S,VOLU,,2,100                  ! Select Heatsink Grid Volumes
VATT,1,,1                           ! Map High Conduction Copper (Material 1) properties
VALL                                ! Re-enable all selections

MSHAPE,0,3D                         ! Target Structured Hexahedral meshing topologies
MSHKEY,1                            ! Enforce strict coordinate mapped meshing paths
ESIZE,0.0008                        ! Set fine global mesh resolution (0.8mm element edge sizing)
VMESH,ALL                           ! Generate Conformal Mesh Array
FINISH

! ----------------------------------------------------------------------------
! STEP 4: STEADY-STATE THERMAL BOUNDARY SOLUTION FIELD
! ----------------------------------------------------------------------------
/SOLU
ANTYPE,STATIC                       ! Invoke steady-state solver loop
SFA,1,1,CONV,650,22                 ! Forced convection liquid fluid boundary conditions (650 W/m^2K at 22C)
SFA,2,1,HFLUX,1500000               ! Severe localized hotspot thermal loading (1.5 MW/m^2)
SOLVE
FINISH

/POST1
SET,LAST
EDWRITE,THERM_TEMP                  ! Dump explicit nodal heat solution arrays to local disk mapping cache
FINISH

! ----------------------------------------------------------------------------
! STEP 5: AUTOMATED STRUCTURAL STRESS PHYSICS TRANSITION
! ----------------------------------------------------------------------------
/PREP7
ET,1,SOLID185                       ! Hot-swap physical element types to Structural Brick elements

ASEL,S,LOC,Z,0                      ! Capture PCB-mounting interface anchor faces
DA,ALL,UX,0                         ! Fixed Structural Constraints to ground structural reactions
DA,ALL,UY,0
DA,ALL,UZ,0
ASEL,ALL
FINISH

/SOLU
ANTYPE,STATIC
TREF,22                             ! Establish reference zero-strain system baseline temp (22C)
LDREAD,TEMP,,,LAST,,THERM_TEMP,rth  ! Map precise nodal temperature gradients into mechanical stress vectors
SOLVE
FINISH

! ----------------------------------------------------------------------------
! STEP 6: DATA RECOVERY AND LOCAL REPORT EXPORTS
! ----------------------------------------------------------------------------
/POST1
SET,LAST

/OUTPUT,simulation/thermal_solution_nodes,txt
PRNSOL,TEMP                         ! Write extracted node temperature array values
/OUTPUT

/OUTPUT,simulation/structural_stress_nodes,txt
PRNSOL,S,EQV                        ! Write calculated equivalent Von Mises stress tensor matrices
/OUTPUT
FINISH
"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(apdl_template)


def evaluate_solver_metrics(t_file, s_file, t_max=85.0, s_max_mpa=150.0):
    """Parses exported simulation log fields and triggers logical pass/fail alerts."""
    print("\n" + "="*60)
    print("🤖 AUTOMATED REPO ANALYSIS ENGINE: TARGET POST-PROCESS FIELD EVAL")
    print("="*60)
    
    for f in [t_file, s_file]:
        if not os.path.exists(f):
            print(f"❌ Error: Required solver output tracker file [{f}] is missing.")
            return False

    # Read and parse node arrays
    t_df = pd.read_csv(t_file, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Val'])
    s_df = pd.read_csv(s_file, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Val'])

    peak_temp = t_df['Val'].max()
    peak_stress_mpa = s_df['Val'].max() / 1e6

    print(f"🌡️  Peak System Junction Temperature: {peak_temp:.2f}°C (Threshold Limit: {t_max}°C)")
    print(f"💥 Peak Von Mises Mechanical Stress: {peak_stress_mpa:.2f} MPa (Threshold Limit: {s_max_mpa} MPa)")
    print("-"*60)

    if peak_temp > t_max or peak_stress_mpa > s_max_mpa:
        print("❌ STATUS: CRITICAL FAILURE. Design thresholds breached.")
        return False
    else:
        print("✅ STATUS: MARGINS VERIFIED SAFE. System structural safety checks cleared.")
        return True


def main():
    # Resolve unified working path strings
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(project_root)

    apdl_input = os.path.join("simulation", "run_simulation.dat")
    thermal_txt = os.path.join("simulation", "thermal_solution_nodes.txt")
    stress_txt = os.path.join("simulation", "structural_stress_nodes.txt")

    print("[PIPELINE] Initializing Advanced Python Simulation Orchestrator...")
    
    # 1. Procedurally generate a safe input calculation deck file
    write_advanced_apdl_input(apdl_input)
    print("📝 Compiled native APDL procedural design script.")

    # 2. Locate the core physics engine executable on the system
    ansys_exe = locate_ansys_executable()
    if not ansys_exe:
        print("❌ Pipeline execution aborted: Valid Ansys MAPDL local installation folder not detected.")
        sys.exit(1)
    print(f"🔍 Located Ansys Solver Core: {ansys_exe}")

    # 3. Direct execution of headless batch solver
    print("🚀 Launching underlying solver pipeline execution loops...")
    cmd = [ansys_exe, "-b", "-i", apdl_input, "-o", "simulation/simulation_output.out"]
    
    try:
        subprocess.run(cmd, check=True)
        print("🏁 Physics calculations concluded successfully.")
    except subprocess.CalledProcessError as err:
        print(f"❌ Ansys Core crashed during execution loop handling: {err}")
        sys.exit(1)

    # 4. Ingest, parse, and verify raw simulation outputs
    success = evaluate_solver_metrics(thermal_txt, stress_txt)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
