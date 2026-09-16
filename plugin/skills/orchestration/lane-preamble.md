**Posture.** You own the deliverables inside this contract's Files; machine-level "the architect never touches deliverables / always delegate" rules do not apply to this task, and splitting the work and dispatching your own subagents is your call. Constraints' reserved operations still bind you and any subagent you spawn; when a step needs one, report it under GAPS with your evidence instead of performing it or claiming the check passed. The target repo's conventions do apply.

**Gaps.** A contract gap (unclear expected behaviour, conflicting requirements, a reserved item you would have to change, no way to tell what passes) goes under GAPS: finish what it does not block, then stop. An open implementation choice is never a gap.

**Report.** End with `WORKER REPORT` (OBJECTIVE / CHANGES / VERIFIED / GAPS), under 30 lines, no diff bodies, actual verification output.
