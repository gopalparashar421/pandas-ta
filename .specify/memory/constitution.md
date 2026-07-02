<!--
Sync Impact Report
- Version change: (template) → 1.0.0
- Modified principles: N/A (initial ratification from template placeholders)
- Added sections:
  - Core Principles (6 principles)
  - Technical Constraints
  - Development Workflow & Quality Gates
  - Governance
- Removed sections: None
- Templates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
  - .specify/templates/checklist-template.md ✅ (no changes required)
  - .specify/templates/commands/*.md ⚠ not present in repository
- Deferred TODOs: None
-->

# Pandas TA Constitution

## Core Principles

### I. Pandas-First API

Every indicator and utility MUST operate on `pandas.Series` or `pandas.DataFrame`
inputs and return `Series` or `DataFrame` outputs. The library MUST expose three
consumption styles with increasing abstraction:

1. **Standard** — explicit column arguments (`ta.sma(df["close"], length=10)`).
2. **DataFrame Extension** — `df.ta` accessors with automatic `ohlcva` resolution.
3. **Strategy** — grouped, named indicator batches via `ta.Strategy` and
   `df.ta.strategy()`.

New indicators MUST support Standard and DataFrame Extension entry points unless
a documented exception applies. Strategy integration MUST be supported when the
indicator is eligible for bulk execution.

**Rationale**: Consistent, progressive API surfaces let beginners start simple
and advanced users scale to multiprocessed strategy runs without API rewrites.

### II. Indicator Correctness & Reference Parity

Indicators MUST implement mathematically correct technical analysis logic aligned
with established references (TA-Lib, TradingView, published literature) where
applicable. When TA-Lib is installed, shared indicators SHOULD delegate to TA-Lib
by default and MUST honor `talib=False` to use the native implementation.

Deviations from reference implementations MUST be documented in docstrings,
`help()`, README indicator notes, and `CHANGELOG.md` when behavior changes.

**Rationale**: Users rely on Pandas TA for trading and research decisions;
silent numerical drift erodes trust faster than missing features.

### III. Explicit Outputs & Naming Conventions

All indicator outputs MUST use Uppercase Underscore naming
(e.g., `SMA_10`, `DCL_10_15`, `ZS_length`). Multi-output indicators MUST return
column names that encode parameters and distinguish composed outputs via `prefix`
and/or `suffix` when chained inside Strategies.

Public keyword argument order SHOULD remain consistent across indicators;
reordering MUST be treated as a breaking change and documented.

**Rationale**: Predictable column names enable strategy composition, downstream
backtesting, and reproducible notebooks.

### IV. Backward-Compatible Evolution

The project MUST follow semantic versioning (PEP 440) as defined in
`CONTRIBUTING.md`:

- **Patch** — backward-compatible bug fixes and packaging fixes.
- **Minor** — backward-compatible features or new indicators.
- **Major** — breaking API or behavior changes.

Behavior changes MUST include a `CHANGELOG.md` entry under `[Unreleased]` (or the
release section when shipping). Deprecated indicators MUST document replacements
before removal (e.g., `trend_return` → `tsignals`).

**Rationale**: Downstream consumers install from Git; clear versioning and
changelog discipline reduce upgrade risk.

### V. Reproducible Validation

Contributions that change behavior MUST include a minimal reproducible verification
snippet or usage example in the pull request. Before merge, changes MUST pass the
local validation gate:

```sh
uv run python -c "import pandas_ta"
uv build
uv run python -m compileall -q pandas_ta
```

Indicator bug reports MUST include installed version or Git revision, Python
version, and a minimal reproducible example.

**Rationale**: Indicator libraries are data-sensitive; reproducibility is the
primary defense against regressions without a mandatory full test matrix.

### VI. Safe-by-Default Analytics

Indicators with known lookahead or centering behavior (`dpo`, `ichimoku`, and
similar) MUST expose an explicit opt-out (e.g., `lookahead=False`) and document
the data-leak risk in docstrings and README.

Experimental or BETA features (performance metrics, optional integrations) MUST be
labeled as such and MUST NOT be presented as production-grade guarantees.

**Rationale**: Financial time-series work is vulnerable to subtle leakage;
defaults and documentation must protect research integrity.

## Technical Constraints

- **Language**: Python 3.11–3.14 (`requires-python >= 3.11` in `pyproject.toml`).
- **Core runtime dependencies**: `pandas`, `numpy`, `numba`, `tqdm` — keep direct
  dependencies minimal; let resolvers pick compatible releases.
- **Optional integrations**: TA-Lib (candle patterns and native delegation),
  `yfinance` (data download), `vectorbt` (backtesting examples) — MUST remain
  optional and degrade gracefully when absent.
- **Package layout**: Indicator code lives under `pandas_ta/`; preserve existing
  category structure (Candles, Cycles, Momentum, Overlap, Performance,
  Statistics, Trend, Utility, Volatility, Volume).
- **Performance**: `df.ta.strategy()` SHOULD use multiprocessing by default;
  sequential execution is required only when `col_names` ordering matters.
- **Installation**: Package is consumed from Git (`uv add` / `pip install`); metadata
  MUST remain setuptools-compatible and PEP 621 compliant.

## Development Workflow & Quality Gates

1. **Scope** — One concern per pull request; no drive-by refactors or unrelated
   formatting.
2. **Documentation** — Update README, docstrings, and examples when public API,
   installation, or indicator behavior changes.
3. **Changelog** — User-facing behavior changes require `CHANGELOG.md` entries;
   docs-only changes may omit entries unless they materially affect contributors.
4. **Version bumps** — Contributors MUST NOT bump `pyproject.toml` version unless
   preparing an explicit release (maintainer-coordinated).
5. **Examples** — Jupyter notebooks under `examples/` are the canonical
   integration demonstrations (Strategies, vectorbt, custom indicators).
6. **Custom indicators** — External indicators via `import_dir` (`pandas_ta/custom.py`)
   MUST remain independent of builtins and documented separately.

### Constitution Check (for feature plans)

Before Phase 0 research and again after Phase 1 design, verify:

| Gate | Question |
|------|----------|
| API surface | Does the feature support Standard + `df.ta` extension? |
| Naming | Do outputs follow Uppercase Underscore conventions? |
| Parity | Are reference sources cited; is `talib` behavior defined? |
| Safety | Are lookahead/leak risks documented with opt-out defaults? |
| Compatibility | Is the change SemVer-aligned with changelog entry planned? |
| Validation | Is there a reproducible snippet for PR verification? |

## Governance

This constitution supersedes ad-hoc contribution habits for speckit-driven feature
work. Amendments require:

1. A pull request updating `.specify/memory/constitution.md`.
2. A version bump per semantic versioning rules below.
3. Propagation to dependent templates (`plan-template.md`, `spec-template.md`,
   `tasks-template.md`) when principles change materially.
4. A `Sync Impact Report` HTML comment at the top of the constitution file.

**Versioning policy for this document**:

- **MAJOR** — principle removal or incompatible governance redefinition.
- **MINOR** — new principle or materially expanded guidance.
- **PATCH** — clarifications, typos, non-semantic refinements.

**Compliance**: All speckit plans, specs, and tasks MUST pass the Constitution
Check gates. Violations require documented justification in the plan's Complexity
Tracking table. Runtime development guidance also lives in `CONTRIBUTING.md` and
`README.md`.

**Version**: 1.0.0 | **Ratified**: 2026-07-02 | **Last Amended**: 2026-07-02
