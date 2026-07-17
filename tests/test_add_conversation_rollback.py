#!/usr/bin/env python3
"""Tests for add_conversation's rollback-on-partial-failure behavior
(todos.md 2.4.3).

If the JSON file write succeeds but the SQLite index update fails, the
file + index.json/topics.json entries used to be left behind while the
call still reported "success" (the SQLite return value was silently
discarded). These tests force a *real* SQLite failure (not a mock) and
assert nothing is left orphaned.
"""

import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from conversation_memory import ConversationMemoryServer  # noqa: E402


@pytest.fixture
def temp_storage():
    temp_dir = tempfile.mkdtemp(prefix="claude_memory_rollback_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def server(temp_storage):
    return ConversationMemoryServer(temp_storage)


def _all_conversation_files(server):
    return list(server.conversations_path.rglob("conv_*.json"))


def _index_conversations(server):
    with open(server.index_file, "r", encoding="utf-8") as f:
        return json.load(f).get("conversations", [])


def _topics_index(server):
    with open(server.topics_file, "r", encoding="utf-8") as f:
        return json.load(f).get("topics", {})


@pytest.mark.asyncio
async def test_add_conversation_succeeds_normally(server):
    """Baseline / non-regression: a healthy SQLite index still works."""
    if not server.use_sqlite_search:
        pytest.skip("SQLite search unavailable")

    result = await server.add_conversation(
        content="Notes about python and docker", title="Baseline"
    )
    assert result["status"] == "success"
    assert len(_all_conversation_files(server)) == 1
    assert len(_index_conversations(server)) == 1


@pytest.mark.asyncio
async def test_add_conversation_rolls_back_on_real_sqlite_failure(server):
    """Force a genuine SQLite failure (not a mock): drop the conversations
    table so the next INSERT raises sqlite3.OperationalError, which is
    caught inside SearchDatabase.add_conversation() and surfaced as a
    False return. add_conversation must then undo the file + index writes
    rather than reporting success with an orphaned file on disk.
    """
    if not server.use_sqlite_search:
        pytest.skip("SQLite search unavailable")

    with sqlite3.connect(server.search_db.db_path) as conn:
        conn.execute("DROP TABLE conversations")
        conn.commit()

    result = await server.add_conversation(
        content="Notes about python and docker that should not survive",
        title="Should Roll Back",
    )

    assert result["status"] == "error"
    assert "rolled back" in result["message"]

    # No orphaned JSON file anywhere under conversations_path.
    assert _all_conversation_files(server) == []

    # index.json must not reference the failed conversation.
    assert _index_conversations(server) == []

    # topics.json ("python"/"docker" were extracted from the content) must
    # not reference the failed conversation under any topic.
    topics = _topics_index(server)
    all_conv_ids = {
        e.get("conversation_id")
        for entries in topics.values()
        for e in entries
        if isinstance(e, dict)
    }
    assert not any(cid and cid.startswith("conv_") for cid in all_conv_ids)


@pytest.mark.asyncio
async def test_add_conversation_rollback_leaves_other_conversations_intact(server):
    """Rollback must only remove the failed conversation's own entries,
    not unrelated conversations already in the index."""
    if not server.use_sqlite_search:
        pytest.skip("SQLite search unavailable")

    good = await server.add_conversation(
        content="Existing conversation about kubernetes", title="Existing"
    )
    assert good["status"] == "success"
    good_id = Path(good["file_path"]).stem

    with sqlite3.connect(server.search_db.db_path) as conn:
        conn.execute("DROP TABLE conversations")
        conn.commit()

    bad = await server.add_conversation(
        content="This one should roll back", title="Bad"
    )
    assert bad["status"] == "error"

    # The earlier, healthy conversation is untouched.
    remaining_files = _all_conversation_files(server)
    assert len(remaining_files) == 1
    assert remaining_files[0].stem == good_id

    index_ids = {c["id"] for c in _index_conversations(server)}
    assert index_ids == {good_id}


@pytest.mark.asyncio
async def test_rollback_helper_is_best_effort_on_missing_file(server):
    """_rollback_add_conversation must not raise if the file is already
    gone (e.g. removed by something else before rollback runs)."""
    missing_path = server.conversations_path / "conv_20260101_000000_ffffffff.json"
    # Should not raise even though the file was never created.
    server._rollback_add_conversation(
        missing_path, "conv_20260101_000000_ffffffff", ["python"]
    )

    topics = _topics_index(server)
    assert all(
        e.get("conversation_id") != "conv_20260101_000000_ffffffff"
        for e in topics.get("python", [])
    )
