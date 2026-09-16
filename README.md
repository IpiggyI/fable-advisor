# Fable Advisor

**A role pool with postures. Any model can run the main agent.**

Claude Code and Cursor let the session and its subagents run on different models. This plugin is a **role pool**: three roles (`explorer` / `worker` / `advisor`) at three tiers (`light` / `standard` / `senior`), reached through four lanes named by mechanism. The main agent — whichever model is running the session — owns requirements, decomposition, delivery contracts, routing, and acceptance.

Two **postures** describe the main agent's relation to deliverables, and they differ in exactly one rule:

- **Orchestrating posture**: deliverables change only through a worker. The main agent (the architect, in this posture) writes contracts, dispatches, and accepts.
- **Implementing posture**: the main agent may edit deliverables directly — and may still dispatch any role.

Model identity never selects posture: a user declaration or an upstream instruction wins; with neither, an existing upstream task artifact (issue, spec, task file) means orchestrating, otherwise implementing.

| Role | Permissions | Returns |
|---|---|---|
| `explorer` | read-only | evidence (`file:line`, symbols, verbatim quotes) |
| `worker` | writes inside the contract's Files | a diff plus verification evidence, as a `WORKER REPORT` |
| `advisor` | read-only | a verdict under 300 words, in two request shapes: **decision** (before committing) or **acceptance** (after: contract, diff, receipt → criteria met?) |

Tiers `light` / `standard` / `senior` are orthogonal to role: any role at any tier. A takeover of a stuck task is a senior worker under a takeover contract. The advisor's authority comes from the code it reads, not its tier.

A **lane** answers how a vendor is reached; roles and tiers answer what is dispatched. Which (role, tier) maps to which lane and dial is a **fill table** in your user routing profile, which the caller names to the skill; the plugin ships no default table.

| Lane | Mechanism | Invocation |
|---|---|---|
| grok lane | Grok family (catalog default, currently grok-4.6) | `scripts/run-grok.mjs` runner (Claude Code); pinned-model dispatch (Cursor) |
| codex lane | GPT family, via the codex runner (currently GPT-6 Astra default and GPT-5.6 Luna) | `scripts/run-codex.mjs` (Claude Code). In Cursor: the same runner through the Shell tool, with no receipt gate |
| claude lane | Claude subagents: one agent file per (role, effort) — `explorer-h`, `explorer-xh`, `worker-md`, `worker-h`, `worker-xh`, `advisor-l`, `advisor-md`, `advisor-h`, `advisor-xh`; no external CLI | the file fixes the effort, the per-dispatch `model` picks the fill |
| handoff lane | Any harness you pick | `.fable-advisor/handoff/<slug>.md`, run by hand — never routed here unless you declare it |

**Spend judgment where it is scarce. Keep volume out of the main agent's context. In the orchestrating posture every deliverable change has a reader other than its author.** For high-stakes work, race two fills on the same spec and pick the stronger diff.

The plugin ships the **orchestration skill** — posture and the delegation boundary, the role × tier × lane pool, two-stage routing (pick (role, tier) by judgment dependence, then Pareto-select inside that cell of the fill table), the five-part delivery contract, the **decision-type gate**, escalation (one failed rework ticket plus attribution), and the verification rules that keep lanes honest.

## Install

```
claude plugin marketplace add IpiggyI/fable-advisor
claude plugin install fable-advisor@fable-advisor
```

This is a fork of [`DannyMac180/fable-advisor`](https://github.com/DannyMac180/fable-advisor).

Updating an existing installation to the latest release:

```
claude plugin marketplace update fable-advisor
claude plugin update fable-advisor@fable-advisor
```

**Lite mode — one file, 30 seconds.** Don't want the full pattern? Copy [`plugin/agents/advisor-h.md`](plugin/agents/advisor-h.md) into `~/.claude/agents/`. You get advisor consults at the decision-type gate without the orchestration layer (see "Implementing posture" below).

## Requirements

- **Claude Code ≥ 2.1.170.**
- **No Fable access** (e.g. API-key billing)? Change `model: fable` → `model: opus` in the advisor files if you want the claude-lane advisor to resolve — there are four of them (`advisor-l`, `advisor-md`, `advisor-h`, `advisor-xh`), so edit whichever dials you actually dispatch, or all four to be safe. Session and advisor may then share a model; the advisor's remaining value is **context isolation** — it reads the code from scratch, without the session's accumulated assumptions — not a stronger-model second opinion.
- **Grok lane:** the `scripts/run-grok.mjs` runner needs the [xAI Grok CLI](https://x.ai/cli) installed and authenticated (install from [x.ai/cli](https://x.ai/cli), then `grok login`); optional spec key `effort` is whitelisted `low | medium | high | xhigh` (out of range is `spec_invalid`; omit it to send no `--effort` and use the CLI default), and the receipt records the value the runner submitted. Without the CLI the receipt reports `grok_unavailable` — it never silently falls back to a Claude model; see [lanes-claude-code.md](plugin/skills/orchestration/lanes-claude-code.md).
- **Codex lane (optional):** `scripts/run-codex.mjs` (Node ≥ 18) needs the [OpenAI Codex CLI](https://github.com/openai/codex) installed and authenticated (`npm i -g @openai/codex`, then `codex login`) and invokes the GPT family among `gpt-6-astra` (default) and `gpt-5.6-luna`, with `model_reasoning_effort` `low | medium | high | xhigh | max` (defaults: astra → `medium`, luna → `max`) and optional `service_tier=fast` (~1.5× faster at ~2.5× ChatGPT credit consumption, no intelligence loss). Every run writes a structured receipt (`.fable-advisor/receipts/<spec_hash>.json`); in Claude Code a plugin Stop hook blocks claiming completion while a queued spec has no complete receipt, and without CLI/model access the runner reports `codex_unavailable` — see [lanes-claude-code.md](plugin/skills/orchestration/lanes-claude-code.md).
- **Report mode (both runners):** read-only roles reach the Grok or GPT family through spec key `mode: "report"`; an unchanged working tree is `complete`, a dirty tree is `unexpected_diff`. Remaining details: [lanes-claude-code.md](plugin/skills/orchestration/lanes-claude-code.md).
- **Claude lane (no CLI required):** a `worker-*` agent runs the work on Claude (the file's `effort:` is the dial; a per-dispatch `model` picks the fill, since `worker-*` and `explorer-*` pin no model), so the plugin stays self-contained when neither CLI is installed; from a Claude main agent the standing disclosures are same family (no cross-vendor review) and shared Anthropic quota. Same-model dispatch pins this lane to the session model instead of the default `opus` alias (in Cursor: `generalPurpose` with no `model`; in Claude Code: a `worker-*` agent with per-dispatch `model` set to the session model) — see [lanes-claude-code.md](plugin/skills/orchestration/lanes-claude-code.md).
- Heads-up: if a pinned Claude model isn't available on your account, Claude Code silently falls back to your session model — the pattern degrades quietly rather than erroring. If results feel unremarkable, check your plan. (This quiet fallback applies only to Claude model pins — the grok and codex lanes always fail loudly with a structured error.)

Model resolution order in Claude Code (v2.1.251+): per-invocation `model` parameter → agent frontmatter `model` → `CLAUDE_CODE_SUBAGENT_MODEL` → session model.

## Use it

Ask for work. The orchestration skill selects posture, then routes:

```
Add rate limiting to our public API. Design it, delegate the
implementation, and verify the evidence before you call it done.
```

In the orchestrating posture the main agent writes the spec, picks a fill from the fill table (rate limiting touches concurrency — a good case for racing two fills and picking the stronger diff), and applies tiered acceptance when the `WORKER REPORT` comes back: verification evidence plus a diff stat by default, with scoped or delegated full review as the stakes rise. Only then does it report done.

**Escalation.** A failed acceptance gets a rework ticket (lane-owned defect; never a hand fix) or a corrected contract (contract gap). When that rework ticket also fails, attribute: capability → a higher-tier worker in a fresh session under a takeover contract (original contract, prior report, receipt); contract gap → a corrected contract on the same lane session. A senior tier may also be a first choice.

To make the doctrine always-on, add to your project's `CLAUDE.md`:

```
Spend judgment where it is scarce; keep volume out of this context.
In the orchestrating posture, deliverables go through a worker.
Dispatch explorer / worker / advisor at a tier from the fill table.
At the decision-type gate, consult an `advisor-*` agent and act on its verdict.
```

## Using it in Cursor

Cursor loads installed Claude Code plugins through its compatibility paths.
The grok and claude lanes are Task dispatches with an explicit `model`; the GPT family is reached by running the **codex runner through the Shell tool**, with no receipt gate.
A user-level Cursor `preToolUse` hook denies an `advisor-*` dispatch whose pin is missing, empty or `inherit`; it matches the `advisor-` prefix, so a dial added later is covered.
Everything else is in [lanes-cursor.md](plugin/skills/orchestration/lanes-cursor.md).
See [ADR 0010](docs/adr/0010-dual-harness-single-source.md), [ADR 0011](docs/adr/0011-cursor-lane-family-gate-user-level.md), and [ADR 0014](docs/adr/0014-role-pool-posture.md).

## Decision-type gate

Consult the advisor at these decision types. The list binds any main agent, at any tier, in either posture — no mechanical enforcement, no per-diff review:

- committing to an architecture, data migration, API shape, or refactor strategy
- overturning an established plan
- changing a public interface or a cross-module dependency
- relaxing acceptance criteria
- the same problem failing twice

These all take the **decision** shape: pass the decision, the constraints, and the options considered. The advisor's **acceptance** shape is reached through the orchestration skill's **Tier 3**. Every `advisor-*` agent is a read-only skeptic: it reads your actual code and returns a verdict in under 300 words. `advisor-h` is the default dial; `advisor-l` and `advisor-md` are cheaper, `advisor-xh` is for a contested call. It never implements. Act on the verdict or surface the disagreement; never silently ignore it. Running it from any session still pays: it sees the code fresh, without your conversation's accumulated assumptions.

## Implementing posture

When no upstream task artifact exists and you have not declared orchestrating, the main agent may edit deliverables itself — and still dispatch explorer, worker, or advisor, and still consult the advisor at the decision-type gate.

```
Migrate our checkout sessions from Postgres to Redis — plan it,
consult your advisor before committing, then implement.
```

## FAQ

**Is this Anthropic's "advisor tool"?** No — that's a server-side API feature. These are plain Claude Code subagents plus a skill: readable, editable, no beta flags.

**Does this work on claude.ai?** No — subagent model routing is Claude Code only (CLI, desktop, VS Code, web). Cursor is supported via its Claude-plugin compatibility paths (see above).

**Why not just run everything on one model?** You can. Volume is still most of a session's tokens, and lanes keep that volume out of the main agent's context. Spend judgment where it is scarce — on contracts, routing, and acceptance — and let workers type.

**Upgrading from an earlier version?** v5.0.0 is breaking: session modes that followed from model identity are retired in favour of postures; the three old lane names become grok lane, codex lane, and claude lane (see [ADR 0014](docs/adr/0014-role-pool-posture.md)); the `implementer` agent is removed and `worker` is added; runner specs gain grok `effort` and `mode` (`implement` | `report`) on both runners, with report-mode error classes `unexpected_diff` and `empty_report`; the Cursor gate now checks only for an explicit non-inherit pin. Also breaking, without a version bump to signal it: the `subagent_type`s `fable-advisor:worker` and `fable-advisor:fable-advisor` no longer exist, and dispatching either old name returns `Agent type not found` — the retired `worker` was `effort: medium` with `model: opus` pre-pinned, so its same-dial replacement is `fable-advisor:worker-md` (also medium, but it pre-pins no model — give the model per dispatch); use `fable-advisor:worker-h` instead if you want the fill table's default worker dial. `fable-advisor:advisor-h` replaces `fable-advisor` with identical values. Agent files load only when a session starts, so restart the session after upgrading. The 4.2.0 line remains on branch `feature/v4-architect-mode`.

**Why Grok and GPT-family lanes in a Claude plugin?** Vendor diversity. Models from one family share blind spots; an independent implementation from a different lineage catches what same-family review misses. The main agent can be any model — the lanes are producers, reached by mechanism, not a ranking of who should run the session.

## Go deeper

I write [**Attention Heads**](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) — deep, evidence-backed writing on AI, cognition, and agentic engineering. The **Agentic Engineering Field Notes** series is where I publish practical advice on the craft of using AI. [Subscribe](https://attentionheads.substack.com/subscribe?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) to get new posts to your inbox.

## License

MIT
