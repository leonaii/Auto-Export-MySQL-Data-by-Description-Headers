@echo off
chcp 65001 >nul
echo ======================================
echo    MySQL 表数据导出工具 - 打包脚本
echo ======================================
echo.

echo [1/3] 检查依赖...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
) else (
    echo PyInstaller 已安装
)

echo.
echo [2/3] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name=MySQLExporter ^
    --icon=NONE ^
    --add-data="README.md;." ^
    --hidden-import=pymysql ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    main.py

echo.
echo [3/3] 打包完成！
echo.
echo 可执行文件位置: dist\MySQLExporter.exe
echo.
echo ======================================
echo           打包完成！
echo ======================================
pause
