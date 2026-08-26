import os
import pandas as pd

def parse_ansys_report(file_path):
    """Parses standard exported tabular space/tab-separated data from Ansys."""
    if not os.path.exists(file_path):
        print(f"Error: Target data file {file_path} not found.")
        return None
    try:
        # Read text report, skipping header rows if present
        df = pd.read_csv(file_path, sep=r'\s+', comment='#', skiprows=1, 
                         names=['NodeID', 'X', 'Y', 'Z', 'Value'])
        return df
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return None

def analyze_hpc_grid_metrics(thermal_file, stress_file, temp_limit=85.0, stress_limit_mpa=150.0):
    print("="*60)
    print("🚀 DISPENSATION GRID PERFORMANCE ANLYSIS REPORT")
    print("="*60)
    
    # 1. Evaluate Thermal Results
    t_df = parse_ansys_report(thermal_file)
    if t_df is not None:
        max_temp = t_df['Value'].max()
        avg_temp = t_df['Value'].mean()
        print(f"🔥 Thermal: Max Temp = {max_temp:.2f}°C | Avg Temp = {avg_temp:.2f}°C")
        if max_temp > temp_limit:
            print(f"❌ WARNING: Maximum Temperature exceeds safe junction limit of {temp_limit}°C!")
        else:
            print("✅ Thermal performance metrics are within safe margins.")
            
    # 2. Evaluate Structural Stress Results
    s_df = parse_ansys_report(stress_file)
    if s_df is not None:
        max_stress_pa = s_df['Value'].max()
        max_stress_mpa = max_stress_pa / 1e6  # Convert Pascals to MPa
        print(f"💪 Structural: Max Von Mises Stress = {max_stress_mpa:.2f} MPa")
        if max_stress_mpa > stress_limit_mpa:
            print(f"❌ WARNING: Structural stress exceeds allowable material limits ({stress_limit_mpa} MPa)!")
        else:
            print("✅ Structural stress indices are safely below structural yielding thresholds.")
    print("="*60)

if __name__ == "__main__":
    # Target placeholders mapped to automated export tasks inside workbench journals
    thermal_out = "simulation/thermal_solution_nodes.txt"
    stress_out = "simulation/structural_stress_nodes.txt"
    
    # Run analysis pipeline
    analyze_hpc_grid_metrics(thermal_out, stress_out)
