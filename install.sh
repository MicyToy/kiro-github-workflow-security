#!/bin/bash
# GitHub Workflow Security Power 安装脚本

set -e

POWER_NAME="github-workflow-security"
POWER_DIR="$HOME/.kiro/powers/$POWER_NAME"
WORKSPACE_KIRO_DIR=".kiro"

echo "🚀 安装 GitHub Workflow Security Power..."

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo "⚠️  警告: 当前目录不是 Git 仓库"
    read -p "是否继续安装? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 创建工作区 .kiro 目录
mkdir -p "$WORKSPACE_KIRO_DIR"/{skills,scripts,data}

# 复制文件
echo "📦 复制文件..."
cp "$POWER_DIR/skills/github-workflow-security.md" "$WORKSPACE_KIRO_DIR/skills/"
cp "$POWER_DIR/scripts/harden-workflows.py" "$WORKSPACE_KIRO_DIR/scripts/"
cp "$POWER_DIR/scripts/get-action-commit.py" "$WORKSPACE_KIRO_DIR/scripts/"
cp "$POWER_DIR/data/action-commit-map.json" "$WORKSPACE_KIRO_DIR/data/"
cp "$POWER_DIR/README.md" "$WORKSPACE_KIRO_DIR/"

# 设置执行权限
chmod +x "$WORKSPACE_KIRO_DIR/scripts/harden-workflows.py"
chmod +x "$WORKSPACE_KIRO_DIR/scripts/get-action-commit.py"

echo "✅ 安装完成!"
echo ""
echo "📚 使用方法:"
echo "  1. 在 Kiro 中使用: '使用 github-workflow-security skill 扫描并加固所有 workflow'"
echo "  2. 命令行使用: 'python3 .kiro/scripts/harden-workflows.py'"
echo "  3. 查看文档: 'cat .kiro/README.md'"
echo ""
echo "🔍 快速测试:"
echo "  python3 .kiro/scripts/get-action-commit.py actions/checkout v4"
