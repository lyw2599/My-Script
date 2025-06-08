@echo off
setlocal enabledelayedexpansion

:: 设置文件所在目录
set "folder=C:\Your\Folder\Path"

:: 查找最新的PPT文件
for /f "delims=" %%f in ('dir /b /o-d "%folder%\*-*-*.ppt"') do (
    start "" "%folder%\%%f"
    exit /b
)
