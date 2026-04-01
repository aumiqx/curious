"""
Engine — The main loop that ties observation, prediction, learning, and evolution together.
"""

import json
import os
import time
import uuid
from pathlib import Path

from curious.providers.base import LLMProvider, create_provider
from curious.seed.world_model import WorldModel, Prediction
from curious.seed.learner import extract_lesson, get_learning_prompt, compute_surprise
from curious.seed.curiosity import find_knowledge_frontier, get_exploration_prompt
from curious.harness.fitness import measure_fitness, format_fitness
from curious.harness.evolve import run_evolution_cycle, get_evolution_history, read_seed_files
from curious.observers.git_observer import GitObserver
from curious.observers.file_observer import FileObserver


class CuriousEngine:
    def __init__(
        self,
        observe_path: str,
        llm_string: str = "openai:gpt-4o-mini",
        data_dir: str | None = None,
    ):
        self.observe_path = Path(observe_path).resolve()
        self.data_dir = Path(data_dir or os.path.join(self.observe_path, ".curious"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Evolution directory
        self.evolution_dir = self.data_dir / "evolution"
        self.evolution_dir.mkdir(exist_ok=True)

        # LLM
        self.llm = create_provider(llm_string)

        # World model
        db_path = str(self.data_dir / "brain.db")
        self.world_model = WorldModel(db_path)

        # Observers
        self.observers = []
        if (self.observe_path / ".git").exists():
            self.observers.append(GitObserver(str(self.observe_path)))
        self.observers.append(FileObserver(str(self.observe_path)))

        # State
        self.generation = self._load_generation()
        self.cycle_count = 0

    def _load_generation(self) -> int:
        history = get_evolution_history(self.evolution_dir)
        return len(history)

    def initialize(self):
        """Run initial observation to bootstrap the world model."""
        from rich.console import Console
        console = Console()

        console.print("\n[bold cyan]🧬 curious[/] — initializing...\n")

        # Collect initial observations
        all_obs = []
        for observer in self.observers:
            obs = observer.get_initial_context()
            all_obs.extend(obs)

        for obs in all_obs:
            self.world_model.add_observation(obs["source"], obs["content"])

        console.print(f"  Collected [bold]{len(all_obs)}[/] initial observations")
        console.print(f"  Data stored in [dim]{self.data_dir}[/]")

        # Make initial predictions
        console.print("  Making initial predictions...\n")
        self._make_predictions()

        stats = self.world_model.get_stats()
        console.print(f"  [green]✓[/] {stats['total_predictions']} predictions generated")
        console.print(f"  [green]✓[/] {stats['total_observations']} observations stored")
        console.print(f"\n  Ready. Run [bold]curious start[/] to begin learning.\n")

    def _make_predictions(self):
        """Use LLM to generate predictions based on current observations."""
        observations = self.world_model.get_recent_observations(limit=30)
        accuracy = self.world_model.get_accuracy()

        # Gather lessons from recently resolved predictions
        lessons = []
        expired = self.world_model.get_expired_predictions()
        for pred in expired[:10]:
            # Auto-resolve expired predictions as incorrect (simple heuristic)
            # In a real system, the resolution would be smarter
            self.world_model.resolve_prediction(pred.id, was_correct=False)
            lesson = extract_lesson(pred, False, observations)
            lessons.append(lesson)

        prompt = get_learning_prompt(lessons, accuracy, observations)

        try:
            predictions_data = self.llm.ask_json(prompt)
            if isinstance(predictions_data, list):
                for p in predictions_data[:5]:
                    pred = Prediction(
                        id=str(uuid.uuid4())[:8],
                        statement=p.get("statement", ""),
                        confidence=float(p.get("confidence", 0.5)),
                        evidence=p.get("evidence", []),
                        created_at=time.time(),
                        deadline=time.time() + (float(p.get("deadline_hours", 24)) * 3600),
                    )
                    self.world_model.add_prediction(pred)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            pass  # LLM returned invalid JSON — skip this cycle

    def _explore(self):
        """Use curiosity to explore knowledge frontiers."""
        observations = self.world_model.get_recent_observations(limit=20)
        frontiers = find_knowledge_frontier(self.world_model)

        if not frontiers:
            return

        prompt = get_exploration_prompt(frontiers, observations)

        try:
            result = self.llm.ask_json(prompt)
            # Store the analysis as an observation
            analysis = result.get("analysis", "")
            if analysis:
                self.world_model.add_observation("curiosity", analysis)

            # Add exploration predictions
            for p in result.get("predictions", [])[:3]:
                pred = Prediction(
                    id=str(uuid.uuid4())[:8],
                    statement=p.get("statement", ""),
                    confidence=float(p.get("confidence", 0.5)),
                    evidence=p.get("evidence", []),
                    created_at=time.time(),
                    deadline=time.time() + (float(p.get("deadline_hours", 24)) * 3600),
                )
                self.world_model.add_prediction(pred)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    def _observe(self):
        """Poll all observers for new data."""
        for observer in self.observers:
            new_obs = observer.poll()
            for obs in new_obs:
                self.world_model.add_observation(obs["source"], obs["content"])

    def _resolve_predictions(self):
        """Check expired predictions and resolve them."""
        expired = self.world_model.get_expired_predictions()
        if not expired:
            return

        observations = self.world_model.get_recent_observations(limit=30)
        obs_text = "\n".join(f"[{o['source']}] {o['content']}" for o in observations[:20])

        for pred in expired[:5]:
            prompt = f"""Given these recent observations about a software project:

{obs_text}

This prediction was made earlier:
"{pred.statement}"
(confidence: {pred.confidence:.0%}, deadline has passed)

Based on the observations, was this prediction CORRECT or INCORRECT?
Consider partial correctness. Be fair but strict.

Respond in JSON:
```json
{{"correct": true/false, "reasoning": "brief explanation"}}
```"""

            try:
                result = self.llm.ask_json(prompt)
                was_correct = bool(result.get("correct", False))
                self.world_model.resolve_prediction(pred.id, was_correct)
            except (json.JSONDecodeError, KeyError, TypeError):
                self.world_model.resolve_prediction(pred.id, was_correct=False)

    def run_cycle(self, evolve: bool = False) -> dict:
        """Run one full cycle: observe → resolve → learn → predict → (evolve)."""
        self.cycle_count += 1
        cycle_result = {"cycle": self.cycle_count, "actions": []}

        # 1. Observe
        self._observe()
        cycle_result["actions"].append("observed")

        # 2. Resolve expired predictions
        self._resolve_predictions()
        cycle_result["actions"].append("resolved_predictions")

        # 3. Make new predictions (learning from resolved ones)
        self._make_predictions()
        cycle_result["actions"].append("made_predictions")

        # 4. Explore knowledge frontiers
        self._explore()
        cycle_result["actions"].append("explored_frontiers")

        # 5. Optionally evolve
        if evolve:
            self.generation += 1
            evo_result = run_evolution_cycle(
                self.llm, self.world_model, self.evolution_dir, self.generation
            )
            cycle_result["evolution"] = evo_result
            cycle_result["actions"].append(f"evolved: {evo_result['action']}")

        # Fitness
        cycle_result["fitness"] = measure_fitness(self.world_model)
        cycle_result["stats"] = self.world_model.get_stats()
        cycle_result["llm_usage"] = self.llm.get_usage()

        return cycle_result

    def get_status(self) -> dict:
        """Get current status of the engine."""
        return {
            "fitness": measure_fitness(self.world_model),
            "stats": self.world_model.get_stats(),
            "generation": self.generation,
            "cycle_count": self.cycle_count,
            "evolution_history": get_evolution_history(self.evolution_dir),
            "seed_files": read_seed_files(),
            "llm_usage": self.llm.get_usage(),
        }
