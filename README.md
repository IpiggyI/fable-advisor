# Fable Advisor

**The smartest model runs the show. Lanes own the implementation.**

Claude Code lets every subagent run on a different model — and lets the session itself run on a different model than its subagents. This plugin exploits that with the **architect pattern**: your session runs on a **flagship-tier** model (e.g. Fable 5 or Opus 5), acting as a full-time architect. It owns requirements, decomposition, delivery contracts, routing, and acceptance — and routes every implementation task in two stages: narrow to the lanes adequate for the task, then choose among them against your declared routing profile (speed, price, capability, specialty), which with no declarations is just the cheapest adequate lane:

| Lane | Producer | Invocation | Route here when |
|---|---|---|---|
| Routine | **Grok** (catalog default, currently grok-4.6) | `scripts/run-grok.mjs` runner (default) | The contract fully determines the outcome — Grok-family routine lane via the [Grok CLI](https://x.ai/cli) |
| Cross-vendor | GPT family, via the codex runner (currently GPT-6 Astra default and GPT-5.6 Luna) | `run-codex.mjs` runner (architect-driven) | Correctness-critical, or you want a second independent implementation to compare |
| In-house | Opus (in-house Claude) | `implementer` agent | Deliberately routed when your routing profile points here — this lane's specialty, a small-but-tricky task worth isolating from the architect's context, same-model dispatch of doctrine prose, or a declared quota/deadline constraint — and the safety net when the grok and the codex runners are both unavailable (same family as the architect, so no cross-vendor review) |
| Handoff | Any harness you pick | `.fable-advisor/handoff/<slug>.md`, run by hand | You declared it — the architect writes a self-contained spec, you run it on your own subscription, and it accepts the diff (never routed here uninvited) |
| Judgment | Fable series | `fable-advisor` agent | Commitment boundaries — see below |

Tokens route by volume: the expensive model emits the fewest tokens (judgment and contracts), cheap lanes emit the most (code). Implementation mechanics are ~90% of a session's tokens and the Grok-family routine lane (currently grok-4.6) handles them at near-parity — so this runs far cheaper than flagship-for-everything, and every implementation comes from a *different model family* than the architect that reviews it: cross-vendor review is built into the routing, not bolted on. For high-stakes work, race the grok and codex runners on the same spec and let the architect pick the stronger diff.

The plugin ships the **orchestration skill** — the routing doctrine that teaches the session when to use each lane, the cost discipline that keeps the expensive model's own token volume minimal (emit judgment not volume, keep context lean, decide what is reserved not how it is built), the five-part delivery contract that makes context-free delegation safe, and the verification rules that keep cheap lanes honest.

## Install

```
claude plugin marketplace add DannyMac180/fable-advisor
claude plugin install fable-advisor@fable-advisor
```

Updating an existing installation to the latest release:

```
claude plugin marketplace update fable-advisor
claude plugin update fable-advisor@fable-advisor
```

Then start your session as the architect on a flagship-tier model (Fable or Opus both qualify):

```
/model fable
```

**Lite mode — one file, 30 seconds.** Don't want the full pattern? Copy [`plugin/agents/fable-advisor.md`](plugin/agents/fable-advisor.md) into `~/.claude/agents/` and keep your session on Sonnet. You get advisor consults at commitment boundaries without the orchestration layer (see "Advisor-only mode" below).

## Requirements

- **Claude Code ≥ 2.1.170** with a subscription that includes a flagship-tier model — Fable or Opus (Pro, Max, Team, or Enterprise — all current consumer plans qualify).
- **No Fable access** (e.g. API-key billing)? Use `/model opus` for the session and change `model: fable` → `model: opus` in the advisor file. Session and advisor then share the same model; the advisor's remaining value is **context isolation** — it reads the code from scratch, without the session's accumulated assumptions — not a cross-model second opinion.
- **Grok lane (the default implementer):** the `scripts/run-grok.mjs` runner needs the [xAI Grok CLI](https://x.ai/cli) installed and authenticated (install from [x.ai/cli](https://x.ai/cli), then `grok login`). It drives Grok headlessly (`grok --prompt-file … --output-format streaming-json`), validating the requested model against the live `grok models` catalog — a new grok generation is usable the day the CLI lists it. Without the CLI the receipt reports `grok_unavailable` — it never silently falls back to a Claude model.
- **Codex lane (optional):** the codex lane is a deterministic runner (`scripts/run-codex.mjs`, requires Node ≥ 18) driven directly by the architect — no wrapper agent. It needs the [OpenAI Codex CLI](https://github.com/openai/codex) installed and authenticated (`npm i -g @openai/codex`, then `codex login`) and invokes the **GPT family**, model-selectable per task among `gpt-6-astra` (default) and `gpt-5.6-luna`, with `model_reasoning_effort` selectable across `low | medium | high | xhigh | max` (default follows the model: astra → `medium`, luna → `max`) and an optional `service_tier=fast` when you want speed over quality. If astra fails before a session is established, the runner retries once on luna; the receipt records `model_requested` / `model_used` / `fallback_reason`. Every run produces a structured receipt (`.fable-advisor/receipts/<spec_hash>.json`) with the session id, changed files, verification output, and diagnostics (`end_to_close_ms`; `no_diff` / `git_status_failed` when the tree did not change or `git status` failed). A plugin Stop hook blocks claiming completion while a queued spec has no complete receipt. Without CLI/model access the runner reports `codex_unavailable` and the other lanes remain unaffected.
- **In-house lane (no CLI required):** the `implementer` agent runs the work directly on Claude Opus, so the plugin stays self-contained and usable out of the box. The architect routes here deliberately — when your declared routing profile marks the task as this lane's specialty, when a small-but-tricky task is better isolated from the architect's context, when a declared quota or deadline constraint points this way, or for same-model dispatch of the plugin's own doctrine prose — and automatically when neither the Grok nor the Codex CLI is installed. Opus matches the architect's flagship tier and unit price — the win is context isolation (implementation detail stays out of the architect's context), not a cheaper rate. Same-model dispatch pins the in-house lane to the session model instead of the default `opus` alias (in Cursor: `generalPurpose` with no `model`; in Claude Code it degrades to ordinary Opus, disclosed). The trade-off is no cross-vendor review — its output shares the architect's model family — so routine work still defaults to the CLI lanes; routing here is deliberate and disclosed.
- Heads-up: if a pinned Claude model isn't available on your account, Claude Code silently falls back to your session model — the pattern degrades quietly rather than erroring. If results feel unremarkable, check your plan. (This quiet fallback applies only to Claude model pins — the grok and codex lanes always fail loudly with a structured error.)

Model resolution order in Claude Code: `CLAUDE_CODE_SUBAGENT_MODEL` env var → per-invocation `model` parameter → agent frontmatter → session model.

## Use it

With the session on a flagship model, just ask for work — the orchestration skill routes it:

```
Add rate limiting to our public API. Design it, delegate the
implementation, and verify the evidence before you call it done.
```

The architect writes the spec, picks the lane (rate limiting touches concurrency — a good case for racing the grok and codex runners and picking the stronger diff), and applies tiered acceptance when the report comes back: verification evidence plus a diff stat by default, with scoped or delegated full review as the stakes rise. Only then does it report done.

To make the doctrine always-on, add one line to your project's `CLAUDE.md`:

```
You are the architect running the most expensive model — minimize your
own token volume. Delegate all deliverables through the orchestration
skill's routing table, delegate broad codebase
exploration to cheap read-only agents, and verify evidence before
accepting any lane's report.
```

## Using it in Cursor

Cursor loads installed Claude Code plugins through its compatibility paths, so the orchestration skill and the `fable-advisor` agent work there out of the box — and none of the CLI machinery is needed. Cursor exposes every lane's model natively: the architect delegates by dispatching a subagent pinned to the lane's model — the Grok-family slug in this turn's allowlist for routine work, a GPT-family slug for cross-vendor, an Opus slug for in-house. The dispatch prompt opens by pointing the subagent at `plugin/skills/orchestration/lane-preamble.md`; the five-part delivery contract follows. The report returns in-band, and there are no pending files, receipts, or receipt gate — acceptance runs entirely on the tiered verification protocol. Pin the model on every vendor-lane and named-agent dispatch: agent frontmatter `model:` is not honored for plugin-loaded agents in Cursor, so a bare named-agent dispatch (including `fable-advisor`) silently inherits the session model — the Cursor variant of the quiet-fallback heads-up above. Same-model dispatch of doctrine prose is the exception: a `generalPurpose` dispatch with `model` omitted, inheriting the session model on purpose. A rework ticket is a Task `resume` of the prior dispatch. A user-level Cursor `preToolUse` hook (canonical copy `cursor-hooks/`, not the plugin receipt-gate) denies `fable-advisor` / `implementer` when the pin is missing, `inherit`, or the wrong family — see [ADR 0011](docs/adr/0011-cursor-lane-family-gate-user-level.md). Two things to know: an ad-hoc model pin carries a fixed effort tier (bracket parameters like `<slug>[effort=high]` need a custom agent definition file — add one only when a task genuinely needs it), and each vendor's models draw on their own quota pool in Cursor, so the price gradient between lanes and the whole cost case above apply unchanged. See [ADR 0010](docs/adr/0010-dual-harness-single-source.md).

## Commitment boundaries

Even the architect gets a second opinion. The `fable-advisor` agent is a read-only skeptic — consulted before architecture decisions, migrations, API designs, and whenever a problem has resisted two attempts. It reads your actual code and returns a verdict in under 300 words. It never implements. Running it from a flagship-tier session still pays: it sees the code fresh, without your conversation's accumulated assumptions.

## Advisor-only mode (the original pattern)

The inverse arrangement, for when you'd rather keep the session cheap: run the session on Sonnet and consult `fable-advisor` only at commitment boundaries.

```
Migrate our checkout sessions from Postgres to Redis — plan it,
consult your advisor before committing, then implement.
```

A typical consult costs cents. To make it automatic, add to your project's `CLAUDE.md`:

```
Before committing to any architecture decision, migration, or refactor
touching 3+ files, consult the fable-advisor agent and act on its verdict.
```

## FAQ

**Is this Anthropic's "advisor tool"?** No — that's a server-side API feature. These are plain Claude Code subagents plus a skill: readable, editable, no beta flags.

**Does this work on claude.ai?** No — subagent model routing is Claude Code only (CLI, desktop, VS Code, web).

**Why not just run everything on the flagship model?** You can. It's excellent. It's also the most expensive lane per token, and most of a session's tokens are implementation mechanics that the cheap lanes handle at near-parity. Spend the premium where judgment lives.

**Upgrading from v2?** v3 replaced the Sonnet/Opus `implementer` agent with `grok-implementer` — Grok 4.5 via the [Grok CLI](https://x.ai/cli) is now the default typing lane. v3.1 upgrades the optional codex lane from GPT-5.5 to GPT-5.6 Sol at high reasoning. The `fable-advisor` agent and advisor-only mode work exactly as before. If you preferred the Claude implementer, it's still bundled as the `implementer` agent — now an in-house fallback lane that runs when neither the Grok nor the Codex CLI is installed, rather than the default. v3.2 removes the codex wrapper agent: the architect drives `scripts/run-codex.mjs` directly and acceptance is enforced by a receipt-gate Stop hook. v3.3 switches the in-house fallback `implementer` to Opus by default — the lane's value is context isolation, not a cheaper unit price. v3.4 promotes that lane from fallback-only to one the architect can route to on purpose, driven by your declared routing profile (specialty, quota, deadline), and makes routing two-stage: filter to the lanes adequate for the task, then choose among them by Pareto trade-off — see [ADR 0006](docs/adr/0006-pareto-lane-routing-inhouse-promotion.md). v3.5 adds the opt-in **handoff lane**: the architect writes a self-contained spec to `.fable-advisor/handoff/<slug>.md` for you to run by hand on any harness you already pay for, and accepts the work by reading the diff and re-running the verification itself — it is never routed there unless you declare it, see [ADR 0007](docs/adr/0007-handoff-lane.md). v3.6 adds tiered diff acceptance, hard report budgets for both implementer lanes, and the spec-prep scout rule — see [ADR 0008](docs/adr/0008-context-discipline.md). v3.7 removes the grok wrapper agent the same way v3.2 removed codex's: the architect drives `scripts/run-grok.mjs` directly, the model is validated against the live `grok models` catalog, and the named-spawn guardrail retires with the wrapper — see [ADR 0009](docs/adr/0009-grok-lane-dewrapper-runner.md). v3.9 makes the doctrine dual-harness: in Cursor the lanes are pinned-model subagent dispatches — no CLIs, no runners, no receipts — see [ADR 0010](docs/adr/0010-dual-harness-single-source.md). (The advisor's `readonly` frontmatter flag turned out not to be enforced for plugin-loaded agents in Cursor — its read-only stance there rests on the agent's own charter; in Claude Code the `tools` whitelist enforces it mechanically.) v4.0.0 replaces build-instruction specs with a delivery contract, draws the delegation boundary by artifact class, and makes `lane-preamble.md` the single source for the executor-side contract. Rework tickets resume the lane session (`resume_session_id` on the CLI runners; Task `resume` in Cursor). The codex whitelist is `gpt-6-astra` / `gpt-5.6-luna` with per-model default effort and a single-hop astra→luna fallback recorded in the receipt (`model_requested` / `model_used` / `fallback_reason`). Both runners refuse a silent no-op (`no_diff`, `git_status_failed`), record `end_to_close_ms`, and the skill documents the wait protocol (the runner process exiting is the completion point). Runtime Markdown under `plugin/` has a Chinese mirror under `docs/zh/`.

**Why Grok and GPT-family lanes in a Claude plugin?** Vendor diversity. Models from one family share blind spots; an independent implementation from a different lineage catches what same-family review misses — and with Claude as the architect, *every* diff now gets cross-vendor review for free. The architect stays Claude — the lanes are producers, not judges.

## Go deeper

I write [**Attention Heads**](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) — deep, evidence-backed writing on AI, cognition, and agentic engineering. The **Agentic Engineering Field Notes** series is where I publish practical advice on the craft of using AI. [Subscribe](https://attentionheads.substack.com/subscribe?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) to get new posts to your inbox.

## License

MIT
