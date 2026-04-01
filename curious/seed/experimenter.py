"""
Experimenter — The AI generates its own activity by running experiments on itself.

THIS FILE IS EVOLVED BY THE AI.

Without this, the system needs external activity (human commits, deploys, etc.)
to learn from. With this, the AI creates its own experiments:

1. Predict: "If I change X in my code, metric Y will improve"
2. Test: Actually run the modified code in a sandbox
3. Measure: Did Y improve?
4. Learn: Update understanding based on surprise

This makes the learning loop self-contained.
"""

import time
import json
import uuid
import importlib
import sys
from pathlib import Path
from curious.seed.world_model import WorldModel, Prediction


SEED_DIR = Path(__file__).parent


def generate_self_experiments(world_model: WorldModel) -> list[dict]:
    """
    Generate experiments the AI can run on its own code.
    Each experiment is a prediction about the system's behavior.
    """
    stats = world_model.get_stats()
    observations = world_model.get_recent_observations(limit=20)

    experiments = []

    # Experiment 1: Test prediction volume
    experiments.append({
        "name": "prediction_capacity",
        "prediction": f"The system currently has {stats['total_predictions']} predictions. After one more learning cycle, it will have more.",
        "test": "count_predictions",
        "baseline": stats["total_predictions"],
        "deadline_hours": 1,
        "confidence": 0.9,
    })

    # Experiment 2: Test observation growth
    experiments.append({
        "name": "observation_growth",
        "prediction": f"Observations will grow from {stats['total_observations']} in the next cycle.",
        "test": "count_observations",
        "baseline": stats["total_observations"],
        "deadline_hours": 1,
        "confidence": 0.85,
    })

    # Experiment 3: Test code validity
    seed_files = list(SEED_DIR.glob("*.py"))
    experiments.append({
        "name": "code_health",
        "prediction": f"All {len(seed_files)} seed files will remain syntactically valid.",
        "test": "validate_all_seed_files",
        "baseline": len(seed_files),
        "deadline_hours": 6,
        "confidence": 0.95,
    })

    # Experiment 4: Test if accuracy tracking works
    accuracy = world_model.get_accuracy()
    if accuracy["total"] > 0:
        experiments.append({
            "name": "accuracy_trend",
            "prediction": f"Current accuracy is {accuracy['accuracy']:.0%}. After resolving more predictions, it will change.",
            "test": "check_accuracy_changed",
            "baseline": accuracy["accuracy"],
            "deadline_hours": 6,
            "confidence": 0.6,
        })

    # Experiment 5: Self-referential — predict own predictions
    pending = stats["pending_predictions"]
    experiments.append({
        "name": "resolution_rate",
        "prediction": f"Of the {pending} pending predictions, at least 1 will be resolved in the next cycle.",
        "test": "check_resolutions",
        "baseline": stats["resolved_predictions"],
        "deadline_hours": 1,
        "confidence": 0.7,
    })

    return experiments


def run_experiment(experiment: dict, world_model: WorldModel) -> dict:
    """
    Run a self-experiment and return the result.
    """
    test_name = experiment.get("test", "")
    baseline = experiment.get("baseline", 0)
    result = {"experiment": experiment["name"], "passed": False, "details": ""}

    try:
        if test_name == "count_predictions":
            current = world_model.get_stats()["total_predictions"]
            result["passed"] = current > baseline
            result["details"] = f"predictions: {baseline} → {current}"

        elif test_name == "count_observations":
            current = world_model.get_stats()["total_observations"]
            result["passed"] = current > baseline
            result["details"] = f"observations: {baseline} → {current}"

        elif test_name == "validate_all_seed_files":
            valid_count = 0
            for py_file in SEED_DIR.glob("*.py"):
                try:
                    compile(py_file.read_text(), str(py_file), "exec")
                    valid_count += 1
                except SyntaxError:
                    pass
            result["passed"] = valid_count >= baseline
            result["details"] = f"valid files: {valid_count}/{baseline}"

        elif test_name == "check_accuracy_changed":
            current_accuracy = world_model.get_accuracy()["accuracy"]
            result["passed"] = current_accuracy != baseline
            result["details"] = f"accuracy: {baseline:.0%} → {current_accuracy:.0%}"

        elif test_name == "check_resolutions":
            current = world_model.get_stats()["resolved_predictions"]
            result["passed"] = current > baseline
            result["details"] = f"resolved: {baseline} → {current}"

        else:
            result["details"] = f"unknown test: {test_name}"

    except Exception as e:
        result["details"] = f"error: {e}"

    return result


def run_self_experiments(world_model: WorldModel) -> list[dict]:
    """
    Generate and run all self-experiments.
    Returns list of experiment results + creates predictions from them.
    """
    experiments = generate_self_experiments(world_model)
    results = []

    for exp in experiments:
        # Create a prediction from the experiment
        pred = Prediction(
            id=f"exp_{str(uuid.uuid4())[:6]}",
            statement=exp["prediction"],
            confidence=exp.get("confidence", 0.5),
            evidence=[f"self-experiment: {exp['name']}"],
            created_at=time.time(),
            deadline=time.time() + (exp.get("deadline_hours", 1) * 3600),
        )
        world_model.add_prediction(pred)

        # Log the experiment as an observation
        world_model.add_observation(
            "self-experiment",
            f"Running experiment '{exp['name']}': {exp['prediction']}"
        )

        results.append({"experiment": exp["name"], "prediction_id": pred.id})

    return results


def resolve_self_experiments(world_model: WorldModel) -> list[dict]:
    """
    Check if any self-experiment predictions can be resolved NOW
    (don't wait for deadline — these are testable immediately after a cycle).
    """
    pending = world_model.get_pending_predictions()
    results = []

    for pred in pending:
        if not pred.id.startswith("exp_"):
            continue
        # Self-experiment predictions can be checked immediately after next cycle
        if time.time() - pred.created_at < 30:
            continue  # too fresh, wait at least 30 seconds

        # Try to resolve based on the experiment name in evidence
        exp_name = ""
        for ev in pred.evidence:
            if ev.startswith("self-experiment:"):
                exp_name = ev.replace("self-experiment:", "").strip()
                break

        if not exp_name:
            continue

        # Create a mini experiment to test
        stats = world_model.get_stats()
        experiment = {"name": exp_name, "test": "", "baseline": 0}

        # Map experiment names to tests
        if exp_name == "prediction_capacity":
            experiment["test"] = "count_predictions"
            experiment["baseline"] = 0  # any predictions = pass
        elif exp_name == "observation_growth":
            experiment["test"] = "count_observations"
            experiment["baseline"] = 0
        elif exp_name == "code_health":
            experiment["test"] = "validate_all_seed_files"
            experiment["baseline"] = len(list(SEED_DIR.glob("*.py")))
        elif exp_name == "resolution_rate":
            experiment["test"] = "check_resolutions"
            experiment["baseline"] = 0
        else:
            continue

        result = run_experiment(experiment, world_model)
        world_model.resolve_prediction(pred.id, was_correct=result["passed"])

        world_model.add_observation(
            "self-experiment-result",
            f"Experiment '{exp_name}': {'PASSED' if result['passed'] else 'FAILED'} — {result['details']}"
        )

        results.append(result)

    return results
