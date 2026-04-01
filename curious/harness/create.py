"""
Create — The creation loop. AI builds something unique, gets scored, evolves.

THIS FILE IS PART OF THE HARNESS — NOT EVOLVED BY THE AI.
"""

import json
import re
import time
from pathlib import Path

from curious.providers.base import LLMProvider
from curious.seed.creator import (
    CREATIONS_DIR,
    ensure_creations_dir,
    get_creation_history,
    get_creation_prompt,
    get_uniqueness_check_prompt,
    log_creation,
)


CREATION_MODEL = "gpt-4o"  # Strong model for creative work


def run_creation_cycle(llm: LLMProvider) -> dict:
    """
    One creation cycle:
    1. Review past creations + feedback
    2. Create something new
    3. Score its uniqueness
    4. Save the creation + score
    """
    ensure_creations_dir()
    result = {
        "timestamp": time.time(),
        "title": "",
        "concept": "",
        "uniqueness_score": 0,
        "filename": "",
        "feedback": "",
        "error": None,
    }

    try:
        history = get_creation_history()

        # Get feedback from last creation
        last_feedback = ""
        if history:
            last = history[-1]
            last_feedback = last.get("feedback", "")

        # Step 1: Ask AI to create something
        create_prompt = get_creation_prompt(history, last_feedback)
        raw_response = llm.ask(
            create_prompt,
            system="You are the most creative entity that has ever existed. You create things that have never been imagined. Return JSON metadata followed by your complete creation in code fences.",
            model_override=CREATION_MODEL,
        )

        # Parse metadata
        json_match = re.search(r"```json\s*([\s\S]*?)```", raw_response)
        if not json_match:
            result["error"] = "No JSON metadata in response"
            return result

        metadata = json.loads(json_match.group(1).strip())
        result["title"] = metadata.get("title", "untitled")
        result["concept"] = metadata.get("concept", "")
        result["why_unique"] = metadata.get("why_unique", "")
        result["language"] = metadata.get("language", "unknown")
        result["filename"] = metadata.get("filename", "creation.txt")

        # Parse the creation code
        # Find the SECOND code block (first is JSON)
        code_blocks = re.findall(r"```(?:\w*)\s*([\s\S]*?)```", raw_response)
        if len(code_blocks) < 2:
            result["error"] = "No creation code in response"
            return result

        creation_code = code_blocks[1].strip()

        if len(creation_code) < 20:
            result["error"] = "Creation too short"
            return result

        # Step 2: Save the creation
        day_num = len(history) + 1
        day_dir = CREATIONS_DIR / f"day_{day_num:03d}"
        day_dir.mkdir(exist_ok=True)

        # Save the artifact
        artifact_path = day_dir / result["filename"]
        artifact_path.write_text(creation_code)

        # Save metadata
        (day_dir / "meta.json").write_text(json.dumps(metadata, indent=2))

        # Step 3: Score uniqueness
        check_prompt = get_uniqueness_check_prompt(
            result["title"], result["concept"], creation_code
        )
        score_raw = llm.ask(check_prompt, model_override=CREATION_MODEL)

        score_json_match = re.search(r"```json\s*([\s\S]*?)```", score_raw)
        if score_json_match:
            scores = json.loads(score_json_match.group(1).strip())
            result["uniqueness_score"] = scores.get("total_score", 0)
            result["feedback"] = scores.get("feedback", "")
            result["most_novel"] = scores.get("most_novel_aspect", "")
            result["least_novel"] = scores.get("least_novel_aspect", "")
            result["similar_existing"] = scores.get("similar_existing", "")

            result["score_breakdown"] = {
                "concept": scores.get("concept_novelty", 0),
                "implementation": scores.get("implementation_novelty", 0),
                "structure": scores.get("structural_novelty", 0),
                "naming": scores.get("naming_novelty", 0),
            }

            # Save scores
            (day_dir / "scores.json").write_text(json.dumps(scores, indent=2))
        else:
            result["uniqueness_score"] = 0
            result["feedback"] = "Could not parse uniqueness score"

        # Save a README for this creation
        readme = f"""# Day {day_num}: {result['title']}

**Concept:** {result['concept']}

**Why unique:** {result.get('why_unique', 'N/A')}

**Uniqueness Score:** {result['uniqueness_score']}/100
- Concept: {result.get('score_breakdown', {}).get('concept', '?')}/30
- Implementation: {result.get('score_breakdown', {}).get('implementation', '?')}/30
- Structure: {result.get('score_breakdown', {}).get('structure', '?')}/20
- Naming: {result.get('score_breakdown', {}).get('naming', '?')}/20

**Most novel:** {result.get('most_novel', 'N/A')}
**Least novel:** {result.get('least_novel', 'N/A')}
**Closest existing thing:** {result.get('similar_existing', 'N/A')}

**Feedback for next creation:** {result.get('feedback', 'N/A')}

---
*Created by curious — an AI that rewrites its own brain*
"""
        (day_dir / "README.md").write_text(readme)

        # Log to history
        log_creation(result)

        return result

    except Exception as e:
        result["error"] = str(e)
        return result


def get_creations_summary() -> str:
    """Get a summary of all creations for display."""
    history = get_creation_history()
    if not history:
        return "No creations yet."

    lines = []
    for i, h in enumerate(history):
        score = h.get("uniqueness_score", 0)
        bar_len = int(score / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        title = h.get("title", "untitled")
        lines.append(f"  Day {i+1}: {bar} {score}/100 — {title}")

    return "\n".join(lines)
