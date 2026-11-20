# Development and deployment scripts

The scripts in this directory support local development, CI validation,
packaging, installation, and release verification.

## Development and CI

- `check_import_boundaries.py` and `check_client_import_boundaries.mjs`
  validate dependency boundaries.
- `ci_gate.py` and `ci_scope.py` select and enforce CI checks.
- `pytest_timing.py` reports test timing information.
- `docker_compose_smoke.py` checks the Compose deployment path.
- `install_channel_dependencies.py` installs dependencies for all channels.

## Packaging and releases

- `build_tui_wheels.py` builds terminal UI wheels.
- `native_acceptance_input.py` and `release_candidate.py` prepare release
  validation.
- `verify_installed_release.py`, `verify_packaged_update.py`, and
  `verify_release_approval.py` verify release artifacts and approvals.
- `release_install_guide.py` generates installation guidance.

## Installation and data utilities

- `install.ps1` and `install.sh` provide platform-specific installers.
- `scrape_public_sources.py`, `eservices_agent.py`, and
  `prepare_public_form.py` support public-service data workflows.
- `benchmark_session_storage.py` measures session-storage behavior.

Run each script's documented help or use the repository's documented entry
points before invoking it in CI or a deployment environment.
