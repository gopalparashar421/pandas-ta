# Contributing

Thanks for contributing to pandas_ta.

This project is packaged from Git, built with setuptools, and installed with uv-friendly metadata. Keep contributions focused, reproducible, and easy to review.

## Getting Started

1. Fork the repository and create a feature branch from `main`.
2. Use Python 3.14 for local development. The published package metadata supports Python 3.11 and newer.
3. Create a local environment and install the project dependencies.

```sh
uv sync
```

If you prefer a fresh editable install instead of `uv sync`, use:

```sh
uv venv
uv pip install -e .
```

## Development Expectations

1. Keep pull requests scoped to one concern.
2. Preserve the existing package layout under `pandas_ta/`.
3. Avoid unrelated formatting or refactors in the same change.
4. Update documentation when behavior, installation, or public APIs change.

## Validation Before Opening a PR

Run these checks locally before opening or updating a pull request:

```sh
uv run python -c "import pandas_ta"
uv build
uv run python -m compileall -q pandas_ta
```

If your change affects an indicator, include a short usage example or a reproducible verification snippet in the pull request description.

## Changelog Rules

This repository uses `CHANGELOG.md` and follows the Keep a Changelog structure.

For pull requests that change behavior, add an entry under `## [Unreleased]` in the most appropriate section:

- `Added` for new indicators or new capabilities
- `Changed` for behavior changes that remain backward compatible
- `Deprecated` for features scheduled for removal
- `Removed` for deleted functionality
- `Fixed` for bug fixes
- `Security` for security-related fixes

Write changelog entries as short, user-facing bullet points. Describe the observable change, not the implementation detail.

Examples:

- `Added the <indicator> helper for ...`
- `Fixed import metadata so pandas_ta installs cleanly from Git`
- `Changed <indicator> default behavior to ...`

Docs-only, comment-only, and internal maintenance changes usually do not need a changelog entry unless they materially affect contributors or releases.

## Versioning Rules

The package version lives in `pyproject.toml` under `[project].version`.

This project follows semantic versioning guidance for contributor-facing changes:

- Patch: backward-compatible bug fixes and packaging fixes
- Minor: backward-compatible features or new indicators
- Major: breaking API or behavior changes

For Python packaging, version strings must remain PEP 440 compatible.

In normal feature or bug-fix pull requests, contributors should update `CHANGELOG.md` but should not bump the package version unless the pull request is explicitly intended to be a release or a maintainer asks for the version update.

If you are preparing a release change, keep these files aligned:

1. `pyproject.toml`
2. `CHANGELOG.md`
3. Any versioned documentation or release notes touched by the change

## Pull Request Notes

Include the following in your pull request:

1. A short summary of the problem and the fix
2. Any changelog entry you added
3. Validation steps you ran locally
4. Screenshots or sample output when relevant

## Reporting Issues

When filing a bug, include:

1. A minimal reproducible example
2. The installed version or Git revision
3. Your Python version
4. Any traceback or error output

Keeping reports reproducible makes indicator and packaging issues much easier to fix.