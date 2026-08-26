@echo off
SETLOCAL EnableDelayedExpansion

:: Automatically resolve the project root directory relative to this script
SET "PROJECT_DIR=%~dp0.."
CD /d "%PROJECT_DIR%"

echo [START] Initializing HPC Simulation Pipeline Environment...
echo [INFO] Project Root Directory: %PROJECT_DIR%

:: Set the path to your explicit Ansys MAPDL installation executable
SET "ANSYS_MAPDL_EXE=C:\Program Files\ANSYS Inc\v261\ansys\bin\winx64\MAPDL.exe"

:: Verify Ansys executable presence before proceeding
IF NOT EXIST "%ANSYS_MAPDL_EXE%" (
    echo [ERROR] Ansys MAPDL executable not found at: "%ANSYS_MAPDL_EXE%"
    echo Please verify your Ansys installation pathway configuration.
    GOTO :END
)

echo [SOLVER] Launching Ansys MAPDL Engine in headless batch mode...
echo [SOLVER] Processing simulation/run_simulation.dat ...

:: Execute the full multiphysics batch solver core
"%ANSYS_MAPDL_EXE%" -b -i "simulation\run_simulation.dat" -o "simulation\simulation_output.out"
echo [SOLVER] Ansys execution finished. Raw log saved to simulation/simulation_output.out

:: Verify output result data files were successfully written by the solver
IF NOT EXIST "simulation\thermal_solution_nodes.txt" (
    echo [ERROR] Simulation failed to export node reports. Review simulation_output.out for errors.
    GOTO :END
)

echo [POST-PROCESS] Launching Python evaluation suite to check safety thresholds...
echo.

:: Run the automatic metrics and safety margin parser script
python scripts\extract_results.py

:END
echo.
echo [FINISHED] Engineering pipeline automation tasks completed.
ENDLOCAL
pause
