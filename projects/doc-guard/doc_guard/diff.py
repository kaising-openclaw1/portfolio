"""Content diff engine for detecting and reporting document changes."""

import difflib
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiffLine:
    """A single line in a diff result."""
    line_number_old: Optional[int]
    line_number_new: Optional[int]
    type: str  # 'added', 'removed', 'unchanged'
    content: str


@dataclass
class ContentDiff:
    """Result of comparing two versions of content.

    Attributes:
        old_content: Original content.
        new_content: Modified content.
        additions: Lines that were added.
        deletions: Lines that were removed.
        modifications: Lines that were changed.
        similarity: Similarity ratio (0.0 to 1.0).
        unified_diff: Unified diff string.
    """
    old_content: str = ""
    new_content: str = ""
    additions: List[str] = field(default_factory=list)
    deletions: List[str] = field(default_factory=list)
    modifications: List[dict] = field(default_factory=list)
    similarity: float = 1.0
    unified_diff: str = ""

    @classmethod
    def compare(cls, old_content: str, new_content: str,
                old_label: str = "original", new_label: str = "modified") -> "ContentDiff":
        """Compare two versions of content and produce a diff report.

        Args:
            old_content: Original text.
            new_content: Modified text.
            old_label: Label for the original version.
            new_label: Label for the modified version.

        Returns:
            ContentDiff instance with full comparison results.
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        # Unified diff
        unified_diff = "".join(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=old_label, tofile=new_label,
            lineterm=""
        ))

        # Similarity
        matcher = difflib.SequenceMatcher(None, old_content, new_content)
        similarity = matcher.ratio()

        # Detailed diff
        additions = []
        deletions = []
        modifications = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            elif tag == "insert":
                for line in new_lines[j1:j2]:
                    additions.append(line.rstrip("\n"))
            elif tag == "delete":
                for line in old_lines[i1:i2]:
                    deletions.append(line.rstrip("\n"))
            elif tag == "replace":
                modifications.append({
                    "old": [l.rstrip("\n") for l in old_lines[i1:i2]],
                    "new": [l.rstrip("\n") for l in new_lines[j1:j2]],
                })

        return cls(
            old_content=old_content,
            new_content=new_content,
            additions=additions,
            deletions=deletions,
            modifications=modifications,
            similarity=similarity,
            unified_diff=unified_diff,
        )

    @property
    def is_modified(self) -> bool:
        """Whether any changes were detected."""
        return self.similarity < 1.0

    @property
    def change_summary(self) -> dict:
        """Human-readable change summary."""
        return {
            "additions": len(self.additions),
            "deletions": len(self.deletions),
            "modifications": len(self.modifications),
            "similarity": round(self.similarity * 100, 2),
            "total_changes": len(self.additions) + len(self.deletions) + len(self.modifications),
        }

    def to_markdown(self) -> str:
        """Format diff as a markdown report."""
        if not self.is_modified:
            return "✅ 内容未发生变化"

        summary = self.change_summary
        lines = [
            "📋 **变更报告**",
            f"- 相似度: {summary['similarity']}%",
            f"- 新增行: {summary['additions']}",
            f"- 删除行: {summary['deletions']}",
            f"- 修改段落: {summary['modifications']}",
            "",
            "### 详细差异",
            "```diff",
            self.unified_diff,
            "```",
        ]
        return "\n".join(lines)
