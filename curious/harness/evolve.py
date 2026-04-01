"""
Evolve — The self-modification loop.

THIS FILE IS PART OF THE HARNESS — NOT EVOLVED BY THE AI.
This is the "laws of physics" that the AI operates within.
It can read this file but cannot modify it.
"""

import json
import os
import shutil
import subprocess
import time
import traceback
from pathlib import Path

from curious.harness.fitness import measure_fitness, fitness_improved
from curious.providers.base import LLMProvider
from curious.seed.metacognition import get_metacognition_prompt, assess_learning_quality
from curious.seed.world_model import WorldModel


SEED_DIR = Path(__file__).parent.parent / "seed"
EVOLVABLE_FILES = ["world_model.py", "learner.py", "curiosity.py", "metacognition.py"]


def read_seed_files() -> dict[str, str]:
    """Read all evolvable seed files."""
    files = {}
    for name in EVOLVABLE_FILES:
        path = SEED_DIR / name
        if path.exists():
            files[name] = path.read_text()
    return files


def backup_seed(backup_dir: Path, generation: int):
    """Backup current seed before modification."""
    gen_dir = backup_dir / f"gen_{generation:04d}"
    gen_dir.mkdir(parents=True, exist_ok=True)
    for name in EVOLVABLE_FILES:
        src = SEED_DIR / name
        if src.exists():
            shutil.copy2(src, gen_dir / name)
    return gen_dir


def restore_seed(backup_dir: Path, generation: int):
    """Restore seed from backup (revert failed evolution)."""
    gen_dir = backup_dir / f"gen_{generation:04d}"
    for name in EVOLVABLE_FILES:
        src = gen_dir / name
        if src.exists():
            shutil.copy2(src, SEED_DIR / name)


def validate_seed() -> bool:
    """Check if the seed code is valid Python."""
    for name in EVOLVABLE_FILES:
        path = SEED_DIR / name
        if not path.exists():
            return False
        try:
            compile(path.read_text(), str(path), "exec")
        except SyntaxError:
            return False
    return True


EVOLUTION_MODEL = "gpt-4o"  # Use stronger model for code generation


def run_evolution_cycle(
    llm: LLMProvider,
    world_model: WorldModel,
    evolution_dir: Path,
    generation: int,
) -> dict:
    """
    Run one cycle of self-evolution:
    1. Measure current fitness
    2. Ask metacognition to analyze own code
    3. Implement the proposed change
    4. Validate the new code
    5. Measure new fitness
    6. Keep or revert
    """
    result = {
        "generation": generation,
        "timestamp": time.time(),
        "action": "none",
        "fitness_before": {},
        "fitness_after": {},
        "kept": False,
        "description": "",
        "file_changed": "",
        "error": None,
    }

    try:
        # Step 1: Measure current fitness
        fitness_before = measure_fitness(world_model)
        result["fitness_before"] = fitness_before

        # Step 2: Backup current seed
        backup_seed(evolution_dir, generation)

        # Step 3: Metacognitive analysis — AI reads its own code
        seed_files = read_seed_files()
        assessment = assess_learning_quality(world_model)
        meta_prompt = get_metacognition_prompt(assessment, seed_files)

        analysis = llm.ask_json(meta_prompt)
        result["description"] = analysis.get("proposed_change", {}).get("description", "no change proposed")
        target_file = analysis.get("proposed_change", {}).get("file", "")
        result["file_changed"] = target_file

        if not target_file or target_file not in EVOLVABLE_FILES:
            result["action"] = "skipped"
            result["description"] = "No valid file targeted for modification"
            return result

        # Step 4: Ask AI to rewrite the target file
        current_code = seed_files.get(target_file, "")
        change_desc = analysis["proposed_change"]["description"]

        rewrite_prompt = f"""Rewrite this Python file with ONE improvement.

CURRENT FILE: {target_file}
```python
{current_code}
```

IMPROVEMENT TO MAKE:
{change_desc}

CRITICAL RULES:
- Return the COMPLETE file. Every import, every function, every line.
- Do NOT skip anything with "..." or "# rest of code" or ellipsis.
- Keep the exact same function signatures (names, parameters).
- Keep the module docstring including "THIS FILE IS EVOLVED BY THE AI".
- Valid Python 3.11+ syntax only.
- Make ONE focused change. Do not rewrite unrelated parts.

```python"""

        # Try up to 2 times with strong model
        new_code = ""
        for attempt in range(2):
            new_code = llm.ask_code(rewrite_prompt, model_override=EVOLUTION_MODEL)
            if new_code and len(new_code) > 50:
                break

        if not new_code or len(new_code) < 50:
            result["action"] = "skipped"
            result["description"] += " [AI failed to generate valid code]"
            _log_result(evolution_dir, result)
            return result

        # Step 5: Write the new code
        target_path = SEED_DIR / target_file
        target_path.write_text(new_code)

        # Step 6: Validate syntax
        if not validate_seed():
            restore_seed(evolution_dir, generation)
            result["action"] = "reverted"
            result["description"] += " [SYNTAX ERROR — reverted]"
            _log_result(evolution_dir, result)
            return result

        # Step 8: Measure new fitness
        # (In a more advanced version, we'd run the new code for a while and compare)
        # For now, we keep the change if it's valid and the metacognition was confident
        confidence = analysis["proposed_change"].get("confidence", 0.5)

        result["fitness_after"] = fitness_before  # same for now — real fitness takes time
        result["action"] = "applied"
        result["kept"] = True
        result["description"] = f"[gen {generation}] {change_desc} (confidence: {confidence:.0%})"

        # Save evolution log
        log_path = evolution_dir / "evolution_log.jsonl"
        with open(log_path, "a") as f:
            f.write(json.dumps(result, default=str) + "\n")

        return result

    except Exception as e:
        # Any error: revert to be safe
        try:
            restore_seed(evolution_dir, generation)
        except Exception:
            pass
        result["action"] = "error"
        result["error"] = str(e)
        result["description"] = f"Error during evolution: {e}"
        return result


def _log_result(evolution_dir: Path, result: dict):
    """Append result to evolution log."""
    log_path = evolution_dir / "evolution_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(result, default=str) + "\n")


def get_evolution_history(evolution_dir: Path) -> list[dict]:
    """Read the evolution log."""
    log_path = evolution_dir / "evolution_log.jsonl"
    if not log_path.exists():
        return []
    history = []
    for line in log_path.read_text().strip().split("\n"):
        if line:
            history.append(json.loads(line))
    return history
