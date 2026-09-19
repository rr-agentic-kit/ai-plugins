from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowError:
    code: str
    message: str


class GlabError(Exception):
    def __init__(self, message: str, *, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


class GhError(Exception):
    def __init__(self, message: str, *, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


class GitError(Exception):
    pass
