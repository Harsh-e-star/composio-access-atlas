<p align="center">
  <h1 align="center">🗺️ Composio Access Atlas</h1>
  <p align="center">
    <strong>An autonomous research agent that maps 100 apps for Composio — auth, access, API surface, MCP readiness — with cited evidence verified against live docs.</strong>
  </p>
  <p align="center">
    <a href="https://harsh-e-star.github.io/composio-access-atlas/"><strong>🔗 Live Case Study</strong></a> · <a href="https://github.com/Harsh-e-star/composio-access-atlas"><strong>📂 Repository</strong></a>
  </p>
</p>

---

## ✨ Highlights

| Metric | Value |
|---|---|
| Apps researched | **100** (10 categories × 10 apps) |
| Pass A (primary research) | 96 / 100 succeeded |
| Pass B (independent blind replication) | 100 / 100 succeeded |
| Evidence quotes verified on live page | 782 / 847 (92.3%) |
| Core fields backed by verified quote | 434 / 500 (86.8%) |
| Total LLM cost | $12.38 (~$0.12 per app) |
| Human spot-check accuracy | 18 / 20 (90%) |
| Automated test suite | **49 / 49 passed** |

---

## 🎯 What It Does

Composio Access Atlas is a **multi-pass research agent** that programmatically investigates 100 SaaS apps and produces a structured, evidence-backed dataset answering:

> *"Can a developer build a Composio integration for this app today, and what does it take?"*

For each app, it extracts: **authentication methods**, **access tier** (self-serve → gated), **API protocols**, **API breadth**, **official MCP availability**, and a **buildability verdict** — every claim backed by a source URL and a verbatim quote re-checked against the live page.

### Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  PASS A — Primary Research (Claude Sonnet)                                  │
│                                                                              │
│  Registry ──→ Discovery ──→ LLM Extraction ──→ Evidence Check ──→ Verdict   │
│  (100 apps)   (fetch URLs,    (structured       (re-fetch URL,    (rule-     │
│                probe devdocs,  JSON output,       string-match     based:     │
│                Playwright,     URL + quote        the quote)       tier +     │
│                GitHub search)  per field)                          protocol)  │
├──────────────────────────────────────────────────────────────────────────────┤
│  PASS B — Independent Replication (Claude Haiku)                             │
│                                                                              │
│  Web-search agent re-researches every app from its name alone.               │
│  Never sees Pass A data. Fields compared: agree / partial / contradiction.   │
├──────────────────────────────────────────────────────────────────────────────┤
│  RECONCILIATION (deterministic rules R0–R4)                                  │
│                                                                              │
│  Only changes a field when the other pass has a verified quote.              │
│  Unverified conflicts → "unknown" + flagged for human review.                │
├──────────────────────────────────────────────────────────────────────────────┤
│  HUMAN AUDIT                                                                 │
│                                                                              │
│  Stratified 20-app × 6-field sample. The only accuracy measure reported.     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Verdicts at a Glance

| Verdict | Count | Meaning |
|---|:---:|---|
| 🟢 **READY** | 71 | Free/self-serve, documented API, can build today |
| 🟡 **CONDITIONAL** | 11 | Paid plan, trial, or admin approval needed first |
| 🔴 **GATED** | 5 | Partner / sales outreach required |
| ❓ **UNKNOWN** | 13 | Insufficient evidence — needs human research |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- At least one LLM API key (Gemini, Groq, or Anthropic)

### Installation

```bash
# Clone the repository
git clone https://github.com/Harsh-e-star/composio-access-atlas.git
cd composio-access-atlas

# Set up the virtual environment
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m playwright install chromium

# Configure your LLM provider
cp .env.example .env
# Edit .env and add at least one API key: GEMINI_API_KEY, GROQ_API_KEY, or ANTHROPIC_API_KEY
```

### Verify Setup

```bash
python -m agent.main --llm-check     # confirm LLM provider is reachable
python -m pytest tests               # run the full test suite (49 tests)
```

### Run the Agent

| Command | Description |
|---|---|
| `python -m agent.main --app GitHub` | Research a single app (Pass A) |
| `python -m agent.main --limit 5` | Trial run on first 5 apps |
| `python -m agent.main --all --resume` | Full 100-app run (skips completed, retries failures) |
| `python -m agent.main --all --pass b` | Independent blind replication (Pass B) |
| `python -m agent.main --verify` | Run verification, comparison, reconciliation & scoring |
| `python -m agent.build_site` | Rebuild the case study page and all exports |
| `python -m pytest tests` | Run all 49 automated tests |

### AI Provider Configuration

The agent supports a **multi-provider fallback chain**: Gemini → Groq → Anthropic → Claude CLI.

Set `AI_PROVIDER=auto` in `.env` to enable automatic failover on quota, rate-limit, or server errors. Each saved record names the provider that answered. Check your setup anytime with `--llm-check`.

> **Note:** Pass B requires web search, which is only available via the Claude CLI provider. The 100-app dataset in `data/` was produced using Claude (Sonnet for Pass A, Haiku for Pass B).

---

## 📊 Key Results

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

---

## 📁 Project Structure

```
composio-access-atlas/
├── agent/                        # Research agent source code (~1,900 lines)
│   ├── main.py                   # CLI entrypoint
│   ├── discover.py               # Stage 1: URL discovery & scoring
│   ├── fetch.py                  # HTTP fetcher with retry & robots.txt
│   ├── llm.py                    # Multi-provider LLM client (Gemini/Groq/Anthropic/Claude)
│   ├── stages.py                 # Stages 2–6: extraction, evidence check, verdicts
│   ├── verify.py                 # Verification, A↔B comparison, reconciliation
│   ├── schema.py                 # Pydantic models for structured output
│   ├── registry.py               # 100-app registry (names, categories, seed URLs)
│   ├── analytics.py              # Statistics and scoring
│   ├── evaluate.py               # Accuracy evaluation
│   ├── build_site.py             # Site & export generator
│   └── site_template.html        # HTML template for the case study
├── data/
│   ├── runs/pass_a/              # Raw per-app Pass A research records (100 JSON files)
│   ├── runs/pass_b/              # Raw per-app Pass B research records (100 JSON files)
│   ├── final/atlas.json          # Reconciled dataset with corrections log
│   ├── final/first_pass_snapshot.json  # Pass A frozen snapshot (never modified)
│   ├── audit/                    # Human audit worksheets, AI review, corrections
│   └── logs/                     # Stage trace + HTTP request log
├── docs/index.html               # Self-contained case study (GitHub Pages)
├── case_study.html               # Same case study (repo root copy)
├── exports/                      # Flat CSV/JSON exports of the 100-app dataset
├── tests/                        # 49 automated tests (agent + LLM + browser)
├── archive/legacy_prototype/     # Earlier prototype (not the submission)
├── requirements.txt              # Python dependencies
├── .env.example                  # LLM provider configuration template
└── .gitignore
```

---

## 🔬 Verification & Evaluation Integrity

The project uses a **multi-level verification system** designed so that no level can inflate accuracy:

| Level | Method | What It Proves |
|---|---|---|
| **Level 1** | Deterministic schema checks (Pydantic, label sets, ID consistency) | Data is well-formed — not that it is factually correct |
| **Level 2** | Independent blind Pass B re-researches every app | A second opinion exists — agreement ≠ correctness |
| **Reconciliation** | Rules R0–R4 applied before human labels exist | Fields only change when the other pass has a verified quote |
| **Level 3** | Stratified human audit (20 apps × 6 fields) | The only real accuracy measure; "unknown" is never credited |

> **Unit tests passing ≠ research being correct.** This distinction is stated explicitly throughout the project.

---

## ⚠️ Known Limitations

- **Quote ≠ support**: Stage 6 proves a quote *exists* on the cited page, not that it *supports* the extracted value. Only human audit checks support.
- **Bot-blocked docs**: Sites returning HTTP 403 or enforcing robots.txt (e.g., Salesforce) are not bypassed — those fields stay "unknown".
- **Shared vendor errors**: Both passes use Claude models from the same vendor, so they can share systematic errors.
- **Discovery gaps**: Keyword-scored link ranking can miss relevant pages without expected keywords.
- **No demand signal**: Verdicts reflect *feasibility*, not business priority. Customer demand is unknown.
- **Point-in-time snapshot**: Results reflect documentation state at each app's `researched_at` timestamp.

---

## 🌐 Deploy (GitHub Pages)

`docs/index.html` is fully self-contained — all data is embedded inline, no external scripts or API calls. To deploy:

1. Push the repository to GitHub
2. Go to **Settings → Pages → Source**: select `main` branch, `/docs` folder
3. The site is live at `https://<username>.github.io/composio-access-atlas/`

---

## 📝 Outputs Reference

| Path | Description |
|---|---|
| `data/runs/pass_a/NNN.json` | Raw per-app research record (sources, claims, verification, cost, duration) |
| `data/runs/pass_b/NNN.json` | Independent blind replication record |
| `data/final/first_pass_snapshot.json` | Pass A exactly as produced — never modified |
| `data/final/atlas.json` | Reconciled dataset + corrections log + Level 1 issues |
| `exports/composio_100_apps.csv` | Flat 100-row export (one row per app) |
| `exports/composio_100_apps.json` | Same data in JSON format |
| `composio_100_apps_full_export.csv` | 600 field-level rows (first pass, second pass, final, evidence status) |
| `data/audit/human_audit_worksheet.csv` | Human audit template (fill ground truth, then re-run `--verify`) |
| `data/audit/composio_verified_corrections.csv` | Accepted/deferred corrections with source evidence |
| `data/audit/composio_accuracy_evaluation.json` | AI-referenced and human accuracy results (labelled separately) |
| `data/logs/trace.jsonl` | Per-stage execution trace |
| `data/logs/requests.jsonl` | Every HTTP request made during research |

---

> `archive/legacy_prototype/` contains an **earlier prototype** that used hand-written records, a simulated agent, and unaudited accuracy figures. It is **not** the submission — none of its numbers are used. The real system is `agent/` + `data/` + `docs/`.

---

<p align="center">
  <strong>Built by <a href="https://github.com/Harsh-e-star">Harsh Raj</a></strong>
</p>
