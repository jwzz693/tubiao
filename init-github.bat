@echo off
chcp 65001 >nul
echo ========================================
echo   图标资源工具包 - Git 初始化脚本
echo ========================================
echo.

:: 检查 git 是否可用
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Git，请先安装: https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 初始化 Git 仓库
echo [1/4] 初始化 Git 仓库...
cd /d "%~dp0"
git init

:: 添加所有文件
echo.
echo [2/4] 添加文件到 Git...
git add .

:: 首次提交
echo.
echo [3/4] 创建首次提交...
git commit -m "🎨 初始化图标资源工具包"

:: 提示设置远程仓库
echo.
echo ========================================
echo ✅ Git 仓库初始化完成!
echo ========================================
echo.
echo [4/4] 接下来请在 GitHub 创建仓库并推送:
echo.
echo   1. 打开 https://github.com/new
echo   2. 创建名为 "icon-toolkit" 的仓库（不勾选 README）
echo   3. 运行以下命令:
echo.
echo      git remote add origin https://github.com/你的用户名/icon-toolkit.git
echo      git branch -M main
echo      git push -u origin main
echo.
echo   或使用 GitHub CLI:
echo      gh repo create icon-toolkit --public --source=. --push
echo.
echo ========================================
pause
