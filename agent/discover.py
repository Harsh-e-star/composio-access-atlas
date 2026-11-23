"""Stage 1 — Discovery (deterministic crawler + optional LLM URL search fallback).

Fetches the seed URLs from the brief, scores same-site links by research
keywords, fetches the best candidates, renders JS-only pages with Playwright,
and queries the GitHub search API for MCP repositories.
"""
from __future__ import annotations

import asyncio, os, re, subprocess
from urllib.parse import urlparse

import httpx

from .fetch import Fetcher, parse_html

KEYWORDS = {
    # keyword: weight (matched against URL path + anchor text)
    "authentication": 6, "authorization": 4, "oauth": 6, "api-key": 5, "api key": 5,
    "api_key": 5, "token": 3, "auth": 4, "getting-started": 3, "getting started": 3,
    "quickstart": 3, "quick-start": 3, "introduction": 2, "overview": 1, "pricing": 4,
    "plans": 2, "rate-limit": 3, "rate limit": 3, "limits": 1, "mcp": 6,
    "model context": 6, "api reference": 4, "reference": 2, "/api": 3, "developer": 2,
    "webhook": 2, "partner": 3, "app review": 3, "access": 2, "sandbox": 2, "graphql": 2,
    "credentials": 4, "app": 0,
}
BAD = re.compile(r"(\.pdf|\.zip|\.png|\.jpg|login|signin|sign-in|signup|careers|/blog/|"
                 r"/jobs|/legal|privacy|cookie|/terms|facebook\.com/sharer|twitter\.com|x\.com/|"
                 r"linkedin\.com/company|youtube\.com/watch|/changelog/\d)", re.I)


def _site(host: str) -> str:
    parts = host.lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def score_link(url: str, text: str, sites: set[str]) -> int:
    p = urlparse(url)
    if _site(p.netloc) not in sites and "github.com" not in p.netloc:
        return 0
    if BAD.search(url):
        return 0
    hay = (p.path + " " + text).lower()
    s = sum(w for k, w in KEYWORDS.items() if k in hay)
    if re.match(r"(docs|developer|developers|api|dev)\.", p.netloc):
        s += 2
    return s


async def render(url: str) -> dict | None:
    """Playwright fallback for client-rendered documentation."""
    try:
        from playwright.async_api import async_playwright
        async with _RENDER_SEM, async_playwright() as pw:
            b = await pw.chromium.launch()
            pg = await b.new_page()
            await pg.goto(url, wait_until="networkidle", timeout=30000)
            html = await pg.content()
            await b.close()
        d = parse_html(html, url)
        d["rendered"] = True
        return d
    except Exception:
        return None


_GH_TOKEN: str | None = None


def gh_token() -> str | None:
    global _GH_TOKEN
    if _GH_TOKEN is None:
        _GH_TOKEN = os.environ.get("GITHUB_TOKEN") or ""
        if not _GH_TOKEN:
            try:
                _GH_TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True,
                                           text=True, timeout=10).stdout.strip()
            except Exception:
                _GH_TOKEN = ""
    return _GH_TOKEN or None


_GH_SEM = asyncio.Semaphore(1)
_RENDER_SEM = asyncio.Semaphore(3)


async def github_mcp_search(name: str) -> list[dict]:
    """Search GitHub repositories for '<name> mcp'. Returns owner/stars/description."""
    q = re.sub(r"\(.*?\)", "", name).strip()
    headers = {"Accept": "application/vnd.github+json"}
    if (t := gh_token()):
        headers["Authorization"] = f"Bearer {t}"
    async with _GH_SEM, httpx.AsyncClient(timeout=20) as c:
        for attempt in range(3):
            r = await c.get("https://api.github.com/search/repositories",
                            params={"q": f'"{q}" mcp in:name,description', "sort": "stars",
                                    "per_page": 8}, headers=headers)
            if r.status_code == 403 or r.status_code == 429:
                await asyncio.sleep(20 * (attempt + 1)); continue
            break
        await asyncio.sleep(2.2)  # stay under 30 searches/min
    if r.status_code != 200:
        return [{"error": f"github_search_http_{r.status_code}"}]
    return [{"repo": it["full_name"], "url": it["html_url"], "owner": it["owner"]["login"],
             "owner_type": it["owner"]["type"], "stars": it["stargazers_count"],
             "description": (it.get("description") or "")[:200],
             "updated": it.get("pushed_at")} for it in r.json().get("items", [])]


async def discover(app: dict, f: Fetcher, max_pages: int = 9,
                   extra_seeds: list[str] | None = None) -> dict:
    seeds = list(dict.fromkeys((extra_seeds or []) + app["seeds"]))
    # If the brief only gave a homepage, probe conventional developer locations.
    # Each probe is fetched; only ones that resolve with content are kept.
    probes = []
    for u in list(seeds):
        p = urlparse(u)
        if p.path in ("", "/") and not re.match(r"(docs|developers?|api)\.", p.netloc):
            d = _site(p.netloc)
            probes += [f"https://developers.{d}", f"https://developer.{d}", f"https://docs.{d}",
                       f"https://{p.netloc}/developers", f"https://{p.netloc}/docs/api",
                       f"https://{p.netloc}/api"]
    pages, failures = [], []
    seed_results = await asyncio.gather(*(f.get(u) for u in seeds + probes))
    for r in seed_results:
        if r["url"] in probes and (r["error"] or len(r["text"]) < 100):
            continue  # probe miss: not a failure worth reporting
        if r["text"] and len(r["text"]) < 1500 and not r["error"]:
            rr = await render(r["final_url"])
            if rr and len(rr["text"]) > len(r["text"]):
                r = {**r, **rr}
        (pages if r["text"] else failures).append(r)
    sites = {_site(urlparse(u).netloc) for u in seeds}
    sites |= {_site(urlparse(p["final_url"]).netloc) for p in pages}
    sites.discard("github.com")
    cands: dict[str, int] = {}
    for p in pages:
        for l in p["links"]:
            s = score_link(l["url"], l["text"], sites)
            if s >= 4 and l["url"] not in seeds:
                cands[l["url"]] = max(cands.get(l["url"], 0), s)
    ranked, buckets = [], {}
    for u in sorted(cands, key=lambda u: -cands[u]):
        path = urlparse(u).path.lower()
        b = "pricing" if ("pricing" in path or "plans" in path) else "/".join(path.split("/")[:3])
        if buckets.get(b, 0) >= (2 if b == "pricing" else 3):
            continue
        buckets[b] = buckets.get(b, 0) + 1
        ranked.append(u)
        if len(ranked) >= max_pages:
            break
    got = await asyncio.gather(*(f.get(u) for u in ranked))
    for r in got:
        if r["text"] and len(r["text"]) < 1500 and not r["error"]:
            rr = await render(r["final_url"])
            if rr and len(rr["text"]) > len(r["text"]):
                r = {**r, **rr}
        (pages if len(r["text"]) > 200 else failures).append(r)
    # second hop: follow strong links from the pages we just fetched
    if len(pages) < max_pages + len(seeds):
        more: dict[str, int] = {}
        have = {p["url"] for p in pages} | {p["final_url"] for p in pages} | set(cands)
        for p in pages:
            for l in p["links"]:
                s = score_link(l["url"], l["text"], sites)
                if s >= 6 and l["url"] not in have:
                    more[l["url"]] = max(more.get(l["url"], 0), s)
        hop = sorted(more, key=lambda u: -more[u])[:5]
        for r in await asyncio.gather(*(f.get(u) for u in hop)):
            (pages if len(r["text"]) > 200 else failures).append(r)
    # dedupe by final URL
    seen, uniq = set(), []
    for p in pages:
        if p["final_url"] not in seen:
            seen.add(p["final_url"]); uniq.append(p)
    gh = await github_mcp_search(app["name"])
    return {"pages": uniq, "failures": [{"url": x["url"], "error": x["error"] or "empty"}
                                         for x in failures], "github_mcp": gh}
