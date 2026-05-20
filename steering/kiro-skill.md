### 通过 Kiro Skill（推荐）

在 Kiro 中直接使用自然语言指令即可激活安全加固流程：

#### 基本用法
```
使用 github-workflow-security skill 扫描并加固所有 workflow
```

#### 自定义 Permissions
```
使用 github-workflow-security skill，设置 permissions 为：
permissions:
  contents: read
  pull-requests: write
```

#### 升级 Action 版本
```
使用 github-workflow-security skill 扫描并更新所有 action 到最新版本
```
