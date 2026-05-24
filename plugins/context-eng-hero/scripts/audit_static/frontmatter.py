from __future__ import annotations

try:
    import yaml as _yaml_impl
except ImportError:
    _yaml_impl = None  # type: ignore

yaml = _yaml_impl

_PYYAML_HINT = (
    "pyyaml not installed; from plugin root run: "
    "python3 -m pip install -r scripts/requirements.txt"
)


def _active_yaml():
    import audit_static

    return audit_static.yaml


def parse_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    yaml_lib = _active_yaml()
    if not text.startswith("---"):
        return None, text, "missing opening --- delimiter"
    end = text.find("\n---", 3)
    if end == -1:
        return None, text, "missing closing --- delimiter"
    block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    if yaml_lib is None:
        return None, body, _PYYAML_HINT
    try:
        data = yaml_lib.safe_load(block) or {}
    except yaml_lib.YAMLError as exc:
        return None, body, f"YAML parse error: {exc}"
    if not isinstance(data, dict):
        return None, body, "frontmatter must be a YAML mapping"
    return data, body, None
