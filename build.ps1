# MySQL 表数据导出工具 - 打包脚本
# PowerShell 版本

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   MySQL 表数据导出工具 - 打包脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# [1/3] 检查依赖
Write-Host "[1/3] 检查依赖..." -ForegroundColor Yellow
try {
    $null = pip show pyinstaller 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyInstaller 已安装" -ForegroundColor Green
    } else {
        throw
    }
} catch {
    Write-Host "PyInstaller 未安装，正在安装..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host ""
Write-Host "[2/3] 开始打包..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Gray
Write-Host ""

# 执行打包命令
pyinstaller --onefile `
    --windowed `
    --name=MySQLExporter `
    --icon=NONE `
    --add-data="README.md;." `
    --hidden-import=pymysql `
    --hidden-import=pandas `
    --hidden-import=openpyxl `
    main.py

Write-Host ""
Write-Host "[3/3] 打包完成！" -ForegroundColor Green
Write-Host ""
Write-Host "可执行文件位置: dist\MySQLExporter.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "          打包完成！" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
