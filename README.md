# GitHub Workflow Security Power

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

自动扫描和加固 GitHub Actions workflow 文件的安全性工具。

## ✨ 功能特性

- 🔒 **安全加固**: 自动添加最小权限配置
- 🔗 **版本固定**: 将 action tag 替换为不可变 commit SHA
- 🛡️ **供应链安全**: 防止依赖被恶意修改
- 📊 **详细报告**: 显示处理统计和未映射的 actions
- 🚀 **易于使用**: 支持 Kiro skill 和命令行两种方式

## 📦 安装

### 方式 1: 使用安装脚本

```bash
cd your-project
bash ~/.kiro/powers/github-workflow-security/install.sh
```

### 方式 2: 手动安装

```bash
# 创建目录
mkdir -p .kiro/{skills,scripts,data}

# 复制文件
cp ~/.kiro/powers/github-workflow-security/skills/* .kiro/skills/
cp ~/.kiro/powers/github-workflow-security/scripts/* .kiro/scripts/
cp ~/.kiro/powers/github-workflow-security/data/* .kiro/data/
cp ~/.kiro/powers/github-workflow-security/README.md .kiro/

# 设置权限
chmod +x .kiro/scripts/*.py
```

## 🚀 快速开始

### 在 Kiro 中使用

```
使用 github-workflow-security skill 扫描并加固所有 workflow
```

### 命令行使用

```bash
# 加固所有 workflow 文件
python3 .kiro/scripts/harden-workflows.py

# 查询 action 的 commit hash
python3 .kiro/scripts/get-action-commit.py actions/checkout v4

# 查询分支的最新 commit
python3 .kiro/scripts/get-action-commit.py actions/checkout main

# 添加到映射表
python3 .kiro/scripts/get-action-commit.py actions/checkout v4 --save
```

## 📖 使用示例

### 示例 1: 基本加固

```bash
$ python3 .kiro/scripts/harden-workflows.py

🔍 扫描到 3 个 workflow 文件

📄 处理文件: .github/workflows/ci.yml
  ℹ️  已有 permissions 配置，跳过
  ✓ 替换 actions/checkout@v4 → 34e114876b0b... # v4.3.1
  ✓ 替换 docker/setup-buildx-action@v3 → 8d2750c68a42... # v3.12.0
  ✅ 文件已更新

============================================================
📊 处理摘要
============================================================
  扫描文件数: 3
  添加 permissions: 1
  替换 action 版本: 12

✅ 所有 workflow 文件已处理完成
```

### 示例 2: 自定义 Permissions

```bash
python3 .kiro/scripts/harden-workflows.py --permissions "permissions:\n  contents: read\n  pull-requests: write\n"
```

### 示例 3: 查询 Action Commit Hash

```bash
$ python3 .kiro/scripts/get-action-commit.py actions/checkout v4

🔍 正在查询 actions/checkout@v4 ...

✓ 成功获取 commit hash:
  Action: actions/checkout
  Tag: v4
  Version: v4.3.1
  Commit SHA: 34e114876b0b11c390a56381ad16ebd13914f8d5

📋 使用格式:
  - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

## 🔧 工作原理

### 1. Permissions 检查

检查 workflow 是否包含 `permissions` 配置，如果没有则添加：

```yaml
permissions:
  contents: read
```

### 2. Action 版本替换

将 action 版本从 tag 替换为 commit SHA：

```yaml
# 替换前
- uses: actions/checkout@v4

# 替换后
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

### 3. 映射表管理

维护常用 action 的映射表（`.kiro/data/action-commit-map.json`），提高处理速度。

### 4. 自动获取

对于未映射的 action，自动从 GitHub API 获取 commit SHA。

## 📁 文件结构

```
.kiro/
├── skills/
│   └── github-workflow-security.md          # Skill 定义
├── scripts/
│   ├── harden-workflows.py                  # 主加固脚本
│   └── get-action-commit.py                 # 获取 commit hash 工具
├── data/
│   └── action-commit-map.json               # Action 映射表
└── README.md                                # 使用文档
```

## 🎯 支持的 Actions

当前映射表包含以下常用 actions：

| Action | 版本 | Commit SHA |
|--------|------|------------|
| actions/checkout | v2, v3, v4 | ✅ |
| actions/setup-java | v3, v4 | ✅ |
| actions/setup-node | v4 | ✅ |
| actions/cache | v4 | ✅ |
| pnpm/action-setup | v2, v4 | ✅ |
| docker/setup-buildx-action | v3 | ✅ |
| docker/login-action | v3 | ✅ |
| docker/build-push-action | v5 | ✅ |
| stCarolas/setup-maven | v5 | ✅ |
| whelk-io/maven-settings-xml-action | v22 | ✅ |

## ⚙️ 配置选项

### harden-workflows.py

```bash
python3 .kiro/scripts/harden-workflows.py [OPTIONS]

选项:
  --dir DIR                    Workflow 目录 (默认: .github/workflows)
  --permissions PERMISSIONS    自定义 permissions 配置
  --map-file MAP_FILE         映射表文件路径
  -h, --help                  显示帮助信息
```

### get-action-commit.py

```bash
python3 .kiro/scripts/get-action-commit.py <action-name> <tag|branch> [--save]

参数:
  action-name                 Action 名称 (如: actions/checkout)
  tag                        版本标签 (如: v4, v4.3.1)
  branch                     分支名称 (如: master, main, develop)
  --save, -s                 保存到映射表 (仅适用于 tag)

说明:
  - 脚本会自动检测输入是版本标签还是分支名称
  - 版本标签格式: v开头的数字 (如 v4, v4.3.1)
  - 其他格式会被视为分支名称
  - 分支的 commit hash 不会保存到映射表（因为会随时间变化）

示例:
  # 使用版本标签
  python3 .kiro/scripts/get-action-commit.py actions/checkout v4
  python3 .kiro/scripts/get-action-commit.py actions/checkout v4 --save
  
  # 使用分支（自动检测）
  python3 .kiro/scripts/get-action-commit.py actions/checkout main
  python3 .kiro/scripts/get-action-commit.py actions/setup-node master
  python3 .kiro/scripts/get-action-commit.py some/action develop
```

## 🔐 安全最佳实践

1. **最小权限原则**: 只授予必要的权限
2. **固定版本**: 使用 commit SHA 而非可变 tag
3. **定期更新**: 定期检查并更新 action 版本
4. **审计日志**: 通过 Git 历史追踪修改
5. **映射维护**: 及时更新映射表

## ⚠️ 注意事项

1. **GitHub API 限制**: 未认证请求限制 60次/小时
2. **Git 管理**: 所有修改由 Git 管理
3. **权限验证**: 修改后需验证 workflow 正常运行
4. **兼容性**: 支持 `.yml` 和 `.yaml` 格式

## 🤝 贡献

欢迎添加更多 actions 到映射表：

```bash
python3 .kiro/scripts/get-action-commit.py <action-name> <tag> --save
```

## 📄 许可证

MIT License

## 🔗 相关资源

- [GitHub Actions 安全最佳实践](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [使用 Commit SHA 固定 Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
- [Workflow Permissions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#permissions)

## 📞 支持

如有问题或建议，请提交 Issue 或 Pull Request。
