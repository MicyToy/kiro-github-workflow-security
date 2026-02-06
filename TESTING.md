# GitHub Workflow Security Power - 测试指南

## 快速测试

### 1. 测试 get-action-commit.py

```bash
# 测试查询功能
python3 ~/.kiro/powers/github-workflow-security/scripts/get-action-commit.py actions/checkout v4

# 预期输出:
# ✓ 成功获取 commit hash:
#   Action: actions/checkout
#   Tag: v4
#   Version: v4.3.1
#   Commit SHA: 34e114876b0b11c390a56381ad16ebd13914f8d5
```

### 2. 测试 harden-workflows.py

```bash
# 在测试项目中运行
cd /path/to/test/project
python3 ~/.kiro/powers/github-workflow-security/scripts/harden-workflows.py --help

# 预期输出: 显示帮助信息
```

### 3. 测试安装脚本

```bash
# 创建测试目录
mkdir -p /tmp/test-workflow-security
cd /tmp/test-workflow-security
git init

# 创建测试 workflow
mkdir -p .github/workflows
cat > .github/workflows/test.yml << 'EOF'
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
EOF

# 运行安装脚本
bash ~/.kiro/powers/github-workflow-security/install.sh

# 验证文件已复制
ls -la .kiro/

# 运行加固脚本
python3 .kiro/scripts/harden-workflows.py

# 检查结果
cat .github/workflows/test.yml
```

### 4. 测试 Kiro Skill

在 Kiro 中执行：

```
使用 github-workflow-security skill 扫描并加固所有 workflow
```

## 测试用例

### 用例 1: 添加 Permissions

**输入 workflow:**
```yaml
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```

**预期输出:**
```yaml
name: Test
on: push

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

### 用例 2: 替换 Action 版本

**输入:**
```yaml
- uses: actions/checkout@v4
- uses: docker/setup-buildx-action@v3
```

**预期输出:**
```yaml
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
- uses: docker/setup-buildx-action@8d2750c68a42422c14e847fe6c8ac0403b4cbd6f # v3.12.0
```

### 用例 3: 跳过已有 Permissions

**输入:**
```yaml
name: Test
on: push
permissions:
  contents: write
jobs:
  test:
    runs-on: ubuntu-latest
```

**预期行为:**
- 不修改 permissions
- 只替换 action 版本

### 用例 4: 处理未映射的 Action

**输入:**
```yaml
- uses: some/unknown-action@v1
```

**预期行为:**
- 尝试从 GitHub API 获取
- 如果失败，在报告中列出
- 不修改原始内容

## 验证清单

- [ ] get-action-commit.py 可以查询 action commit hash
- [ ] get-action-commit.py --save 可以保存到映射表
- [ ] harden-workflows.py 可以扫描 workflow 文件
- [ ] harden-workflows.py 可以添加 permissions
- [ ] harden-workflows.py 可以替换 action 版本
- [ ] harden-workflows.py 可以处理未映射的 action
- [ ] 安装脚本可以正确复制文件
- [ ] Kiro skill 可以正常工作
- [ ] 修改后的 workflow 格式正确
- [ ] Git 可以追踪所有修改

## 性能测试

```bash
# 测试处理大量 workflow 文件
time python3 .kiro/scripts/harden-workflows.py

# 预期: 每个文件 < 1秒
```

## 错误处理测试

### 测试 1: 不存在的目录

```bash
python3 .kiro/scripts/harden-workflows.py --dir /nonexistent

# 预期: 显示错误信息
```

### 测试 2: 无效的 workflow 文件

```bash
echo "invalid yaml" > .github/workflows/invalid.yml
python3 .kiro/scripts/harden-workflows.py

# 预期: 显示错误但继续处理其他文件
```

### 测试 3: GitHub API 限制

```bash
# 连续查询多个未映射的 action
for i in {1..70}; do
  python3 .kiro/scripts/get-action-commit.py actions/checkout v$i 2>&1 | grep -i "rate limit"
done

# 预期: 显示 rate limit 错误
```

## 回归测试

在每次修改后运行：

```bash
# 1. 备份测试项目
cp -r test-project test-project.backup

# 2. 运行加固脚本
cd test-project
python3 .kiro/scripts/harden-workflows.py

# 3. 验证 workflow 语法
# 使用 actionlint 或 GitHub Actions 验证器

# 4. 对比差异
diff -r test-project.backup test-project

# 5. 恢复备份
rm -rf test-project
mv test-project.backup test-project
```

## 集成测试

```bash
# 完整流程测试
cd test-project

# 1. 安装 power
bash ~/.kiro/powers/github-workflow-security/install.sh

# 2. 查询并添加新 action
python3 .kiro/scripts/get-action-commit.py actions/cache v4 --save

# 3. 加固 workflow
python3 .kiro/scripts/harden-workflows.py

# 4. 验证结果
cat .github/workflows/*.yml

# 5. 提交更改
git add .
git commit -m "chore: harden GitHub Actions workflows"
```

## 故障排除

### 问题 1: Python 版本不兼容

```bash
python3 --version
# 需要 Python 3.8+
```

### 问题 2: 权限问题

```bash
chmod +x .kiro/scripts/*.py
```

### 问题 3: 映射表损坏

```bash
# 验证 JSON 格式
python3 -m json.tool .kiro/data/action-commit-map.json
```

## 报告问题

如果测试失败，请提供：

1. Python 版本
2. 操作系统
3. 错误信息
4. 测试用的 workflow 文件
5. 完整的命令输出
