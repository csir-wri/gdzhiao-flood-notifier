@ECHO ON
PUSHD "%~dp0"
SETLOCAL

:: Activate the virtual environment in the current directory
IF EXIST .venv\Scripts\activate.bat (
    ECHO Activating virtual environment
    CALL "%~dp0.venv\Scripts\activate.bat"
    ECHO.
)

:: Run the script
ECHO Running the script with predefined arguments
PYTHON main.py --config_dir .\config --data_dir .\sample_data

:: Deactivate the virtual environment in the current directory
IF EXIST .venv\Scripts\activate.bat (
    ECHO Deactivating virtual environment
    CALL "%~dp0\.venv\Scripts\deactivate.bat"
)

ENDLOCAL