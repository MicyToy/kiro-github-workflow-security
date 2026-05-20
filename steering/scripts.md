### 使用项目脚本

为了保证操作的规范性和安全性，在手动操作或脚本集成时，**应优先使用 `scripts/` 目录下的专用脚本**，避免直接运行原生 `bash` 或 `git` 命令。

#### 1. 准备工作：拉取代码
```bash
# 自动检出并拉取指定分支（如 main）
bash scripts/git-checkout-pull.sh main
```

#### 2. 核心功能：扫描并加固 Workflow
```bash
# 加固所有 workflow 文件（使用默认 permissions）
python3 scripts/harden-workflows.py

# 使用自定义 permissions
python3 scripts/harden-workflows.py --permissions "permissions:\n  contents: read\n  pull-requests: write\n"

# 指定 workflow 目录
python3 scripts/harden-workflows.py --dir .github/workflows
```

#### 3. 辅助功能：查询最新版本
```bash
# 获取指定 action 的最新 Release Tag
bash scripts/github-fetch-release.sh actions/checkout
```

#### 4. 辅助功能：获取 Action 映射
```bash
# 查询并显示映射格式
python3 scripts/get-action-commit.py actions/cache v4

# 查询分支的最新 commit
python3 scripts/get-action-commit.py actions/cache main

# 查询并直接保存到映射表
python3 scripts/get-action-commit.py actions/cache v4 --save
```

#### 5. 完成工作：提交变更
```bash
# 自动添加变更并提交（支持多行 message）
bash scripts/git-commit.sh "chore: harden github workflows security"
```

#### 工具参数详解

- **`harden-workflows.py`**:
  - `--permissions`: 指定自定义权限。
  - `--dir`: 指定扫描目录。
  - `--map-file`: 指定映射文件。
- **`get-action-commit.py`**:
  - `action_name`: Action 仓库名。
  - `tag`: Tag 或分支名。
  - `--save`: 是否保存到 `data/action-commit-map.json`。
