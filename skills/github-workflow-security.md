# GitHub Workflow 安全加固

这个 skill 用于自动扫描和加固 GitHub Actions workflow 文件的安全性。

## 激活方式

当用户提到以下关键词时，自动激活此 skill：
- workflow security / workflow 安全
- github actions security / GitHub Actions 安全
- action commit hash / action 提交哈希
- workflow permissions / workflow 权限
- 加固 workflow / harden workflow

## 功能

1. **扫描项目中的所有 GitHub workflow 文件**
   - 自动查找 `.github/workflows/` 目录下的所有 YAML 文件

2. **检查和添加 permissions 配置**
   - 如果 workflow 已设置 `permissions`，则跳过
   - 如果未设置，根据用户提示添加 permissions
   - 默认添加 `permissions: { contents: read }`

3. **将 action 版本从 tag 替换为 commit SHA**
   - 扫描所有 `uses:` 步骤
   - 将版本标签（如 `@v4`）替换为完整的 commit SHA
   - 格式：`actions/checkout@<commit-sha> # v4.3.1`
   - 提高供应链安全性，防止标签被恶意修改

4. **自动获取 commit SHA**
   - 如果本地映射不存在，自动从 GitHub API 获取
   - 获取对应 tag 的 commit hash 和详细版本号

## 使用方法

### 方式 1: 通过 Kiro Skill（推荐）

在 Kiro 中直接使用：
```
使用 github-workflow-security skill 扫描并加固所有 workflow
```

或指定自定义 permissions：
```
使用 github-workflow-security skill，设置 permissions 为：
permissions:
  contents: read
  pull-requests: write
```

### 方式 2: 直接运行脚本

```bash
# 加固所有 workflow 文件（使用默认 permissions）
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py

# 使用自定义 permissions
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --permissions "permissions:\n  contents: read\n  pull-requests: write\n"

# 指定 workflow 目录
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --dir .github/workflows
```

### 方式 3: 添加新的 action 映射

```bash
# 查询并显示映射格式
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/cache v4

# 查询分支的最新 commit
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/cache main

# 查询并直接保存到映射表
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/cache v4 --save
```

## 实现逻辑
调用SKILL中包含的脚本，完成workflow安全加固的任务。替换完成后可根据用户选择进行Review。

### 步骤 1: 扫描 workflow 文件
- 列出 `.github/workflows/` 目录下的所有 `.yml` 和 `.yaml` 文件
- 读取每个文件内容

### 步骤 2: 检查 permissions
```yaml
# 如果文件中没有 permissions 字段，添加：
permissions:
  contents: read
```

### 步骤 3: 替换 action 版本为 commit SHA
对于每个 `uses:` 行：
1. 解析 action 名称和版本（如 `actions/checkout@v4`）
2. 从 `~/.kiro/powers/github-workflow-security/data/action-commit-map.json` 查找映射
3. 如果找到映射，直接使用
4. 如果未找到，调用 Python 脚本从 GitHub API 获取
5. 替换格式：
```yaml
# 原始格式
- uses: actions/checkout@v4

# 替换为
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

### 步骤 4: 获取 commit SHA 和报告未映射的 action
如果需要从 GitHub 获取 commit SHA：
1. 解析 action 名称和版本标签（如 `actions/checkout@v4`）
2. 构造 GitHub API URL: `https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{tag}`
3. 获取 tag 对应的 commit SHA
4. 获取详细版本号（如果是语义化版本）

### 步骤 5: Review修改
替换完成后，提示用户是否需要使用AI Review内容。如果是：
1. 使用`git diff`查看本次修改
2. 将修改输入到AI，由AI Review是否完成了SKILL的目标。

**重要**: 替换完成后，输出所有在映射表（`~/.kiro/powers/github-workflow-security/data/action-commit-map.json`）中不存在的 action，提示用户将其添加到映射表中，格式如下：
```
⚠️ 发现未映射的 action，建议添加到映射表：
- some/action@v1 → some/action@abc123... # v1.2.3

可使用以下命令获取 commit hash：
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py some/action v1
```
### 步骤 6: 提交修改
用户Review完成后，询问用户是否需要提交。如果用户回答是，则：

1. 自动提交代码。commit message中列出处理过的action版本，格式为
  ```
    chrone: update action versions
    - some/action@v1
  ```
2. 始终调用`git-commit.sh`脚本提交，提交message由参数传入。

## Action Commit SHA 映射表

映射表存储在独立文件中以减少 context 消耗：`~/.kiro/powers/github-workflow-security/data/action-commit-map.json`

使用时读取该文件获取预定义的 action commit SHA 映射。如果映射不存在，则使用 Python 脚本从 GitHub API 获取。

## GitHub API 使用

### 使用 Python 脚本获取 commit SHA

项目提供了便捷的 Python 脚本来获取 action 的 commit hash：

```bash
# 基本用法
python ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/checkout v4

# 查询分支
python ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/checkout main

# 其他示例
python ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py docker/setup-buildx-action v3.12.0
python ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py pnpm/action-setup 4.2.0
```

脚本会输出：
- Action 名称和版本
- Commit SHA
- 格式化的 uses 语句
- 映射表格式（可直接复制到 skill 文件）

### 手动使用 curl 获取

如果需要手动查询：

```bash
# 获取 tag 的 commit SHA
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{tag}

# 获取 release 信息
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}
```

## 注意事项

1. **API 限制**: GitHub API 对未认证请求有速率限制（60次/小时）
2. **Git 管理**: 由于项目使用 Git 管理，修改前不需要额外备份
3. **验证**: 修改后使用 `actionlint` 或 GitHub Actions 语法检查验证
4. **权限**: 确保 permissions 设置符合实际需求，过度限制可能导致 workflow 失败
5. **未映射提示**: 完成替换后会提示所有未在映射表中的 action，建议添加到映射表

## 安全最佳实践

1. **最小权限原则**: 只授予必要的 permissions
2. **固定版本**: 使用 commit SHA 而非可变的 tag
3. **定期更新**: 定期检查并更新 action 版本
4. **审计日志**: 记录所有修改，便于追溯

## 文件结构

```
github-workflow-security/
├── skills/
│   └── github-workflow-security.md          # Skill 定义文件
├── scripts/
│   └── get-action-commit.py                 # 获取 commit hash 的工具脚本
└── data/
    └── action-commit-map.json               # Action commit SHA 映射表
```

## 示例输出

```
✓ 扫描到 3 个 workflow 文件
✓ .github/workflows/ci.yml
  - 已有 permissions 配置，跳过
  - 替换 actions/checkout@v4 → actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
  - 替换 docker/setup-buildx-action@v3 → docker/setup-buildx-action@8d2750c68a42422c14e847fe6c8ac0403b4cbd6f # v3.12.0
  - 替换 pnpm/action-setup@v4 → pnpm/action-setup@41ff72655975bd51cab0327fa583b6e92b6d3061 # v4.2.0
  - 替换 actions/setup-node@v4 → actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
  - 替换 docker/login-action@v3 → docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3.7.0
  - 替换 docker/build-push-action@v5 → docker/build-push-action@ca052bb54ab0790a636c9b5f226502c73d547a25 # v5.4.0
  ✓ 已更新 6 个 action 版本

✓ 所有 workflow 文件已加固完成
```
