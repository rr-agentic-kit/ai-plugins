"""Unit tests for s-coder node_types_probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = (
    Path(__file__).resolve().parents[3]
    / "plugins"
    / "rrraw"
    / "skills"
    / "s-coder"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

import node_types_probe as ntp  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_ready_when_dep_types_and_include(tmp_path: Path) -> None:
    _write(
        tmp_path / "package.json",
        json.dumps({"devDependencies": {"@types/node": "22.0.0"}}),
    )
    _write(
        tmp_path / "tsconfig.json",
        '{\n  "compilerOptions": { "types": ["node"] },\n  "include": ["src/**/*.ts"]\n}\n',
    )
    src = tmp_path / "src" / "main.ts"
    _write(src, "console.log(process.pid);\n")
    result = ntp.probe(tmp_path, src)
    assert result["verdict"] == "ready"
    assert result["has_types_node_dep"] is True
    assert result["types_includes_node"] is True
    assert result["file_in_include"] is True


def test_missing_dep(tmp_path: Path) -> None:
    _write(tmp_path / "package.json", json.dumps({"devDependencies": {}}))
    _write(
        tmp_path / "tsconfig.json",
        '{ "compilerOptions": { "types": ["node"] }, "include": ["src/**/*.ts"] }',
    )
    result = ntp.probe(tmp_path)
    assert result["verdict"] == "missing_dep"


def test_missing_types(tmp_path: Path) -> None:
    _write(
        tmp_path / "package.json",
        json.dumps({"devDependencies": {"@types/node": "22.0.0"}}),
    )
    _write(tmp_path / "tsconfig.json", '{ "compilerOptions": { "strict": true } }')
    result = ntp.probe(tmp_path)
    assert result["verdict"] == "missing_types"


def test_file_outside_include(tmp_path: Path) -> None:
    _write(
        tmp_path / "package.json",
        json.dumps({"devDependencies": {"@types/node": "22.0.0"}}),
    )
    _write(
        tmp_path / "tsconfig.json",
        '{ "compilerOptions": { "types": ["node"] }, "include": ["src/**/*.ts"] }',
    )
    outside = tmp_path / "drizzle.config.ts"
    _write(outside, "export default {};\n")
    result = ntp.probe(tmp_path, outside)
    assert result["verdict"] == "file_outside_include"


def test_cli_envelope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write(
        tmp_path / "package.json",
        json.dumps({"devDependencies": {"@types/node": "22.0.0"}}),
    )
    _write(
        tmp_path / "tsconfig.json",
        '{ "compilerOptions": { "types": ["node"] } }',
    )
    code = ntp.main(["--cwd", str(tmp_path)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["command"] == "node-types-probe"
    assert payload["result"]["verdict"] == "ready"
