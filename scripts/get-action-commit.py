#!/usr/bin/env python3
"""
GitHub Action Commit Hash 获取工具

用法:
    # 使用版本标签
    python get-action-commit.py actions/checkout v4
    python get-action-commit.py docker/setup-buildx-action v3.12.0
    python get-action-commit.py actions/checkout v4 --save  # 保存到映射表
    
    # 使用分支（不会保存到映射表）
    python get-action-commit.py actions/checkout master
    python get-action-commit.py actions/checkout main
"""

import sys
import json
import urllib.request
import urllib.error
import os
import re
from typing import Optional, Tuple, List
from pathlib import Path
from dataclasses import dataclass


from dataclasses import dataclass


@dataclass
class Version:
    """表示一个语义化版本号"""
    major: int
    minor: Optional[int]
    patch: Optional[int]
    prefix: str  # 如 "v"
    original: str  # 原始字符串
    
    def matches_pattern(self, pattern: 'Version') -> bool:
        """
        检查此版本是否匹配给定的模式
        
        例如:
        - v5.4.0 匹配 v5 (主版本匹配)
        - v5.4.0 匹配 v5.4 (主版本和次版本匹配)
        - v5.4.0 匹配 v5.4.0 (完全匹配)
        - v6.0.0 不匹配 v5 (主版本不同)
        """
        # 主版本必须匹配
        if self.major != pattern.major:
            return False
        
        # 如果模式指定了次版本，次版本也必须匹配
        if pattern.minor is not None:
            if self.minor != pattern.minor:
                return False
        
        # 如果模式指定了补丁版本，补丁版本也必须匹配
        if pattern.patch is not None:
            if self.patch != pattern.patch:
                return False
        
        return True
    
    def __lt__(self, other: 'Version') -> bool:
        """用于排序的比较方法"""
        return (self.major, self.minor or 0, self.patch or 0) < \
               (other.major, other.minor or 0, other.patch or 0)
    
    def __str__(self) -> str:
        """返回完整的版本字符串"""
        parts = [str(self.major)]
        if self.minor is not None:
            parts.append(str(self.minor))
            if self.patch is not None:
                parts.append(str(self.patch))
        return f"{self.prefix}{'.'.join(parts)}"


def parse_version(version_str: str) -> Optional[Version]:
    """
    解析版本号字符串为 Version 对象
    
    支持的格式:
    - v5 (主版本)
    - v5.4 (主版本.次版本)
    - v5.4.0 (主版本.次版本.补丁版本)
    - 5.4.0 (无前缀)
    
    Args:
        version_str: 版本号字符串
    
    Returns:
        Version 对象，如果格式无效则返回 None
    """
    # 提取前缀（如 "v"）
    prefix = ""
    version_part = version_str
    if version_str and not version_str[0].isdigit():
        prefix = version_str[0]
        version_part = version_str[1:]
    
    # 使用正则表达式解析版本号
    # 支持 major, major.minor, major.minor.patch
    pattern = r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?$'
    match = re.match(pattern, version_part)
    
    if not match:
        return None
    
    major = int(match.group(1))
    minor = int(match.group(2)) if match.group(2) else None
    patch = int(match.group(3)) if match.group(3) else None
    
    return Version(
        major=major,
        minor=minor,
        patch=patch,
        prefix=prefix,
        original=version_str
    )


def find_latest_matching_version(versions: List[str], pattern: str) -> Optional[str]:
    """
    从版本列表中找到匹配模式的最新版本
    
    例如:
    - pattern="v5" 匹配所有 v5.x.x 版本，返回最新的
    - pattern="v5.4" 匹配所有 v5.4.x 版本，返回最新的
    - pattern="v5.4.0" 精确匹配 v5.4.0
    
    Args:
        versions: 版本号字符串列表
        pattern: 版本模式字符串
    
    Returns:
        匹配的最新版本字符串，如果没有匹配则返回 None
    """
    pattern_version = parse_version(pattern)
    if not pattern_version:
        return None
    
    matching_versions = []
    
    for v in versions:
        version = parse_version(v)
        if version and version.matches_pattern(pattern_version):
            matching_versions.append(version)
    
    if not matching_versions:
        return None
    
    # 按语义化版本排序，返回最新的
    latest = max(matching_versions)
    return latest.original


def suggest_available_versions(all_tags: List[str], requested_version: str, action_name: str) -> None:
    """
    当版本未找到时，建议可用的版本

    Args:
        all_tags: 所有可用的 tag 列表
        requested_version: 用户请求的版本
        action_name: action 名称
    """
    print(f"\n💡 建议:", file=sys.stderr)

    # 解析请求的版本以获取主版本号
    parsed_requested = parse_version(requested_version)
    if not parsed_requested:
        print(f"  请访问 https://github.com/{action_name}/tags 查看所有可用版本", file=sys.stderr)
        return

    # 按主版本号分组可用的版本
    versions_by_major = {}
    for tag in all_tags:
        parsed = parse_version(tag)
        if parsed:
            major = parsed.major
            if major not in versions_by_major:
                versions_by_major[major] = []
            versions_by_major[major].append(parsed)

    # 如果没有找到任何有效版本
    if not versions_by_major:
        print(f"  未找到有效的版本标签", file=sys.stderr)
        print(f"  请访问 https://github.com/{action_name}/tags 查看所有可用版本", file=sys.stderr)
        return

    # 对每个主版本的版本列表进行排序
    for major in versions_by_major:
        versions_by_major[major].sort(reverse=True)

    # 显示相近的主版本
    requested_major = parsed_requested.major
    nearby_majors = sorted([m for m in versions_by_major.keys()
                           if abs(m - requested_major) <= 2])

    if not nearby_majors:
        nearby_majors = sorted(versions_by_major.keys())[:5]  # 显示前5个主版本

    print(f"  可用的版本 (按主版本分组):", file=sys.stderr)
    for major in nearby_majors:
        versions = versions_by_major[major]
        latest = versions[0]  # 已排序，第一个是最新的

        # 显示该主版本的最新版本
        if major == requested_major:
            print(f"    v{major}.x.x: {latest.original} (最新) ← 您请求的主版本", file=sys.stderr)
        else:
            print(f"    v{major}.x.x: {latest.original} (最新)", file=sys.stderr)

        # 如果该主版本有多个版本，显示前3个
        if len(versions) > 1:
            other_versions = [v.original for v in versions[1:4]]
            if other_versions:
                print(f"             其他: {', '.join(other_versions)}", file=sys.stderr)

    # 如果还有更多主版本未显示
    if len(versions_by_major) > len(nearby_majors):
        remaining = len(versions_by_major) - len(nearby_majors)
        print(f"  ... 还有 {remaining} 个其他主版本", file=sys.stderr)

    print(f"\n  查看所有版本: https://github.com/{action_name}/tags", file=sys.stderr)



def get_branch_commit(action_name: str, branch: str) -> Optional[Tuple[str, str]]:
    """
    从 GitHub API 获取指定分支的最新 commit hash
    
    Args:
        action_name: action 名称，如 'actions/checkout'
        branch: 分支名称，如 'master' 或 'main'
    
    Returns:
        (commit_sha, branch_name) 或 None
    """
    try:
        # 获取分支信息
        branch_url = f'https://api.github.com/repos/{action_name}/branches/{branch}'
        req = urllib.request.Request(branch_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'GitHub-Action-Security-Tool')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            branch_data = json.loads(response.read().decode('utf-8'))
            commit_sha = branch_data['commit']['sha']
            return commit_sha, branch
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ 错误: 未找到分支 '{branch}' 在仓库 {action_name} 中", file=sys.stderr)
            print(f"💡 提示: 尝试使用 'master' 或 'main' 分支", file=sys.stderr)
        else:
            print(f"❌ HTTP 错误 {e.code}: {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 查询分支时出错: {e}", file=sys.stderr)
        return None


def get_commit_hash(action_name: str, tag: str) -> Optional[Tuple[str, str]]:
    """
    从 GitHub API 获取指定 action tag 的 commit hash
    
    如果 tag 是主版本号（如 v5），会自动查找该主版本下的最新版本（如 v5.4.0）
    
    Args:
        action_name: action 名称，如 'actions/checkout'
        tag: 版本标签，如 'v4' 或 'v4.3.1'
    
    Returns:
        (commit_sha, tag_name) 或 None
    """
    # 确保 tag 以 v 开头
    if not tag.startswith('v'):
        tag = f'v{tag}'
    
    # 解析版本号以确定是否需要查找匹配的版本
    parsed_version = parse_version(tag)
    if not parsed_version:
        print(f"❌ 错误: 无效的版本号格式: {tag}", file=sys.stderr)
        return None
    
    # 获取所有 tags（这个 API 调用返回 commit SHA，适用于 lightweight 和 annotated tags）
    # 支持分页以获取所有 tags
    try:
        tags_data = []
        page = 1
        per_page = 100
        
        while True:
            tags_url = f'https://api.github.com/repos/{action_name}/tags?per_page={per_page}&page={page}'
            req = urllib.request.Request(tags_url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'GitHub-Action-Security-Tool')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                page_data = json.loads(response.read().decode('utf-8'))
                
                if not page_data:
                    break
                
                tags_data.extend(page_data)
                
                # 如果返回的数据少于 per_page，说明已经是最后一页
                if len(page_data) < per_page:
                    break
                
                page += 1
                
                # 安全限制：最多获取 500 个 tags
                if len(tags_data) >= 500:
                    break
        
        # 如果是主版本号（如 v5）或主次版本号（如 v5.4），需要查找最新的匹配版本
        if parsed_version.minor is None or parsed_version.patch is None:
            print(f"🔍 检测到主版本号 {tag}，正在查找最新的匹配版本...")
            
            # 提取所有 tag 名称
            all_tags = [t['name'] for t in tags_data]
            
            # 查找匹配的最新版本
            latest_matching = find_latest_matching_version(all_tags, tag)
            
            if latest_matching:
                print(f"✓ 找到匹配版本: {latest_matching}")
                tag = latest_matching
            else:
                print(f"❌ 错误: 未找到匹配 {tag} 的版本", file=sys.stderr)
                # 建议可用的版本
                suggest_available_versions(all_tags, tag, action_name)
                return None
        
        # 从 tags_data 中查找对应的 tag 并获取其 commit SHA
        for tag_info in tags_data:
            if tag_info['name'] == tag:
                commit_sha = tag_info['commit']['sha']
                return commit_sha, tag
        
        # 如果没找到，说明 tag 不存在
        print(f"❌ 错误: 标签 '{tag}' 在仓库 {action_name} 中不存在", file=sys.stderr)
        
        # 建议可用的版本
        all_tags = [t['name'] for t in tags_data]
        suggest_available_versions(all_tags, tag, action_name)
        return None
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"❌ 错误: 未找到仓库 {action_name}", file=sys.stderr)
        else:
            print(f"❌ HTTP 错误 {e.code}: {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 查询 tags 时出错: {e}", file=sys.stderr)
        return None


def get_map_file_path() -> Path:
    """获取映射表文件路径"""
    script_dir = Path(__file__).parent
    map_file = script_dir.parent / 'data' / 'action-commit-map.json'
    return map_file


def load_action_map() -> dict:
    """加载现有的映射表"""
    map_file = get_map_file_path()
    if map_file.exists():
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_to_map(action_name: str, tag: str, commit_sha: str, version: str) -> bool:
    """保存到映射表文件"""
    try:
        map_file = get_map_file_path()
        map_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有映射
        action_map = load_action_map()
        
        # 添加新映射
        key = f"{action_name}@{tag}"
        action_map[key] = {
            "sha": commit_sha,
            "version": version
        }
        
        # 保存回文件（格式化输出）
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(action_map, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 已保存到映射表: {map_file}")
        return True
    except Exception as e:
        print(f"\n❌ 保存失败: {e}", file=sys.stderr)
        return False


def format_output(action_name: str, tag: str, commit_sha: str, version: str, saved: bool = False, is_branch: bool = False) -> None:
    """格式化输出结果"""
    print(f"\n✓ 成功获取 commit hash:")
    print(f"  Action: {action_name}")
    if is_branch:
        print(f"  Branch: {tag}")
        print(f"  Commit SHA: {commit_sha}")
        print(f"\n📋 使用格式:")
        print(f"  - uses: {action_name}@{commit_sha} # {tag} branch")
        print(f"\n⚠️  注意: 分支的 commit hash 会随时间变化，建议定期更新")
    else:
        print(f"  Tag: {tag}")
        print(f"  Version: {version}")
        print(f"  Commit SHA: {commit_sha}")
        print(f"\n📋 使用格式:")
        print(f"  - uses: {action_name}@{commit_sha} # {version}")
        
        if not saved:
            print(f"\n📝 映射表格式:")
            print(f"  \"{action_name}@{tag}\": {{")
            print(f"    \"sha\": \"{commit_sha}\",")
            print(f"    \"version\": \"{version}\"")
            print(f"  }}")
            print(f"\n💡 提示: 使用 --save 参数可直接保存到映射表")


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python get-action-commit.py <action-name> <tag|branch> [--save]")
        print("\n示例:")
        print("  # 使用版本标签")
        print("  python get-action-commit.py actions/checkout v4")
        print("  python get-action-commit.py docker/setup-buildx-action v3.12.0")
        print("  python get-action-commit.py pnpm/action-setup 4.2.0")
        print("  python get-action-commit.py actions/checkout v4 --save  # 保存到映射表")
        print("\n  # 使用分支（不会保存到映射表）")
        print("  python get-action-commit.py actions/checkout master")
        print("  python get-action-commit.py actions/checkout main")
        sys.exit(1)
    
    action_name = sys.argv[1]
    tag_or_branch = sys.argv[2]
    should_save = '--save' in sys.argv or '-s' in sys.argv
    
    # 首先尝试作为版本标签处理
    parsed_version = parse_version(tag_or_branch if tag_or_branch.startswith('v') else f'v{tag_or_branch}')
    
    # 如果是有效的版本号格式，作为 tag 处理
    if parsed_version:
        print(f"🔍 正在查询 {action_name}@{tag_or_branch} ...")
        
        # 获取 tag 的 commit hash
        result = get_commit_hash(action_name, tag_or_branch)
        
        if result:
            commit_sha, actual_tag = result
            
            # actual_tag 现在已经是完整的版本号（如 v5.4.0）
            version = actual_tag
            
            # 如果指定了 --save，保存到映射表
            saved = False
            if should_save:
                saved = save_to_map(action_name, tag_or_branch, commit_sha, version)
            
            format_output(action_name, tag_or_branch, commit_sha, version, saved, is_branch=False)
            sys.exit(0)
        else:
            print(f"\n❌ 无法获取 {action_name}@{tag_or_branch} 的 commit hash")
            print("\n💡 提示:")
            print("  1. 检查 action 名称是否正确")
            print("  2. 检查 tag 版本是否存在")
            print("  3. 如果要查询分支，请使用 'master' 或 'main'")
            print(f"  4. 访问 https://github.com/{action_name}/tags 查看可用版本")
            sys.exit(1)
    else:
        # 无效的版本号格式，尝试作为分支处理
        print(f"🔍 正在查询 {action_name} 的 {tag_or_branch} 分支最新 commit ...")
        
        if should_save:
            print("⚠️  注意: 分支 commit 不会保存到映射表（因为会随时间变化）")
        
        # 获取分支的最新 commit
        result = get_branch_commit(action_name, tag_or_branch)
        
        if result:
            commit_sha, branch = result
            format_output(action_name, branch, commit_sha, branch, saved=False, is_branch=True)
            sys.exit(0)
        else:
            print(f"\n❌ 无法获取 {action_name} 的 {tag_or_branch} 分支 commit hash")
            print("\n💡 提示:")
            print("  1. 检查 action 名称是否正确")
            print("  2. 检查分支名称是否存在")
            print(f"  3. 访问 https://github.com/{action_name}/branches 查看可用分支")
            sys.exit(1)


if __name__ == '__main__':
    main()
