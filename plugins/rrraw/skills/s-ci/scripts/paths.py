"""Local disk paths for rr-ci sidecar files (never repo cwd root)."""

from __future__ import annotations

from pathlib import Path

from gitutil import repo_root

CI_DIR_REL = ".ai/ci"


def ci_dir() -> Path:
    """Repo-root `.ai/ci/` — mkdir if missing. All rr-ci disk writes land here."""
    path = Path(repo_root()) / CI_DIR_REL
    path.mkdir(parents=True, exist_ok=True)
    return path


def ci_file(name: str) -> Path:
    """Absolute path under `.ai/ci/` for a basename (no nested dirs)."""
    return ci_dir() / Path(name).name


def ci_rel(path: Path) -> str:
    """Repo-relative posix path for envelope `log_path` / chat announce."""
    return path.relative_to(Path(repo_root())).as_posix()
