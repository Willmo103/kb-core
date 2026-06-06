# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.12] - 2026-06-06
### Added
- GitHub Release asset download and check helpers (`download_github_release_asset`, `check_github_latest_release`) inside `utils.py`.
- Automated Python wheel building and publishing to GitHub Releases in the CI/CD pipeline.
- Explicit git tag pushing in the release workflow to resolve lightweight tag publication issues.

## [0.1.5] - 2026-06-01
### Changed
- Purged previous build artifacts in `build.py` by adding clean steps.
- Cleaned up formatting and indentation inside `build.py`.

## [0.1.4] - 2026-05-31
### Added
- Comprehensive test suite covering core utilities, configuration, notification client, and template rendering logic.

## [0.1.3] - 2026-05-30
### Changed
- Added docstrings to all Python modules and functions.

## [0.1.2] - 2026-05-29
### Added
- Release workflow enhancements to automatically generate a GitHub Release with new tags.

## [0.1.1] - 2026-05-29
### Added
- Standardized the repository structure with tests, docs, and build automation.
- Fixed Gotify client notification bug in `notifier.py` to check `FETCH_ENABLED` and use `_client_token` instead of `POST_ENABLED` and `_gotify_token`.
- Configured a `dev` dependency group in `pyproject.toml` containing `pytest` and `pytest-mock`.

## [0.1.0] - 2026-05-29
### Added
- Initial project structure with `README.md`, configurations parsing (`config.py`), notification helpers (`notifier.py`), rendering logic (`renderer.py`), root types (`types.py`), and common file/hashing utilities (`utils.py`).
