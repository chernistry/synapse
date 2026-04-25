# Synapse, nine months later — April 2026 retrospective

*Alex Chernysh — 2026-04-25*

> A retrospective written nine months after the original paper. The unchanged
> 2025 paper is served at <https://chernistry.github.io/synapse/>; `root/paper.md`
> is a 2026 copy-edited reading version of the same text.

---

## What the paper proposed

Synapse (mid-2025) proposed an autonomous AI agent that would orchestrate the
full software-engineering loop — code generation, testing, refinement — and,
critically, choose its *own* success criteria each iteration via a mix of MCDM
methods (SMART, TOPSIS, BWM) and a reinforcement-learning policy layer. The
idea was validated on a deliberately tiny synthetic experiment: a single drone,
a 2D map, two scenarios. The paper got the *shape* of the problem right —
adaptive governance over a deterministic loop is genuinely how this should
work — and got the *substrate* wrong, because in mid-2025 there was nothing
solid to build that loop on.

## What aged well

- **Deterministic control plane, not LLM-driven scheduling.** The paper kept
  the scoring and selection machinery formal and explainable — MCDM methods a
  human can audit, not a bare LLM judgment — with the LLM confined to one
  layer. Nine months later that separation turned out to be the single most
  important call in the design. Bernstein's scheduler is plain Python — zero tokens spent
  on coordination, full audit trail, no nondeterminism in the control flow.

- **Adaptive metric selection beats fixed metrics.** The Synapse pathfinding
  experiment showed an agent that re-weights `safety / time / energy` per
  scenario beats a fixed-weight baseline. The same instinct landed in Kotef's
  per-tick backlog re-prioritization and in Bernstein's per-task agent /
  model routing.

- **MCDM7 as a framework, not a checklist.** The seven-axis trade-off lens
  (PerfGain / SecRisk / DevTime / Maintainability / Cost / Scalability / DX)
  ended up in the personal `CLAUDE.md` rulebook and stayed there. Forcing a
  written trade-off statement on every non-trivial decision is the discipline
  that travelled — the math underneath barely matters by comparison.

## What didn't work

- **The agent-runtime substrate didn't exist yet.** Synapse imagined an agent
  orchestrating real code work, but in mid-2025 there were no production CLI
  agents to orchestrate. Claude Code, Codex CLI, Gemini CLI all shipped later.
  Bernstein became *possible* only once those existed; everything Synapse
  described about "the agent does X" was hand-waved over a missing primitive.

- **No MCP, no real grounding.** The "agent reads its own metrics and decides
  what to optimise" loop in the paper was synthetic — the agent had no real
  tools, no real files, no real environment. Production grounding came with
  MCP in late 2025 and matured through early 2026. Without it, Synapse's
  feedback loop was a closed simulation talking to itself.

- **N=1 is not a benchmark.** The repo's only reproducible result file
  (`results/experiment_results_20250708_225100.csv`) is two rows: StaticAgent
  vs SYNAPSEAgent on one scenario (S1\_DynamicWind), 170.28 vs 122.32 energy,
  3.97 vs 1.24 safety, 59.71 vs 61.50 time. The paper says so itself in the
  Limitations section, but it bears repeating: this is a single data point,
  not evidence. That result also carries a known confound — a list-aliasing
  bug in the post-solve path analysis — so read it as a smoke test, not a
  measurement.

- **The paper's §5 tables are not reproducible here.** Section 5 and Appendix A
  present a 100-scenario run (training / validation / holdout, per-scenario PPS
  and SRS tables) and the rendered site charts twenty holdout rows. That data
  came from an earlier grid-world implementation whose raw CSVs were not
  preserved; only the continuous S1\_DynamicWind run above survives in the repo.
  So the numbers in §5 are the historical artefact, and the two-row CSV is the
  only thing you can re-run. The 10,000-scenario claim floated in a v1.1 draft
  was a planning artefact, never computed. The prose in the 2025 paper oversells
  throughout — read the numbers, not the adjectives.

## What this became

- **Kotef** — <https://github.com/chernistry/kotef>. The first prototype that
  put SYNAPSE's loop on a real repository: a `planner → researcher → coder →
  verifier → janitor` supervisor flow with durable state in `.sdd/runtime/`,
  MCP-grounded tools, and resume by thread ID. Single-agent. The metric
  profile became a quality-gate config; the adaptive layer became a
  backlog-driven planner that re-derives priorities each tick. Kotef is where
  I first trusted that the loop survived contact with file systems.

- **Bernstein** — <https://bernstein.run>. Production multi-agent orchestrator;
  40+ adapters, Apache-2.0, on PyPI, external contributors. MCP and A2A
  support, deterministic Python scheduling, git-worktree isolation per task,
  HMAC-signed audit trail, janitor verification step — and, by mid-2026,
  deterministic replay with hash-mismatch detection and verification-gated
  merges. What Kotef was for one agent, Bernstein is for many. The "control
  plane that doesn't burn tokens on its own scheduling" is exactly the Synapse
  intuition, shipped. MCDM-style trade-off scoring lives in the agent / model
  routing logic.

- **Personal `CLAUDE.md` / coding rules.** Still names "MCDM7" and "Adaptive
  Governance" by their Synapse names. The vocabulary stuck because the lens is
  useful, not because the prototype worked.

## What I'd do differently if I were writing it now

**Ground every claim in a real agent runtime.** Skip the synthetic toy. Run
the loop on Claude Code or Codex against a real repo with real test commands.
The interesting failure modes only show up when the agent is touching files
that someone else might have to read.

**Use MCP for tool grounding.** Don't hand-roll a "give the agent state and
let it choose metrics" loop — hang it off a small MCP server that exposes the
metrics, the diff, and the test results as proper tools. Cheaper to build,
honest about what's actually grounded.

**Run a proper experiment.** N ≥ 50 seeds, factorial over scenario types,
Mann-Whitney U with Cliff's δ for effect size. The original paper claimed
statistical significance from results that weren't actually computed. If the
experiment isn't worth doing properly, it isn't worth claiming.

**Be more careful about the word "autonomous."** In hindsight, a strong
deterministic control plane with human-in-the-loop checkpoints — which is what
Bernstein's janitor step is — beats an autonomous agent attempting metric
drift on its own. Autonomy is not a virtue. Honesty about where the human
checkpoint sits is.

---

Synapse was the prototype of how I think. Kotef proved the loop survived a
real repository. Bernstein is the production version that runs on many. The
repo stays public because the lineage is more honest than the polish.
