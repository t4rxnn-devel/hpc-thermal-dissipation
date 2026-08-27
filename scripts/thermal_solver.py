import numpy as np

def simulate_cold_plate_heat(width_mm=100, height_mm=100, dx=1.0, dy=1.0, timesteps=500):
    # Material Constants: Oxygen-Free High-Conductivity Copper (OFHC)
    k_copper = 0.398      # Thermal conductivity in Watts / (mm * Kelvin)
    rho_copper = 8.94e-3  # Density in g/mm^3
    cp_copper = 0.385     # Specific heat capacity in J/(g * Kelvin)
    alpha = k_copper / (rho_copper * cp_copper)  # Thermal diffusivity

    # Grid initialization
    nx, ny = int(width_mm / dx), int(height_mm / dy)
    T = np.ones((nx, ny)) * 20.0  # Entire plate starts at 20°C (coolant temp)

    # High-Stakes Boundary Conditions (Simulating localized hotspot)
    cx, cy = nx // 2, ny // 2
    hotspot_radius = int(10 / dx)

    # Create coordinate grid for vectorized masking
    x = np.arange(nx)
    y = np.arange(ny)
    xx, yy = np.meshgrid(x, y, indexing='ij')
    hotspot_mask = (xx - cx)**2 + (yy - cy)**2 < hotspot_radius**2

    # Stability criterion calculation for explicit finite difference method
    dt = 0.1 * (min(dx, dy)**2) / (2 * alpha)

    for _ in range(timesteps):
        T_new = T.copy()

        # Vectorized 2D Laplacian derivation using array slicing for massive speedup
        d2x = (T[2:, 1:-1] - 2 * T[1:-1, 1:-1] + T[:-2, 1:-1]) / dx**2
        d2y = (T[1:-1, 2:] - 2 * T[1:-1, 1:-1] + T[1:-1, :-2]) / dy**2
        
        # Update interior nodes vectorially
        T_new[1:-1, 1:-1] = T[1:-1, 1:-1] + alpha * dt * (d2x + d2y)

        # Enforce boundary conditions (constant hotspot load)
        T_new[hotspot_mask] = 85.0

        T = T_new

    print(f"Simulation Complete. Peak Edge Gradient Vector: {np.max(T):.2f}°C")
    return T

if __name__ == "__main__":
    simulate_cold_plate_heat()
