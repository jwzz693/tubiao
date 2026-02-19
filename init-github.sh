#!/bin/bash
# 图标资源工具包 - Git 初始化脚本

echo "========================================"
echo "  图标资源工具包 - Git 初始化脚本"
echo "========================================"
echo

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 初始化 Git
echo "[1/4] 初始化 Git 仓库..."
git init

# 添加文件
echo
echo "[2/4] 添加文件到 Git..."
git add .

# 首次提交
echo
echo "[3/4] 创建首次提交..."
git commit -m "🎨 初始化图标资源工具包"

echo
echo "========================================"
echo "✅ Git 仓库初始化完成!"
echo "========================================"
echo
echo "[4/4] 推送到 GitHub:"
echo
echo "  方式一 - 手动创建仓库后推送:"
echo "    git remote add origin https://github.com/你的用户名/icon-toolkit.git"
echo "    git branch -M main"
echo "    git push -u origin main"
echo
echo "  方式二 - 使用 GitHub CLI:"
echo "    gh repo create icon-toolkit --public --source=. --push"
echo
echo "========================================"
