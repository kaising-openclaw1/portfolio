"""Core checksum engine using SHA-256 with optional content hashing."""

import hashlib
import json
import os
from pathlib import Path
from typing import Union


def compute_checksum(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    """Compute checksum for given content.

    Args:
        content: Text or bytes content to hash.
        algorithm: Hash algorithm (sha256, md5, sha1).

    Returns:
        Hex digest string.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    h = hashlib.new(algorithm)
    h.update(content)
    return h.hexdigest()


def compute_file_checksum(filepath: Union[str, Path], algorithm: str = "sha256",
                          chunk_size: int = 8192) -> str:
    """Compute checksum for a file without loading it entirely into memory.

    Args:
        filepath: Path to the file.
        algorithm: Hash algorithm.
        chunk_size: Read chunk size in bytes.

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(content: Union[str, bytes], expected: str,
                    algorithm: str = "sha256") -> bool:
    """Verify content against an expected checksum.

    Args:
        content: Content to verify.
        expected: Expected hex digest.
        algorithm: Hash algorithm used.

    Returns:
        True if checksum matches.
    """
    return compute_checksum(content, algorithm) == expected


def verify_file_checksum(filepath: Union[str, Path], expected: str,
                         algorithm: str = "sha256") -> bool:
    """Verify a file against an expected checksum."""
    return compute_file_checksum(filepath, algorithm) == expected


class ChecksumStore:
    """Persistent storage for document checksums.

    Stores checksums in a JSON file for tracking document integrity over time.
    """

    def __init__(self, store_path: Union[str, Path] = ".docguard_store.json"):
        self.store_path = Path(store_path)
        self._data = self._load()

    def _load(self) -> dict:
        if self.store_path.exists():
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"documents": {}, "metadata": {"version": "1.0"}}

    def save(self):
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def record(self, doc_id: str, checksum: str, metadata: dict = None):
        """Record a checksum for a document."""
        import time
        self._data["documents"][doc_id] = {
            "checksum": checksum,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        self.save()

    def get(self, doc_id: str) -> dict:
        """Get stored record for a document."""
        return self._data["documents"].get(doc_id)

    def verify(self, doc_id: str, current_checksum: str) -> bool:
        """Verify current checksum against stored record."""
        record = self.get(doc_id)
        if not record:
            return None  # No record exists
        return record["checksum"] == current_checksum

    def list_documents(self) -> dict:
        """List all tracked documents."""
        return dict(self._data["documents"])

    def remove(self, doc_id: str):
        """Remove a document from tracking."""
        self._data["documents"].pop(doc_id, None)
        self.save()
