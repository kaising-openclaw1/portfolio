"""Rollback manager for automatic document recovery."""

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class Snapshot:
    """A point-in-time snapshot of document content."""
    content: str
    timestamp: float
    checksum: str
    label: str = ""

    @property
    def iso_time(self) -> str:
        from datetime import datetime
        return datetime.fromtimestamp(self.timestamp).isoformat()


class RollbackManager:
    """Manages document snapshots for rollback capability.

    Usage:
        rb = RollbackManager("my_doc")
        rb.snapshot(content, "before_ai_edit")
        # ... AI modifies the document ...
        if corruption_detected:
            content = rb.rollback()
    """

    def __init__(self, doc_id: str, history_path: Union[str, Path] = None,
                 max_snapshots: int = 50):
        self.doc_id = doc_id
        self.max_snapshots = max_snapshots
        self.history_path = Path(history_path or f".docguard_{doc_id}_history.json")
        self._snapshots: List[Snapshot] = self._load()

    def _load(self) -> List[Snapshot]:
        if self.history_path.exists():
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Snapshot(**s) for s in data.get("snapshots", [])]
        return []

    def _save(self):
        data = {
            "doc_id": self.doc_id,
            "snapshots": [
                {
                    "content": s.content,
                    "timestamp": s.timestamp,
                    "checksum": s.checksum,
                    "label": s.label,
                }
                for s in self._snapshots
            ],
        }
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def snapshot(self, content: str, label: str = "", checksum: str = None) -> Snapshot:
        """Create a new snapshot.

        Args:
            content: Document content to save.
            label: Human-readable label for this snapshot.
            checksum: Optional pre-computed checksum.

        Returns:
            The created Snapshot.
        """
        from doc_guard.checksum import compute_checksum
        snap = Snapshot(
            content=content,
            timestamp=time.time(),
            checksum=checksum or compute_checksum(content),
            label=label or f"snapshot_{len(self._snapshots)}",
        )
        self._snapshots.append(snap)

        # Trim old snapshots if exceeding max
        if len(self._snapshots) > self.max_snapshots:
            self._snapshots = self._snapshots[-self.max_snapshots:]

        self._save()
        return snap

    def rollback(self, steps: int = 1) -> Optional[Snapshot]:
        """Roll back to a previous snapshot.

        Args:
            steps: How many snapshots back to go (1 = most recent before current).

        Returns:
            The snapshot content, or None if not enough history.
        """
        idx = len(self._snapshots) - 1 - steps
        if idx < 0:
            return None
        return self._snapshots[idx]

    def list_snapshots(self) -> List[dict]:
        """List all available snapshots."""
        return [
            {
                "label": s.label,
                "timestamp": s.iso_time,
                "checksum": s.checksum,
                "content_length": len(s.content),
            }
            for s in self._snapshots
        ]

    def get_snapshot(self, label: str = None, index: int = -1) -> Optional[Snapshot]:
        """Get a specific snapshot by label or index."""
        if label:
            for s in self._snapshots:
                if s.label == label:
                    return s
            return None
        return self._snapshots[index] if self._snapshots else None

    def clear(self):
        """Clear all snapshot history."""
        self._snapshots = []
        if self.history_path.exists():
            self.history_path.unlink()
