@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  python "%SCRIPT_DIR%lib\rc_draw.py" %*
  exit /b %errorlevel%
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%SCRIPT_DIR%lib\rc_draw.py" %*
  exit /b %errorlevel%
)

echo 错误: 需要 Python 3（未找到 python / py）>&2
exit /b 1
