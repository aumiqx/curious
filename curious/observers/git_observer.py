"""Git Observer — watches a git repository for changes."""

import subprocess
import time
from pathlib import Path


class GitObserver:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.last_commit: str | None = None
        self.source_name = "git"

    def _run_git(self, *args) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def get_initial_context(self) -> list[dict]:
        """Get initial snapshot of the repo."""
        observations = []

        # Recent commits
        log = self._run_git("log", "--oneline", "-20", "--no-decorate")
        if log:
            observations.append({
                "source": self.source_name,
                "content": f"Recent commits:\n{log}",
            })

        # Current branch
        branch = self._run_git("branch", "--show-current")
        if branch:
            observations.append({
                "source": self.source_name,
                "content": f"Current branch: {branch}",
            })

        # File structure (top-level)
        files = self._run_git("ls-tree", "--name-only", "HEAD")
        if files:
            observations.append({
                "source": self.source_name,
                "content": f"Top-level files:\n{files}",
            })

        # Recent activity — which files change most
        activity = self._run_git("log", "--pretty=format:", "--name-only", "-50")
        if activity:
            file_counts: dict[str, int] = {}
            for f in activity.split("\n"):
                f = f.strip()
                if f:
                    file_counts[f] = file_counts.get(f, 0) + 1
            top_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            activity_text = "\n".join(f"  {f}: {c} changes" for f, c in top_files)
            observations.append({
                "source": self.source_name,
                "content": f"Most active files (last 50 commits):\n{activity_text}",
            })

        self.last_commit = self._run_git("rev-parse", "HEAD")
        return observations

    def poll(self) -> list[dict]:
        """Check for new changes since last poll."""
        observations = []
        current_commit = self._run_git("rev-parse", "HEAD")

        if self.last_commit and current_commit != self.last_commit:
            # New commits
            log = self._run_git("log", "--oneline", f"{self.last_commit}..{current_commit}")
            if log:
                observations.append({
                    "source": self.source_name,
                    "content": f"New commits:\n{log}",
                })

            # Changed files
            diff = self._run_git("diff", "--name-status", self.last_commit, current_commit)
            if diff:
                observations.append({
                    "source": self.source_name,
                    "content": f"Files changed:\n{diff}",
                })

            self.last_commit = current_commit

        # Check for uncommitted changes
        status = self._run_git("status", "--porcelain")
        if status:
            observations.append({
                "source": self.source_name,
                "content": f"Uncommitted changes:\n{status}",
            })

        return observations
