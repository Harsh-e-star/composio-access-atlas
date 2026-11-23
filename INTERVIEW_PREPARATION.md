# Interview preparation: Composio Access Atlas

This guide covers the system as it is actually implemented in `agent/`. When a number matters, take it from the generated `data/final/atlas.json`, `README.md § Results`, or the live page. Don't quote numbers from memory. Section H at the end holds the run results and gets regenerated after each full run.

---

## A. The project in plain language

**What Composio does.** Composio gives AI agents ready-made tools for third-party apps (Slack, GitHub, Salesforce…). Each app's toolkit bundles authentication handling (OAuth, API keys), a set of actions ("create issue", "send message"), and triggers. Agents call these tools instead of every developer writing their own integration.

**The problem this assignment solves.** Before building a toolkit, someone has to research the app: how auth works, whether a developer can get credentials without paying or asking permission, how big the API is, and whether an MCP server already exists. Doing that by hand for hundreds of apps is slow and inconsistent: two researchers reach different conclusions, and the sources are rarely recorded.

**Who uses this.** Product ops, who decide what to research and track it. Integration engineers, who want the auth and API facts. PMs, who prioritise. Partnerships, who need the list of apps that require outreach.

**What I built.**
1. A Python research pipeline (`python -m agent.main`) that, for each of the 100 apps, fetches the vendor's real documentation, has an LLM extract structured facts, requires a verbatim quote and URL for every claim, and decides a buildability verdict with fixed rules.
2. An independent second pass: a different model with web search, given only the app name, that never sees pass A.
3. A verification layer: Level 1 consistency checks, a quote re-check against the live pages, A-vs-B comparison, evidence-based reconciliation, and a stratified human-audit worksheet with a scorer.
4. A single self-contained HTML case study built from that data (`docs/index.html`).

**Which parts are AI-driven, which are deterministic, which need a human.**

| Part | Driven by |
|---|---|
| Discovery: fetch seed URLs, probe developer subdomains, score links, Playwright rendering, GitHub search | Deterministic code |
| Discovery fallback when the brief gives no URL (Paygent Connect) | LLM with web search (Claude Haiku) |
| Extraction of auth / access / API / MCP facts with quotes (Stages 2–4) | LLM (Claude Sonnet), one structured call per app |
| Buildability verdict, group, blocker, approach (Stage 5) | Deterministic rules in `stages.assess` |
| Evidence check: does the quote really appear on the page (Stage 6) | Deterministic |
| Independent pass B | LLM agent (Claude Haiku) with WebSearch + WebFetch |
| Reconciliation rules R0–R4 | Deterministic |
| Ground truth and accuracy | **Human** (worksheet). The AI never fills it in. |
| Narrative findings text on the page | Written by me and Claude Code from the computed numbers |

Be ready to say clearly: "Stages 1, 5 and 6 are not 'agents'. They're code. Only extraction and pass B are LLM-driven."

---

## B. Technical concepts (beginner to advanced)

**API.** A contract that lets one program ask another for data or actions over the network.

**REST.** APIs built around resources at URLs (`/contacts/123`) and HTTP verbs. Stateless; usually JSON.

**GraphQL.** A single endpoint where the client sends a query naming exactly the fields it wants. Good for nested data; harder to rate-limit and cache. Linear, Shopify, Monday and GitHub (v4) use it.

**gRPC.** A binary RPC protocol over HTTP/2 with Protobuf schemas. Fast; rare in public SaaS APIs.

**HTTP methods.** GET reads, POST creates or acts, PUT replaces, PATCH partially updates, DELETE removes. GET, PUT and DELETE should be idempotent.

**Authentication vs authorization.** Authentication proves *who* you are; authorization decides *what you may do*. OAuth2 is mainly an authorization framework.

**OAuth2.** A user grants a third-party app limited access to their account without sharing their password. The app gets an *access token* scoped to specific permissions.

**Authorization-code flow.** The app redirects the user to the provider's consent screen, which returns a one-time *code* to the app's redirect URL. The app's server exchanges the code plus its client secret for tokens. This is the standard flow for Composio-style multi-tenant integrations.

**PKCE.** Proof Key for Code Exchange. The client sends a hash of a random secret with the authorize request and the raw secret at token exchange, so an intercepted code is useless. Required for public clients (mobile, SPA, CLI) and recommended for everyone.

**Client-credentials flow.** Machine-to-machine; no user involved.

**Access token / refresh token.** Access tokens are short-lived (often 1h) and sent on every call. Refresh tokens are long-lived and swapped for new access tokens. A toolkit platform must store refresh tokens securely and refresh them before they expire. Some providers rotate refresh tokens on each use, which is a common source of bugs.

**Scopes.** Named permissions (`chat:write`, `repo`). They matter for least privilege and for app review: many providers review apps that request sensitive scopes.

**API keys.** Static secrets issued from a dashboard. Easiest to integrate, but long-lived; if leaked, they work until revoked; and they are usually account-wide rather than per-user. That's why the pipeline rates static-key-only access on money or ads surfaces as "high" security risk.

**Personal access tokens (PAT) / private-app tokens.** User-generated bearer tokens that act as you (GitHub PAT, HubSpot private app). Technically bearer tokens, not OAuth.

**Basic auth.** `Authorization: Basic base64(user:pass)`. Some APIs use the API key as the username (Freshdesk, Harvest-style).

**Service accounts / JWT bearer.** A non-human identity signs a JWT with a private key and exchanges it for a token (Google, Salesforce JWT flow). Often needs admin setup.

**Rate limits.** Caps on requests per window, usually signalled by HTTP 429 and `Retry-After`. Toolkits need backoff, which is the same pattern my fetcher uses.

**Webhooks.** The provider calls *your* URL when an event happens. This powers Composio "triggers". Needs a public endpoint and signature verification.

**SDK.** An official client library wrapping the API in a language.

**MCP (Model Context Protocol).** An open protocol (from Anthropic) that standardises how an AI application discovers and calls tools, reads resources and gets prompts from a server. *MCP server*: exposes tools (e.g. GitHub's MCP server exposes "create_issue"). *MCP client*: the AI app (Claude, Cursor) that connects to servers. Transports are stdio (local) or HTTP/SSE (remote). Official vs community matters for Composio: an official server is maintained by the vendor, while community servers vary in quality, auth and security.

**Agent tools / toolkits / tool calling.** The LLM gets a list of tool schemas (name, description, JSON parameters). Instead of text it emits a structured call, the runtime executes it and returns the result. A toolkit is a curated set of tools plus auth for one app.

**Structured output.** Forcing the model to return JSON matching a schema. I pass the Pydantic-generated JSON Schema via `--json-schema` (CLI) or a forced tool call (API), then validate with Pydantic, so bad labels like `"kinda_free"` are rejected (`tests/test_agent.py::test_invalid_llm_output_rejected`).

**Pydantic.** A Python library for typed data models with validation. `schema.py` defines `Extraction`, `Assessment` and `AppRecord`; `Literal[...]` fields restrict values to allowed labels.

**Hallucination.** The model states something unsupported. Mitigations here: the model only sees fetched pages, every claim must carry a verbatim quote and URL, Stage 6 checks the quote exists, "unknown" is the default, and a second independent pass is compared against the first.

**Prompt injection.** Text inside a fetched page trying to instruct the model ("ignore previous instructions…"). Mitigations: system prompts declare page text untrusted, the extraction model has *no tools* (it can't act on an injection, only mis-extract), and outputs are schema-validated. Residual risk: an injection could still bias the extracted values. The quote check and pass B limit the damage.

**Error handling.** Retries with exponential backoff on 429/5xx, `www.` fallback on TLS failures, robots.txt respect, transient failures not cached, per-app errors recorded in the record (`error` field) rather than crashing the run.

**Caching.** `.cache/http/` keys responses by URL hash, so re-runs are cheap and the Stage 6 re-check uses the same snapshot the model saw, unless the cache is cleared.

**Checkpointing / resumability.** Each app writes `data/runs/pass_X/NNN.json` on completion. `--resume` skips apps with a successful file and re-runs failed ones.

**Async execution.** `asyncio` lets many network requests be in flight at once. Workers pull apps from a queue (`--workers`); a semaphore caps concurrency and a per-host lock enforces 1 request/second per domain.

**SQLite / FastAPI / React.** These belong to the *legacy* prototype in `archive/legacy_prototype/`, which I no longer present as the system (it ran on hand-written data). The current deliverable is a static page, a deliberate reliability choice: no server to keep alive, nothing to break during review.

**Deployment.** GitHub Pages serves `docs/index.html` from the repo; the page embeds its data, so it has no backend dependency.

---

## C. Code walkthrough

### `agent/registry.py`
- **Purpose:** the exact 100 apps from the brief, with stable IDs, the category derived from ID (`(id-1)//10`), and seed URLs derived *only* from the brief's hint.
- **`load()`** → list of dicts `{id,name,hint,category,seeds,ambiguous}`.
- **`_seeds(hint)`**: `"harvestapp.com (help.getharvest.com/api-v2)"` → `["https://help.getharvest.com/api-v2", "https://harvestapp.com"]`. `"paygent (NMI-powered)"` → `[]`, which triggers the web-search fallback.
- **Failure modes:** a hint with no domain gives no seeds. **Design reasoning:** seeds are starting points, never evidence. **Improve:** let product ops edit the registry as YAML.

### `agent/fetch.py`
- **`Fetcher.get(url)`** → `{url, final_url, status, title, text, links, error, fetched_at}`. Checks the cache, robots.txt and per-host throttle; retries 429/5xx with 2s/4s backoff; parses HTML to text; logs every request to `data/logs/requests.jsonl`; on a TLS/connect failure for a bare domain, retries `www.` (found when `zoho.com` served a broken certificate chain).
- **`parse_html`**: strips script/style/nav/footer and collects absolute links.
- **`quote_in_text(quote, text)`**: normalises both (lowercase, alphanumerics only) and passes on exact substring match, or for long quotes when ≥50% of overlapping 8-word windows match (tolerates ellipses and formatting).
- **Failure modes:** bot protection (Salesforce developer docs return 403), JS-rendered pages, pages truncated at 60k chars. **Improve:** sitemap/llms.txt discovery; keep a page-version hash for each quote.

### `agent/discover.py` (Stage 1)
- **`discover(app, fetcher)`**: fetch seeds plus probes (`developers.`, `developer.`, `docs.`, `/developers`, `/api`…) when the seed is a bare homepage. Score every link on the fetched pages by keyword weights (auth, oauth, pricing, mcp, rate limit…). Cap 2 pricing pages and 3 per path prefix for diversity. Fetch the top 9, then a second hop of 5. Render pages with <1500 chars using Playwright. Run a GitHub repo search for `"<name>" mcp`.
- **Why:** the first trial pulled 9 pricing pages for Salesforce and an empty JS shell for HubSpot, and these rules fixed the HubSpot case. Salesforce was still blocked (403).
- **`github_mcp_search`** returns repo, owner, owner type and stars. It's a *lead* list; the LLM must judge ownership (vendor org vs individual).

### `agent/llm.py`
- **`complete_json(system, prompt, schema, model, tools)`** → `(dict, meta)`. Backend `claude-cli` runs `claude -p --output-format json --json-schema … --tools ""` (no tools for extraction; WebSearch/WebFetch for pass B) and reads `structured_output` and `total_cost_usd`. Backend `anthropic` uses a forced tool call on the Messages API.
- **Why the CLI:** no API key was available; the CLI makes real model calls on a logged-in account and reports real cost, which is honest and reproducible. **Failure modes:** timeouts, invalid JSON (raised as `LLMError` and recorded as the app's error).

### `agent/stages.py`
- **`prompt_a`**: builds the source pack (`S1…Sn`, each with URL, title and keyword-windowed `snippets()` within a ~48k-char budget) plus the GitHub leads and failed-URL list.
- **`SYSTEM_A`**: rules and *definitions* (what counts as each auth type, the access tier as the most restrictive gate to *test* credentials, breadth classes, official vs community MCP).
- **`assess(extraction, category)`** (Stage 5, deterministic):
  - identity "no" → UNKNOWN; protocols == {none} → NO_SUPPORTED_INTERFACE; no protocol or tier unknown → UNKNOWN
  - partner_or_sales → GATED; paid_plan or admin_approval → CONDITIONAL; free/trial → READY
  - group map: READY→BUILD NOW, CONDITIONAL→BUILD WITH PREREQUISITES, GATED→OUTREACH REQUIRED, else RESEARCH FURTHER
  - approach: official MCP → wrap it; CLI only → CLI skill; else a custom toolkit over the protocol
  - security risk: Finance/Ecommerce/Marketing are "elevated"; with static-key-only auth they're "high"
- **`verify_claims`** (Stage 6): for each claim, fetch the URL (cache-first) and set `verified` plus `verify_note`.
- **Known limitation:** Stage 6 proves the quote *exists*, not that it *supports* the value. Example: on GitHub the model cited "GitHub recommends that you use a GitHub App instead" for "OAuth tokens supported". The quote is real but only weakly supportive. Only the human audit catches this.

### `agent/main.py`
- CLI: `--app`, `--ids`, `--limit`, `--all`, `--resume`, `--pass a|b`, `--workers`, `--verify`.
- **`research(app, fetcher, pass)`** runs the stages, writes a trace event per stage to `data/logs/trace.jsonl`, and saves an `AppRecord` with cost, duration, sources and any error.

### `agent/verify.py`
- **`level1`**: coverage of IDs, duplicate names, name/category match, primary auth ∈ methods, official MCP has URL, tier vs flag contradictions, URL format, identity confirmed.
- **`compare(a,b,field)`** → agree / partial (set overlap, or adjacent tiers free↔trial, paid↔admin) / contradiction / insufficient (either side unknown).
- **`reconcile(a,b)`**: start from A and change a field only by rule:
  - **R0**: A failed → use B; both failed → all unknown.
  - **R1 gap-fill**: A unknown, B has verified evidence → take B.
  - **R2 union**: auth/protocol sets overlap and B adds verified items → union.
  - **R3 override**: scalar conflict where only B's value has verified evidence → take B.
  - **R4 abstain**: conflict and neither side verified → unknown plus `needs_human_review`.
  - If both are verified and conflict → keep A and flag the contradiction for human review.
- **`audit_sample`**: per category, sorted by `sha256("atlas-2026:<id>")`, take one app with an A/B disagreement (if any) plus one more. That gives 20 apps, reproducibly.
- **`write_worksheet`**: 20 apps × 6 fields = 120 rows, each with pass A, pass B, corrected value, source URLs and an excerpt. It won't overwrite a sheet that already holds human labels.
- **`score`**: only counts rows with `human_ground_truth` filled. Accuracy = correct / evaluated, with "unknown" never credited (unless the truth is unknown). Reports first-pass, second-pass and corrected accuracy, app-level exact match, per-field accuracy and the error list.

### `agent/analytics.py` and `agent/build_site.py`
- `compute(apps)` produces every number on the page, with denominators.
- `build_site` writes `docs/index.html` and `case_study.html` (one file, data embedded as JSON, no external scripts) plus `exports/composio_100_apps.{csv,json}`.

### Tests (`tests/`)
- `test_agent.py`: registry integrity, quote matching, retry behaviour, network-failure-not-cached, robots respect, schema rejection, verdict rules, comparison, reconciliation rules (including "doesn't mutate pass A" and "doesn't trust unverified B"), sampling reproducibility, and the accuracy formula.
- `test_site.py`: Playwright checks that KPIs match the embedded data, charts render, search and filters work, the drawer shows evidence links, exports download, there's no horizontal scroll at 375px, and there are no JS errors.
- **Say plainly:** the tests prove the software works. They don't prove the research is correct.

---

## D. Verification concepts

- **Ground truth:** the correct answer, established by a human reading the official documentation.
- **Human review:** a person checks the agent's answers against the docs. I never let the AI fill this in.
- **Sampling / stratified sampling:** you can't hand-check all 600 fields, so you check a subset. Stratified means a fixed number per category (2 × 10), so one easy category can't dominate.
- **First-pass accuracy:** correct fields from pass A alone ÷ fields evaluated.
- **Corrected accuracy:** the same, after the verification loop (reconciliation).
- **App-level exact match:** share of apps where all 6 audited fields are correct. Much harsher.
- **Precision / recall:** for a yes/no property like "has official MCP", precision = of the apps the agent marked yes, how many really are; recall = of the apps that truly have one, how many the agent found. "Unknown" lowers recall but protects precision.
- **Evidence coverage:** share of core fields backed by at least one verified quote.
- **Confidence / calibration:** a confidence score is calibrated if "80% confident" claims are right ~80% of the time. I deliberately don't use LLM self-reported confidence; I use structural signals instead (verified evidence, A/B agreement).
- **Holdout evaluation:** evaluate on data not used to design the method. My reconciliation rules were fixed before any labels existed, but the audit sample is also where I report the before/after, so it's an in-sample estimate. I say so on the page.
- **Error taxonomy:** wrong_value, missing_value, over_inclusion, source_misread, outdated_source, identity_error, unresolvable.
- **Evaluation leakage:** if I corrected answers using the human labels and then measured accuracy on those same labels, I'd get ~100% for free. I don't. The scorer reads labels; the reconciler never does.

---

## E. Product-manager thinking

- **Product discovery:** understanding the problem before building. Here: what does an integration engineer need to know before starting a toolkit?
- **Customer problem statement:** "Product ops spends hours per app researching auth and access by hand, with inconsistent outputs and no sources, so roadmap decisions are slow and hard to audit."
- **Requirements:** 100 apps, the fixed fields, evidence per claim, honest uncertainty, reproducible.
- **MVP:** a pipeline plus a page that answers "which can we build now, which need outreach" with sources. Not a SaaS product.
- **Product-market fit (internal):** product ops would reuse it for the next 500 apps, and engineers trust its auth notes enough to start work.
- **RICE:** Reach × Impact × Confidence ÷ Effort. I can estimate Confidence (evidence) and Effort (auth/access friction) but **not Reach or Impact**: those need customer-demand data I don't have, which is why the page doesn't rank BUILD NOW.
- **ICE:** Impact × Confidence × Ease. Same gap: Impact needs demand.
- **Opportunity cost:** an engineer week on a gated app with no partner deal is a week not spent on a self-serve app customers want.
- **Build vs buy vs partner:** official MCP exists → reuse/wrap (buy-ish); self-serve API → build a toolkit; gated → partner first.
- **Product metrics for this tool:** research time/app, cost/app, field accuracy on audit, % unknown, % human-review needed.
- **North Star:** "verified integration decisions per week": decisions product ops trusts enough to act on.
- **OKR example:** O: make integration research scale. KR1: ≥90% field accuracy on monthly audit. KR2: <$0.50 and <5 min per app. KR3: unknown rate <15%.
- **Stakeholders:** engineering (wants auth details), partnerships (wants the outreach list with evidence), leadership (wants the headline), customers (want their app).
- **Integration roadmap:** demand × feasibility. Feasibility comes from this atlas; demand from customer requests.
- **Commercial gating:** a partnership or paid plan is a *finding*, not a failure.
- **Demand vs feasibility:** easy to build ≠ worth building. Every recommendation on the page says this.

---

## F. Interview question bank (with model answers)

### Architecture and implementation
1. **Walk me through what happens when you run `--app GitHub`.** Registry lookup; discovery fetches docs.github.com/rest and probes; link scoring pulls auth pages; GitHub search finds `github/github-mcp-server`; Sonnet reads ~11 pages and returns schema JSON with quotes; Stage 6 re-fetches each cited URL to confirm the quote; Stage 5 rules give READY; the record is saved to `data/runs/pass_a/061.json` and the trace logged.
2. **Why one LLM call for stages 2–4 instead of three agents?** Same sources, so three calls would triple cost for little gain, and one call keeps the sections internally consistent. I label it honestly as one extraction stage that produces three sections.
3. **Why use the Claude CLI rather than the API?** No API key was available. The CLI makes real calls and reports cost. The API backend is implemented too (`ATLAS_LLM=anthropic`).
4. **Why didn't you use Composio's SDK/MCP?** Composio's toolkits act on apps; my job was reading public docs, where plain HTTP plus a fetcher with robots/throttling is simpler and fully inspectable. A natural extension: use Composio's GitHub toolkit for MCP-repo checks, or Composio's search tools. I didn't want to claim Composio usage I didn't have.
5. **How do you stop the model from inventing facts?** The model only sees fetched text, unknown is the default, every field needs a verbatim quote, Stage 6 verifies the quote, and an independent pass is compared.
6. **What does Stage 6 not catch?** A real quote that doesn't support the claim, and stale pages. The human audit covers it.
7. **Why rules for the verdict instead of asking the LLM?** Reproducible, explainable, testable, and the same inputs always give the same verdict. The LLM's job is facts; policy is code.
8. **How does resume work?** Per-app JSON checkpoints; `--resume` skips successful ones and re-runs errors; transient network failures aren't cached.
9. **How do you stay polite to vendor sites?** robots.txt, 1 req/s per host, an identifying UA, caching, small page caps.
10. **What happens when a site blocks you?** Logged; no bypass; the field stays unknown or pass B fills it if pass B's quote can be verified. Salesforce developer docs returned 403. I chose not to evade it.
11. **Why Playwright?** Some docs render client-side; plain HTTP returns an empty shell. Rendering is used only for pages under 1,500 chars.
12. **Why GitHub search for MCP?** Community servers live on GitHub; search gives owner, stars and description. Ownership decides official vs community.
13. **How does pass B stay independent?** Separate process and prompt, different model (Haiku vs Sonnet), its own web search, never given pass A output.
14. **Is pass B really independent if both are Claude models?** Partly. Same model family means correlated errors are possible. Agreement isn't proof; that's why the human audit exists. A stronger design would use a different vendor's model or a human for pass B.
15. **Explain reconciliation rule R3.** Scalar conflict where only B has a verified quote → take B. Unverified evidence never overrides.
16. **Why keep A when both are verified and conflict?** No principled tie-breaker. Keep the primary pass, flag the contradiction, send it to human review.
17. **What's the cost per app?** See § H. It's real `total_cost_usd` from the CLI.
18. **How would you scale to 1,000 apps?** More workers (rate limits are per host, so it parallelises across vendors), batch API, a queue such as Redis/SQS, a shared cache, a scheduled monthly refresh with diffs.
19. **How would you keep it fresh?** Store page hashes; re-run when the docs change; alert on verdict changes.
20. **What's the security risk of the pipeline itself?** Prompt injection from pages (no tools on the extraction model, so limited), secret handling (no keys stored in the repo), and the CLI runs with `--tools ""` for extraction.
21. **Why a static page and not the FastAPI app?** Reliability for reviewers: nothing to run, nothing to go down. Live execution is honest only from the CLI, and the page shows a real saved trace instead of a fake "Run" button.
22. **What was in the old backend/frontend?** An earlier prototype with hand-written data and a simulated agent (`asyncio.sleep` steps) and an unsupported 98.3% figure. I rebuilt it rather than present that.
23. **How do you handle multiple auth methods?** It's a list; charts count per method, so totals exceed 100, with a separate "multi-method" count.
24. **How is access tier defined?** The most restrictive gate to get working *test* credentials. Production restrictions (app review) are captured separately so self-serve isn't confused with production-approved.
25. **How do you define API breadth?** Broad = many resource types with read and write; Medium = core resources, partial write; Limited = few/read-only/single-purpose; Unknown. No endpoint counts invented.
26. **Why tri-state yes/no/unknown?** So unknown isn't silently treated as "no", e.g. "no MCP" vs "we didn't find evidence".
27. **What tests prove most?** The reconciliation tests (doesn't trust unverified B, doesn't mutate A), the scorer test (unknown not credited), sampling reproducibility.
28. **What would break first in production?** Discovery on bot-protected or JS-heavy docs, then quote matching on reformatted pages.
29. **How do you detect identity errors (e.g. "Sherlock")?** `identity_confirmed` must be yes from the sources; Level 1 flags otherwise; the six ambiguous apps are marked in the registry.
30. **Why snippets rather than full pages?** Context budget and cost. Keyword-dense windows keep the auth/pricing text; the risk is dropping a relevant paragraph without keywords.

### Accuracy and verification
31. **What's your accuracy?** Only what the human worksheet says (§ H). If it's not filled, I say "pending". I don't use agreement as an accuracy proxy.
32. **Then how do you know anything is right?** Three signals: verified-quote rate, A/B agreement, and the human audit. The first two are necessary but not sufficient.
33. **Isn't A/B agreement good enough?** No: two passes can share an error (same model family, same outdated page).
34. **Why 20 apps?** The brief asks for a sample. 2 per category gives coverage; 120 fields gives a usable estimate (±~5–9 points at 95% CI depending on accuracy).
35. **How did you choose the sample?** Deterministic hash order, one disagreement case per category. Biasing toward disagreements makes the audit harder, not easier, and I disclose it.
36. **Doesn't oversampling disagreements bias accuracy downward?** Yes, slightly. It's a conservative estimate. I'd also report the stratum-weighted estimate if asked.
37. **Is your corrected accuracy a held-out number?** No. The rules were fixed before labelling, so there's no tuning leakage, but it's measured on the same sample. A true holdout would need a second sample after any rule change.
38. **What would you do if corrected accuracy were lower than first-pass?** Report it; inspect which rule hurt (likely R4 abstain turning correct-but-unverified values into unknown) and change the rule, then re-audit on a fresh sample.
39. **Precision vs recall for official MCP?** Unknown protects precision. I'd measure both on the audit.
40. **What's the most common error type?** See the audit results. Before the audit, the observed failure modes were discovery misses (blocked or JS docs) and tier ambiguity between free and trial.
41. **How do you handle outdated documentation?** Timestamp every fetch; quotes tie to that snapshot; a re-run detects drift.
42. **What does "evidence support rate" mean exactly?** Verified quotes ÷ all quotes. It says nothing about whether the quote supports the value.
43. **How would you improve verification?** An entailment check (a second model asked "does this quote support this value?"), a human spot-check queue for contradictions, and per-field confidence from the signals.
44. **Calibration?** I'd bucket fields by signal (verified + agree vs others) and measure the audit accuracy per bucket; if verified+agree is ~95% and others ~60%, that's a usable confidence.
45. **Why not have the AI do the human audit?** That's grading its own homework, and the brief asks for human checks. Claiming it as human would be dishonest.

### Product
46. **What's the headline finding?** See the page's findings (§ H). Answer with the number and denominator.
47. **Which auth dominates and why does it matter?** OAuth2 (see counts). Composio's managed OAuth (refresh, per-user consent) is the core moat; static-key apps are quick wins but carry security risk.
48. **Which categories are most self-serve vs gated?** Read from the category chart; developer tools are typically the most self-serve, while ads/commerce/finance have more approval gates.
49. **Most common blocker?** From the blocker counts: say which and how many.
50. **Where are the easy wins?** READY plus static key/PAT plus broad API: hours to a working toolkit. But demand decides which.
51. **What needs outreach?** The OUTREACH REQUIRED list. Partnerships should start these early because lead time is weeks or months.
52. **Should Composio build everything READY?** No. READY is feasibility. Prioritise by customer requests × workflow value.
53. **How would you prioritise with demand data?** RICE: Reach = requesting customers, Impact = workflow value, Confidence = evidence/agreement, Effort = tier/auth friction from the atlas.
54. **MCP strategy?** Where official servers exist, Composio's value is managed auth, governance and observability on top; where only community servers exist, Composio can offer the hardened version.
55. **When is a custom toolkit better than MCP reuse?** When the MCP server is narrow, local-only (stdio), unmaintained, or uses static keys while Composio needs per-user OAuth.
56. **What did you learn about commercial gating?** Gating is concentrated in specific categories (see data); it's a partnerships problem, not an engineering one.
57. **What would you tell the partnerships team on Monday?** The outreach list with the evidence link for each gate, ordered by customer requests.
58. **What would you tell engineering?** Start with READY apps that customers asked for, OAuth infrastructure reused across them, and the list of apps where an official MCP exists to benchmark.
59. **How do you measure this tool's success?** Hours saved per app, audit accuracy, % decisions not reversed later.
60. **What's the biggest risk in your recommendations?** Missing demand data and the unknowns. That's why RESEARCH FURTHER exists.

### Hard / skeptical questions
61. **"You used AI to write this. What did you actually do?"** I set the requirements and honesty rules, chose the architecture (fetch-then-extract, independent pass, quote verification, rule-based verdicts), debugged real failures (pricing-page crawl, JS docs, Zoho TLS, Salesforce 403), and decided what not to claim. I can explain every file.
62. **"Your verdict rules are simplistic."** Yes, deliberately: auditable and stable. The nuance lives in the fields (app review, production restrictions) and the drawer rationale.
63. **"Free vs trial: does that distinction matter?"** For testing, both are self-serve; for long-term CI testing, trials expire. It's kept as a separate tier and treated as "partial" agreement.
64. **"Why should we trust a Haiku pass B?"** I don't trust it alone; it only changes a field when its quote verifies against the live page.
65. **"What if the vendor page lies or is marketing?"** Prefer docs over marketing; the source URL is shown so the reviewer sees the type.
66. **"Your Salesforce record is UNKNOWN; isn't that embarrassing?"** It's honest. Salesforce's developer site blocked automated fetches, and I didn't evade that, so pass B's claims couldn't be verified. A human fixes it in 2 minutes, and that's exactly the "where it needed a human" point.
67. **"Cost?"** See § H: cents per app, versus ~20–40 minutes of human time per app.
68. **"What would you do with another week?"** Entailment checks, a different-vendor model for pass B, complete the human audit and a second holdout sample, Composio's own catalogue as a comparison baseline, and demand data joined in.
69. **"Is 'official MCP' reliable?"** It depends on ownership judgement. Repos under the vendor's org count; "awesome lists" don't. Audited in the sample.
70. **"Why didn't you include endpoint counts?"** Not reliably obtainable from docs without invention; breadth classes are honest.

### Behavioural
71. **Tell me about a time you found your own work was wrong.** The previous prototype showed 98.3% accuracy that wasn't backed by a real audit. I replaced it with real runs and "Human audit pending" rather than keep an impressive number.
72. **A time you dealt with ambiguity.** Paygent Connect had no URL; I added a discovery fallback and an identity check, and kept it unknown when evidence was thin.
73. **How do you handle a stakeholder who wants a single accuracy number now?** Give what's measured (evidence rate, agreement), explain why it isn't accuracy, and offer the audit in N hours.
74. **How do you prioritise under a time limit?** Accuracy and honesty first, then coverage, then polish.
75. **How do you work with engineers?** Give them sourced facts, not opinions; flag uncertainty explicitly.
76. **A disagreement you'd escalate?** Shipping a recommendation that depends on missing demand data as if it were proven.
77. **How do you use AI tools responsibly?** Verify outputs, keep a human in the loop for ground truth, never let AI impersonate review.
78. **What are you proudest of here?** The verification design: quotes checked against live pages, plus refusing to fake the audit.
79. **What would you do differently?** Start pass B on a different model vendor; budget human-audit time from day one.
80. **Why product ops?** It sits where data quality decides roadmap quality, which is exactly this assignment.

### Case questions
81. **A customer requests an app not in the list. What do you do?** Add it to the registry, run `--app`, review the drawer evidence, check demand, and route it to build / partner / research.
82. **The pipeline says READY but engineering hits a paywall. Why?** Probably the tier was assessed on test credentials while the needed endpoint is plan-gated. Fix: per-endpoint plan notes, and add it to the error taxonomy.
83. **Two vendors both need partnerships. Which first?** The one with more customer demand and shorter approval lead time; ask partnerships for the timeline.
84. **How would you present this to leadership in 1 minute?** Headline finding, the build/prereq/outreach split, the trust level (evidence %, audit status), the ask (demand data plus partnership owners).
85. **How would you reduce cost by 5×?** Smaller model for extraction on easy apps, cached pages, a fixed source pack, skipping pass B where A has full verified coverage.
86. **How would you reduce unknowns?** Better discovery (sitemaps, llms.txt, OpenAPI specs), Playwright for blocked-but-public pages where permitted, a human queue.
87. **How do you decide if an MCP server is "good enough" to reuse?** Ownership, maintenance (last commit), auth model (per-user OAuth?), tool coverage, transport (remote vs stdio), licence.
88. **How would you detect a vendor changing auth (e.g. deprecating API keys)?** Monthly diff of auth methods per app; alert.
89. **What KPI dashboard would you build for integration ops?** Pipeline: researched, audited accuracy, unknown %, apps by group, time to decision, outreach status.
90. **An exec asks "how many apps can we ship this quarter?"** Feasible ≠ shippable: count READY and requested, multiply by engineering capacity per toolkit; note the gated lead times.

### Concept checks
91. **OAuth vs API key in one line?** OAuth = delegated, scoped, per-user, expiring; API key = static, account-wide secret.
92. **Why PKCE?** It prevents authorization-code interception for public clients.
93. **What's a refresh-token rotation gotcha?** Using an old refresh token after rotation can revoke the session; concurrent refreshes race.
94. **What's admin consent?** A workspace admin must approve an app's scopes before users can use it (Slack, Microsoft, Atlassian orgs).
95. **What's app review?** The provider manually reviews an app before granting production or sensitive scopes (Meta, Google sensitive scopes).
96. **MCP vs a REST API?** MCP is an agent-facing tool protocol with discovery; REST is an app-facing data API. MCP servers often wrap REST APIs.
97. **What is stdio vs remote MCP?** stdio runs locally as a subprocess; remote is served over HTTP and can use OAuth.
98. **What's structured output's failure mode?** Valid JSON with wrong content, which is why schema validation isn't truth validation.
99. **What's idempotency and why should agent tools care?** Retrying a create action can duplicate records; tools need idempotency keys.
100. **What's the difference between unit tests and research accuracy here?** Unit tests check the code does what I specified; research accuracy checks whether what I specified matches reality.
101. **What's a confusion matrix for access tier?** Rows = truth tier, columns = predicted tier; shows e.g. free↔trial confusions separately from free↔partner errors.
102. **Why report denominators?** "40 apps" means different things out of 100 vs out of 60 known.

---

## G. Presentation scripts

**30-second intro.** "I built a research agent that reads each of the 100 apps' real developer docs, extracts auth, access, API and MCP facts with a verbatim quote for every claim, re-checks those quotes against the live pages, and runs a second independent pass to catch disagreements. The page shows the patterns first, then every app with its evidence, and it's explicit about what the agent couldn't establish."

**One-minute pitch.** Problem → manual research doesn't scale and isn't sourced. Solution → fetch-then-extract pipeline with quote verification and an independent pass. Outcome → [headline numbers from § H]. Trust → [evidence rate], [audit status]. Ask → demand data to turn feasibility into a roadmap.

**Two-minute walkthrough.** (1) Hero KPIs, including "human audit pending/measured". (2) Findings cards. (3) Readiness by category. (4) Auth bars, noting multi-method. (5) Filter the explorer to GATED, open one app, show the quote ✓ and link. (6) Agent section: point at the LLM vs deterministic vs human labels. (7) Verification: agreement, the corrections table, and where it struggled. (8) Recommendations, plus the demand caveat.

**Five-minute technical.** Registry → discovery (seeds, probes, scoring, diversity caps, Playwright, GitHub) → extraction prompt (definitions, quotes required, untrusted text) → Stage 6 quote matching → Stage 5 rules → pass B → reconciliation R0–R4 → worksheet and scorer → static site. Close with the failure cases (Salesforce 403, Zoho TLS, pricing-page crawl) and what each taught.

**Five-minute product.** Who the users are → the question "build now / prerequisites / outreach / research" → patterns (auth dominance, category gating, blockers, MCP landscape) → why feasibility ≠ priority → how RICE would plug demand in → next actions for engineering and partnerships → metrics to run this as an ongoing ops process.

**One real error and correction.** Use the Salesforce/HubSpot trial: the first discovery version followed homepage links into 9 pricing pages and returned an empty JS shell for HubSpot's developer portal, so pass A had no auth facts. I added developer-subdomain probes, diversity caps and Playwright rendering; HubSpot then came back with OAuth2 plus private-app tokens, verified. Salesforce stayed blocked by a 403, which I kept as an honest unknown. Also cite a reconciliation correction from the page's corrections table.

**Main product insight.** Read the first headline card. Explain it with the denominator and what Composio should do about it.

**What I'd improve next.** Finish and extend the human audit with a fresh holdout; an entailment check for quotes; a different-vendor model for pass B; demand data; monthly refresh with change alerts.

---

## H. Run results (regenerated from data)

See `README.md § Results`. It's generated from `data/final/atlas.json` at build time, and these are the numbers to quote.
