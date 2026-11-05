# The Claude Code Ecosystem — a field guide

**Live site:** https://ravaniroshan.github.io/claude-code-ecosystem-guide/

A curated, single-page map of the open-source layer that has grown around
Claude Code — and, more broadly, around agentic coding harnesses. It catalogues
**118 repositories** across **11 domains**: foundations, skill packs, memory &
context, design, video, music & audio, images & 3D, documents, web research,
business ops, and specialist domains.

## What's inside

- **118 repos**, sorted by domain, then by GitHub stars
- Live **search** and **domain filter chips**
- Editorial "what it actually does" and "point it at" notes for every repo
- Three composed **recipe pipelines** (reel factory, explainer studio, launch kit)
- Dark mode (follows your system preference), zero dependencies, one file

## Data notes

Star counts were pulled straight from the GitHub REST API on
**5 November 2026** — not from a blog post. Descriptions are editorial
summaries, not quotes.

## Run locally

It's a single self-contained HTML file:

```bash
# open directly…
start index.html        # Windows
open index.html         # macOS

# …or serve it
python -m http.server 8000
```

## Disclaimer

Not affiliated with Anthropic. Inclusion in this guide is not an endorsement.
Check each project's license before building on it — media-generation repos
especially, where model weights and code often carry different terms.
