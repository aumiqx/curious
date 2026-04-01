"""
Curiosity — Decides what to explore next based on knowledge gaps.

THIS FILE IS EVOLVED BY THE AI.
"""

from curious.seed.world_model import WorldModel


def find_knowledge_frontier(world_model: WorldModel) -> list[dict]:
    """
    Identify areas where understanding is weakest.
    These are the frontiers where curiosity should pull.
    """
    observations = world_model.get_recent_observations(limit=100)
    stats = world_model.get_stats()
    accuracy = world_model.get_accuracy()

    # Gather sources and their observation counts
    source_counts: dict[str, int] = {}
    for obs in observations:
        src = obs["source"]
        source_counts[src] = source_counts.get(src, 0) + 1

    frontiers = []

    # Frontier 1: Under-observed areas
    all_sources = set(source_counts.keys())
    for src in all_sources:
        if source_counts[src] < 5:
            frontiers.append({
                "area": src,
                "reason": f"Only {source_counts[src]} observations — barely explored",
                "priority": 0.8,
            })

    # Frontier 2: Areas with high prediction failure rate
    # (This is a simple heuristic — the AI should evolve this)
    if accuracy["total"] > 0 and accuracy["accuracy"] < 0.5:
        frontiers.append({
            "area": "prediction_model",
            "reason": f"Overall accuracy is {accuracy['accuracy']:.0%} — the prediction model itself needs improvement",
            "priority": 0.9,
        })

    # Frontier 3: If no predictions exist yet, everything is frontier
    if stats["total_predictions"] == 0:
        frontiers.append({
            "area": "everything",
            "reason": "No predictions made yet — need to start building understanding",
            "priority": 1.0,
        })

    # Sort by priority (highest first)
    frontiers.sort(key=lambda f: f["priority"], reverse=True)
    return frontiers


def get_exploration_prompt(frontiers: list[dict], observations: list[dict]) -> str:
    """
    Build a prompt for the LLM to explore knowledge gaps.
    """
    frontier_text = "\n".join(
        f"- {f['area']}: {f['reason']} (priority: {f['priority']:.1f})"
        for f in frontiers[:5]
    )

    obs_text = "\n".join(
        f"[{o['source']}] {o['content']}" for o in observations[:20]
    )

    return f"""You are a curiosity-driven learning system.

## Knowledge Frontiers (what you DON'T understand well)
{frontier_text}

## Recent Observations
{obs_text}

## Your Task
Pick the highest-priority frontier and explore it. Ask yourself:
1. What patterns do I see in the observations related to this area?
2. What would I EXPECT to see if I understood this area well?
3. What predictions can I make to TEST my understanding?
4. What am I most uncertain about?

Respond with:
- A brief analysis of what you notice (2-3 sentences)
- 3 specific predictions to test your understanding of this frontier area

JSON format:
```json
{{
  "analysis": "what you noticed",
  "frontier_explored": "which frontier",
  "predictions": [
    {{
      "statement": "specific testable prediction",
      "confidence": 0.5,
      "deadline_hours": 24,
      "evidence": ["reason 1"]
    }}
  ]
}}
```"""
