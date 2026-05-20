### 使用 Git MCP（推荐）

如果你的环境中配置了 Git MCP，可以直接通过对话指令调用相关工具，它会自动处理 API 调用和文件读写：

#### 典型指令示例
```
# 使用 Git MCP 搜索并加固项目中的 workflows
1. 搜索 .github/workflows 目录下的 yml 文件
2. 如果用户要求升级action版本，则使用MCP工具获取新的action Release版本。默认不升级major版本。
3. 对每个文件执行安全加固建议（添加 permissions，固定 action 版本为 SHA）
4. 拉取修复分支，分支格式为 opt/ci_xxx
5. 提交修改并创建 Pull Request。提交message格式：
   chore: update action versions
   - some/action@v1
```

#### 工作流细节
- **搜索**: 自动定位所有 workflow 定义。
- **加固**: 结合 `harden-workflows.py` 的逻辑，通过 MCP 接口进行文件读写。
- **提交**: 自动管理 Git 分支和 PR 创建。
