#!/bin/bash

# git-commit.sh - 自动提交work tree的代码
# 用法: ./git-commit.sh "commit message"
# 支持多行message

set -e

# 检查是否提供了commit message
if [ $# -eq 0 ]; then
    echo "错误: 请提供commit message"
    echo "用法: $0 \"commit message\""
    exit 1
fi

# 将所有参数作为commit message（支持多行）
COMMIT_MESSAGE="$*"

# 检查是否在git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "错误: 当前目录不是git仓库"
    exit 1
fi

# 检查work tree中是否有变更
if git diff-index --quiet HEAD --; then
    echo "提示: work tree中没有变更"
    exit 0
fi

# 添加所有变更到staging area
echo "正在添加变更..."
git add -A

# 提交变更
echo "正在提交代码..."
git commit -m "$COMMIT_MESSAGE"

echo "提交成功！"
