# Concept: Wiki Operating Model

## Pattern

This repository uses a Karpathy-style LLM wiki:

- raw sources are preserved
- synthesis pages accumulate project knowledge
- schema files guide future agents

The point is to avoid rediscovering project context from scratch every session.

## How To Use It

For orientation:

1. Open [`../index.md`](../index.md).
2. Read [`../overview.md`](../overview.md).
3. Follow the relevant subproject or concept page.
4. Check raw sources only when details matter.

For maintenance:

1. Update synthesis pages when durable knowledge changes.
2. Keep raw sources untouched.
3. Update navigation.
4. Append the log.

## Compounding Rule

Any answer that would save the next session more than a minute should become wiki knowledge.

## Primary Sources

- [`../WIKI_SCHEMA.md`](../WIKI_SCHEMA.md)
- [`../../AGENTS.md`](../../AGENTS.md)
