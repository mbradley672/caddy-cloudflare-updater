# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-06-21

### Fixed
- Fixed Linux compatibility issues in watcher.py
- Resolved hardcoded Docker paths that prevented running on native Linux systems
- Fixed file watcher to use correct Python executable and script paths
- Improved logging configuration to use configurable log file path instead of hardcoded `/var/log/` path
- Added proper error handling for subprocess calls in file watcher

### Added
- Environment setup and validation script (`setup_env.py`) for easier credential configuration
- Detailed setup instructions with step-by-step Cloudflare API configuration
- Linux-compatible run script with flexible Caddyfile path detection

### Changed
- Watcher script now uses `sys.executable` for Python path resolution
- Log file path now configurable via `LOG_FILE` environment variable (defaults to `./caddy-updater.log`)
- Improved error messages and debugging information

## [1.0.2] - Previous Release

### Added
- Multi-platform Docker support (AMD64, ARM64)
- Hybrid run mode (watcher + cron combined)
- Comprehensive logging with configurable levels
- File watcher mode for real-time DNS updates

### Fixed
- DNS record synchronization reliability
- Caddyfile parsing improvements

## [1.0.1] - Previous Release

### Added
- Initial release with basic DNS synchronization
- Docker container support
- Cron mode for scheduled updates
- Cloudflare API integration
