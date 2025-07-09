REM Allow override via REZ_HOUDINI_PYTHON or HOUDINI_PYTHON
set "PYTHON_EXEC=%REZ_HOUDINI_PYTHON%"
if "%PYTHON_EXEC%"=="" set "PYTHON_EXEC=%HOUDINI_PYTHON%"
if "%PYTHON_EXEC%"=="" set "PYTHON_EXEC=hython"

REM Test if hython is available
where %PYTHON_EXEC% >nul 2>nul
if errorlevel 1 (
    set "PYTHON_EXEC=python"
)

"%PYTHON_EXEC%" "%REZ_MVL_MAKE_DAILIES_ROOT%\python\mvl_make_dailies\generate_movie.py" %*