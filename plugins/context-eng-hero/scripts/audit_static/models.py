from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Reject reads above this size before loading into memory (local DoS guard).
MAX_READ_BYTES = 2 * 1024 * 1024  # 2 MiB

type CheckResult = dict[str, str]


@dataclass(slots=True)
class AuditContext:
    plugin_root: Path
    rel_path: str
    rel: Path
    target: Path
    text: str
    artifact_type: str
    body: str
    fm: dict | None
    fm_err: str | None
    has_fm: bool

    @classmethod
    def load(cls, plugin_root: Path, rel_path: str) -> AuditContext | list[CheckResult]:
        from audit_static.detect import detect_type
        from audit_static.report import check

        plugin_root = plugin_root.resolve()
        target = (plugin_root / rel_path).resolve()
        try:
            target.relative_to(plugin_root)
        except ValueError as exc:
            return [
                check(
                    "static.paths.within-plugin",
                    "critical",
                    False,
                    str(exc),
                )
            ]
        if not target.is_file():
            return [
                check(
                    "static.file.exists",
                    "critical",
                    False,
                    f"file not found: {rel_path}",
                )
            ]

        file_size = target.stat().st_size
        if file_size > MAX_READ_BYTES:
            return [
                check(
                    "static.file.size",
                    "critical",
                    False,
                    (
                        f"file exceeds size cap ({file_size} bytes > "
                        f"{MAX_READ_BYTES} bytes): {rel_path}"
                    ),
                )
            ]

        text = target.read_text(encoding="utf-8")
        rel = Path(rel_path)
        artifact_type = detect_type(rel)
        from audit_static.frontmatter import parse_frontmatter

        fm, body, fm_err = parse_frontmatter(text)
        return cls(
            plugin_root=plugin_root,
            rel_path=rel_path,
            rel=rel,
            target=target,
            text=text,
            artifact_type=artifact_type,
            body=body,
            fm=fm,
            fm_err=fm_err,
            has_fm=text.startswith("---"),
        )
