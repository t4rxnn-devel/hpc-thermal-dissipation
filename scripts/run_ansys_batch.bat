@echo off
SETLOCAL EnableDelayedExpansion

:: Resolve the project root folder layout dynamically
SET "PROJECT_DIR=%~dp0.."
CD /d "%PROJECT_DIR%"

echo ============================================================================
:: GRAPHICAL LAUNCHER FOR ADVANCED PYTHON SIMULATION PIPELINE
echo ============================================================================
echo [LAUNCHER] Booting Python multi-physics controller loop...
echo.

:: Execute the master Python script pipeline natively
python scripts\run_ansys_batch.py

:: Capture the exit status code passed back by the Python automation core
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [LAUNCHER] ❌ WARNING: Pipeline execution failed or design constraints breached.
    echo [LAUNCHER] Review log files located inside the /simulation folder directory.
) ELSE (
    echo.
    echo [LAUNCHER] ✅ SUCCESS: Simulation pipeline completed operations cleanly.
)

ENDLOCAL
pause
