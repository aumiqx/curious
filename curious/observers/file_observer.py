"""File Observer — watches for file system changes."""

import os
import time
from pathlib import Path


class FileObserver:
    def __init__(self, watch_path: str, extensions: list[str] | None = None):
        self.watch_path = Path(watch_path).resolve()
        self.extensions = extensions or [".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".md"]
        self.source_name = "files"
        self.file_states: dict[str, float] = {}  # path -> last modified time
        self._snapshot()

    def _should_watch(self, path: Path) -> bool:
        if any(part.startswith(".") for part in path.parts):
            return False
        if "node_modules" in path.parts or "__pycache__" in path.parts or ".next" in path.parts:
            return False
        return path.suffix in self.extensions

    def _snapshot(self):
        self.file_states = {}
        if not self.watch_path.exists():
            return
        for path in self.watch_path.rglob("*"):
            if path.is_file() and self._should_watch(path):
                try:
                    self.file_states[str(path)] = path.stat().st_mtime
                except OSError:
                    pass

    def get_initial_context(self) -> list[dict]:
        """Get file structure overview."""
        ext_counts: dict[str, int] = {}
        total_files = 0
        for path_str in self.file_states:
            p = Path(path_str)
            ext_counts[p.suffix] = ext_counts.get(p.suffix, 0) + 1
            total_files += 1

        ext_summary = ", ".join(f"{ext}: {count}" for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        return [{
            "source": self.source_name,
            "content": f"Project has {total_files} tracked files. Types: {ext_summary}",
        }]

    def poll(self) -> list[dict]:
        """Detect file changes since last poll."""
        observations = []
        current: dict[str, float] = {}

        if not self.watch_path.exists():
            return observations

        for path in self.watch_path.rglob("*"):
            if path.is_file() and self._should_watch(path):
                try:
                    current[str(path)] = path.stat().st_mtime
                except OSError:
                    pass

        # New files
        new_files = set(current.keys()) - set(self.file_states.keys())
        if new_files:
            names = [str(Path(f).relative_to(self.watch_path)) for f in list(new_files)[:10]]
            observations.append({
                "source": self.source_name,
                "content": f"New files created: {', '.join(names)}",
            })

        # Modified files
        modified = []
        for path_str, mtime in current.items():
            if path_str in self.file_states and mtime > self.file_states[path_str]:
                modified.append(str(Path(path_str).relative_to(self.watch_path)))

        if modified:
            observations.append({
                "source": self.source_name,
                "content": f"Files modified: {', '.join(modified[:10])}",
            })

        # Deleted files
        deleted = set(self.file_states.keys()) - set(current.keys())
        if deleted:
            names = [str(Path(f).relative_to(self.watch_path)) for f in list(deleted)[:10]]
            observations.append({
                "source": self.source_name,
                "content": f"Files deleted: {', '.join(names)}",
            })

        self.file_states = current
        return observations
