"""curious CLI — An AI that rewrites its own brain."""

import json
import os
import sys
import time
import click
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text


console = Console()


def get_engine(observe_path: str = ".", llm: str = "openai:gpt-4o-mini"):
    from curious.engine import CuriousEngine
    return CuriousEngine(observe_path=observe_path, llm_string=llm)


@click.group()
def main():
    """🧬 curious — An AI that rewrites its own brain."""
    pass


@main.command()
@click.option("--observe", "-o", default=".", help="Path to observe")
@click.option("--llm", "-l", default="openai:gpt-4o-mini", help="LLM provider (e.g., openai:gpt-4o-mini, ollama:llama3)")
def init(observe, llm):
    """Initialize curious on a project."""
    engine = get_engine(observe, llm)
    engine.initialize()


@main.command()
@click.option("--observe", "-o", default=".", help="Path to observe")
@click.option("--llm", "-l", default="openai:gpt-4o-mini", help="LLM provider")
@click.option("--interval", "-i", default=300, help="Seconds between cycles (default: 300)")
@click.option("--evolve-every", "-e", default=5, help="Evolve every N cycles (default: 5)")
@click.option("--max-cycles", "-m", default=0, help="Max cycles (0 = infinite)")
def start(observe, llm, interval, evolve_every, max_cycles):
    """Start the learning loop."""
    engine = get_engine(observe, llm)

    console.print(f"\n[bold cyan]🧬 curious[/] — starting learning loop")
    console.print(f"  Observing: [dim]{Path(observe).resolve()}[/]")
    console.print(f"  LLM: [dim]{llm}[/]")
    console.print(f"  Interval: [dim]{interval}s[/]")
    console.print(f"  Evolution: [dim]every {evolve_every} cycles[/]")
    console.print(f"  Press Ctrl+C to stop\n")

    cycle = 0
    try:
        while True:
            cycle += 1
            if max_cycles and cycle > max_cycles:
                break

            should_evolve = (cycle % evolve_every == 0)
            evolve_marker = " [bold magenta]+ EVOLVING[/]" if should_evolve else ""

            console.print(f"[dim]━━━ Cycle {cycle}{evolve_marker} ━━━[/]")

            result = engine.run_cycle(evolve=should_evolve)

            # Print summary
            stats = result["stats"]
            fitness = result["fitness"]
            usage = result["llm_usage"]

            console.print(f"  Predictions: {stats['total_predictions']} total, {stats['pending_predictions']} pending")
            console.print(f"  Accuracy: [{'green' if stats['accuracy'] > 0.5 else 'yellow' if stats['accuracy'] > 0.3 else 'red'}]{stats['accuracy']:.0%}[/] ({stats['correct_predictions']}/{stats['resolved_predictions']})")
            console.print(f"  Fitness: [cyan]{fitness['composite']:.1%}[/]")
            console.print(f"  LLM: {usage['total_calls']} calls, ~${usage['estimated_cost_usd']:.4f}")

            # Show experiment results
            if result.get("experiments_resolved"):
                resolved = result["experiments_resolved"]
                console.print(f"  [bold]🧪 Experiments:[/] {result.get('experiments_created', 0)} created, {resolved} resolved")

            if should_evolve and "evolution" in result:
                evo = result["evolution"]
                if evo["action"] == "applied":
                    console.print(f"  [bold magenta]🧬 Evolution:[/] {evo['description']}")
                elif evo["action"] == "reverted":
                    console.print(f"  [yellow]⟲ Reverted:[/] {evo['description']}")
                elif evo["action"] == "error":
                    console.print(f"  [red]✗ Error:[/] {evo['error']}")

            console.print()

            if max_cycles and cycle >= max_cycles:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        console.print(f"\n[bold cyan]🧬 curious[/] — stopped after {cycle} cycles")
        _print_summary(engine)


@main.command()
@click.option("--observe", "-o", default=".", help="Path to observe")
@click.option("--llm", "-l", default="openai:gpt-4o-mini", help="LLM provider")
def dashboard(observe, llm):
    """Show current status dashboard."""
    engine = get_engine(observe, llm)
    status = engine.get_status()
    _print_dashboard(status)


@main.command()
@click.option("--observe", "-o", default=".", help="Path to observe")
@click.option("--llm", "-l", default="openai:gpt-4o-mini", help="LLM provider")
def explain(observe, llm):
    """Ask the AI to explain its own evolution."""
    engine = get_engine(observe, llm)
    status = engine.get_status()

    history = status["evolution_history"]
    if not history:
        console.print("[yellow]No evolution history yet. Run [bold]curious start[/] first.[/]")
        return

    seed_files = status["seed_files"]
    history_text = "\n".join(
        f"Gen {h['generation']}: {h['description']} ({'kept' if h.get('kept') else 'reverted'})"
        for h in history[-20:]
    )

    prompt = f"""You are a self-evolving AI system. Explain your own evolution history.

## Evolution History
{history_text}

## Current Cognitive Architecture
"""
    for name, code in seed_files.items():
        prompt += f"\n### {name}\n```python\n{code}\n```\n"

    prompt += """
## Your Task
Explain in plain English:
1. What key changes did you make to yourself and WHY?
2. Which changes had the biggest impact?
3. What did you learn about your own learning process?
4. What would you change next?

Be specific. Reference actual code changes."""

    console.print("\n[bold cyan]🧬 curious[/] — self-reflection\n")

    response = engine.llm.ask(prompt, system="You are a self-aware AI explaining your own cognitive evolution. Be specific and insightful.")
    console.print(Panel(response, title="[bold]Self-Reflection[/]", border_style="cyan"))


@main.command()
@click.option("--observe", "-o", default=".", help="Path to observe")
@click.option("--llm", "-l", default="openai:gpt-4o-mini", help="LLM provider")
@click.argument("question")
def ask(observe, llm, question):
    """Ask the AI a question — answers from accumulated understanding."""
    engine = get_engine(observe, llm)

    observations = engine.world_model.get_recent_observations(limit=50)
    stats = engine.world_model.get_stats()
    predictions = engine.world_model.get_pending_predictions()

    obs_text = "\n".join(f"[{o['source']}] {o['content']}" for o in observations)
    pred_text = "\n".join(f"- {p.statement} (confidence: {p.confidence:.0%})" for p in predictions[:10])

    prompt = f"""You are a learning system that has been observing a software project.

## What You've Observed ({stats['total_observations']} observations)
{obs_text}

## Your Current Predictions
{pred_text}

## Your Track Record
Accuracy: {stats['accuracy']:.0%} ({stats['correct_predictions']}/{stats['resolved_predictions']} correct)

## Question
{question}

Answer based on your accumulated understanding. Be honest about what you know vs. what you're uncertain about."""

    response = engine.llm.ask(prompt, system="You are a knowledgeable system that has been deeply observing a software project. Answer from understanding, not guessing.")
    console.print(f"\n{response}\n")


def _print_summary(engine):
    """Print final summary."""
    status = engine.get_status()
    stats = status["stats"]
    fitness = status["fitness"]
    usage = status["llm_usage"]

    console.print(f"\n  [bold]Summary:[/]")
    console.print(f"  Predictions: {stats['total_predictions']} made, {stats['accuracy']:.0%} accurate")
    console.print(f"  Observations: {stats['total_observations']}")
    console.print(f"  Generation: {status['generation']}")
    console.print(f"  Fitness: {fitness['composite']:.1%}")
    console.print(f"  LLM cost: ~${usage['estimated_cost_usd']:.4f}\n")


def _print_dashboard(status):
    """Print the dashboard."""
    stats = status["stats"]
    fitness = status["fitness"]

    console.print()
    console.print(Panel(
        f"[bold]Generation:[/] {status['generation']}  |  "
        f"[bold]Cycles:[/] {status['cycle_count']}  |  "
        f"[bold]Predictions:[/] {stats['total_predictions']}  |  "
        f"[bold]Accuracy:[/] {stats['accuracy']:.0%}",
        title="[bold cyan]🧬 curious[/]",
        border_style="cyan",
    ))

    # Fitness
    from curious.harness.fitness import format_fitness
    console.print(Panel(format_fitness(fitness), title="Fitness", border_style="green"))

    # Evolution history
    history = status["evolution_history"]
    if history:
        table = Table(title="Evolution History (last 10)")
        table.add_column("Gen", style="cyan")
        table.add_column("Action", style="green")
        table.add_column("Description")

        for h in history[-10:]:
            action_style = "green" if h.get("kept") else "red"
            table.add_row(
                str(h["generation"]),
                f"[{action_style}]{h['action']}[/]",
                h.get("description", "")[:80],
            )
        console.print(table)

    console.print()


if __name__ == "__main__":
    main()
