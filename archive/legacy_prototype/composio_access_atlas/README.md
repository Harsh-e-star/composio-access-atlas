# Access Atlas / 100 — Composio AI Product Ops research prototype

**Important status (23 November 2026):** This is an honest, reproducible **prototype**, not a completed or deployed 100-app research run. It includes all 100 assigned apps; **41** entries have source-reviewed annotations and official documentation hyperlinks, while **59** remain in the research queue. A runnable two-pass online research agent is included but **has not been run** in this offline environment. There is no invented repo URL, live URL, Composio credential, or measured 100-app AI-agent accuracy.

## Included files

- `index.html` — **single standalone HTML case study**, no server or CDN required. Includes searchable/filterable 100-app matrix, stats computed only on source-reviewed records, clickable evidence, CSV/JSON exports, agent architecture and transparent audit.
- `data/apps.json` — 100 seed records, one per app, with citations and missing-data flags.
- `data/audit.json` — 14-app, 42-field deterministic baseline audit and correction record.
- `scripts/build_data.py` — regenerate the source-labelled dataset.
- `scripts/audit.py` — regenerate exact baseline-vs-reviewed-sample figures.
- `scripts/research_agent.py` — native-web-search researcher + independent skeptic + disagreement escalation, resumable JSON checkpoint after each app. **Requires API credentials / network.**
- `scripts/build_html.py` — regenerate the self-contained HTML page from dataset + audit. Embeds `data/agent_results.json` drafts if available and labels them as non-human-verified.
- `tests/test_data.py` — data-integrity, reproducibility, classification, and citation sanity checks.

## Open the case study immediately

Open `index.html` in any modern desktop/mobile browser, or host it statically (`python -m http.server 8000` and open <http://localhost:8000>). It works offline except clicking evidence URLs.

## Generate and check the local dataset

```bash
python scripts/build_data.py
python scripts/audit.py
python scripts/build_html.py
python -m unittest discover -s tests -v
```

## Execute the research agent (5-app test, then full remaining queue)

Python 3.11+ recommended. Online research uses the **OpenAI Responses API web search tool**, which has usage costs. Start with **5** to check model behavior and cost; do not accidentally fire 200 search calls without checking billing.

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python scripts/research_agent.py --start 1 --limit 5
# Check data/agent_results.json; then cover the research queue:
python scripts/research_agent.py --start 1 --limit 100 --only-unknown
python scripts/build_html.py
```

The second command is resumable: existing per-app results are skipped. Each run does two separate web-supported research calls per new app. The researcher returns field-level evidence links; the skeptical checker re-queries official documentation, corrects doubtful claims, and flags disagreements. Schema checks reject malformed URLs and normalize access/MCP labels. Errors are checkpointed rather than hidden. **Agent-corroborated** is intentionally not the same as **human verified**: uncertain entries and independent random holdout samples must be checked manually before final submission.

## Sampling and accuracy: do not misrepresent

The dashboard's `40.5% → corrected on checked cases` section is **a rule-based heuristic baseline** tested against **14 source-reviewed cases × 3 fields** (not an executed AI agent). The baseline guessed an auth mechanism, access tier and API surface. It agreed on 17/42 fields. The human adjudication replaced wrong values with inspected official-doc labels, so 42/42 checked cells now reflect those same adjudicated labels **by construction**. This is *not* independent model accuracy or a valid holdout improvement claim. It is a reproducible evidence of specific error types (e.g., DataForSEO is HTTP Basic; LinkedIn Ads access is tiered; Mermaid is local CLI).

**For the final submission:** run the actual research agent and retain its first_pass vs second_pass outputs. Pick a **random 15–20 app holdout** from all 100, stratified by category and access complexity, *before* looking at second-pass labels. Manually verify `auth`, `access`, `surface` and `MCP` against official docs, recording source URLs and date. Report field agreement and coverage separately, include raw disagreements and whether the checked sample was used for fixes. Re-sample an independent holdout after fixes; if you only re-check the same items, label it a regression set, not held-out accuracy.

## Product methodology

1. **Record access dimensions independently:** OAuth vs API key/token; self-serve *development* vs production approval; protocol; official MCP vs third-party; local CLI vs hosted API.
2. **Explicit unknowns:** docs URL not located ≠ no API. Source-reviewed only means the cited official pages were inspected and conclusions derived from them; it does not mean live credential tests were executed.
3. **Action buckets:** ship self-serve experiments; test account/tenant-gated ones; request approvals or licensing for restricted products; reuse MCP/CLI whenever appropriate.
4. **Evidence links:** every doc-reviewed row includes an official URL (sometimes more than one). Some commercial-gating claims warrant a second primary source and live signup check before shipment.
5. **Restrictions:** robots, rate limits, terms, and scope review matter for scraping/communication tools. Do not send production messages or access user data during research.

## Optional Composio MCP extension (not implemented or run)

Composio's current Python SDK supports a session MCP endpoint with `composio.create(user_id, mcp=True)` and `session.mcp.url`/`headers` (see [sessions via MCP](https://docs.composio.dev/docs/sessions-via-mcp)). You can attach existing Composio research/browser tools to an MCP-capable agent; avoid claiming this is integrated until it is run with a real session and shown in logs. The base pipeline is valid without it, as allowed by the assignment.

## Deploy and submit (manual actions)

1. Create a **public** GitHub repository, add this project, and commit the evidence-backed revisions.
2. Deploy the **single `index.html`** with GitHub Pages, Netlify or Vercel. A local `file://` preview is not a live link.
3. Include the live page and repository URLs in the Composio submission form. **Replace this prototype with a fully researched and independently audited run before presenting it as complete.**

## Source methodology and caveats

Docs reflect a snapshot from **23 November 2026**. Vendor policies change. The project did not programmatically fetch official pages from this offline Python runtime; initial first-party document research was performed using web retrieval and recorded as curated JSON. In particular, HubSpot service keys and Zendesk's API-token retirement have current transition policies, so stale generic summaries are risky. Some rows have only one supporting documentation URL for multiple claims; treat commercial access as a follow-up verification item.
