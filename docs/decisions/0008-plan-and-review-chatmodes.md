# 0008 — Plan and Review chat modes

Date: 2026-08-19
Status: Accepted

## Context

Two workflows recur:

1. Long planning sessions where the maintainer wants the agent to research
   widely (fetch web, SSH into a VPS, curl APIs, inspect Docker) but not
   change anything.
2. Code reviews focused on over-engineering, reusability, and
   industry-standard practices — not just correctness.

The default agent mode allows editing files and running any command. It's the
wrong shape for both workflows.

## Decision

Two custom chat modes in `.github/chatmodes/`:

**Plan** — allows read + research tools including `run_in_terminal` (for SSH,
curl, docker inspection), forbids all edit/create/install tools. System prompt
mandates read-only terminal use. Combined with `run_in_terminal` staying off
`chat.tools.autoApprove` in `.vscode/settings.json`, every shell command
surfaces a confirm dialog as a safety net.

**Review** — read-only. Enforces four checks in a specific order:

1. Over-engineering (loads `ponytail-review` skill)
2. Reusability / no redundancy (uses `vscode_listCodeUsages` on every non-trivial function)
3. Industry-standard practices (PEP 8, type hints, Pydantic v2, thin routes, strict TS, one-line comments, naming, error handling, test discipline)
4. Layout (files over 300 lines mixing concerns, dumping-ground utils)

Output shape: one line per finding, grouped by delete / merge / rewrite / nit.

## Consequences

**Enables**

- Safe research sessions without accidentally editing files
- Consistent review output focused on what humans miss

**Rules out**

- Nothing meaningful — modes are opt-in, default mode is unchanged

## Trade-offs

- Terminal in Plan mode is technically write-capable. Mitigated by the
  system prompt + the auto-approve confirm dialog. Not a hard sandbox.

## Alternatives considered

- Prompt-only review: works but has to be re-typed every time.
- Separate agent tool per phase: over-complicates a two-workflow problem.
