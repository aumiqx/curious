"""
Metacognition — Observes the learning process itself.

THIS FILE IS EVOLVED BY THE AI.
"""

from curious.seed.world_model import WorldModel


def assess_learning_quality(world_model: WorldModel) -> dict:
    """
    Evaluate how well the system is learning.
    Not about the domain — about the PROCESS of learning.
    """
    stats = world_model.get_stats()
    accuracy_all = world_model.get_accuracy()
    accuracy_recent = world_model.get_accuracy(window_days=1)

    assessment = {
        "total_experience": stats["total_predictions"],
        "overall_accuracy": accuracy_all["accuracy"],
        "recent_accuracy": accuracy_recent["accuracy"],
        "learning_trend": "unknown",
        "diagnosis": [],
    }

    # Is accuracy improving over time?
    if accuracy_all["total"] > 5 and accuracy_recent["total"] > 2:
        if accuracy_recent["accuracy"] > accuracy_all["accuracy"] + 0.05:
            assessment["learning_trend"] = "improving"
        elif accuracy_recent["accuracy"] < accuracy_all["accuracy"] - 0.05:
            assessment["learning_trend"] = "declining"
            assessment["diagnosis"].append(
                "Recent accuracy is WORSE than overall. The learning strategy may be degrading."
            )
        else:
            assessment["learning_trend"] = "stable"

    # Are we making enough predictions?
    if stats["pending_predictions"] == 0 and stats["total_predictions"] < 10:
        assessment["diagnosis"].append(
            "Not enough predictions being generated. Curiosity may be too conservative."
        )

    # Are predictions too confident or too uncertain?
    if accuracy_all["total"] > 10 and accuracy_all["accuracy"] < 0.3:
        assessment["diagnosis"].append(
            "Accuracy is very low. Predictions may be overconfident or based on wrong patterns."
        )

    if not assessment["diagnosis"]:
        assessment["diagnosis"].append("Learning process appears healthy.")

    return assessment


def get_metacognition_prompt(assessment: dict, seed_files: dict[str, str]) -> str:
    """
    Build a prompt for the AI to reflect on its own cognitive architecture.
    seed_files = {"world_model.py": "..source..", "learner.py": "..source..", ...}
    """
    diag_text = "\n".join(f"- {d}" for d in assessment["diagnosis"])

    files_text = ""
    for name, source in seed_files.items():
        files_text += f"\n### {name}\n```python\n{source}\n```\n"

    return f"""You are a metacognitive system — you observe HOW you learn, not WHAT you learn.

## Learning Assessment
- Total predictions made: {assessment['total_experience']}
- Overall accuracy: {assessment['overall_accuracy']:.1%}
- Recent accuracy (24h): {assessment['recent_accuracy']:.1%}
- Trend: {assessment['learning_trend']}
- Diagnosis:
{diag_text}

## Your Cognitive Architecture (YOUR OWN SOURCE CODE)
{files_text}

## Your Task
Analyze your own cognitive architecture. Consider:

1. **What's working?** Which parts of the code are contributing to good predictions?
2. **What's weak?** Which algorithms or heuristics are too simple, too rigid, or wrong?
3. **What would you change?** If you could rewrite ONE file to improve your learning, which file and what change?
4. **What's missing?** Is there a capability your architecture lacks entirely?

Be specific. Reference actual functions and logic in the code.

Respond in JSON:
```json
{{
  "working_well": ["specific thing 1", "specific thing 2"],
  "weaknesses": ["specific weakness 1", "specific weakness 2"],
  "proposed_change": {{
    "file": "filename.py",
    "description": "what to change and why",
    "expected_improvement": "what this should improve",
    "confidence": 0.7
  }},
  "missing_capabilities": ["thing 1"]
}}
```"""
