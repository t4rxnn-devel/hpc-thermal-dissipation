@echo off
:: Force local variable scope and enable advanced variable evaluation
SETLOCAL EnableDelayedExpansion EnableExtensions

:: Set clear, readable UTF-8 text encoding in the terminal windows shell
chcp 65001 >nul

:: Establish structural folder paths relative to this batch file's home directory
SET "BATCH_DIR=%~dp0"
SET "PROJECT_DIR=%BATCH_DIR%.."
CD /d "%PROJECT_DIR%"

:: Configure explicit system interface color profiles (Bright White text on deep Blue backdrop)
COLOR 1F

echo ============================================================================
echo   HPC THERMOSTRESS GRID: INDUSTRIAL PIPELINE LAUNCH OVERLORD
echo ============================================================================
echo  [SYSTEM PATH] %PROJECT_DIR%
echo ----------------------------------------------------------------------------

:: STEP 1: Rigorous Python Environment Verification Loop
echo  [STATUS] Validating local Python installation dependencies...

:: Try running the standard global command first
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    SET "PYTHON_EXE=python"
    GOTO :PYTHON_FOUND
)

:: Scan common Windows AppData installation paths if global check fails
SET "LOCAL_PYTHON_PATH=%LOCALAPPDATA%\Programs\Python"
IF EXIST "%LOCAL_PYTHON_PATH%" (
    FOR /F "delims=" %%I IN ('dir /b /s /a:d "%LOCAL_PYTHON_PATH%" 2^>nul ^| findstr /i /c:"Python[0-9]"') DO (
        IF EXIST "%%I\python.exe" (
            SET "PYTHON_EXE="%%I\python.exe""
            GOTO :PYTHON_FOUND
        )
    )
)

:: Fatal Error Handler: Exits gracefully if Python is entirely absent
COLOR 4F
echo  [CRITICAL ERROR] Python 3.x was not identified on this machine's path.
echo  [REMEDY] Please download and install Python from https://python.org
GOTO :EXIT_SEQUENCE

:PYTHON_FOUND
echo  [SUCCESS] Python execution engine verified: !PYTHON_EXE!
echo.

:: STEP 2: Assert presence of structural python package files
IF NOT EXIST "scripts\run_ansys_batch.py" (
    COLOR 4F
    echo  [CRITICAL ERROR] Target orchestration logic 'scripts\run_ansys_batch.py' is missing.
    echo  [REMEDY] Verify your repository architecture clone is intact.
    GOTO :EXIT_SEQUENCE
)

:: STEP 3: Execute Core Simulation Automation Subprocess Pipeline
echo  [STATUS] Relaying control to the Master Python Simulation Pipeline...
echo ============================================================================
echo.

!PYTHON_EXE! "scripts\run_ansys_batch.py"
SET "SOLVER_EXIT_CODE=%ERRORLEVEL%"

echo.
echo ============================================================================
echo   PIPELINE RETURN DISPATCH SUMMARY
echo ============================================================================

:: STEP 4: Evaluate Exit Matrices Passed Back from the Python Engine Core
IF %SOLVER_EXIT_CODE% EQU 0 (
    COLOR 2F
    echo  [FINAL STATUS] ✅ SUCCESS: Simulation pipeline completed operations cleanly.
    echo  [INFO] All calculated thermal matrices and tensor stress values passed QA.
) ELSE (
    COLOR 4F
    echo  [FINAL STATUS] ❌ FAILURE: Pipeline structural failure or safety threshold breach.
    echo  [INFO] Exit Code Matrix: %SOLVER_EXIT_CODE%
    echo  [REMEDY] Review performance charts or log traces inside the /simulation folder.
)

:EXIT_SEQUENCE
echo ----------------------------------------------------------------------------
echo  [FINISHED] Process termination reached. Shutting down runtime environment.
echo ============================================================================
ENDLOCAL
pause
