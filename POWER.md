# GitHub Workflow Security Power

自动扫描和加固 GitHub Actions workflow 文件的安全性工具。

## 功能特性

### 🔒 安全加固
- **Permissions 检查**: 自动检查并添加最小权限配置
- **版本固定**: 将 action 版本从可变 tag 替换为不可变 commit SHA
- **供应链安全**: 防止 tag 被恶意修改，提高供应链安全性

### 🔍 智能扫描
- 自动扫描 `.github/workflows/` 目录下的所有 workflow 文件
- 识别所有使用的 GitHub Actions
- 检测缺失的安全配置

### 📊 详细报告
- 显示处理的文件数量
- 统计添加的 permissions 配置
- 列出替换的 action 版本
- 提示未映射的 action

### 🚀 易于使用
- 一键加固所有 workflow 文件
- 支持自定义 permissions 配置
- 提供命令行工具和 Kiro skill 两种使用方式

## 使用场景

1. **新项目初始化**: 为新项目的 workflow 添加安全配置
2. **安全审计**: 定期检查和更新 workflow 的安全设置
3. **合规要求**: 满足企业安全合规要求
4. **供应链安全**: 防止依赖的 action 被恶意修改

## 快速开始

### 在 Kiro 中使用

```
使用 github-workflow-security skill 扫描并加固所有 workflow
```

### 命令行使用

```bash
# 加固所有 workflow 文件
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py

# 查询 action 的 commit hash
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/checkout v4

# 添加到映射表
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/checkout v4 --save
```

## 工作原理
调用SKILL中包含的脚本，完成workflow安全加固的任务。替换完成后可根据用户选择进行Review。

### 1. Permissions 检查
检查 workflow 文件是否包含 `permissions` 配置。如果没有，添加默认配置：
```yaml
permissions:
  contents: read
```

### 2. Action 版本替换
将 action 的版本从 tag 替换为 commit SHA：
```yaml
# 替换前
- uses: actions/checkout@v4

# 替换后
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

### 3. 映射表管理
维护常用 action 的 commit SHA 映射表（`~/.kiro/powers/github-workflow-security/data/action-commit-map.json`），提高处理速度。

### 4. 自动获取
对于未映射的 action，自动从 GitHub API 获取对应的 commit SHA。

### 5. 修改检查
替换完成后，提示用户是否需要使用AI复查内容是否正确修复。

## 文件结构

```
github-workflow-security/
├── skills/
│   └── github-workflow-security.md          # Skill 定义
├── scripts/
│   ├── harden-workflows.py                  # 主加固脚本
│   └── get-action-commit.py                 # 获取 commit hash 工具
├── data/
│   └── action-commit-map.json               # Action 映射表
└── README.md                                # 使用文档
```

## 配置选项

### 自定义 Permissions

```bash
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --permissions "permissions:\n  contents: read\n  pull-requests: write\n"
```

### 指定 Workflow 目录

```bash
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --dir .github/workflows
```

### 指定映射表文件

```bash
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --map-file custom-map.json
```

## 安全最佳实践

1. **最小权限原则**: 只授予 workflow 必要的权限
2. **固定版本**: 使用 commit SHA 而非可变的 tag
3. **定期更新**: 定期检查并更新 action 版本
4. **审计日志**: 通过 Git 历史追踪所有修改
5. **映射维护**: 及时更新映射表中的 action 版本

## 注意事项

1. **GitHub API 限制**: 未认证请求有速率限制（60次/小时），建议预先维护映射表
2. **Git 管理**: 所有修改由 Git 管理，无需额外备份
3. **权限验证**: 修改后需验证 workflow 是否正常运行
4. **兼容性**: 支持 `.yml` 和 `.yaml` 格式的 workflow 文件

## 示例输出

```
🔍 扫描到 3 个 workflow 文件

📄 处理文件: .github/workflows/ci.yml
  ℹ️  已有 permissions 配置，跳过
  ✓ 替换 actions/checkout@v4 → 34e114876b0b... # v4.3.1
  ✓ 替换 docker/setup-buildx-action@v3 → 8d2750c68a42... # v3.12.0
  ✓ 替换 actions/setup-node@v4 → 49933ea5288c... # v4.4.0
  ✅ 文件已更新

============================================================
📊 处理摘要
============================================================
  扫描文件数: 3
  添加 permissions: 1
  替换 action 版本: 12

✅ 所有 workflow 文件已处理完成
```

## 支持的 Actions

当前映射表包含以下常用 actions：
- actions/checkout (v2, v3, v4)
- actions/setup-java (v3, v4)
- actions/setup-node (v4)
- actions/cache (v4)
- pnpm/action-setup (v2, v4)
- docker/setup-buildx-action (v3)
- docker/login-action (v3)
- docker/build-push-action (v5)
- stCarolas/setup-maven (v5)
- whelk-io/maven-settings-xml-action (v22)

可以通过工具脚本轻松添加更多 actions。

## 贡献

欢迎添加更多常用 actions 到映射表！使用以下命令：

```bash
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py <action-name> <tag> --save
```

## 许可证

MIT License
