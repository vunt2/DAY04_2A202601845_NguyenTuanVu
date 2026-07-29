---
name: tech_news
track: core
kind: live_api
provider: Hacker News Firebase API
requires_env: []
inputs: [mode, limit, query]
outputs: [items, source_url]
side_effect: false
---
# tech_news

Retrieves current technology stories from the public Hacker News API. Use
`mode="top"` for ranked top stories or `mode="new"` for the newest stories.
Optionally provide `query` to keep only stories whose title or text contains
the supplied words. This tool is read-only and needs no API key.

