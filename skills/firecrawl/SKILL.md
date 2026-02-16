---
name: firecrawl
description: >
  Web scraping, search, and structured data extraction via Firecrawl MCP.
  Scrape JS-rendered pages, extract structured data, crawl/map websites.
  Handles anti-bot mechanisms, proxies, and dynamic content automatically.
triggers:
  - "scrape"
  - "crawl"
  - "extract data"
  - "map site"
  - "web search"
  - "parse URL"
  - "structured extraction"
  - "site analysis"
  - "get content from"
---

# Firecrawl — Web Scraping & Data Extraction

Scrape any URL into clean markdown, search the web with content extraction, extract structured data. Handles JS-rendered pages, anti-bot mechanisms, and proxies automatically.

## Tools

| Tool | Purpose | Best For |
|------|---------|----------|
| `firecrawl_scrape` | Scrape single URL | Known page extraction |
| `firecrawl_search` | Web search + extraction | Finding information |
| `firecrawl_map` | Discover URLs on a site | Sitemap creation |
| `firecrawl_crawl` | Crawl multiple pages | Multi-page extraction |
| `firecrawl_extract` | Structured data extraction | Schema-based extraction |
| ~~`firecrawl_agent`~~ | ~~Autonomous agent~~ | **DON'T USE** (timeouts) |

## Most Common: Scrape

```json
{
  "url": "https://example.com",
  "formats": ["markdown"],
  "onlyMainContent": true,
  "maxAge": 172800000
}
```

| Parameter | Description |
|-----------|-------------|
| `url` | URL to scrape (required) |
| `formats` | `["markdown", "html", "screenshot", "links"]` |
| `onlyMainContent` | Skip navigation/footer (recommended) |
| `maxAge` | Cache age in ms (172800000 = 2 days, 500% faster!) |
| `waitFor` | Wait for JS rendering in ms |
| `actions` | Interactions before scraping (click, scroll, etc.) |

### Document Parsing

Firecrawl auto-parses documents by URL extension:
- **PDF**: Text + OCR for scans (1 credit/page)
- **Excel**: `.xlsx`, `.xls` → HTML tables
- **Word**: `.docx`, `.doc`, `.odt`, `.rtf`

## Search (Web + Extract)

```json
{
  "query": "latest AI research 2025",
  "limit": 5,
  "sources": [{"type": "web"}, {"type": "news"}],
  "scrapeOptions": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

**Sources** (optional, as object array):
- `{"type": "web"}` — Web search (default)
- `{"type": "news"}` — News
- `{"type": "images"}` — Images

**Search operators:** `""` exact phrase · `-` exclude · `site:` domain · `inurl:` · `intitle:`

## Map → Scrape Workflow

```
1. firecrawl_map(url: "https://docs.example.com", limit: 100)
   → List of all documentation URLs

2. Filter relevant URLs

3. firecrawl_scrape for each relevant URL
```

## Structured Extraction

```json
{
  "urls": ["https://example.com/product"],
  "prompt": "Extract product information",
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "price": {"type": "number"},
      "description": {"type": "string"}
    },
    "required": ["name", "price"]
  }
}
```

## Actions (Dynamic Pages)

For pages with login, buttons, etc:

```json
{
  "url": "https://example.com/login",
  "actions": [
    {"type": "write", "text": "user@email.com"},
    {"type": "press", "key": "Tab"},
    {"type": "write", "text": "password"},
    {"type": "click", "selector": "button[type='submit']"},
    {"type": "wait", "milliseconds": 2000}
  ]
}
```

Available: `click` · `write` · `press` · `scroll` · `wait` · `screenshot`

## Performance Tips

1. **Use `maxAge`** — cache for 500% faster re-scrapes
2. **`onlyMainContent: true`** — drastically reduces tokens
3. **Map before crawl** — targeted instead of blind crawling
4. **Set limits** — prevents token overflow
5. **Specific selectors** — `includeTags`/`excludeTags` for precision

## Credits (Hobby Tier: $19/mo, 3000 credits)

| Action | Credits |
|--------|---------|
| Scrape | 1 / page |
| Crawl | 1 / page |
| Map | 1 / page |
| Search | 2 / 10 results |
| Extract | [Calculator](https://www.firecrawl.dev/extract-calculator) |

## When to Use

- ✅ JS-rendered pages (React, Vue, etc.)
- ✅ News/article extraction
- ✅ Structured data from web pages
- ✅ Document parsing (PDF, Excel, Word)
- ✅ Site mapping and discovery
- ❌ Simple static pages (WebFetch is faster)
- ❌ Library docs (Context7 is better)
