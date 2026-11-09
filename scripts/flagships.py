"""The flagship set, read from its one authority: docs/brand-positioning.md.

Every checker that needs to know which repositories are flagships (the metadata
audit, the rollout contract) reads this table instead of carrying its own list
or count; adding or retiring a flagship is a one-table edit in the doc.
"""

from __future__ import annotations

import re
from pathlib import Path

CLAIMS_DOC = "docs/brand-positioning.md"
# "## Six flagship propositions" today; the number word is not part of the contract.
SECTION_RE = re.compile(r"^## [^\n]*flagship propositions[^\n]*$", re.MULTILINE)
NEXT_HEADING_RE = re.compile(r"^#{2,3} ", re.MULTILINE)
FLAGSHIP_ROW_RE = re.compile(
    r"^\|\s*\[([a-z0-9.-]+)\]\[[^\]]*\]\s*\|\s*(.+?)\s*\|", re.MULTILINE
)


def flagship_sentences(doc: Path) -> dict[str, str]:
    """{repo name: positioning sentence} for the flagship table; {} if absent."""
    if not doc.is_file():
        return {}
    text = doc.read_text(encoding="utf-8")
    start = SECTION_RE.search(text)
    if start is None:
        return {}
    section = text[start.end() :]
    end = NEXT_HEADING_RE.search(section)
    if end is not None:  # the table sits directly under the heading
        section = section[: end.start()]
    return {m.group(1): m.group(2).strip() for m in FLAGSHIP_ROW_RE.finditer(section)}
