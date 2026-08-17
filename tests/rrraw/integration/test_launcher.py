"""Subprocess tests for the POSIX launcher."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest
from helpers import SCRIPTS_DIR, write_planning

LAUNCHER = SCRIPTS_DIR / "validate_planning.sh"
REPO_ROOT = SCRIPTS_DIR.parents[2]
PKG_DIR = SCRIPTS_DIR / "validate_planning_script"


SH = shutil.which("sh") or "/bin/sh"


def _run_launcher(
    planning_dir: Path,
    *,
    launcher: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [SH, str(launcher or LAUNCHER), str(planning_dir)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def _copy_tree(tmp_path: Path) -> Path:
    dest = tmp_path / "scripts"
    dest.mkdir(parents=True)
    shutil.copy(LAUNCHER, dest / "validate_planning.sh")
    shutil.copytree(
        PKG_DIR,
        dest / "validate_planning_script",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    return dest / "validate_planning.sh"


def _bin_with_dirname(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    dirname = bin_dir / "dirname"
    dirname.write_text(
        "#!/bin/sh\n"
        '[ "$1" = "--" ] && shift\n'
        "case $1 in\n"
        '  */*) printf "%s\\n" "${1%/*}" ;;\n'
        '  *) printf "%s\\n" . ;;\n'
        "esac\n",
        encoding="utf-8",
    )
    basename = bin_dir / "basename"
    basename.write_text(
        "#!/bin/sh\n" '[ "$1" = "--" ] && shift\n' 'printf "%s\\n" "${1##*/}"\n',
        encoding="utf-8",
    )
    mode = dirname.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    dirname.chmod(mode)
    basename.chmod(mode)
    return bin_dir


def _fake_old_python(bin_dir: Path) -> Path:
    fake = bin_dir / "python3"
    fake.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then\n'
        "  printf '%s\\n' '3.12'\n"
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return fake


def _env_path(*dirs: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PATH"] = os.pathsep.join(str(d) for d in dirs)
    if extra:
        env.update(extra)
    return env


def test_launcher_valid_cascade(tmp_path: Path):
    write_planning(tmp_path)
    proc = _run_launcher(tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "OK" in proc.stdout


def test_launcher_without_uv_uses_python(tmp_path: Path):
    write_planning(tmp_path)
    env = os.environ.copy()
    path_dirs = [p for p in env.get("PATH", "").split(os.pathsep) if p]
    filtered = [p for p in path_dirs if not (Path(p) / "uv").exists()]
    venv_bin = REPO_ROOT / ".venv" / "bin"
    if venv_bin.is_dir():
        filtered = [str(venv_bin), *[p for p in filtered if Path(p) != venv_bin]]
    env["PATH"] = os.pathsep.join(filtered)
    proc = _run_launcher(tmp_path, env=env)
    if proc.returncode == 127:
        pytest.skip("no CPython 3.14+ with PyYAML outside uv")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "OK" in proc.stdout


def test_launcher_python_not_python3(tmp_path: Path):
    write_planning(tmp_path)
    launcher = _copy_tree(tmp_path / "plugin")
    bin_dir = _bin_with_dirname(tmp_path)
    venv_python = REPO_ROOT / ".venv" / "bin" / "python"
    if not venv_python.is_file():
        pytest.skip("no .venv python to alias as python")
    wrapper = bin_dir / "python"
    wrapper.write_text(
        f"#!/bin/sh\nexec '{venv_python}' \"$@\"\n",
        encoding="utf-8",
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    env = _env_path(bin_dir)
    proc = _run_launcher(tmp_path, launcher=launcher, env=env)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "OK" in proc.stdout


def test_launcher_too_old_python_names_version(tmp_path: Path):
    write_planning(tmp_path)
    launcher = _copy_tree(tmp_path / "plugin")
    bin_dir = _bin_with_dirname(tmp_path)
    fake = _fake_old_python(bin_dir)
    env = _env_path(bin_dir)
    proc = _run_launcher(tmp_path, launcher=launcher, env=env)
    assert proc.returncode == 127
    err = proc.stderr
    assert "3.12" in err
    assert "no Python interpreter found" not in err
    assert str(fake) in err or "python3" in err


def test_launcher_empty_path_no_uv(tmp_path: Path):
    write_planning(tmp_path)
    launcher = _copy_tree(tmp_path / "plugin")
    bin_dir = _bin_with_dirname(tmp_path)
    env = _env_path(bin_dir)
    proc = _run_launcher(tmp_path, launcher=launcher, env=env)
    assert proc.returncode == 127
    assert "no Python interpreter found" in proc.stderr


def test_launcher_no_yaml_prints_pip_hint(tmp_path: Path):
    write_planning(tmp_path)
    launcher = _copy_tree(tmp_path / "plugin")
    bin_dir = _bin_with_dirname(tmp_path)
    fake = bin_dir / "python3"
    fake.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "-c" ]; then\n'
        "  case $2 in\n"
        "    *version_info*)\n"
        "      printf '%s\\n' '3.14'\n"
        "      exit 0\n"
        "      ;;\n"
        "  esac\n"
        "  exit 1\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    env = _env_path(bin_dir)
    proc = _run_launcher(tmp_path, launcher=launcher, env=env)
    assert proc.returncode == 127
    assert "no Python interpreter found" not in proc.stderr
    assert "3.12" not in proc.stderr
    assert "validate_planning_script/requirements.txt" in proc.stderr
