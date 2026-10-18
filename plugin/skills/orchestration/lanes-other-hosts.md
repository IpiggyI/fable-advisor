# The lanes in other hosts — the host's own entrances

Read this before the first dispatch in another host: one that loads this skill and is neither Claude Code nor Cursor, including one that imports Claude Code settings or plugins but runs differently. Roles, tiers, the ladder, the delivery contract and verification in [SKILL.md](SKILL.md) apply as usual. The rules below replace only the parts of SKILL.md that depend on the routing profile.

## Entrances

- **Only the host's own entrances.** Carry over no other host's runner, receipt gate, route gate or model pin; dispatch only through entrances the host itself provides. Do not rely on plugin hooks the host loads: the route is text, and nothing checks it mechanically.
- **An agent file the host cannot run.** When the model an agent file fixes cannot run on this host (such as the `model: fable` of `advisor-*`), that file is an unavailable entrance. Do not dispatch it; give its role to an entrance the host provides, point that dispatch at the executor-side contract the role needs, and say so in the disclosure.
- **The executor-side contract.** The dispatch prompt points at the preamble its role needs by its absolute path: [lane-preamble.md](lane-preamble.md) for a worker, [lane-preamble-report.md](lane-preamble-report.md) for an explorer or advisor.

## Routing without the profile

Do not read the routing profile. Stage 1 of SKILL.md "Routing" applies as usual: the tier comes from the task's difficulty and the ladder, and above `mainstay` the dispatch carries a basis of a kind SKILL.md accepts. Three parts of SKILL.md depend on the profile and are replaced by the rules below: the choice inside a cell in stage 2, the lane order in "Re-routing", and the floor at the failed model's ranking in R2.

- **Tiers by effort.** On one model, `mainstay` uses the entrance's default effort, `crux` one level above the default, and `rescue` the highest effort the entrance offers. When the entrance cannot set effort, the tier decides only the contract shape, the basis and the ladder, and the dial is the bare model.
- **First choice.** Use the entrance's default model. When the host offers several models, switch only when the task falls on one model's specialty or the user declares a model, and say so in the disclosure.
- **Re-routing.** When an entrance or a model is unavailable, switch to another model the host offers, with the same tier and effort rules, and disclose the switch; when no other model is available, report to the user. This is not a capability failure.
- **R2 and R3.** A raise moves the effort up to the next tier by the rules above; when the host offers several models, the raise may also switch model by the task, disclosed. R3 counts by dial: one dial is raised at most once, and when no higher effort exists, the task goes to the user.
- **The route line.** The format is SKILL.md "The route". Its `dial` is the host's actual model id with the effort, or the bare model.

## Session reuse

The routing profile has no reuse window for other hosts. A rework ticket, a corrected contract and a follow-up message therefore open a fresh session by default, carrying the defect, the original contract and the prior report. The past-window exception in SKILL.md "Session reuse" still applies, and the other rules there are unchanged.
