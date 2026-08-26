#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC ThermoStress Grid: Independent Performance Data Auditor
"""

import os
import sys
import pandas as pd

def run_standalone_audit():
    t_file = os.path.join("simulation", "thermal_solution_nodes.txt")
    s_file = os.path.join("simulation", "structural_stress_nodes.txt")
    
    print("🛠️  Running isolated analysis log audit sequence...")
    
    for path in [t_file, s_file]:
        if not os.path.exists(path):
            print(f"❌ AUDITOR ERROR: Core log file [{path}] is unreadable or empty.")
            sys.exit(1)
            
    try:
        t_df = pd.read_csv(t_file, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Val'])
        s_df = pd.read_csv(s_file, sep=r'\s+', comment='#', skiprows=1, names=['NodeID', 'Val'])
        
        t_clean = pd.to_numeric(t_df['Val'], errors='coerce').dropna()
        s_clean = pd.to_numeric(s_df['Val'], errors='coerce').dropna()
        
        print(f"✨ Audit Matrix Clear: Maximum Temp = {t_clean.max():.2f}°C")
        print(f"✨ Audit Matrix Clear: Maximum Von Mises Tension = {(s_clean.max()/1e6):.2f} MPa")
    except Exception as err:
        print(f"❌ AUDITOR FAILED: Extraneous formatting mismatch encountered: {err}")
        sys.exit(1)

if __name__ == "__main__":
    run_standalone_audit()
