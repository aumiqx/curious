"""
Learner — Updates the world model from surprise (prediction errors).

THIS FILE IS EVOLVED BY THE AI.
"""

from curious.seed.world_model import WorldModel, Prediction


def compute_surprise(prediction: Prediction, was_correct: bool) -> float:
    """
    Surprise = how unexpected the outcome was.
    High confidence + wrong = high surprise (learn a lot)
    Low confidence + wrong = low surprise (expected uncertainty)
    High confidence + correct = low surprise (confirmed)
    Low confidence + correct = medium surprise (lucky or emerging pattern)
    """
    if was_correct:
        return 1.0 - prediction.confidence  # surprised it was right
    else:
        return prediction.confidence  # surprised it was wrong


def extract_lesson(prediction: Prediction, was_correct: bool, observations: list[dict]) -> str:
    """
    Generate a plain-text lesson from a resolved prediction.
    This is fed to the LLM to update understanding.
    """
    surprise = compute_surprise(prediction, was_correct)
    outcome = "CORRECT" if was_correct else "WRONG"

    lesson = f"Prediction: {prediction.statement}\n"
    lesson += f"Confidence: {prediction.confidence:.0%}\n"
    lesson += f"Outcome: {outcome}\n"
    lesson += f"Surprise level: {surprise:.2f}\n"
    lesson += f"Evidence used: {', '.join(prediction.evidence)}\n"

    if surprise > 0.5:
        lesson += "HIGH SURPRISE — This reveals a gap in understanding. "
        if was_correct:
            lesson += "The prediction succeeded despite low confidence. There may be a pattern not yet captured."
        else:
            lesson += "The prediction failed despite high confidence. The underlying model is wrong about something."

    return lesson


def get_learning_prompt(
    lessons: list[str],
    current_accuracy: dict,
    observations: list[dict],
) -> str:
    """
    Build a prompt for the LLM to generate new predictions
    based on what was learned from recent surprises.
    """
    obs_text = "\n".join(
        f"[{o['source']}] {o['content']}" for o in observations[:30]
    )

    lessons_text = "\n---\n".join(lessons) if lessons else "No recent lessons."

    return f"""You are a learning system observing a software project.

## Recent Observations
{obs_text}

## Lessons from Recent Predictions
{lessons_text}

## Current Accuracy
Total resolved: {current_accuracy['total']}
Correct: {current_accuracy['correct']}
Accuracy: {current_accuracy['accuracy']:.1%}

## Your Task
Based on what you've observed and learned, make 5 NEW predictions about this system.

For each prediction:
1. State what you predict will happen (be specific and testable)
2. Set a deadline (1h, 6h, 24h, or 72h from now)
3. Rate your confidence (0.0 to 1.0)
4. List the evidence that supports this prediction

Focus on predictions where you're UNCERTAIN — that's where learning happens fastest.

Respond in this exact JSON format:
```json
[
  {{
    "statement": "specific prediction",
    "confidence": 0.5,
    "deadline_hours": 24,
    "evidence": ["observation 1", "observation 2"]
  }}
]
```"""
