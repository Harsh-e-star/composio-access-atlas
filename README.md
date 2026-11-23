# Composio Access Atlas

An evidence-grounded research agent that maps **100 apps** for Composio: auth methods, how a developer gets credentials (self-serve vs gated), API surface, MCP availability and a buildability verdict. Every claim cites a source URL and a verbatim quote, and the quote is re-checked against the live page.

- **Case study (single HTML page):** `docs/index.html` (also `case_study.html`) · live: https://harsh-e-star.github.io/composio-access-atlas/ · repo: https://github.com/Harsh-e-star/composio-access-atlas
- **Run the agent:** `python -m agent.main --app GitHub`

> `archive/legacy_prototype/` holds an **earlier prototype**. It used hand-written records, a simulated agent (timed `asyncio.sleep` steps) and accuracy figures that no real audit supported. It is **not** the submission and none of its numbers are used here. The real system is `agent/` + `data/` + `docs/`.

## What it does

```
registry (100 apps from the brief)
  └─ Stage 1  Discovery        deterministic   fetch brief's seed URLs, probe developer subdomains,
  │                                            score links (auth/pricing/MCP…), Playwright for JS docs,
  │                                            GitHub search for MCP repos; LLM web-search only if no URL
  └─ Stage 2-4 Extraction      LLM (Sonnet)    one structured call per app over the fetched pages:
  │                                            API surface, auth, access – each claim = URL + verbatim quote
  └─ Stage 6  Evidence check   deterministic   re-fetch each cited URL, confirm the quote is on the page
  └─ Stage 5  Buildability     deterministic   rules: tier + protocol → READY/CONDITIONAL/GATED/NO IFACE/UNKNOWN
Pass B  Independent research   LLM (Haiku)     web search + fetch from the app name only; never sees pass A
Reconcile                      deterministic   rules R0–R4 (change a field only when the other pass has
                                               verified evidence; unverified conflicts → unknown)
Human audit                    human           stratified 20-app × 6-field worksheet; the only accuracy measure
```

**Where a human is needed:** ground-truth labels for the audit, apps whose docs block automated access (e.g. Salesforce developer docs return HTTP 403 to bots, and the agent does not evade that), and every flagged contradiction.

## Quick start

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m playwright install chromium
# LLM backend: a logged-in Claude Code CLI (`claude`), or `export ANTHROPIC_API_KEY=...`
```

| Command | What it does |
|---|---|
| `python -m agent.main --app GitHub` | research one app (pass A) |
| `python -m agent.main --limit 5` | five-app trial |
| `python -m agent.main --all --resume` | all 100, skipping apps already done; failed ones retried |
| `python -m agent.main --all --pass b` | independent second pass |
| `python -m agent.main --verify` | Level 1 checks, A↔B comparison, reconciliation, audit worksheet, scoring |
| `python -m agent.build_site` | rebuild `docs/index.html`, `case_study.html`, `exports/`, README results |
| `python -m pytest tests` | software + browser tests |

**AI providers.** Copy `.env.example` to `.env` (git-ignored) and set any of `GEMINI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, or use a logged-in Claude Code CLI. With `AI_PROVIDER=auto` the agent tries Gemini → Groq → Anthropic → Claude CLI and falls back on quota or rate-limit errors. Every saved record names the provider that answered. Check your setup with `python -m agent.main --llm-check`. The independent pass B needs web search, which only the Claude CLI provider has. The 100-app run in `data/` used Claude (Sonnet for pass A, Haiku for pass B). Gemini and Groq support was added afterwards and is covered by mocked tests only until it is run with a key.

## Outputs

| Path | Contents |
|---|---|
| `data/runs/pass_a/NNN.json`, `data/runs/pass_b/NNN.json` | raw per-app records (sources, claims, verification, cost, duration) |
| `data/final/first_pass_snapshot.json` | pass A exactly as produced, never modified |
| `data/final/atlas.json` | reconciled dataset + corrections log + Level 1 issues |
| `data/audit/human_audit_worksheet.csv` | human audit sheet (fill `human_ground_truth`, `reviewer`, `review_date`, then `--verify`) |
| `data/logs/trace.jsonl`, `data/logs/requests.jsonl` | per-stage trace and every HTTP request |
| `exports/composio_100_apps.{csv,json}` | flat export |
| `composio_100_apps_full_export.csv` | 600 field-level rows (first pass, second pass, final, evidence status) |
| `data/audit/external_ai_review/` | external AI review inputs + our source re-check + correction decisions |
| `data/audit/composio_verified_corrections.csv` | accepted / deferred corrections with sources |
| `data/audit/composio_accuracy_evaluation.json` | AI-referenced and human results, labelled separately |
| `data/audit/composio_human_review_sample.csv`, `human_spotcheck_log.csv` | 60-check human worksheet; log for the 20 self-reported checks |

## Verification and evaluation integrity

1. **Level 1 (deterministic):** IDs/categories/names, allowed labels (Pydantic), primary auth ∈ methods, official MCP has a URL, tier vs flag consistency, identity confirmed. These checks do not establish facts.
2. **Level 2 (independent pass):** pass B re-researches every app blind. Each field is compared as agree / partial / contradiction / insufficient. Agreement is not treated as correctness.
3. **Reconciliation** (fixed before any human labels existed): R1 fill an unknown from verified B evidence · R2 union of auth/protocol sets when B's extra items are verified · R3 take B when only B is verified · R4 set to unknown and flag when neither side is verified. Pass A's original output is preserved.
4. **Level 3 (human):** a deterministic stratified sample (2 per category, seed `atlas-2026`, one A/B-disagreement app per category where one exists). Accuracy = correct fields / evaluated fields, and "unknown" is never credited. **No accuracy is reported until a human fills the worksheet.** The before/after is measured on the same sample, so it is not a held-out estimate.

Unit tests passing ≠ research being correct.

<!-- RESULTS:START -->
## Results (generated 2026-11-23T16:54:32Z)

- Apps researched by pass A: **96/100** succeeded; independent pass B: **100/100**.
- Verdicts: READY 71, CONDITIONAL 11, GATED 5, NO_SUPPORTED_INTERFACE 0, UNKNOWN 13 (of 100).
- Groups: RESEARCH FURTHER 13, BUILD NOW 71, BUILD WITH PREREQUISITES 11, OUTREACH REQUIRED 5.
- Access tier: free_self_serve 65, trial_self_serve 10, paid_plan 6, admin_approval 6, partner_or_sales 6, unknown 7.
- Auth methods (multi-label, of 100): OAuth2 78, API key 48, Bearer/PAT 51, Basic 19, Service account/JWT 7, Other 15; 77 apps support more than one method; 4 unknown.
- Official vendor MCP: **82** apps; unknown 7; community MCP found for 85.
- Evidence: 782/847 quotes re-verified on the live page; 434/500 core fields backed by a verified quote (86.8%).
- A↔B field comparison: insufficient 210, partial 67, agree 278, contradiction 45.
- Corrections applied by reconciliation: 87 field changes.
- Cost: $12.38 total LLM spend, $0.124 per app (both passes); 124.0 s per app (both passes, wall time).
- **Human review:** self-reported manual spot check 18/20 (90%), items not yet itemised (`data/audit/human_spotcheck_log.csv`); structured 60-check audit pending (`data/audit/composio_human_review_sample.csv`).
- **AI-referenced check** (external AI review, official pages re-fetched; not human): first pass and loop-corrected both 4/21 on fields flagged as suspect; 17 re-verified corrections applied as rule R5, 4 deferred, Paygent Connect identity unresolved.
<!-- RESULTS:END -->

## Known limitations

- Stage 6 proves a quote **exists** on the cited page, not that it **supports** the value; only the human audit checks support.
- Bot-protected docs (HTTP 403 / robots.txt) are not bypassed; those fields stay unknown unless pass B's evidence verifies.
- Pass B is a different model, but from the same vendor, so the two passes can share errors.
- Discovery is keyword-scored; a relevant page without the keywords can be missed. Page text is truncated to keyword-dense windows.
- Customer demand is unknown, so groups reflect feasibility only and are not a roadmap.
- Results are a snapshot of the docs at the `researched_at` time.

## Deploy (GitHub Pages)

`docs/index.html` is self-contained (data embedded, no external scripts). Push the repo, then go to Settings → Pages → Source: `main` / `/docs`.
