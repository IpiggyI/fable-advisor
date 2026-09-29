# Triage Labels

The skills speak in terms of five canonical triage roles; this repo uses the same strings as labels, plus one terminal state.

| Label             | Meaning                                  |
| ----------------- | ---------------------------------------- |
| `needs-triage`    | Maintainer needs to evaluate this issue  |
| `needs-info`      | Waiting on reporter for more information |
| `ready-for-agent` | Fully specified, ready for an AFK agent  |
| `ready-for-human` | Requires human implementation            |
| `wontfix`         | Will not be actioned                     |
| `resolved`        | Terminal: the work has landed and passed acceptance |

## How labels are recorded

This repo's tracker is local markdown (see `issue-tracker.md`), so there are no GitHub labels. A label is the value of the `Status:` line near the top of an issue file:

```md
Status: ready-for-agent
```

One role per issue. Changing triage state means editing that line, not adding a second one. Set `resolved` when the work has landed and passed acceptance; it is the same string the Wayfinding operations in `issue-tracker.md` use. A spec's `resolved` covers its issues that carry no `Status:` line.
