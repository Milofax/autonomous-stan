---
name: context7
description: >
  Live documentation for 60,000+ public libraries via Context7 MCP.
  Use INSTEAD of training knowledge for any framework, library, or SDK.
  Current API docs, code examples, migration guides — always up to date.
triggers:
  - "docs for"
  - "API reference"
  - "how does X work"
  - "current syntax"
  - "library docs"
  - "code example"
  - "best practice for"
  - "latest version"
  - "migration guide"
---

# Context7 — Live Library Documentation

Current documentation for 60,000+ libraries. Use INSTEAD of training knowledge for any public framework, library, or SDK.

## Why Context7?

Training data is stale. Context7 has **live docs** — the API reference, code examples, and migration guides for the **current** version. When you need library-specific information, Context7 is faster and more accurate than web search.

## Tools

| Tool | Purpose |
|------|---------|
| `resolve-library-id` | Find the Context7 ID for a library name |
| `query-docs` | Get documentation snippets for a library + topic |

## Workflow

### Standard: Resolve → Query

```
1. resolve-library-id(libraryName: "next.js")
   → "/vercel/next.js"

2. query-docs(
     context7CompatibleLibraryID: "/vercel/next.js",
     topic: "app router",
     tokens: 5000
   )
```

### Direct Query (known ID)

```
query-docs(
  context7CompatibleLibraryID: "/anthropics/claude-code",
  topic: "hooks",
  tokens: 10000
)
```

## Popular Library IDs

| Library | ID | Tokens |
|---------|----|----|
| Next.js | /vercel/next.js | 583K |
| Vercel AI SDK | /vercel/ai | 898K |
| Claude Code | /anthropics/claude-code | 214K |
| shadcn/ui | /websites/ui_shadcn | 258K |
| Prisma | /prisma/docs | 953K |
| LangGraph | /langchain-ai/langgraph | 712K |

**61,920+ libraries indexed** — use `resolve-library-id` for anything not listed.

## Parameters

### query-docs

| Parameter | Required | Description |
|-----------|----------|-------------|
| `context7CompatibleLibraryID` | Yes | Library ID from resolve step |
| `topic` | No | Filter to specific topic |
| `tokens` | No | Max tokens to return |

### resolve-library-id

| Parameter | Required | Description |
|-----------|----------|-------------|
| `libraryName` | Yes | Library name to look up |

## Tips

1. **Use topic filter** — reduces tokens, increases relevance
2. **Set token budget** — prevents context overflow
3. **Cache library IDs** — reuse across queries
4. **Be specific** — "authentication" beats "how to build app"

## When to Use

- ✅ API documentation for any public library
- ✅ Code examples and patterns
- ✅ Migration between versions
- ✅ Framework-specific best practices
- ❌ General programming concepts (use web)
- ❌ Private/internal documentation
- ❌ Historical versions (only current docs)
