"""
Fitness — Measures how well the cognitive architecture is performing.

THIS FILE IS PART OF THE HARNESS — NOT EVOLVED BY THE AI.
"""

from curious.seed.world_model import WorldModel


def measure_fitness(world_model: WorldModel) -> dict:
    """
    Compute a single fitness score and its components.
    Higher is better. Range 0.0 to 1.0.
    """
    stats = world_model.get_stats()
    accuracy_all = world_model.get_accuracy()
    accuracy_recent = world_model.get_accuracy(window_days=1)

    components = {}

    # Component 1: Prediction accuracy (0-1)
    components["accuracy"] = accuracy_all["accuracy"] if accuracy_all["total"] > 0 else 0.0

    # Component 2: Learning speed — is recent accuracy improving?
    if accuracy_recent["total"] >= 3 and accuracy_all["total"] >= 5:
        improvement = accuracy_recent["accuracy"] - accuracy_all["accuracy"]
        components["learning_speed"] = max(0.0, min(1.0, 0.5 + improvement))
    else:
        components["learning_speed"] = 0.5  # neutral when insufficient data

    # Component 3: Prediction volume — are we making enough predictions?
    target_predictions = 20
    volume_ratio = min(1.0, stats["total_predictions"] / target_predictions)
    components["prediction_volume"] = volume_ratio

    # Component 4: Observation coverage
    target_observations = 50
    coverage = min(1.0, stats["total_observations"] / target_observations)
    components["observation_coverage"] = coverage

    # Weighted composite score
    weights = {
        "accuracy": 0.4,
        "learning_speed": 0.3,
        "prediction_volume": 0.15,
        "observation_coverage": 0.15,
    }

    fitness = sum(components[k] * weights[k] for k in weights)
    components["composite"] = fitness

    return components


def fitness_improved(before: dict, after: dict) -> bool:
    """Check if fitness improved after a modification."""
    return after.get("composite", 0) > before.get("composite", 0)


def format_fitness(components: dict) -> str:
    """Pretty-print fitness scores."""
    lines = []
    for key, value in components.items():
        bar_len = int(value * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        label = key.replace("_", " ").title()
        lines.append(f"  {label:.<25} {bar} {value:.1%}")
    return "\n".join(lines)
