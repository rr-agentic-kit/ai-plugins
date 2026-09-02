from __future__ import annotations

from collections.abc import Callable

from audit_static.models import AuditContext, CheckResult
from audit_static.runners.description import run_description
from audit_static.runners.frontmatter import run_frontmatter
from audit_static.runners.keys import run_keys
from audit_static.runners.links import run_links
from audit_static.runners.naming import run_naming
from audit_static.runners.paths import run_paths
from audit_static.runners.sections import run_sections
from audit_static.runners.workflow import run_ref_file, run_workflow

Runner = Callable[[AuditContext], list[CheckResult]]

RUNNERS: tuple[Runner, ...] = (
    run_frontmatter,
    run_keys,
    run_naming,
    run_description,
    run_paths,
    run_sections,
    run_ref_file,
    run_workflow,
    run_links,
)
