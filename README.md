# Fable Advisor

**A role pool with postures. Any model can run the main agent.**

Claude Code and Cursor let the session and its subagents run on different models. This plugin is a **role pool**: three roles (`explorer` / `worker` / `advisor`) at three tiers (`light` / `standard` / `senior`), reached through four lanes named by mechanism. The main agent — whichever model is running the session — owns requirements, decomposition, delivery contracts, routing, and acceptance. It does not have to be a flagship Claude.

Two **postures** describe the main agent's relation to deliverables, and they differ in exactly one rule:

- **Orchestrating posture**: deliverables change only through a worker. The main agent (the architect, in this posture) writes contracts, dispatches, and accepts.
- **Implementing posture**: the main agent may edit deliverables directly — and may still dispatch any role.

Every role is dispatchable in both. Model identity never selects posture: a user declaration or an upstream instruction wins; with neither, an existing upstream task artifact (issue, spec, task file) means orchestrating, otherwise implementing. Implementing never means "no dispatches".

| Role | Permissions | Returns |
|---|---|---|
| `explorer` | read-only | evidence (`file:line`, symbols, verbatim quotes) |
| `worker` | writes inside the contract's Files | a diff plus verification evidence, as a `WORKER REPORT` |
| `advisor` | read-only | a verdict under 300 words, in two request shapes: **decision** (before committing) or **acceptance** (after: contract, diff, receipt → criteria met?) |

Tiers `light` / `standard` / `senior` are orthogonal to role: any role at any tier. A takeover of a stuck task is a senior worker plus a takeover contract, not another role. The advisor's authority comes from the code it reads, not its tier.

A **lane** answers how a vendor is reached; roles and tiers answer what is dispatched. Which (role, tier) maps to which lane and dial is a user-side **fill table** in your rules — this repo names no model rankings.

| Lane | Mechanism | Invocation |
|---|---|---|
| grok lane | Grok family (catalog default, currently grok-4.6) | `scripts/run-grok.mjs` runner (Claude Code); pinned-model dispatch (Cursor) |
| codex lane | GPT family, via the codex runner (currently GPT-6 Astra default and GPT-5.6 Luna) | `scripts/run-codex.mjs` (Claude Code). In Cursor: the same runner through the Shell tool, with no receipt gate |
| claude lane | Claude subagents (`worker`, `fable-advisor`, the harness explorer); no external CLI | `worker` agent — per-dispatch `model` sets the tier |
| handoff lane | Any harness you pick | `.fable-advisor/handoff/<slug>.md`, run by hand — never routed here unless you declare it |

**Spend judgment where it is scarce. Keep volume out of the main agent's context. In the orchestrating posture every deliverable change has a reader other than its author.** A code block longer than an interface signature is a contract not yet delegated. For high-stakes work, race two fills on the same spec and pick the stronger diff.

The plugin ships the **orchestration skill** — posture and the delegation boundary, the role × tier × lane pool, two-stage routing (pick (role, tier) by judgment dependence, then Pareto-select inside that cell of the fill table), the five-part delivery contract, the **decision-type gate**, escalation (one failed rework ticket plus attribution), and the verification rules that keep lanes honest.

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

Start a session on any model. Posture is a declaration or whether an upstream task artifact exists, never the model name:

```
/model fable
```

**Lite mode — one file, 30 seconds.** Don't want the full pattern? Copy [`plugin/agents/fable-advisor.md`](plugin/agents/fable-advisor.md) into `~/.claude/agents/`. You get advisor consults at the decision-type gate without the orchestration layer (see "Implementing posture" below).

## Requirements

- **Claude Code ≥ 2.1.170.** Any session model can be the main agent.
- **No Fable access** (e.g. API-key billing)? Change `model: fable` → `model: opus` in the advisor file if you want the claude-lane advisor to resolve. Session and advisor may then share a model; the advisor's remaining value is **context isolation** — it reads the code from scratch, without the session's accumulated assumptions — not a stronger-model second opinion.
- **Grok lane:** the `scripts/run-grok.mjs` runner needs the [xAI Grok CLI](https://x.ai/cli) installed and authenticated (install from [x.ai/cli](https://x.ai/cli), then `grok login`). It drives Grok headlessly (`grok --prompt-file … --output-format streaming-json`), validating the requested model against the live `grok models` catalog — a new grok generation is usable the day the CLI lists it. Optional spec key `effort`: whitelist `low | medium | high | xhigh`; out of range is `spec_invalid` and the runner does not spawn; omit the key to send no `--effort` flag and use the CLI default. The receipt records the value actually used. Without the CLI the receipt reports `grok_unavailable` — it never silently falls back to a Claude model.
- **Codex lane (optional):** a deterministic runner (`scripts/run-codex.mjs`, requires Node ≥ 18). It needs the [OpenAI Codex CLI](https://github.com/openai/codex) installed and authenticated (`npm i -g @openai/codex`, then `codex login`) and invokes the **GPT family**, model-selectable per task among `gpt-6-astra` (default) and `gpt-5.6-luna`, with `model_reasoning_effort` selectable across `low | medium | high | xhigh | max` (default follows the model: astra → `medium`, luna → `max`) and an optional `service_tier=fast` when you want speed over quality. If astra fails before a session is established, the runner retries once on luna; the receipt records `model_requested` / `model_used` / `fallback_reason`. Every run produces a structured receipt (`.fable-advisor/receipts/<spec_hash>.json`) with the session id, changed files, verification output, and diagnostics (`end_to_close_ms`; `no_diff` / `git_status_failed` when the tree did not change in implement mode or `git status` failed). In Claude Code a plugin Stop hook blocks claiming completion while a queued spec has no complete receipt. Without CLI/model access the runner reports `codex_unavailable` and the other lanes remain unaffected.
- **Report mode (both runners):** spec key `mode` is `implement` (default, current semantics) or `report`. Report mode is how `explorer` and `advisor` reach the Grok or GPT family: the CLI runs with a read-only tool set; `files` is the read scope and may be empty; `verification` may be empty. An unchanged working tree is the normal outcome and is `complete`; the receipt carries `mode` and `report` (the CLI's final message). A dirty tree is the error class `unexpected_diff`, never `complete`. A clean tree whose report text is empty or whitespace-only is the error class `empty_report`, never `complete`. An unknown `mode` is `spec_invalid`.
- **Claude lane (no CLI required):** the `worker` agent runs the work on Claude (default alias `opus`; a per-dispatch `model` sets the tier), so the plugin stays self-contained and usable out of the box. Route here when the fill table names this lane, when a task is worth isolating from the main agent's context, for same-model dispatch of the plugin's own doctrine prose, or when neither CLI runner is installed. From a Claude main agent the standing disclosures are: same family (no cross-vendor review), shared Anthropic quota, highest unit price — what you buy is context isolation, not a cheaper rate. Same-model dispatch pins the claude lane to the session model instead of the default `opus` alias (in Cursor: `generalPurpose` with no `model`; in Claude Code: the `worker` agent with per-dispatch `model` set to the session model). It is a dial of this lane, used for doctrine prose in the orchestrating posture, not a fifth lane.
- Heads-up: if a pinned Claude model isn't available on your account, Claude Code silently falls back to your session model — the pattern degrades quietly rather than erroring. If results feel unremarkable, check your plan. (This quiet fallback applies only to Claude model pins — the grok and codex lanes always fail loudly with a structured error.)

Model resolution order in Claude Code: `CLAUDE_CODE_SUBAGENT_MODEL` env var → per-invocation `model` parameter → agent frontmatter → session model.

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
Dispatch explorer / worker / advisor at a tier from the fill table,
and consult the advisor at the decision-type gate.
```

## Using it in Cursor

Cursor loads installed Claude Code plugins through its compatibility paths, so the orchestration skill and the `fable-advisor` agent work there out of the box. The grok lane and the claude lane are native Task dispatches with an explicit `model` pin. The GPT family is **not** in the Task enum: it is reached by running the **codex runner through the Shell tool**, with the same pending/receipt flow as Claude Code, **without a receipt gate** (whether Cursor loads plugin Stop hooks is unverified — this lane fails open, at the same safety level as the handoff lane; the main agent judges the receipt itself).

The dispatch prompt for a Task lane opens by pointing the subagent at `plugin/skills/orchestration/lane-preamble.md`; the five-part delivery contract follows. Task reports return in-band; there are no receipts or receipt gate for those dispatches — acceptance runs entirely on the tiered verification protocol. Pin the model on every vendor-lane and named-agent dispatch: agent frontmatter `model:` is not honored for plugin-loaded agents in Cursor, so a bare named-agent dispatch (including `fable-advisor`) silently inherits the session model. The advisor's read-only stance in Cursor rests on its charter: the `readonly: true` frontmatter flag is not enforced for plugin-loaded agents there, while in Claude Code the `tools` whitelist enforces it mechanically. Same-model dispatch of doctrine prose is the exception: a `generalPurpose` dispatch with `model` omitted, inheriting the session model on purpose. A rework ticket is a Task `resume` of the prior dispatch. A user-level Cursor `preToolUse` hook (canonical copy `cursor-hooks/`, not the plugin receipt-gate) denies `fable-advisor` when the pin is missing or `inherit`; it does not check family — see [ADR 0011](docs/adr/0011-cursor-lane-family-gate-user-level.md) and [ADR 0014](docs/adr/0014-role-pool-posture.md). Two things to know: an ad-hoc model pin carries a fixed effort tier (bracket parameters like `<slug>[effort=high]` need a custom agent definition file — add one only when a task genuinely needs it), and each vendor's models draw on their own quota pool in Cursor, so lane prices and the cost discipline apply unchanged. Do not copy allowlist slugs out of this README; use the slug live in this turn's allowlist. See [ADR 0010](docs/adr/0010-dual-harness-single-source.md).

## Decision-type gate

Consult the advisor at these decision types. The list binds any main agent, at any tier, in either posture — no mechanical enforcement, no per-diff review:

- committing to an architecture, data migration, API shape, or refactor strategy
- overturning an established plan
- changing a public interface or a cross-module dependency
- relaxing acceptance criteria
- the same problem failing twice
- before declaring a multi-step deliverable done (this one takes the advisor's **acceptance** shape)

The others take the **decision** shape: pass the decision, the constraints, and the options considered. The `fable-advisor` agent is a read-only skeptic: it reads your actual code and returns a verdict in under 300 words. It never implements. Act on the verdict or surface the disagreement; never silently ignore it. Running it from any session still pays: it sees the code fresh, without your conversation's accumulated assumptions.

## Implementing posture

When no upstream task artifact exists and you have not declared orchestrating, the main agent may edit deliverables itself — and still dispatch explorer, worker, or advisor, and still consult the advisor at the decision-type gate.

```
Migrate our checkout sessions from Postgres to Redis — plan it,
consult your advisor before committing, then implement.
```

A typical consult costs cents. To make the gate automatic, add to your project's `CLAUDE.md`:

```
At the decision-type gates in the orchestration skill, consult the
fable-advisor agent and act on its verdict.
```

## FAQ

**Is this Anthropic's "advisor tool"?** No — that's a server-side API feature. These are plain Claude Code subagents plus a skill: readable, editable, no beta flags.

**Does this work on claude.ai?** No — subagent model routing is Claude Code only (CLI, desktop, VS Code, web). Cursor is supported via its Claude-plugin compatibility paths (see above).

**Why not just run everything on one model?** You can. Volume is still most of a session's tokens, and lanes keep that volume out of the main agent's context. Spend judgment where it is scarce — on contracts, routing, and acceptance — and let workers type.

**Upgrading from v2?** v3 replaced the Sonnet/Opus `implementer` agent with `grok-implementer` — Grok 4.5 via the [Grok CLI](https://x.ai/cli) is now the default typing lane. v3.1 upgrades the optional codex lane from GPT-5.5 to GPT-5.6 Sol at high reasoning. The `fable-advisor` agent and advisor-only mode work exactly as before. If you preferred the Claude implementer, it's still bundled as the `implementer` agent — now an in-house fallback lane that runs when neither the Grok nor the Codex CLI is installed, rather than the default. v3.2 removes the codex wrapper agent: the architect drives `scripts/run-codex.mjs` directly and acceptance is enforced by a receipt-gate Stop hook. v3.3 switches the in-house fallback `implementer` to Opus by default — the lane's value is context isolation, not a cheaper unit price. v3.4 promotes that lane from fallback-only to one the architect can route to on purpose, driven by your declared routing profile (specialty, quota, deadline), and makes routing two-stage: filter to the lanes adequate for the task, then choose among them by Pareto trade-off — see [ADR 0006](docs/adr/0006-pareto-lane-routing-inhouse-promotion.md). v3.5 adds the opt-in **handoff lane**: the architect writes a self-contained spec to `.fable-advisor/handoff/<slug>.md` for you to run by hand on any harness you already pay for, and accepts the work by reading the diff and re-running the verification itself — it is never routed there unless you declare it, see [ADR 0007](docs/adr/0007-handoff-lane.md). v3.6 adds tiered diff acceptance, hard report budgets for both implementer lanes, and the spec-prep scout rule — see [ADR 0008](docs/adr/0008-context-discipline.md). v3.7 removes the grok wrapper agent the same way v3.2 removed codex's: the architect drives `scripts/run-grok.mjs` directly, the model is validated against the live `grok models` catalog, and the named-spawn guardrail retires with the wrapper — see [ADR 0009](docs/adr/0009-grok-lane-dewrapper-runner.md). v3.9 makes the doctrine dual-harness: in Cursor the lanes are pinned-model subagent dispatches — no CLIs, no runners, no receipts — see [ADR 0010](docs/adr/0010-dual-harness-single-source.md). v4.0.0 replaces build-instruction specs with a delivery contract, draws the delegation boundary by artifact class, and makes `lane-preamble.md` the single source for the executor-side contract. Rework tickets resume the lane session (`resume_session_id` on the CLI runners; Task `resume` in Cursor). The codex whitelist is `gpt-6-astra` / `gpt-5.6-luna` with per-model default effort and a single-hop astra→luna fallback recorded in the receipt (`model_requested` / `model_used` / `fallback_reason`). Both runners refuse a silent no-op (`no_diff`, `git_status_failed`), record `end_to_close_ms`, and the skill documents the wait protocol (the runner process exiting is the completion point). Runtime Markdown under `plugin/` has a Chinese mirror under `docs/zh/`. v5.0.0 is breaking: session modes that followed from model identity are retired in favour of postures; the three old lane names become grok lane, codex lane, and claude lane (see [ADR 0014](docs/adr/0014-role-pool-posture.md)); the `implementer` agent is removed and `worker` is added; runner specs gain grok `effort` and `mode` (`implement` | `report`) on both runners, with report-mode error classes `unexpected_diff` and `empty_report`; the Cursor gate now checks only for an explicit non-inherit pin. The 4.2.0 line remains on branch `feature/v4-architect-mode`.

**Why Grok and GPT-family lanes in a Claude plugin?** Vendor diversity. Models from one family share blind spots; an independent implementation from a different lineage catches what same-family review misses. The main agent can be any model — the lanes are producers, reached by mechanism, not a ranking of who should run the session.

## Go deeper

I write [**Attention Heads**](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) — deep, evidence-backed writing on AI, cognition, and agentic engineering. The **Agentic Engineering Field Notes** series is where I publish practical advice on the craft of using AI. [Subscribe](https://attentionheads.substack.com/subscribe?utm_source=github&utm_medium=readme&utm_campaign=fable-advisor) to get new posts to your inbox.

## License

MIT
