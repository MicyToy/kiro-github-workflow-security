#!/usr/bin/env python3
"""
GitHub Workflow 安全加固脚本

自动扫描并加固 GitHub Actions workflow 文件：
1. 检查并添加 permissions 配置
2. 将 action 版本从 tag 替换为 commit SHA
3. 报告未映射的 action
"""

import sys
import json
import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


class WorkflowHardener:
    """Workflow 安全加固器"""
    
    def __init__(self, workflows_dir: str = ".github/workflows", 
                 map_file: Optional[str] = None):
        self.workflows_dir = Path(workflows_dir)
        
        # 如果没有指定映射文件，使用 power 自身目录中的文件
        if map_file is None:
            # 获取脚本所在目录
            script_dir = Path(__file__).parent.resolve()
            # power 目录结构: scripts/harden-workflows.py
            # 映射文件位置: data/action-commit-map.json
            power_dir = script_dir.parent
            self.map_file = power_dir / 'data' / 'action-commit-map.json'
        else:
            self.map_file = Path(map_file)
        
        self.action_map = self._load_action_map()
        self.unmapped_actions = []
        self.stats = {
            'files_scanned': 0,
            'permissions_added': 0,
            'actions_replaced': 0,
            'unmapped_found': 0
        }
        self.logger = logging.getLogger(__name__)
    
    def _load_action_map(self) -> Dict:
        """加载 action commit SHA 映射表"""
        if self.map_file.exists():
            with open(self.map_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _get_commit_from_api(self, action_name: str, tag: str) -> Optional[Tuple[str, str]]:
        """从 GitHub API 获取 commit SHA"""
        if not tag.startswith('v'):
            tag = f'v{tag}'
        
        api_url = f'https://api.github.com/repos/{action_name}/git/refs/tags/{tag}'
        
        try:
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'GitHub-Action-Security-Tool')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'object' in data:
                    commit_sha = data['object']['sha']
                    return commit_sha, tag
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.logger.warning(f"无法从 API 获取 {action_name}@{tag}: tag 不存在")
            else:
                self.logger.error(f"无法从 API 获取 {action_name}@{tag}: HTTP {e.code}")
        except Exception as e:
            self.logger.error(f"无法从 API 获取 {action_name}@{tag}: {e}")
        
        return None
    
    def _check_permissions(self, content: str) -> bool:
        """检查是否已设置 permissions
        
        检查顶层和 job 级别的 permissions 配置。
        如果存在任何 permissions 配置则返回 True。
        
        Returns:
            bool: True 如果存在任何 permissions 配置，否则 False
        """
        has_top_level = False
        has_job_level = False
        
        # 检查顶层 permissions（支持块格式和内联格式）
        # 块格式: permissions:\n  contents: read
        # 内联格式: permissions: read-all 或 permissions: {}
        top_level_pattern = r'^permissions:\s*(?:\n|$|[^\n]+)'
        if re.search(top_level_pattern, content, re.MULTILINE):
            has_top_level = True
            self.logger.info("检测到顶层 permissions 配置")
        
        # 检查 job 级别的 permissions
        # 匹配 jobs: 块中的任何 permissions 配置
        # 格式: jobs:\n  job-name:\n    permissions:
        job_permissions_pattern = r'^jobs:\s*\n(?:.*\n)*?^\s+\w+:\s*\n(?:.*\n)*?^\s+permissions:\s*(?:\n|$|[^\n]+)'
        if re.search(job_permissions_pattern, content, re.MULTILINE):
            has_job_level = True
            self.logger.info("检测到 job 级别 permissions 配置")
        
        if has_top_level or has_job_level:
            self.logger.info("已存在 permissions 配置，将跳过添加默认 permissions")
            return True
        
        self.logger.info("未检测到 permissions 配置")
        return False
    
    def _add_permissions(self, content: str, permissions: str = "permissions:\n  contents: read\n") -> str:
        """添加 permissions 配置"""
        self.logger.info("添加默认 permissions 配置到 workflow 文件")
        
        # 在 on: 之后添加 permissions
        if 'on:' in content:
            content = re.sub(
                r'(on:.*?\n(?:  .*\n)*)',
                r'\1\n' + permissions + '\n',
                content,
                count=1
            )
            self.logger.info("已在 'on:' 配置后添加 permissions")
        else:
            # 如果没有 on:，在 name: 之后添加
            content = re.sub(
                r'(name:.*?\n)',
                r'\1\n' + permissions + '\n',
                content,
                count=1
            )
            self.logger.info("已在 'name:' 配置后添加 permissions")
        
        return content
    
    def _replace_action_versions(self, content: str) -> Tuple[str, int]:
        """替换 action 版本为 commit SHA"""
        replaced_count = 0
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # 匹配 uses: owner/repo@version 格式（支持不同缩进）
            match = re.match(r'^(\s*-?\s*uses:\s+)([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)@([a-zA-Z0-9._-]+)(\s*(?:#.*)?)$', line)
            
            if match:
                prefix = match.group(1)
                action_name = match.group(2)
                version = match.group(3)
                comment = match.group(4).rstrip()
                
                # 如果已经是 commit SHA（40个字符的十六进制），跳过
                if len(version) == 40 and all(c in '0123456789abcdef' for c in version.lower()):
                    new_lines.append(line)
                    continue
                
                # 查找映射
                key = f"{action_name}@{version}"
                if key in self.action_map:
                    mapping = self.action_map[key]
                    commit_sha = mapping['sha']
                    mapped_version = mapping['version']
                    replaced_count += 1
                    print(f"  ✓ 替换 {action_name}@{version} → {commit_sha[:12]}... # {mapped_version}")
                    new_lines.append(f"{prefix}{action_name}@{commit_sha} # {mapped_version}")
                else:
                    # 尝试从 API 获取
                    result = self._get_commit_from_api(action_name, version)
                    if result:
                        commit_sha, tag = result
                        replaced_count += 1
                        print(f"  ✓ 替换 {action_name}@{version} → {commit_sha[:12]}... # {tag} (从 API 获取)")
                        new_lines.append(f"{prefix}{action_name}@{commit_sha} # {tag}")
                    else:
                        # 记录未映射的 action
                        self.unmapped_actions.append(f"{action_name}@{version}")
                        print(f"  ⚠️  未找到映射: {action_name}@{version}")
                        new_lines.append(line)
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        return new_content, replaced_count
    
    def harden_file(self, filepath: Path, custom_permissions: Optional[str] = None) -> bool:
        """加固单个 workflow 文件"""
        try:
            rel_path = filepath.relative_to(Path.cwd())
        except ValueError:
            rel_path = filepath
        print(f"\n📄 处理文件: {rel_path}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # 1. 检查并添加 permissions
            if not self._check_permissions(content):
                permissions = custom_permissions or "permissions:\n  contents: read\n"
                content = self._add_permissions(content, permissions)
                print(f"  ✓ 添加 permissions 配置")
                self.stats['permissions_added'] += 1
                modified = True
            else:
                print(f"  ℹ️  已有 permissions 配置，跳过添加（保留现有配置）")
            
            # 2. 替换 action 版本
            content, replaced = self._replace_action_versions(content)
            if replaced > 0:
                self.stats['actions_replaced'] += replaced
                modified = True
            
            # 3. 保存修改
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ 文件已更新")
                return True
            else:
                print(f"  ℹ️  无需修改")
                return False
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}", file=sys.stderr)
            return False
    
    def scan_and_harden(self, custom_permissions: Optional[str] = None) -> None:
        """扫描并加固所有 workflow 文件"""
        if not self.workflows_dir.exists():
            print(f"❌ 目录不存在: {self.workflows_dir}")
            return
        
        # 查找所有 workflow 文件
        workflow_files = list(self.workflows_dir.glob("*.yml")) + \
                        list(self.workflows_dir.glob("*.yaml"))
        
        if not workflow_files:
            print(f"❌ 未找到 workflow 文件: {self.workflows_dir}")
            return
        
        print(f"🔍 扫描到 {len(workflow_files)} 个 workflow 文件")
        
        # 处理每个文件
        for filepath in workflow_files:
            self.harden_file(filepath, custom_permissions)
            self.stats['files_scanned'] += 1
        
        # 输出统计信息
        self._print_summary()
    
    def _print_summary(self) -> None:
        """输出统计摘要"""
        print("\n" + "="*60)
        print("📊 处理摘要")
        print("="*60)
        print(f"  扫描文件数: {self.stats['files_scanned']}")
        print(f"  添加 permissions: {self.stats['permissions_added']}")
        print(f"  替换 action 版本: {self.stats['actions_replaced']}")
        
        # 输出未映射的 action
        if self.unmapped_actions:
            unique_unmapped = list(set(self.unmapped_actions))
            print(f"\n⚠️  发现 {len(unique_unmapped)} 个未映射的 action:")
            for action in unique_unmapped:
                print(f"  - {action}")
            print(f"\n💡 使用以下命令获取 commit hash:")
            for action in unique_unmapped:
                parts = action.split('@')
                if len(parts) == 2:
                    print(f"  python3 .kiro/scripts/get-action-commit.py {parts[0]} {parts[1]} --save")
        
        print("\n✅ 所有 workflow 文件已处理完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='GitHub Workflow 安全加固工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 加固所有 workflow 文件（使用默认 permissions）
  python3 harden-workflows.py
  
  # 使用自定义 permissions
  python3 harden-workflows.py --permissions "permissions:\\n  contents: read\\n  pull-requests: write\\n"
  
  # 指定 workflow 目录
  python3 harden-workflows.py --dir .github/workflows
        """
    )
    
    parser.add_argument(
        '--dir',
        default='.github/workflows',
        help='Workflow 文件目录 (默认: .github/workflows)'
    )
    
    parser.add_argument(
        '--permissions',
        help='自定义 permissions 配置'
    )
    
    parser.add_argument(
        '--map-file',
        default=None,
        help='Action 映射表文件路径 (默认: 使用 power 自身目录中的映射文件)'
    )
    
    args = parser.parse_args()
    
    # 创建加固器并执行
    hardener = WorkflowHardener(
        workflows_dir=args.dir,
        map_file=args.map_file
    )
    
    hardener.scan_and_harden(custom_permissions=args.permissions)


if __name__ == '__main__':
    main()
