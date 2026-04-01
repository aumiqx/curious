# 🧬 curious

**An AI that rewrites its own brain.**

`curious` is a self-evolving cognitive architecture. You write the seed — a simple set of learning algorithms. The AI evolves it by rewriting its own source code, testing improvements, and keeping what works.

Day 1: Your code. 18% prediction accuracy.
Day 7: The AI's code. It's rewritten itself 23 times. 71% accuracy. The algorithms look nothing like what you wrote.

**The AI wrote a better brain than you did.**

```bash
pip install curious-ai
curious init --observe ./my-project --llm openai:gpt-4o-mini
curious start
```

> Works with any LLM. Runs locally with Ollama. Self-evolves via GitHub Actions.

---

## How it works

```
You write v1 (simple, dumb seed code)
        │
        ▼
   ┌─────────┐
   │ Observe  │ ← watches your project (git, files, errors)
   └────┬─────┘
        │
   ┌────▼─────┐
   │ Predict  │ ← makes testable predictions about the system
   └────┬─────┘
        │
   ┌────▼─────┐
   │ Measure  │ ← tracks which predictions were right/wrong
   └────┬─────┘
        │
   ┌────▼─────┐
   │ Surprise │ ← learns from prediction errors
   └────┬─────┘
        │
   ┌────▼──────┐
   │ Evolve 🧬 │ ← reads its OWN code, finds weaknesses,
   │           │   rewrites itself, tests the improvement,
   │           │   keeps what works, reverts what doesn't
   └────┬──────┘
        │
        ▼
   v2, v3, v4... each version written by the AI
```

Every self-modification is a git commit. You can see exactly what the AI changed and why.

---

## Quick start

### With OpenAI ($0.10/day)

```bash
pip install curious-ai
export OPENAI_API_KEY=sk-...
curious init --observe ./my-project --llm openai:gpt-4o-mini
curious start
```

### With Ollama (free, unlimited)

```bash
ollama pull llama3
curious init --observe ./my-project --llm ollama:llama3
curious start
```

### With any OpenAI-compatible API

```bash
curious init --observe . --llm http://localhost:8080/v1:my-model
```

---

## Commands

```bash
curious init       # Initialize on a project
curious start      # Start the learning + evolution loop
curious dashboard  # See fitness scores, evolution history, predictions
curious explain    # Ask the AI to explain its own evolution
curious ask "why does the build fail on Fridays?"  # Query from understanding
```

---

## The seed (what the AI evolves)

The `curious/seed/` directory contains the cognitive architecture:

| File | Purpose | The AI evolves... |
|------|---------|-------------------|
| `world_model.py` | Stores predictions with confidence | How predictions are scored and stored |
| `learner.py` | Updates from surprise (prediction errors) | How it learns from being wrong |
| `curiosity.py` | Decides what to explore next | How it targets knowledge gaps |
| `metacognition.py` | Observes its own learning process | How it thinks about its own thinking |

The `curious/harness/` directory is untouchable — it's the evolution loop itself, the "laws of physics" the AI lives within.

---

## Self-evolution via GitHub Actions

Add your `OPENAI_API_KEY` to repository secrets. The included workflow:
- Runs every 6 hours
- Observes the repo
- Runs one evolution cycle
- Commits any self-modifications with a `🧬 evolve:` prefix
- You can watch the git log of an AI rewriting its own brain

```
🧬 evolve: Rewrote curiosity.py — weight by confidence-drop-rate instead of random
🧬 evolve: Added exponential decay to world_model.py prediction confidence
🧬 evolve: Rewrote learner.py — batch surprise analysis instead of individual
🧬 evolve: Optimized metacognition.py — track per-domain accuracy separately
```

---

## Watch it learn

```bash
curious dashboard
```

```
╭─ 🧬 curious ──────────────────────────────────╮
│ Generation: 23  |  Accuracy: 71%  |  Fitness: 0.67 │
╰────────────────────────────────────────────────╯

  Accuracy..................... ████████████████░░░░ 71%
  Learning Speed.............. ██████████████░░░░░░ 64%
  Prediction Volume........... ██████████████████░░ 90%
  Observation Coverage........ ████████████████████ 100%

  ┌─ Evolution History ─────────────────────────┐
  │ Gen 23  applied  Rewrote curiosity.py       │
  │ Gen 22  applied  Updated prediction decay   │
  │ Gen 21  reverted Learner change was worse   │
  │ Gen 20  applied  Added batch processing     │
  └─────────────────────────────────────────────┘
```

---

## Ask it anything

After a few days of learning, the AI has accumulated deep understanding:

```bash
curious ask "what patterns do you see in our codebase?"
```

It answers from **understanding**, not from a cold LLM call — because it's been observing, predicting, and learning for days.

---

## Architecture

```
curious/
├── seed/              ← THE AI EVOLVES THIS
│   ├── world_model.py
│   ├── learner.py
│   ├── curiosity.py
│   └── metacognition.py
│
├── harness/           ← UNTOUCHABLE (laws of physics)
│   ├── evolve.py      evolution loop
│   ├── fitness.py     measures performance
│   └── sandbox.py     safe execution
│
├── providers/         ← ANY LLM
│   └── base.py        OpenAI, Ollama, Groq, Together, any API
│
├── observers/         ← PLUGGABLE INPUTS
│   ├── git_observer.py
│   └── file_observer.py
│
└── cli.py
```

---

## FAQ

**Is this AGI?**
No. But it's the first step — an AI that genuinely improves its own cognitive architecture through self-experimentation. The model weights don't change. The code around the model does. And that code gets measurably better.

**Is it safe?**
The AI can only modify files in `seed/`. The harness is untouchable. Every modification is tested, and auto-reverted if fitness drops. Full git history of every change.

**How much does it cost?**
- Ollama: Free. Unlimited evolution.
- OpenAI GPT-4o-mini: ~$0.10/day for daily evolution cycles.
- The observation and fitness measurement costs nothing (no LLM calls).

**How is this different from AutoGPT / BabyAGI?**
Those are task executors — they solve a problem and stop. `curious` doesn't solve tasks. It **learns continuously** and **rewrites its own learning algorithms**. It gets smarter by existing.

**How is this different from fine-tuning?**
Fine-tuning changes model weights. `curious` changes the code architecture around the model — the prompts, the learning algorithms, the curiosity targeting, the prediction logic. The model stays the same; the cognitive architecture evolves.

---

## Contributing

`curious` is open source under MIT. We'd love contributions:

- **New observers** — error trackers, log files, API monitoring, Slack
- **New providers** — more LLM backends
- **Seed improvements** — better initial seeds for the AI to evolve from
- **Share your evolutions** — publish evolved seeds for others to fork

---

## Star History

If you think AI should learn, not just answer — star this repo.

---

<p align="center">
  Built by <a href="https://github.com/aumiqx">aumiqx</a> — making AI that thinks.
</p>
