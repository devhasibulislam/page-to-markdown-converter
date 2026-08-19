# 0007 — Copilot-only, no cross-agent mirrors

Date: 2026-08-19
Status: Accepted

## Context

The `agents.md` convention is a cross-tool standard: Copilot, Claude Code,
Codex CLI, Cursor, Aider, and Amp all read `AGENTS.md` at repo root. We
considered making `AGENTS.md` the canonical instruction file with
`.github/copilot-instructions.md` as a pointer.

The maintainer works exclusively in Copilot. Cross-tool support is a benefit
only if we actually use those other tools.

## Decision

`.github/copilot-instructions.md` is the single source of truth for agent
instructions. No `AGENTS.md`. No `.claude/CLAUDE.md`. Human-facing docs
(`README.md`, `CONTRIBUTING.md`) stay separate.

## Consequences

**Enables**

- One instruction file to maintain
- Copilot-native path with no indirection

**Rules out**

- Automatic pickup by Claude Code, Codex, Cursor, Aider, Amp
- Contributors using other agents get zero repo-specific context by default

## Reversal path

Trivial: if we adopt another agent, add `AGENTS.md` at repo root as either a
symlink or a copy of `.github/copilot-instructions.md`, and add a
`.claude/CLAUDE.md` pointer. No code change required.

## Alternatives considered

- `AGENTS.md` canonical, Copilot points to it: extra file to maintain now.
- Mirror all three: three files in sync forever.
