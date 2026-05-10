"""DocGuard - Document Integrity Monitoring for AI Workflows.

Protects your documents from silent corruption by LLMs and AI agents
through checksum tracking, content diffing, and auto-rollback.
"""

__version__ = "1.0.0"
__author__ = "kaising"

from doc_guard.core import DocGuard
from doc_guard.checksum import compute_checksum, verify_checksum
from doc_guard.diff import ContentDiff
from doc_guard.rollback import RollbackManager

__all__ = [
    "DocGuard",
    "compute_checksum",
    "verify_checksum",
    "ContentDiff",
    "RollbackManager",
]
