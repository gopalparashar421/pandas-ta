# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and project releases should follow semantic versioning with PEP 440 compatible Python package versions.

## [Unreleased]

### Added

### Changed
- Relaxed runtime dependency metadata to direct dependencies with compatible version ranges so pip and uv can resolve current pandas, numpy, numba, and tqdm releases.
- Updated the repository Python target to 3.14 while keeping published package support at Python 3.11+.

### Deprecated

### Removed

### Fixed
- Added a module-level `pandas_ta.__version__` attribute sourced from installed package metadata.

### Security

Historical release entries can be added over time as the release process is formalized.