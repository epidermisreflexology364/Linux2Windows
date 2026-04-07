# Changelog

All notable changes to this project will be documented here.

## [1.0.0] - 2026-04-06

### Added
- Initial release
- Translation table covering 50+ common Linux commands
- Special-case handlers for `cp`, `rm`, `touch`, `head`, `tail`, `kill`, `killall`, `wc`, `sleep`
- `--dry-run` mode to preview translated commands without executing
- `--show-cmd` flag to print the translated command before running it
- `--list` to display all supported commands
- `--info` to show translation details and flag mappings for a specific command
- `--config` to load custom command mappings from a JSON file
- Auto-detection of `~/.l2w/commands.json` for user-level overrides
- PyInstaller build script (`build.bat`) for standalone `.exe`
- 38 unit tests
