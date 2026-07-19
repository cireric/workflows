# Deepworker Protocol — Deferred Issues

Issues identified during the 2026-07-19 holistic review but deferred to a future optimization round. Each issue includes the problem, proposed fix, estimated effort, and deferral rationale.

---

## #4: Sub-agent Trigger Conditions — Task-Character vs Information-Gap

**Status**: Deferred (known since v0.2 restructuring)

**Problem**: Current DISCOVER Sub-agent Delegation table uses task-character triggers ("task involves modifying code whose internal logic I don't understand"). This is a proxy for the real decision criterion: **information gap**. An agent may encounter an information gap even when the task character doesn't match the trigger, or may match the trigger without actually having a gap.

**Proposed fix**: Rewrite trigger conditions to be information-gap-driven:

| Sub-agent     | Delegate when (information-gap)                                                                 | Do NOT delegate when                                          |
| ------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Explore**   | I need to understand code I haven't read, and reading it myself would cost more than delegating | I already have the information from codegraph or prior reads  |
| **Librarian** | I need external reference information I don't have and can't get from the project               | Project contains the reference, or context7 suffices          |
| **Oracle**    | I face an architecture decision with multiple plausible paths and insufficient basis to choose  | I can reason from information already available               |

**Risk of current design**: Agent skips delegation when task character doesn't match but information gap exists. Or delegates unnecessarily when task character matches but no gap exists.

**Effort**: Medium — requires rewriting the table + updating General principles to center on information gap.

**Defer rationale**: Current triggers work in practice for most cases. The gap is a precision issue, not a correctness issue. Rewriting risks introducing new ambiguity in what counts as an "information gap." Better to validate with eval data first.

---

## #5: PLAN Upstream Consumed Declaration

**Status**: Deferred (identified 2026-07-19)

**Problem**: No mechanism guarantees that PLAN actually consumes UNDERSTAND and DISCOVER outputs. The constraint anchor system prevents downstream from contradicting upstream, but doesn't prevent downstream from **ignoring** upstream.

Example: DISCOVER identifies a consumer, but PLAN's End-to-End Scenario only fires "when ≥2 functions." Single-function deliverables may have PLAN that never references the consumer analysis.

**Proposed fix**: Add to PLAN Phase Transition:

```
> **Upstream consumed**: UNDERSTAND: ✅ (goal + scope + ambiguity scan) | DISCOVER: ✅ (consumer: [referenced how] | assumptions: [N tracked])
```

This forces the agent to explicitly confirm each upstream output was consumed, not just received.

**Risk of current design**: Silent constraint loss. Assumptions or consumer insights from early phases may be dropped without detection until QA GATE (or never).

**Effort**: Small — one line added to PLAN Phase Transition format.

**Defer rationale**: The assumption lifecycle tracking added in this round (PLAN Constraints "Assumptions tracked: N items — UNDERSTAND: X, DISCOVER: Y") partially addresses this for assumptions. Consumer tracking is a narrower gap. Low risk, low effort — can be bundled with next round's changes.

---

## #6: TDD State Tracking in TODO List

**Status**: Deferred (identified 2026-07-19)

**Problem**: EXECUTE's TDD Enhancement describes Red/Green/Refactor discipline and Red validity criterion, but no mechanism verifies TDD flow compliance. An agent can claim "Red: assertion failure" without actually running the test, or skip Red entirely and write implementation first.

Post-Edit Verification checks lsp_diagnostics and lint — not TDD state. TODO Iron Law tracks step completion — not TDD phase within a step.

**Proposed fix**: Extend TODO list format for TDD steps:

```
- [ ] Step 1: ... [TDD: ⬜Red ⬜Green ⬜Refactor]
```

Each TDD phase is checked off as it completes. Post-Edit Verification for TDD steps includes: "current TDD phase matches expected state (Red before Green, Green before Refactor)."

**Risk of current design**: TDD discipline is self-enforced. In practice, agents under time pressure may skip Red or produce invalid Red (exception instead of assertion failure). Eval dimension 5 (interaction constraint) scored C — partially attributable to discipline erosion.

**Effort**: Small — format change + one verification rule.

**Defer rationale**: TDD compliance is a model behavior issue, not a protocol structure issue. Adding tracking format helps visibility but doesn't force compliance — the agent still self-reports. More impactful to improve eval coverage for TDD steps first, then add tracking if eval shows systematic skipping.

---

## Priority for Next Round

1. **Run updated eval** — quantify effect of this round's changes (loop termination, assumption tracking, QA GATE alignment)
2. **#5 (upstream consumed)** — small effort, addresses silent constraint loss
3. **#6 (TDD tracking)** — small effort, but validate with eval first
4. **#4 (information-gap triggers)** — medium effort, needs careful design to avoid new ambiguity
