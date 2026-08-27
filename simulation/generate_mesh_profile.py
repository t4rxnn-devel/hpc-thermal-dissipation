# simulation/generate_mesh_profile.py
import numpy as np
import matplotlib.pyplot as plt
import os

def generate_thermal_contour():
    # Grid and material parameters for the OFHC copper cold plate
    width_mm, height_mm = 100, 100
    dx, dy = 1.0, 1.0
    nx, ny = int(width_mm / dx), int(height_mm / dy)
    
    # Initialize plate at a baseline coolant temperature of 20°C
    T = np.ones((nx, ny)) * 20.0
    cx, cy = nx // 2, ny // 2
    hotspot_radius = int(10 / dx)
    
    x = np.arange(nx)
    y = np.arange(ny)
    xx, yy = np.meshgrid(x, y, indexing='ij')
    hotspot_mask = (xx - cx)**2 + (yy - cy)**2 < hotspot_radius**2
    
    # Run a finite difference thermal spread simulation for contour profiling
    for _ in range(300):
        d2x = (T[2:, 1:-1] - 2 * T[1:-1, 1:-1] + T[:-2, 1:-1]) / dx**2
        d2y = (T[1:-1, 2:] - 2 * T[1:-1, 1:-1] + T[1:-1, :-2]) / dy**2
        T[1:-1, 1:-1] += 0.05 * (d2x + d2y)
        T[hotspot_mask] = 85.0  # Constant high-temperature chip hotspot

    # Ensure output directory exists
    os.makedirs("simulation", exist_ok=True)

    # Plot and save as mesh_profile.png
    plt.figure(figsize=(8, 6))
    contour = plt.imshow(T, cmap='hot', origin='lower', extent=[0, width_mm, 0, height_mm])
    plt.colorbar(contour, label='Temperature (°C)')
    plt.title('Cold Plate Thermal Dissipation Contour')
    plt.xlabel('X Position (mm)')
    plt.ylabel('Y Position (mm)')
    plt.tight_layout()
    plt.savefig('simulation/mesh_profile.png', dpi=300)
    plt.close()
    print("Successfully generated simulation/mesh_profile.png")

if __name__ == "__main__":
    generate_thermal_contour()
