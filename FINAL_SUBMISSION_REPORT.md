# Final submission report: Composio Access Atlas

- **Live page:** https://harsh-e-star.github.io/composio-access-atlas/
- **Repo:** https://github.com/Harsh-e-star/composio-access-atlas
- **Verdict:** CONDITIONAL GO. Ready to submit; the open items below are disclosed on the page.

## Results
| Item | Value |
|---|---|
| Apps / categories / fields | 100 / 10 (10 each) / 600 field rows; no duplicates or gaps |
| Researched by agent | Pass A 96/100, independent pass B 100/100 (real LLM calls on fetched docs) |
| Evidence | 782/847 quotes found on the re-fetched page; 434/500 core fields backed by a verified quote |
| Verdicts | READY 71 · CONDITIONAL 11 · GATED 5 · UNKNOWN 13 |
| Corrections | 69 by the verification loop (R0–R4); 17 from the external AI review after re-fetching the official source (R5); 4 deferred; 1 identity marked unresolved |
| AI-referenced accuracy | First pass 4/21, loop-corrected 4/21 on fields the AI reviewer flagged as suspect (AI review, not human) |
| Human review | **Self-reported manual spot-check accuracy: 90% (18/20)**, items not yet itemised; structured 60-check audit pending |

Old unsupported figures (43.3% → 98.3%, "Human Verified") appear nowhere except the labelled `archive/`.

## Tests and checks (run 2026-11-23)
- `python -m pytest tests`: **49 passed**. This covers the registry, fetch/retry/robots, schema, verdict rules, reconciliation, the scorer, the LLM provider chain (7 tests use **mocked** HTTP), and Playwright browser tests of the page.
- **Live LLM:** `python -m agent.main --llm-check` was answered by Gemini (`gemini-3.5-flash`). Groq (`openai/gpt-oss-120b`) answered live earlier, and live Gemini→Groq fallback was observed on an HTTP 503.
- **Live research run:** GitHub and LinkedIn Ads researched end to end via Gemini (`data/runs_gemini_demo/`). The full 100-app run used Claude and is recorded in `data/logs/trace.jsonl`.
- **Links:** live page, repo and README return 200. 527 evidence and MCP links checked, 0 malformed.
- **Secrets:** 0 key strings in the page, exports, tracked files or git history. `.env` is git-ignored.
- **Page:** no JavaScript errors; no sideways scroll at 375px.

## Unresolved (disclosed on the page)
- 4 deferred corrections: Salesforce auth and protocols (site returns 403 to bots), QuickBooks access tier and protocols (JS-only docs).
- Paygent Connect product identity is unresolved (sources describe NMI).
- 13 apps are RESEARCH FURTHER; 45 pass-A/pass-B contradictions are open.
- Official MCP (82) is an upper bound; some are documentation-only servers.
- The quote check proves a quote exists on the page, not that it supports the claim.
- The independent pass B depends on Claude's web search.

## Remaining manual actions
1. Optional: list your 20 spot-checked items in `data/audit/human_spotcheck_log.csv` so the 18/20 becomes reproducible.
2. Approve the push; then confirm the live page shows the update.
3. Submit the two links.
4. Rotate the Gemini and Groq API keys after submission.
