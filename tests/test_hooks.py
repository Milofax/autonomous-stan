#!/usr/bin/env python3
"""Tests für STAN Hooks (stan-context, stan-track, stan-gate)."""

import json
import os
import subprocess
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add hooks to path
HOOKS_DIR = Path(__file__).parent.parent / ".claude/hooks/stan"
sys.path.insert(0, str(HOOKS_DIR / "lib"))
sys.path.insert(0, str(HOOKS_DIR / "user-prompt-submit"))
sys.path.insert(0, str(HOOKS_DIR / "post-tool-use"))
sys.path.insert(0, str(HOOKS_DIR / "pre-tool-use"))


class TestStanContext:
    """Tests für stan-context Hook (UserPromptSubmit)."""

    def test_context_without_stan_md(self, tmp_path):
        """Ohne stan.md wird Fallback-Message ausgegeben."""
        # Import fresh
        import importlib
        import stan_context
        importlib.reload(stan_context)

        input_data = json.dumps({"user_message": "Hello"})

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('os.getcwd', return_value=str(tmp_path)):
                    with patch.object(stan_context, 'load_learnings', return_value=[]):
                        with patch.object(stan_context, 'get_stats', return_value={
                            "hot_count": 0, "recent_count": 0
                        }):
                            stan_context.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True
        assert "nicht initialisiert" in output["systemMessage"]

    def test_context_with_stan_md(self, tmp_path):
        """Mit stan.md wird Phase und Task angezeigt."""
        import importlib
        import stan_context
        importlib.reload(stan_context)

        # Create stan.md
        stan_md = tmp_path / "stan.md"
        stan_md.write_text("""# Test Project

## Status

| Feld | Wert |
|------|------|
| **Phase** | CREATE |
| **Current Task** | T-001 |
""")

        input_data = json.dumps({"user_message": "Hello"})

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('os.getcwd', return_value=str(tmp_path)):
                    with patch.object(stan_context, 'load_learnings', return_value=[]):
                        with patch.object(stan_context, 'get_stats', return_value={
                            "hot_count": 2, "recent_count": 5
                        }):
                            stan_context.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True
        assert "CREATE" in output["systemMessage"]
        assert "Test Project" in output["systemMessage"]

    def test_context_shows_learnings_count(self, tmp_path):
        """Learnings Count wird angezeigt."""
        import importlib
        import stan_context
        importlib.reload(stan_context)

        input_data = json.dumps({})

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                with patch('os.getcwd', return_value=str(tmp_path)):
                    with patch.object(stan_context, 'load_learnings', return_value=[
                        {"content": "Learning 1"},
                        {"content": "Learning 2"}
                    ]):
                        with patch.object(stan_context, 'get_stats', return_value={
                            "hot_count": 3, "recent_count": 7
                        }):
                            stan_context.main()

        output = json.loads(mock_stdout.getvalue())
        assert "3 hot" in output["systemMessage"]
        assert "7 recent" in output["systemMessage"]


class TestStanTrack:
    """Tests für stan-track Hook (PostToolUse - Bash)."""

    def test_track_ignores_non_bash(self):
        """Nicht-Bash Tools werden ignoriert."""
        import importlib
        import stan_track
        importlib.reload(stan_track)

        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/test"}
        })

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                stan_track.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True
        assert "systemMessage" not in output

    def test_track_ignores_non_test_commands(self):
        """Nicht-Test Commands werden ignoriert."""
        import importlib
        import stan_track
        importlib.reload(stan_track)

        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
            "tool_result": {"output": "files..."}
        })

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                stan_track.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True
        assert "systemMessage" not in output

    def test_track_recognizes_test_commands(self):
        """Test Commands werden erkannt."""
        import importlib
        import stan_track
        importlib.reload(stan_track)

        test_commands = [
            "npm test",
            "npm run test",
            "yarn test",
            "pytest",
            "python -m pytest",
            "cargo test",
            "go test",
        ]

        for cmd in test_commands:
            assert stan_track.is_test_command(cmd), f"{cmd} should be recognized as test"

    def test_track_detects_red_to_green(self, tmp_path):
        """ROT→GRÜN wird erkannt und pending_learning erstellt."""
        import importlib
        import stan_track
        import session_state
        importlib.reload(stan_track)
        importlib.reload(session_state)

        session_file = tmp_path / "session.json"

        with patch.object(session_state, 'get_session_file', return_value=session_file):
            # Erst ROT
            session_state.record_test_result("npm test", 1)

            # Dann GRÜN
            input_data = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": "npm test"},
                "tool_result": {"exit_code": 0}
            })

            with patch('sys.stdin', StringIO(input_data)):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    stan_track.main()

            output = json.loads(mock_stdout.getvalue())
            assert output["continue"] is True
            assert "systemMessage" in output
            assert "Learning erkannt" in output["systemMessage"]


class TestStanGate:
    """Tests für stan-gate Hook (PreToolUse)."""

    def test_gate_ignores_non_bash(self):
        """Nicht-Bash Tools werden durchgelassen."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        input_data = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/test"}
        })

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                stan_gate.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True

    def test_gate_ignores_non_commit(self):
        """Nicht-Commit Commands werden durchgelassen."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "git status"}
        })

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                stan_gate.main()

        output = json.loads(mock_stdout.getvalue())
        assert output["continue"] is True

    def test_gate_blocks_commit_with_pending_learnings(self, tmp_path):
        """Commit wird blockiert wenn pending_learnings existieren."""
        import importlib
        import stan_gate
        import session_state
        importlib.reload(stan_gate)
        importlib.reload(session_state)

        session_file = tmp_path / "session.json"

        with patch.object(session_state, 'get_session_file', return_value=session_file):
            # Add pending learning
            session_state.add_pending_learning("Test learning", "Test context")

            input_data = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": "git commit -m 'test'"}
            })

            with patch('sys.stdin', StringIO(input_data)):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    stan_gate.main()

            output = json.loads(mock_stdout.getvalue())
            assert output["continue"] is False
            assert "BLOCKED" in output["reason"]
            assert "pending" in output["reason"].lower()

    def test_gate_allows_commit_without_pending(self, tmp_path):
        """Commit wird erlaubt wenn keine pending_learnings."""
        import importlib
        import stan_gate
        import session_state
        importlib.reload(stan_gate)
        importlib.reload(session_state)

        session_file = tmp_path / "session.json"

        with patch.object(session_state, 'get_session_file', return_value=session_file):
            input_data = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": "git commit -m 'test'"}
            })

            with patch('sys.stdin', StringIO(input_data)):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    with patch.object(stan_gate, 'get_last_test_status', return_value=True):
                        stan_gate.main()

            output = json.loads(mock_stdout.getvalue())
            assert output["continue"] is True

    def test_gate_warns_on_red_tests(self, tmp_path):
        """Warnung bei roten Tests vor Commit."""
        import importlib
        import stan_gate
        import session_state
        importlib.reload(stan_gate)
        importlib.reload(session_state)

        session_file = tmp_path / "session.json"

        with patch.object(session_state, 'get_session_file', return_value=session_file):
            # Set last test to failed
            session_state.record_test_result("npm test", 1)

            input_data = json.dumps({
                "tool_name": "Bash",
                "tool_input": {"command": "git commit -m 'test'"}
            })

            with patch('sys.stdin', StringIO(input_data)):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    stan_gate.main()

            output = json.loads(mock_stdout.getvalue())
            # Should continue but with warning
            assert output["continue"] is True
            assert "systemMessage" in output
            assert "ROT" in output["systemMessage"]


class TestHelperFunctions:
    """Tests für Helper-Funktionen in den Hooks."""

    def test_is_commit_command(self):
        """is_commit_command() erkennt git commit."""
        import stan_gate

        assert stan_gate.is_commit_command("git commit -m 'test'") is True
        assert stan_gate.is_commit_command("git commit --amend") is True
        assert stan_gate.is_commit_command("GIT COMMIT -m 'test'") is True  # case insensitive
        assert stan_gate.is_commit_command("git status") is False
        assert stan_gate.is_commit_command("git push") is False

    def test_is_test_command(self):
        """is_test_command() erkennt Test-Commands."""
        import stan_track

        # Positiv
        assert stan_track.is_test_command("npm test") is True
        assert stan_track.is_test_command("npm run test") is True
        assert stan_track.is_test_command("pytest") is True
        assert stan_track.is_test_command("pytest tests/") is True
        assert stan_track.is_test_command("cargo test") is True

        # Negativ
        assert stan_track.is_test_command("npm install") is False
        assert stan_track.is_test_command("git commit") is False
        assert stan_track.is_test_command("echo test") is False


class TestWorktreeFunctions:
    """Tests für Worktree-Enforcement Funktionen."""

    def test_is_git_repo_in_git_dir(self, tmp_path):
        """is_git_repo() erkennt Git-Repos."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        # Create a fake git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                assert stan_gate.is_git_repo() is True

    def test_is_git_repo_not_in_git_dir(self, tmp_path):
        """is_git_repo() erkennt Nicht-Git-Verzeichnisse."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(128, "git")
                assert stan_gate.is_git_repo() is False

    def test_is_main_worktree_with_git_dir(self, tmp_path):
        """is_main_worktree() erkennt Haupt-Repo (hat .git Verzeichnis)."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        # Haupt-Repo hat .git als Verzeichnis
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            assert stan_gate.is_main_worktree() is True

    def test_is_main_worktree_with_git_file(self, tmp_path):
        """is_main_worktree() erkennt Worktree (hat .git Datei)."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        # Worktree hat .git als Datei
        git_file = tmp_path / ".git"
        git_file.write_text("gitdir: /path/to/main/.git/worktrees/feature")

        with patch('os.getcwd', return_value=str(tmp_path)):
            assert stan_gate.is_main_worktree() is False

    def test_is_feature_work_few_files(self, tmp_path):
        """is_feature_work() erkennt triviale Änderungen (wenige Dateien)."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.stdout = "README.md\n"
                mock_run.return_value.returncode = 0
                assert stan_gate.is_feature_work() is False

    def test_is_feature_work_many_files(self, tmp_path):
        """is_feature_work() erkennt Feature-Arbeit (viele Dateien)."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.stdout = "a.py\nb.py\nc.py\nd.py\ne.py\nf.py\n"
                mock_run.return_value.returncode = 0
                assert stan_gate.is_feature_work() is True

    def test_is_feature_work_hooks_pattern(self, tmp_path):
        """is_feature_work() erkennt Feature-Arbeit (hooks betroffen)."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.stdout = ".claude/hooks/stan/lib/test.py\n"
                mock_run.return_value.returncode = 0
                assert stan_gate.is_feature_work() is True

    def test_check_worktree_non_git(self, tmp_path):
        """check_worktree() erlaubt Nicht-Git-Projekte."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch.object(stan_gate, 'is_git_repo', return_value=False):
            allowed, reason = stan_gate.check_worktree()
            assert allowed is True
            assert reason is None

    def test_check_worktree_feature_branch(self, tmp_path):
        """check_worktree() erlaubt Feature-Branch."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch.object(stan_gate, 'is_git_repo', return_value=True):
            with patch.object(stan_gate, 'get_current_branch', return_value="feature-branch"):
                allowed, reason = stan_gate.check_worktree()
                assert allowed is True
                assert reason is None

    def test_check_worktree_blocks_feature_on_main(self, tmp_path):
        """check_worktree() blockiert Feature-Arbeit auf main."""
        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        with patch.object(stan_gate, 'is_git_repo', return_value=True):
            with patch.object(stan_gate, 'get_current_branch', return_value="main"):
                with patch.object(stan_gate, 'is_main_worktree', return_value=True):
                    with patch.object(stan_gate, 'is_feature_work', return_value=True):
                        allowed, reason = stan_gate.check_worktree()
                        assert allowed is False
                        assert "BLOCKED" in reason
                        assert "Worktree" in reason
