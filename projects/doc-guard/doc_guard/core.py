"""Core DocGuard class - the main API for document integrity protection."""

import time
from pathlib import Path
from typing import Optional, Union

from doc_guard.checksum import compute_checksum, compute_file_checksum, ChecksumStore
from doc_guard.diff import ContentDiff
from doc_guard.rollback import RollbackManager


class DocGuard:
    """Main interface for document integrity monitoring.

    Protects documents from silent corruption by LLMs and AI agents
    through a combination of checksum verification, content diffing,
    and automatic rollback.

    Usage:
        # Basic usage
        guard = DocGuard("my_document")
        guard.protect("original content here")

        # After AI edits the document
        result = guard.verify("potentially modified content")
        if not result["safe"]:
            print(f"Detected corruption! {result['diff'].change_summary}")
            recovered = guard.rollback()
            print(f"Recovered: {recovered}")

        # File-based usage
        guard = DocGuard("report.md", mode="file")
        guard.protect_file("/path/to/report.md")
    """

    def __init__(self, doc_id: str, mode: str = "content",
                 store_path: Union[str, Path] = None,
                 history_path: Union[str, Path] = None,
                 auto_snapshot: bool = True):
        """Initialize DocGuard for a document.

        Args:
            doc_id: Unique identifier for the document.
            mode: "content" for text content, "file" for file paths.
            store_path: Path for checksum store (default: .docguard_store.json).
            history_path: Path for rollback history.
            auto_snapshot: Whether to automatically snapshot on protect().
        """
        self.doc_id = doc_id
        self.mode = mode
        self.auto_snapshot = auto_snapshot

        self._store = ChecksumStore(store_path or ".docguard_store.json")
        self._rollback = RollbackManager(
            doc_id,
            history_path or f".docguard_{doc_id}_history.json",
        )

        self._original_checksum = None
        self._last_verified = None

    def protect(self, content: str, label: str = "initial") -> dict:
        """Register a document's initial state as the trusted version.

        Args:
            content: The trusted original content.
            label: Label for this protection point.

        Returns:
            Dict with checksum and status.
        """
        checksum = compute_checksum(content)
        self._original_checksum = checksum
        self._store.record(self.doc_id, checksum, {
            "label": label,
            "content_length": len(content),
            "protected_at": time.time(),
        })

        if self.auto_snapshot:
            self._rollback.snapshot(content, label, checksum)

        return {
            "status": "protected",
            "checksum": checksum,
            "doc_id": self.doc_id,
        }

    def protect_file(self, filepath: Union[str, Path], label: str = "initial") -> dict:
        """Protect a file by recording its checksum.

        Args:
            filepath: Path to the file to protect.
            label: Label for this protection point.
        """
        filepath = Path(filepath)
        checksum = compute_file_checksum(filepath)
        self._original_checksum = checksum
        self._store.record(self.doc_id, checksum, {
            "label": label,
            "filepath": str(filepath),
            "protected_at": time.time(),
        })

        if self.auto_snapshot:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self._rollback.snapshot(content, label, checksum)

        return {
            "status": "protected",
            "checksum": checksum,
            "filepath": str(filepath),
        }

    def verify(self, content: str) -> dict:
        """Verify content against the protected version.

        Args:
            content: Content to verify.

        Returns:
            Dict with safety status, diff, and recommendations.
        """
        current_checksum = compute_checksum(content)
        is_safe = self._store.verify(self.doc_id, current_checksum)

        result = {
            "safe": is_safe,
            "checksum": current_checksum,
            "doc_id": self.doc_id,
            "verified_at": time.time(),
        }

        if is_safe is None:
            result["status"] = "unknown"
            result["message"] = "No protected version found. Call protect() first."
        elif is_safe:
            result["status"] = "verified"
            result["message"] = "Content is unchanged and verified."
        else:
            result["status"] = "modified"
            result["message"] = "Content has been modified!"

            # Generate diff
            stored = self._store.get(self.doc_id)
            if stored and self._rollback.get_snapshot(index=0):
                original = self._rollback.get_snapshot(index=0).content
                diff = ContentDiff.compare(original, content)
                result["diff"] = diff
                result["change_summary"] = diff.change_summary

        self._last_verified = result
        return result

    def rollback(self, steps: int = 1) -> Optional[str]:
        """Roll back to a previous version.

        Args:
            steps: How many snapshots back to go.

        Returns:
            Recovered content, or None if rollback not possible.
        """
        snap = self._rollback.rollback(steps)
        if snap:
            return snap.content
        return None

    def snapshot(self, content: str, label: str = "") -> dict:
        """Create a manual snapshot.

        Args:
            content: Content to snapshot.
            label: Label for this snapshot.

        Returns:
            Snapshot info.
        """
        snap = self._rollback.snapshot(content, label)
        return {
            "status": "snapshotted",
            "label": snap.label,
            "timestamp": snap.iso_time,
        }

    def history(self) -> list:
        """List all available snapshots."""
        return self._rollback.list_snapshots()

    def status(self) -> dict:
        """Get current protection status."""
        record = self._store.get(self.doc_id)
        return {
            "doc_id": self.doc_id,
            "protected": record is not None,
            "checksum": record["checksum"] if record else None,
            "protected_at": record.get("timestamp") if record else None,
            "snapshots": len(self._rollback.list_snapshots()),
            "last_verified": self._last_verified,
        }
