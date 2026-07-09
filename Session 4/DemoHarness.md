# DemoHarness Rules

> Auto-accumulated lessons.

---

## [R001] After any read_file for a refactor task, immediately appl...
**Logged:** 2026-07-08 15:51 | **Category:** tool_usage | **Uses:** 0 | **Helpful:** pending

After any read_file for a refactor task, immediately apply edits with write_file or edit_file, then output a final summary with before/after line counts.

> Agent stops after discovery/read and never writes the refactored file or reports results.

---

## [R002] Treat any task verb like 'refactor' as requiring a concre...
**Logged:** 2026-07-08 15:51 | **Category:** general | **Uses:** 0 | **Helpful:** pending

Treat any task verb like 'refactor' as requiring a concrete file modification, not just exploration; finish the loop by writing the changed file back to disk.

> Agent performed discovery steps but treated the task as complete without performing the actual mutation.

---

## [R003] When verifier coaching specifies concrete next steps, exe...
**Logged:** 2026-07-08 15:51 | **Category:** verification | **Uses:** 0 | **Helpful:** pending

When verifier coaching specifies concrete next steps, execute all of them in order including the final write/summary, not just the early discovery steps.

> Agent executed coach's first steps then stopped instead of completing the prescribed edit and report.

---

## [R004] Always read file fully before claiming
**Logged:** 2026-07-08 15:53 | **Category:** tool_usage | **Uses:** 0 | **Helpful:** pending

Always read file fully before claiming

> manual entry via /log_mistake

---
