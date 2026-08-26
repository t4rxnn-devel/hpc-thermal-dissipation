import os

def create_hpc_step_file(output_path, die_w=20.0, die_l=20.0, base_h=5.0, fin_h=3.0, num_fins=5):
    """
    Procedurally generates a standardized ISO-10303-21 (STEP) file 
    representing the HPC micro-channel thermal dissipation grid.
    Dimensions are explicitly passed in millimeters.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fin_w = die_w / (2 * num_fins)  # Interleaved equal fin width layout
    
    # Standard header structure for an ISO STEP file
    step_content = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('HPC Micro-Channel Dissipation Grid Geometric Model'),'2;1');",
        f"FILE_NAME('{os.path.basename(output_path)}','2026-08-26T22:00:00',('Engineering Architecture Team'),('HPC Core'),'Processor Engine','Python CAD Gen','');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
        "ENDSEC;",
        "DATA;"
    ]
    
    # Ground baseline spatial reference matrices
    step_content.extend([
        "#1=DIRECTION('',(0.0,0.0,1.0));",
        "#2=DIRECTION('',(1.0,0.0,0.0));",
        "#3=CARTESIAN_POINT('',(0.0,0.0,0.0));",
        "#4=AXIS2_PLACEMENT_3D('',#3,#1,#2);"
    ])
    
    idx = 5
    volume_ids = []
    
    # Block Generation Logic: Step 1 - Base Heat Spreader Block
    step_content.extend([
        f"#{idx}=CARTESIAN_POINT('',({die_w/2},{die_l/2},{base_h/2}));",
        f"#{idx+1}=AXIS2_PLACEMENT_3D('',#{idx},#1,#2);",
        f"#{idx+2}=BOX('',#{idx+1},{die_w},{die_l},{base_h});"
    ])
    volume_ids.append(f"#{idx+2}")
    idx += 3
    
    # Block Generation Logic: Step 2 - Micro-Channel Fin Grids Loop
    for i in range(num_fins):
        x_offset = (2 * i * fin_w) + (fin_w / 2)
        step_content.extend([
            f"#{idx}=CARTESIAN_POINT('',({x_offset},{die_l/2},{base_h + (fin_h/2)}));",
            f"#{idx+1}=AXIS2_PLACEMENT_3D('',#{idx},#1,#2);",
            f"#{idx+2}=BOX('',#{idx+1},{fin_w},{die_l},{fin_h});"
        ])
        volume_ids.append(f"#{idx+2}")
        idx += 3
        
    # Bind generated volume blocks into a single compound manifold CAD asset
    volumes_str = ",".join(volume_ids)
    step_content.extend([
        f"#{idx}=COMPOUND_SHAPE_REPRESENTATION('',({volumes_str}),#4);",
        "ENDSEC;",
        "END-ISO-10303-21;"
    ])
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(step_content))
    print(f"✅ CAD Functionality: Successfully compiled CAD grid matrix -> {output_path}")

if __name__ == "__main__":
    target_cad = "geometry/grid_heatsink.step"
    # Generate default configuration grid: 20x20mm area, 5mm base, 3mm fins, 6 channels
    create_hpc_step_file(target_cad, die_w=20.0, die_l=20.0, base_h=5.0, fin_h=3.0, num_fins=6)
