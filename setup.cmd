@ECHO OFF
:: Navigate to the batch file's directory
PUSHD "%~dp0"

:: Create the virtual environment
python -m venv .venv

:: Check if creation succeeded
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

:: Activate the virtual environment
CALL .venv\Scripts\activate.bat

:: Install requirements
if exist "requirements.txt" (
    pip install -r requirements.txt
    ECHO Environment has been set up successfully.
) else (
    echo WARNING: requirements.txt not found. Skipping installation.
)

:: Deactivate the virtual environment
CALL deactivate

:: Exit routine
ECHO Press ^<ENTER^> to exit.
PAUSE > NUL
POPD