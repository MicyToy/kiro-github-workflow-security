# GitHub Workflow Security Power

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A tool for automatically scanning and hardening the security of GitHub Actions workflow files.

## ✨ Features

- 🔒 **Security Hardening**: Automatically add minimal permission configurations
- 🔗 **Version Pinning**: Replace action tags with immutable commit SHAs
- 🛡️ **Supply Chain Security**: Prevent dependencies from being maliciously modified
- 📊 **Detailed Reports**: Display processing statistics and unmapped actions
- 🚀 **Easy to Use**: Support both Kiro skill and command-line usage

## 📦 Installation

### Method 1: Using Installation Script

```bash
cd your-project
bash ~/.kiro/powers/github-workflow-security/install.sh
```

### Method 2: Manual Installation

```bash
# Create directories
mkdir -p .kiro/{skills,scripts,data}

# Copy files
cp ~/.kiro/powers/github-workflow-security/skills/* .kiro/skills/
cp ~/.kiro/powers/github-workflow-security/scripts/* .kiro/scripts/
cp ~/.kiro/powers/github-workflow-security/data/* .kiro/data/
cp ~/.kiro/powers/github-workflow-security/README.md .kiro/

# Set permissions
chmod +x .kiro/scripts/*.py
```

## 🚀 Quick Start

### Using with Kiro

```
use the github-workflow-security skill to secure all workflows.
```

### Command-line Usage

```bash
# Harden all workflow files
python3 .kiro/scripts/harden-workflows.py

# Query action commit hash
python3 .kiro/scripts/get-action-commit.py actions/checkout v4

# Query latest commit from branch
python3 .kiro/scripts/get-action-commit.py actions/checkout main

# Add to mapping table
python3 .kiro/scripts/get-action-commit.py actions/checkout v4 --save
```

## 📖 Usage Examples

### Example 1: Basic Hardening

```bash
$ python3 .kiro/scripts/harden-workflows.py

🔍 Scanned 3 workflow files

📄 Processing file: .github/workflows/ci.yml
  ℹ️  Permissions already configured, skipping
  ✓ Replaced actions/checkout@v4 → 34e114876b0b... # v4.3.1
  ✓ Replaced docker/setup-buildx-action@v3 → 8d2750c68a42... # v3.12.0
  ✅ File updated

============================================================
📊 Processing Summary
============================================================
  Files scanned: 3
  Added permissions: 1
  Replaced action versions: 12

✅ All workflow files have been processed
```

### Example 2: Custom Permissions

```bash
python3 .kiro/scripts/harden-workflows.py --permissions "permissions:\n  contents: read\n  pull-requests: write\n"
```

### Example 3: Query Action Commit Hash

```bash
$ python3 .kiro/scripts/get-action-commit.py actions/checkout v4

🔍 Querying actions/checkout@v4 ...

✓ Successfully retrieved commit hash:
  Action: actions/checkout
  Tag: v4
  Version: v4.3.1
  Commit SHA: 34e114876b0b11c390a56381ad16ebd13914f8d5

📋 Usage format:
  - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

## 🔧 How It Works

### 1. Permissions Check

Check if the workflow contains a `permissions` configuration, and add it if not present:

```yaml
permissions:
  contents: read
```

### 2. Action Version Replacement

Replace action versions from tags to commit SHAs:

```yaml
# Before
- uses: actions/checkout@v4

# After
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

### 3. Mapping Table Management

Maintain a mapping table of commonly used actions (`.kiro/data/action-commit-map.json`) to improve processing speed.

### 4. Automatic Retrieval

For unmapped actions, automatically retrieve commit SHA from GitHub API.

## 📁 File Structure

```
.kiro/
├── skills/
│   └── github-workflow-security.md          # Skill definition
├── scripts/
│   ├── harden-workflows.py                  # Main hardening script
│   └── get-action-commit.py                 # Get commit hash tool
├── data/
│   └── action-commit-map.json               # Action mapping table
└── README.md                                # Usage documentation
```

## 🎯 Supported Actions

The current mapping table includes the following commonly used actions:

| Action | Version | Commit SHA |
|--------|---------|------------|
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

## ⚙️ Configuration Options

### harden-workflows.py

```bash
python3 .kiro/scripts/harden-workflows.py [OPTIONS]

Options:
  --dir DIR                    Workflow directory (default: .github/workflows)
  --permissions PERMISSIONS    Custom permissions configuration
  --map-file MAP_FILE         Mapping table file path
  -h, --help                  Show help information
```

### get-action-commit.py

```bash
python3 .kiro/scripts/get-action-commit.py <action-name> <tag|branch> [--save]

Arguments:
  action-name                 Action name (e.g., actions/checkout)
  tag                        Version tag (e.g., v4, v4.3.1)
  branch                     Branch name (e.g., master, main, develop)
  --save, -s                 Save to mapping table (only for tags)

Notes:
  - Script automatically detects whether input is a version tag or branch name
  - Version tag format: starts with 'v' followed by numbers (e.g., v4, v4.3.1)
  - Other formats are treated as branch names
  - Branch commit hashes won't be saved to mapping table (as they change over time)

Examples:
  # Using version tags
  python3 .kiro/scripts/get-action-commit.py actions/checkout v4
  python3 .kiro/scripts/get-action-commit.py actions/checkout v4 --save
  
  # Using branches (auto-detected)
  python3 .kiro/scripts/get-action-commit.py actions/checkout main
  python3 .kiro/scripts/get-action-commit.py actions/setup-node master
  python3 .kiro/scripts/get-action-commit.py some/action develop
```

## 🔐 Security Best Practices

1. **Principle of Least Privilege**: Only grant necessary permissions
2. **Pin Versions**: Use commit SHAs instead of mutable tags
3. **Regular Updates**: Periodically check and update action versions
4. **Audit Logs**: Track changes through Git history
5. **Mapping Maintenance**: Keep the mapping table up to date

## ⚠️ Caveats

1. **GitHub API Limits**: Unauthenticated requests are limited to 60/hour
2. **Git Management**: All changes are managed by Git
3. **Permission Verification**: Verify that workflows run correctly after modifications
4. **Compatibility**: Supports both `.yml` and `.yaml` formats

## 🤝 Contributing

Feel free to add more actions to the mapping table:

```bash
python3 .kiro/scripts/get-action-commit.py <action-name> <tag> --save
```

## 📄 License

MIT License

## 🔗 Related Resources

- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Using Commit SHA to Pin Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
- [Workflow Permissions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#permissions)

## 📞 Support

If you have any questions or suggestions, please submit an Issue or Pull Request.
