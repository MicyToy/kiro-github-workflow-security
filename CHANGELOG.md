# Changelog

All notable changes to the GitHub Workflow Security Power will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-06

### Added
- 🎉 Initial release of GitHub Workflow Security Power
- ✨ Automatic workflow scanning and hardening
- 🔒 Permissions configuration checking and adding
- 🔗 Action version replacement (tag → commit SHA)
- 📊 Detailed processing reports
- 🗂️ Action commit SHA mapping table
- 🛠️ Two Python scripts:
  - `harden-workflows.py`: Main hardening script
  - `get-action-commit.py`: Commit hash query tool
- 📚 Comprehensive documentation:
  - POWER.md: Power overview
  - README.md: Usage guide
  - TESTING.md: Testing guide
  - CHANGELOG.md: Version history
- 🚀 Installation script for easy setup
- 💡 Kiro skill integration
- 🎯 Support for 12+ common GitHub Actions

### Features
- Scan all workflow files in `.github/workflows/`
- Check and add `permissions` configuration
- Replace action tags with commit SHAs
- Maintain action commit SHA mapping table
- Auto-fetch from GitHub API for unmapped actions
- Report unmapped actions with suggestions
- Support custom permissions configuration
- Support custom workflow directory
- Support custom mapping file
- Preserve Git history (no backup needed)

### Supported Actions
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

### Documentation
- Complete POWER.md with feature overview
- Detailed README with examples
- Testing guide with test cases
- Installation script with instructions

### Security
- Implements security best practices
- Uses commit SHA for action versions
- Follows principle of least privilege
- Prevents supply chain attacks

## [Unreleased]

### Planned
- [ ] Add more common actions to mapping table
- [ ] Support for GitHub Enterprise Server
- [ ] Batch processing for multiple repositories
- [ ] Integration with CI/CD pipelines
- [ ] Automatic version update checking
- [ ] Support for custom action registries
- [ ] Workflow validation after hardening
- [ ] Configuration file support

### Ideas
- GitHub App integration
- Slack/Discord notifications
- Scheduled automatic updates
- Action vulnerability scanning
- Compliance reporting
- Team collaboration features

## Version History

### Version Numbering
- **Major version**: Breaking changes
- **Minor version**: New features (backward compatible)
- **Patch version**: Bug fixes

### Release Process
1. Update CHANGELOG.md
2. Update version in power.json
3. Tag release in Git
4. Create GitHub release
5. Update documentation

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
