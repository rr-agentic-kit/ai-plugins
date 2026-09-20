"""Merge origin/dependabot/** into HEAD: verify, delete remotes (mechanical loop)."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import emit
from errors import GitError
from gitutil import has_uncommitted_changes, repo_root, run_git
from paths import ci_dir, ci_rel

COMMAND = "pull-dependabot"
_LOCKFILES = frozenset(
    {
        "pnpm-lock.yaml",
        "package-lock.json",
        "yarn.lock",
        "Cargo.lock",
        "poetry.lock",
        "Gemfile.lock",
        "composer.lock",
        "go.sum",
        "bun.lock",
        "bun.lockb",
    }
)
_SAFE_VERIFY_RE = re.compile(r"^[A-Za-z0-9_./@+=:,\- ]+$")


def add_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser(
        COMMAND,
        help="Merge origin/dependabot/** with verify + remote delete",
        description=(
            "Result keys: branches[], summary{merged,already,deleted,escalated,skipped}, "
            "status (ok|empty|escalate|fatal), log_dir. Exit 2 = escalate."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching remotes only; no merge/verify/delete",
    )
    parser.add_argument(
        "--verify-cmd",
        help="Shell command run after each successful merge (required unless --dry-run)",
    )
    parser.add_argument(
        "--continue-on-fail",
        action="store_true",
        help="After escalate on one branch, continue remaining (default: stop)",
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Skip git push --delete after verify pass",
    )
    parser.set_defaults(handler=_handler)


def _handler(args: argparse.Namespace) -> int:
    return main(
        dry_run=bool(args.dry_run),
        verify_cmd=args.verify_cmd,
        continue_on_fail=bool(args.continue_on_fail),
        no_delete=bool(args.no_delete),
    )


def _log_dir() -> Path:
    path = ci_dir() / "pull-dependabot"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _list_dependabot_branches() -> list[str]:
    run_git(["fetch", "origin", "--prune"], check=False)
    result = run_git(
        [
            "for-each-ref",
            "--format=%(refname:short)",
            "refs/remotes/origin/dependabot/**",
        ],
        check=False,
    )
    branches: list[str] = []
    for line in result.stdout.splitlines():
        ref = line.strip()
        if not ref.startswith("origin/dependabot/"):
            continue
        short = ref.removeprefix("origin/")
        if short and short not in branches:
            branches.append(short)
    branches.sort()
    return branches


def _conflict_paths() -> list[str]:
    out = run_git(["diff", "--name-only", "--diff-filter=U"], check=False).stdout
    return [p for p in out.splitlines() if p.strip()]


def _is_ancestor(remote_ref: str) -> bool:
    return (
        run_git(
            ["merge-base", "--is-ancestor", remote_ref, "HEAD"], check=False
        ).returncode
        == 0
    )


def _try_regen_locks(conflicts: list[str], log: Path) -> bool:
    """Return True if merge completed after lockfile-only regen."""
    if not conflicts or any(c not in _LOCKFILES for c in conflicts):
        return False
    root = Path(repo_root())
    for path in conflicts:
        run_git(["checkout", "--ours", "--", path], check=False)
        run_git(["add", "--", path], check=False)

    regen_log = log.open("a", encoding="utf-8")
    try:
        if "pnpm-lock.yaml" in conflicts or (root / "pnpm-lock.yaml").exists():
            if shutil.which("pnpm") and (root / "package.json").is_file():
                regen_log.write("\n# pnpm install\n")
                regen_log.flush()
                proc = subprocess.run(
                    ["pnpm", "install"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                regen_log.write(proc.stdout)
                regen_log.write(proc.stderr)
                if proc.returncode != 0:
                    return False
                run_git(["add", "--", "pnpm-lock.yaml"], check=False)
        if "Cargo.lock" in conflicts or (
            (root / "Cargo.toml").is_file() and "Cargo.lock" in conflicts
        ):
            if shutil.which("cargo"):
                regen_log.write("\n# cargo generate-lockfile\n")
                regen_log.flush()
                proc = subprocess.run(
                    ["cargo", "generate-lockfile"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                regen_log.write(proc.stdout)
                regen_log.write(proc.stderr)
                if proc.returncode != 0:
                    return False
                run_git(["add", "--", "Cargo.lock"], check=False)
        if "package-lock.json" in conflicts:
            if shutil.which("npm") and (root / "package.json").is_file():
                proc = subprocess.run(
                    ["npm", "install", "--package-lock-only"],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                regen_log.write(proc.stdout + proc.stderr)
                if proc.returncode != 0:
                    return False
                run_git(["add", "--", "package-lock.json"], check=False)
    finally:
        regen_log.close()

    if _conflict_paths():
        return False
    # Complete merge commit if still in merge state
    if (root / ".git" / "MERGE_HEAD").exists() or (
        root / ".git" / "MERGE_MSG"
    ).exists():
        commit = run_git(["commit", "--no-edit"], check=False)
        if commit.returncode != 0:
            return False
    return True


def _abort_merge() -> None:
    run_git(["merge", "--abort"], check=False)


def _run_verify(verify_cmd: str, log: Path) -> int:
    with log.open("w", encoding="utf-8") as fh:
        fh.write(f"# verify: {verify_cmd}\n")
        fh.flush()
        proc = subprocess.run(
            verify_cmd,
            shell=True,
            cwd=repo_root(),
            stdout=fh,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return proc.returncode


def _delete_remote(branch: str) -> bool:
    result = run_git(["push", "origin", "--delete", branch], check=False)
    return result.returncode == 0


def _safe_slug(branch: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", branch)[:120]


def main(
    *,
    dry_run: bool,
    verify_cmd: str | None,
    continue_on_fail: bool,
    no_delete: bool,
) -> int:
    def action() -> int:
        root = Path(repo_root())
        if not dry_run and has_uncommitted_changes():
            return emit.fail(
                COMMAND,
                "dirty_tree",
                "working tree is dirty; commit or stash first",
            )
        if not dry_run:
            if not verify_cmd or not verify_cmd.strip():
                return emit.fail(
                    COMMAND,
                    "missing_verify_cmd",
                    "pass --verify-cmd (e.g. 'just test') unless --dry-run",
                )
            if not _SAFE_VERIFY_RE.fullmatch(verify_cmd.strip()):
                return emit.fail(
                    COMMAND,
                    "invalid_verify_cmd",
                    "verify-cmd has disallowed characters",
                )

        branches = _list_dependabot_branches()
        log_dir = _log_dir()
        if dry_run or not branches:
            status = "empty" if not branches else "ok"
            return emit.succeed(
                COMMAND,
                {
                    "status": status,
                    "dry_run": dry_run,
                    "branches": [
                        {"branch": b, "merge": "listed"} for b in branches
                    ],
                    "summary": {
                        "merged": 0,
                        "already": 0,
                        "deleted": 0,
                        "escalated": 0,
                        "skipped": 0,
                        "listed": len(branches),
                    },
                    "log_dir": ci_rel(log_dir),
                },
            )

        assert verify_cmd is not None
        results: list[dict[str, Any]] = []
        merged = already = deleted = escalated = skipped = 0
        escalate_hit = False

        for branch in branches:
            if escalate_hit and not continue_on_fail:
                results.append(
                    {
                        "branch": branch,
                        "merge": "skipped",
                        "reason": "stopped_after_escalate",
                    }
                )
                skipped += 1
                continue

            remote_ref = f"origin/{branch}"
            if (
                run_git(["rev-parse", "--verify", "-q", remote_ref], check=False).returncode
                != 0
            ):
                results.append(
                    {
                        "branch": branch,
                        "merge": "fatal",
                        "reason": "missing_remote_ref",
                    }
                )
                escalated += 1
                escalate_hit = True
                continue

            if _is_ancestor(remote_ref):
                entry: dict[str, Any] = {
                    "branch": branch,
                    "merge": "already",
                    "commits": {"merge": run_git(["rev-parse", "HEAD"]).stdout.strip()},
                }
                if not no_delete and _delete_remote(branch):
                    entry["deleted"] = True
                    deleted += 1
                else:
                    entry["deleted"] = False
                results.append(entry)
                already += 1
                continue

            merge = run_git(
                ["merge", "--no-ff", "--no-edit", remote_ref], check=False
            )
            merge_log = log_dir / f"{_safe_slug(branch)}.merge.log"
            merge_log.write_text(
                (merge.stdout or "") + (merge.stderr or ""), encoding="utf-8"
            )

            if merge.returncode != 0:
                conflicts = _conflict_paths()
                if conflicts and _try_regen_locks(conflicts, merge_log):
                    # regenerated — fall through to verify
                    pass
                elif conflicts:
                    results.append(
                        {
                            "branch": branch,
                            "merge": "conflicts",
                            "conflict_paths": conflicts,
                            "log": ci_rel(merge_log),
                            "escalate": "non_lockfile_or_regen_failed",
                        }
                    )
                    escalated += 1
                    escalate_hit = True
                    # leave conflict state for agent if continue? safer abort
                    if continue_on_fail:
                        _abort_merge()
                    # if not continue, leave tree in conflict for agent
                    continue
                else:
                    _abort_merge()
                    results.append(
                        {
                            "branch": branch,
                            "merge": "fatal",
                            "reason": (merge.stderr or merge.stdout or "merge failed")[
                                :200
                            ],
                            "log": ci_rel(merge_log),
                        }
                    )
                    escalated += 1
                    escalate_hit = True
                    continue

            # Re-check clean merge state
            if _conflict_paths():
                results.append(
                    {
                        "branch": branch,
                        "merge": "conflicts",
                        "conflict_paths": _conflict_paths(),
                        "escalate": "unresolved_after_regen",
                    }
                )
                escalated += 1
                escalate_hit = True
                continue

            sha = run_git(["rev-parse", "HEAD"]).stdout.strip()
            verify_log = log_dir / f"{_safe_slug(branch)}.verify.log"
            print(f"rr-ci: verifying {branch}…", file=sys.stderr)
            vrc = _run_verify(verify_cmd.strip(), verify_log)
            if vrc != 0:
                results.append(
                    {
                        "branch": branch,
                        "merge": "ok",
                        "commits": {"merge": sha},
                        "verify": "fail",
                        "log": ci_rel(verify_log),
                        "escalate": "verify_failed",
                        "deleted": False,
                    }
                )
                escalated += 1
                escalate_hit = True
                merged += 1  # merge landed; remote kept
                continue

            entry = {
                "branch": branch,
                "merge": "ok",
                "commits": {"merge": sha},
                "verify": "pass",
                "deleted": False,
            }
            if not no_delete:
                entry["deleted"] = _delete_remote(branch)
                if entry["deleted"]:
                    deleted += 1
            results.append(entry)
            merged += 1

        status = "escalate" if escalate_hit else "ok"
        result = {
            "status": status,
            "dry_run": False,
            "branches": results,
            "summary": {
                "merged": merged,
                "already": already,
                "deleted": deleted,
                "escalated": escalated,
                "skipped": skipped,
                "listed": len(branches),
            },
            "log_dir": ci_rel(log_dir),
            "cwd": str(root),
        }
        # omit cwd from envelope to avoid absolute path in skill docs... keep for agent?
        # pre-ship says no absolute paths in authored content; envelope runtime OK
        del result["cwd"]
        exit_code = 2 if escalate_hit else 0
        return emit.succeed(COMMAND, result, exit_code=exit_code)

    return emit.run_guarded(COMMAND, action)
