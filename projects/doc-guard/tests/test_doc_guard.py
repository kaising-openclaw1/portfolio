"""Tests for DocGuard."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from doc_guard.checksum import compute_checksum, verify_checksum, ChecksumStore
from doc_guard.diff import ContentDiff
from doc_guard.rollback import RollbackManager
from doc_guard.core import DocGuard


# --- Checksum Tests ---

class TestChecksum:
    def test_compute_checksum_string(self):
        result = compute_checksum("hello world")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex length

    def test_compute_checksum_bytes(self):
        result = compute_checksum(b"hello world")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_checksum_deterministic(self):
        a = compute_checksum("test content")
        b = compute_checksum("test content")
        assert a == b

    def test_checksum_different_content(self):
        a = compute_checksum("content A")
        b = compute_checksum("content B")
        assert a != b

    def test_verify_checksum(self):
        content = "test data"
        cs = compute_checksum(content)
        assert verify_checksum(content, cs) is True
        assert verify_checksum("wrong data", cs) is False

    def test_file_checksum(self):
        from doc_guard.checksum import compute_file_checksum, verify_file_checksum
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("file content test")
            f.flush()
            cs = compute_file_checksum(f.name)
            assert len(cs) == 64
            assert verify_file_checksum(f.name, cs) is True
            os.unlink(f.name)


# --- ChecksumStore Tests ---

class TestChecksumStore:
    def test_record_and_get(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            store = ChecksumStore(f.name)
            store.record("doc1", "abc123", {"label": "test"})
            record = store.get("doc1")
            assert record["checksum"] == "abc123"
            assert record["metadata"]["label"] == "test"
            os.unlink(f.name)

    def test_verify(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            store = ChecksumStore(f.name)
            store.record("doc1", "abc123")
            assert store.verify("doc1", "abc123") is True
            assert store.verify("doc1", "wrong") is False
            assert store.verify("nonexistent", "abc") is None
            os.unlink(f.name)

    def test_remove(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            store = ChecksumStore(f.name)
            store.record("doc1", "abc")
            store.remove("doc1")
            assert store.get("doc1") is None
            os.unlink(f.name)


# --- ContentDiff Tests ---

class TestContentDiff:
    def test_no_changes(self):
        content = "same content\non two lines"
        diff = ContentDiff.compare(content, content)
        assert diff.similarity == 1.0
        assert diff.is_modified is False
        assert len(diff.additions) == 0
        assert len(diff.deletions) == 0

    def test_additions(self):
        old = "line 1\nline 2"
        new = "line 1\nline 2\nline 3 added"
        diff = ContentDiff.compare(old, new)
        assert diff.is_modified is True
        assert len(diff.additions) > 0

    def test_deletions(self):
        old = "line 1\nline 2\nline 3"
        new = "line 1\nline 3"
        diff = ContentDiff.compare(old, new)
        assert len(diff.deletions) > 0

    def test_change_summary(self):
        old = "hello world"
        new = "hello universe"
        diff = ContentDiff.compare(old, new)
        summary = diff.change_summary
        assert "similarity" in summary
        assert "total_changes" in summary

    def test_markdown_output(self):
        diff = ContentDiff.compare("old", "new")
        md = diff.to_markdown()
        assert "变更报告" in md


# --- RollbackManager Tests ---

class TestRollbackManager:
    def test_snapshot_and_rollback(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            rb = RollbackManager("test_doc", history_path=f.name)
            rb.snapshot("version 1", "v1")
            rb.snapshot("version 2", "v2")

            recovered = rb.rollback(steps=1)
            assert recovered.content == "version 1"
            os.unlink(f.name)

    def test_list_snapshots(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            rb = RollbackManager("test_doc", history_path=f.name)
            rb.snapshot("content", "label1")
            snaps = rb.list_snapshots()
            assert len(snaps) == 1
            assert snaps[0]["label"] == "label1"
            os.unlink(f.name)

    def test_get_snapshot_by_label(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            rb = RollbackManager("test_doc", history_path=f.name)
            rb.snapshot("original", "before_edit")
            rb.snapshot("modified", "after_edit")

            snap = rb.get_snapshot(label="before_edit")
            assert snap.content == "original"
            os.unlink(f.name)

    def test_max_snapshots(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            rb = RollbackManager("test_doc", history_path=f.name, max_snapshots=3)
            for i in range(10):
                rb.snapshot(f"version {i}")
            snaps = rb.list_snapshots()
            assert len(snaps) == 3
            os.unlink(f.name)

    def test_clear(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            rb = RollbackManager("test_doc", history_path=f.name)
            rb.snapshot("data")
            rb.clear()
            assert len(rb.list_snapshots()) == 0
            os.unlink(f.name)


# --- DocGuard Core Tests ---

class TestDocGuard:
    def test_protect_and_verify_unchanged(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")

            guard = DocGuard("doc1", store_path=store, history_path=hist)
            guard.protect("original content")

            result = guard.verify("original content")
            assert result["safe"] is True
            assert result["status"] == "verified"

    def test_protect_and_verify_modified(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")

            guard = DocGuard("doc1", store_path=store, history_path=hist)
            guard.protect("original content")

            result = guard.verify("original content MODIFIED")
            assert result["safe"] is False
            assert result["status"] == "modified"
            assert "diff" in result

    def test_rollback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")

            guard = DocGuard("doc1", store_path=store, history_path=hist)
            guard.protect("original content")

            recovered = guard.rollback()
            assert recovered == "original content"

    def test_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")

            guard = DocGuard("doc1", store_path=store, history_path=hist)
            guard.protect("v1")
            guard.snapshot("v2", "checkpoint")

            history = guard.history()
            assert len(history) == 2

    def test_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")

            guard = DocGuard("doc1", store_path=store, history_path=hist)
            status = guard.status()
            assert status["doc_id"] == "doc1"
            assert status["protected"] is False

            guard.protect("content")
            status = guard.status()
            assert status["protected"] is True

    def test_protect_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = os.path.join(tmpdir, "store.json")
            hist = os.path.join(tmpdir, "hist.json")
            filepath = os.path.join(tmpdir, "test.txt")

            with open(filepath, "w") as f:
                f.write("file content")

            guard = DocGuard("filedoc", store_path=store, history_path=hist)
            result = guard.protect_file(filepath)
            assert result["status"] == "protected"
            assert result["filepath"] == filepath
