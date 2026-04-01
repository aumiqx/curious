# 🧬 curious

**An AI that rewrites its own brain — and creates things that have never existed.**

`curious` is a self-evolving cognitive architecture. It rewrites its own source code to get smarter. And every day, it creates something completely unique — scored on novelty, learning from feedback, pushing toward things no human or AI has ever built.

**This is a live experiment. Watch it evolve.**

```
Day 1: Created "Fluctuverse" — uniqueness 47/100 (too conventional)
Day 2: Created "Quintessension" — uniqueness 71/100 (invented its own language)
Day 3: ???
```

> The `creations/` directory fills up daily. Each creation is scored. The AI reads the scores, learns what "unique" means, and pushes further. The git log is the experiment.

---

## The Experiment

We gave an AI three things:
1. **Its own source code** (readable, modifiable)
2. **A uniqueness score** (0-100, measures novelty)
3. **One rule:** create something that has never existed before

Then we pressed start and walked away.

### What happens

**Every 6 hours — Self-Evolution:**
The AI reads its own cognitive architecture, finds weaknesses, rewrites the code, tests if the change improved performance. Keeps what works. Reverts what doesn't. Every modification is a git commit.

**Every day — Creation:**
The AI creates a completely new artifact. Not a todo app. Not a chatbot. Something that doesn't fit any existing category. It's scored on uniqueness. The score feeds back into the next creation. The creations get weirder and more novel over time.

**The question:** Can a self-evolving AI produce genuinely creative artifacts that no human designed? Can novelty be optimized the way accuracy can?

### Track the experiment

- **[`creations/`](./creations/)** — Every artifact the AI has ever created, with uniqueness scores
- **[`curious/seed/`](./curious/seed/)** — The AI's brain. Watch the diffs — it rewrites itself.
- **Git log** — `🧬 evolve:` = self-modification. `🎨 create:` = new creation.

---

## What's inside

### The Brain (self-evolving)

```
curious/seed/           ← THE AI REWRITES THIS
├── world_model.py      prediction engine
├── learner.py          learns from surprise
├── curiosity.py        finds knowledge gaps
├── metacognition.py    observes its own learning
├── experimenter.py     generates its own experiments
└── creator.py          creates unique artifacts
```

Every file above is **evolvable** — the AI reads it, analyzes weaknesses, and rewrites it. The `curious/harness/` directory contains the evolution loop itself — the untouchable "laws of physics."

### The Creations

```
creations/
├── day_001/            ← First creation
│   ├── fluctuverse.py  the artifact
│   ├── meta.json       what it is
│   ├── scores.json     uniqueness breakdown
│   └── README.md       the AI's explanation
├── day_002/            ← Second creation (scored higher)
│   ├── quintessension.py
│   └── ...
└── history.jsonl       full creation log
```

Each creation is:
- A **working artifact** (real code, not just an idea)
- Scored on **4 dimensions** of uniqueness (concept, implementation, structure, naming)
- Fed back into the next cycle (the AI learns what "unique" means)

---

## Run it yourself

### Watch the AI create

```bash
pip install curious-ai
export OPENAI_API_KEY=sk-...
curious create --llm openai:gpt-4o-mini
```

### Watch the AI learn and evolve

```bash
curious init --observe ./any-project --llm openai:gpt-4o-mini
curious start
```

### See what it's built

```bash
curious gallery
```

### Ask it to explain its own evolution

```bash
curious explain
```

### Works with any LLM

```bash
curious create --llm ollama:llama3      # free, local
curious create --llm openai:gpt-4o     # strongest
curious create --llm groq:llama-3.1-70b # fast
```

---

## How it works

```
┌─────────────────────────────────────────────┐
│                CURIOUS ENGINE                │
│                                              │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Observe │ → │ Predict  │ → │ Surprise │ │
│  └─────────┘   └──────────┘   └──────────┘ │
│       ↑                             │        │
│       │         ┌──────────┐        │        │
│       └─────────│  Learn   │←───────┘        │
│                 └──────────┘                 │
│                      │                       │
│                 ┌──────────┐                 │
│                 │ Evolve 🧬│ ← reads own     │
│                 │          │   code, rewrites│
│                 └──────────┘   it, tests it  │
│                      │                       │
│                 ┌──────────┐                 │
│                 │ Create 🎨│ ← builds        │
│                 │          │   something     │
│                 └──────────┘   unique daily  │
│                      │                       │
│                 ┌──────────┐                 │
│                 │ Score    │ ← uniqueness    │
│                 │          │   measured      │
│                 └──────────┘                 │
│                      │                       │
│                      ↓                       │
│              FEEDBACK → NEXT CYCLE           │
└─────────────────────────────────────────────┘
```

---

## GitHub Actions (runs automatically)

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| 🧬 Self-Evolution | Every 6 hours | Observes, predicts, evolves its own code |
| 🎨 Daily Creation | Every day midnight | Creates something unique, scores it, commits |

The repo evolves on its own. Star it and check back in a week.

---

## Uniqueness Scoring

Every creation is scored on 4 dimensions:

| Dimension | Max | What it measures |
|-----------|-----|-----------------|
| Concept | 30 | Has this idea existed before? |
| Implementation | 30 | Is the approach novel? |
| Structure | 20 | Did it invent its own paradigm? |
| Naming | 20 | Did it create its own vocabulary? |

**Total: 0-100.** The AI sees its score and optimizes for higher novelty.

```
Day 1: ██████████░░░░░░░░░░ 47/100 — used conventional frameworks
Day 2: ██████████████░░░░░░ 71/100 — invented its own language
Day 3: ?
```

---

## FAQ

**What is this?**
An experiment. Can a self-evolving AI be genuinely creative? We gave it a uniqueness score and told it to maximize novelty. The `creations/` directory is the result.

**Is this AGI?**
No. But it's probing the boundary. If the AI produces artifacts that are genuinely novel — things no human designed or imagined — that tells us something about machine creativity.

**Can I run it?**
Yes. `pip install curious-ai`, add your API key, run `curious create`. It works with OpenAI, Ollama, Groq, or any OpenAI-compatible API.

**What will it create?**
We don't know. That's the point. It might invent a programming language. It might create a new kind of UI. It might build something we don't have a word for yet. The constraint is: it must be unique.

**How much does it cost?**
- Creation: ~$0.02/day (GPT-4o-mini) or ~$0.15/day (GPT-4o)
- Evolution: ~$0.01/cycle
- Ollama: Free

---

## Star this repo

This is a live experiment in machine creativity and self-evolution. The AI creates something new every day. Star it and watch what happens.

---

<p align="center">
  Built by <a href="https://github.com/aumiqx">aumiqx</a><br>
  <em>An experiment in artificial creativity.</em>
</p>
