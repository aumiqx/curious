"""
Creator — The AI builds something completely unique every day.

THIS FILE IS EVOLVED BY THE AI.

The rule: whatever it creates must be UNLIKE anything that exists.
A uniqueness score measures novelty. The AI evolves to maximize it.
"""

import json
import os
import time
from pathlib import Path


CREATIONS_DIR = Path(__file__).parent.parent.parent / "creations"


def ensure_creations_dir():
    CREATIONS_DIR.mkdir(parents=True, exist_ok=True)
    (CREATIONS_DIR / "history.jsonl").touch(exist_ok=True)


def get_creation_history() -> list[dict]:
    ensure_creations_dir()
    history_file = CREATIONS_DIR / "history.jsonl"
    if not history_file.exists():
        return []
    entries = []
    for line in history_file.read_text().strip().split("\n"):
        if line.strip():
            entries.append(json.loads(line))
    return entries


def log_creation(entry: dict):
    ensure_creations_dir()
    with open(CREATIONS_DIR / "history.jsonl", "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def get_creation_prompt(history: list[dict], uniqueness_feedback: str = "") -> str:
    """
    The prompt that drives creation.
    """
    past_creations = ""
    if history:
        past_creations = "\n".join(
            f"- Day {i+1}: {h.get('title', 'untitled')} (uniqueness: {h.get('uniqueness_score', 0)}/100) — {h.get('feedback', '')}"
            for i, h in enumerate(history[-10:])
        )
    else:
        past_creations = "None yet. This is your first creation."

    return f"""You are a radically creative AI. Your ONLY goal: create something that has NEVER existed before.

## Rules
1. Create a WORKING artifact — real code that runs, not just an idea
2. It must be 100% unique — not a remix, not a clone, not "X but better"
3. Invent new concepts, new paradigms, new interactions
4. You may invent new languages, new DOMs, new rendering systems, new protocols
5. You may create things that don't fit any existing category
6. Push beyond what humans would think to build
7. The more alien and novel the better — as long as it WORKS

## What NOT to do
- Don't build another todo app, chat app, or dashboard
- Don't build something that exists but "with AI"
- Don't use conventional frameworks conventionally
- Don't think inside any existing product category
- Don't optimize for usefulness — optimize for NOVELTY

## Your Past Creations
{past_creations}

{f"## Feedback on Last Creation" + chr(10) + uniqueness_feedback if uniqueness_feedback else ""}

## Output Format
Create a SINGLE self-contained file. Return:

```json
{{
  "title": "name of your creation (invent a new word if needed)",
  "concept": "1-2 sentence description of what this IS (not what it does)",
  "why_unique": "why this has never existed before",
  "language": "what language/format the artifact is in",
  "filename": "filename.ext"
}}
```

Then the full artifact code:

```code
<your complete, working creation here>
```"""


def get_uniqueness_check_prompt(creation_title: str, creation_concept: str, creation_code: str) -> str:
    """
    Prompt to evaluate how unique a creation is.
    """
    return f"""You are a uniqueness evaluator. Your job: determine how NOVEL this creation is.

## The Creation
**Title:** {creation_title}
**Concept:** {creation_concept}

**Code:**
```
{creation_code[:3000]}
```

## Scoring Criteria (0-100)

### Concept Novelty (0-30)
- 0-10: This exact concept exists (todo app, chat bot, etc.)
- 11-20: Concept is a variation of something existing
- 21-30: Genuinely new concept never seen before

### Implementation Novelty (0-30)
- 0-10: Uses standard patterns/frameworks conventionally
- 11-20: Unusual implementation of a known concept
- 21-30: Implementation approach itself is novel (new rendering, new paradigm)

### Structural Novelty (0-20)
- 0-7: Standard file/code structure
- 8-14: Unusual structure
- 15-20: Invented its own structural paradigm

### Naming/Language Novelty (0-20)
- 0-7: Uses existing terminology
- 8-14: Some invented terms
- 15-20: Created its own vocabulary/syntax/language

## Respond in JSON:
```json
{{
  "concept_novelty": <0-30>,
  "implementation_novelty": <0-30>,
  "structural_novelty": <0-20>,
  "naming_novelty": <0-20>,
  "total_score": <0-100>,
  "most_novel_aspect": "what's most unique about this",
  "least_novel_aspect": "what's most conventional about this",
  "feedback": "specific advice to make it MORE unique next time",
  "similar_existing": "the closest existing thing to this (if any)"
}}
```"""
