---
name: graphiti
description: >
  Long-term knowledge graph via Graphiti MCP. Store and retrieve learnings,
  decisions, contacts, preferences, goals. Semantic search across 18 entity types.
  ALWAYS search_nodes() BEFORE answering questions about stored knowledge.
triggers:
  - "who is"
  - "what do you know"
  - "do you remember"
  - "save this"
  - "learning"
  - "decision"
  - "contact"
  - "remember"
  - "recall"
  - "wer ist"
  - "was weisst du"
  - "kennst du"
  - "speicher"
  - "ich habe gelernt"
  - "entscheidung"
  - "kontakt"
---

# Graphiti — Long-Term Knowledge Graph

Store and retrieve personal knowledge: contacts, learnings, decisions, preferences, goals.

## Core Rule: Search Before Answering

**ALWAYS** call `search_nodes()` before answering questions about stored knowledge.
NEVER guess or invent — search first, then answer.

## Tools

| Tool | Purpose |
|------|---------|
| `add_memory` | Store knowledge (automatic entity extraction) |
| `search_nodes` | Semantic search for entities |
| `search_memory_facts` | Search for facts/relationships (edges) |
| `get_entity_edge` | Get relationship details |
| `get_episodes` | List all episodes |
| `delete_entity_edge` | Delete a relationship |
| `delete_episode` | Delete an episode |
| `clear_graph` | **FORBIDDEN** — never delete knowledge |

## Entity Types (18)

Person · Organization · Location · Event · Project · Requirement · Procedure · Concept
Learning · Document · Topic · Object · Preference · Decision · Goal · Task · Work · Revision

### Key Distinctions

- **Concept vs Learning**: Concept = external knowledge ("OKRs exist") · Learning = personal experience ("OKRs didn't work for us")
- **Decision vs Preference**: Decision = made + justified · Preference = opinion without decision
- **Task vs Goal**: Task = concrete action · Goal = outcome to achieve
- **Work vs Document**: Work = creative work experienced ("reading this novel") · Document = source cited ("according to RFC...")
- **Revision**: Software version tied to a learning ("React 18: concurrent features stable")

## Workflow

### Storing Knowledge

```
add_memory(
  name: "[descriptive name]",
  episode_body: "[full details]",
  source_description: "[source — REQUIRED]",
  group_id: "[project-group or main]"
)
```

**Rules:**
- **ALWAYS include source_description** — knowledge without source is contaminated
- **NEVER store credentials** (passwords, API keys, tokens) — belongs in 1Password
- **Save learnings IMMEDIATELY** when a bug is solved, pattern discovered, or gotcha found

### Retrieving Knowledge

```
search_nodes(
  query: "...",
  group_ids: ["main"],        # or ["main", "Owner-RepoName"]
  entity_types: ["Learning"],  # optional filter
  max_nodes: 10               # default
)
```

- Empty results? Broaden query, remove entity_types filter
- Personal info not found? "I don't have that stored. Want to tell me?"
- General info not found? Research via web → save with source → answer

## Group IDs

- **`main`**: Permanent, cross-project knowledge (contacts, general learnings, preferences)
- **`Owner-RepoName`**: Project-specific knowledge (requirements, procedures, architecture)
- Format: Owner-RepoName with HYPHEN (not slash!) — e.g., `Milofax-taming-stan`

**Decision rule:** "Will I still want to know this in 5 years?" → Yes = `main`

## 3-Strikes Integration

After 3 tool errors: search Graphiti BEFORE retry. Existing learnings might solve the problem.

## Version Rule

For technical learnings, include the version: `"React 18: concurrent features are stable"` — software changes, unversioned knowledge becomes unreliable.
