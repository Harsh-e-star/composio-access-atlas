# Audit report: Composio Access Atlas (2026-11-23)

## Scope
100 apps × 6 fields = 600 field records (`composio_100_apps_full_export.csv`). The integrity checks pass: 100 unique IDs, 10 categories × 10 apps, 6 fields per app, no duplicate app–field pairs. Pass A and pass B records in `data/runs/` are unchanged.

## What produced the data
| Layer | Who | Coverage |
|---|---|---|
| Pass A research | LLM (Claude Sonnet) over pages our fetcher retrieved | 96/100 apps |
| Pass B research | LLM agent (Claude Haiku) with web search | 100/100 apps |
| Evidence re-check | Code: quote must appear on the re-fetched page | 782/847 quotes found |
| Reconciliation R0–R4 | Code rules | 69 field changes |
| External AI review | A separate AI reviewer (files in `data/audit/external_ai_review/`) | Screened 600 fields; source-checked 25 |
| Source re-check of that review | Code: re-fetch each official page, check the key terms are present | 21 proposals |
| Human | Project author | Informal spot check, self-reported |

## External AI review: decisions (`data/audit/composio_verified_corrections.csv`)
- **Accepted (17 fields), applied as rule R5:** Zoho CRM protocols/breadth/MCP; Freshdesk auth; Help Scout auth and protocols (webhooks ≠ WebSocket); Gladly auth; Zoho Cliq auth/protocols/MCP; Google Ads protocols (REST; gRPC, WebSocket removed); Mailchimp official MCP (documentation-search MCP only, not account actions); Airtable protocols (WebSocket removed); Jira auth/protocols/breadth; monday.com protocols (GraphQL only).
- **Deferred (4), not applied:** Salesforce auth and protocols (the official page returns HTTP 403 to automated requests); QuickBooks access tier and protocols (the page is JavaScript-only and our fetcher gets no text). These need a human check.
- **Identity:** Paygent Connect's cited sources document NMI, which is not established as the assigned product. Marked PRODUCT_IDENTITY_UNRESOLVED, so its verdict is UNKNOWN.
- Pass A and pass B values are never modified. Every change is logged in `atlas.json → meta.corrections`.

## Accuracy (labelled separately; nothing measured over all 600 fields)
- **AI-referenced** (external AI review with sources re-fetched by us; *not* human ground truth): first pass **4/21**, loop-corrected **4/21**. This is a non-random sample of fields the reviewer flagged as suspect plus 4 confirmations. "Corrected" means the loop's output *before* R5, to avoid leakage. Conclusion: the loop did not catch these errors, so they were corrected explicitly.
- **Human:** self-reported manual spot-check accuracy: **90% (18/20)**. The 20 items are not yet itemised (`data/audit/human_spotcheck_log.csv`), so this is not reproducible yet and is not attributed to any app or field. It is not a first-pass vs corrected comparison.
- **Structured human audit:** 60 checks (20 apps × auth, access, protocols) in `data/audit/composio_human_review_sample.csv`. Pending.

## Remaining uncertainty
- 13 apps are RESEARCH FURTHER; 45 A/B contradictions are open.
- 4 corrections are deferred, and Paygent Connect's identity is unresolved.
- Official-MCP count (82) is an upper bound; documentation-only MCPs (Mailchimp, HubSpot dev tooling, BigCommerce docs) are counted as official but are not account-action servers.
- Stage 6 checks that a quote exists on the page, not that it supports the claim.

## Engineering
- 49/49 tests pass (`python -m pytest tests`).
- Gemini (`gemini-3.5-flash`) and Groq (`openai/gpt-oss-120b`) were verified live with `--llm-check`. Gemini → Groq fallback was observed live on an HTTP 503.
- Secrets: keys live only in the git-ignored `.env`; the scan below checks tracked files and history.
