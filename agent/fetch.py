"""Polite HTTP fetching: disk cache, per-domain throttle, retries, robots.txt, request log."""
from __future__ import annotations

import asyncio, hashlib, json, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import httpx
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "http"
LOG = ROOT / "data" / "logs" / "requests.jsonl"
UA = "AccessAtlasResearchBot/1.0 (+integration-docs research; respects robots.txt)"
MIN_INTERVAL = 1.0      # seconds between requests to the same host
MAX_TEXT = 60_000       # chars of page text kept per page


class Fetcher:
    def __init__(self, concurrency: int = 8, use_cache: bool = True):
        self.sem = asyncio.Semaphore(concurrency)
        self.use_cache = use_cache
        self._host_locks: dict[str, asyncio.Lock] = {}
        self._host_last: dict[str, float] = {}
        self._robots: dict[str, robotparser.RobotFileParser | None] = {}
        self.client = httpx.AsyncClient(
            headers={"User-Agent": UA, "Accept-Language": "en"},
            follow_redirects=True, timeout=httpx.Timeout(20.0),
        )
        CACHE.mkdir(parents=True, exist_ok=True)
        LOG.parent.mkdir(parents=True, exist_ok=True)

    async def close(self):
        await self.client.aclose()

    def _log(self, **kw):
        kw["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with LOG.open("a") as f:
            f.write(json.dumps(kw) + "\n")

    async def _throttle(self, host: str):
        lock = self._host_locks.setdefault(host, asyncio.Lock())
        async with lock:
            wait = self._host_last.get(host, 0) + MIN_INTERVAL - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            self._host_last[host] = time.monotonic()

    async def _allowed(self, url: str) -> bool:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self._robots:
            rp = robotparser.RobotFileParser()
            try:
                r = await self.client.get(base + "/robots.txt", timeout=10)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                    self._robots[base] = rp
                else:
                    self._robots[base] = None
            except Exception:
                self._robots[base] = None
        rp = self._robots[base]
        return True if rp is None else rp.can_fetch(UA, url)

    async def get(self, url: str, retries: int = 2) -> dict:
        """Return {url, final_url, status, title, text, links, error, fetched_at}."""
        key = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".json")
        if self.use_cache and key.exists():
            return json.loads(key.read_text())
        out = {"url": url, "final_url": url, "status": None, "title": "", "text": "",
               "links": [], "error": None,
               "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        if not await self._allowed(url):
            out["error"] = "blocked_by_robots_txt"
            self._log(url=url, status=None, error=out["error"])
            key.write_text(json.dumps(out))
            return out
        host = urlparse(url).netloc
        async with self.sem:
            for attempt in range(retries + 1):
                await self._throttle(host)
                try:
                    r = await self.client.get(url)
                    out["status"], out["final_url"] = r.status_code, str(r.url)
                    if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                        await asyncio.sleep(2 ** (attempt + 1))
                        continue
                    ctype = r.headers.get("content-type", "")
                    if r.status_code < 400 and ("html" in ctype or "text" in ctype or "json" in ctype):
                        out.update(parse_html(r.text, str(r.url)) if "html" in ctype
                                   else {"text": r.text[:MAX_TEXT]})
                    elif r.status_code >= 400:
                        out["error"] = f"http_{r.status_code}"
                    else:
                        out["error"] = f"unsupported_content_type:{ctype[:40]}"
                    break
                except Exception as e:  # network error, timeout, TLS
                    out["error"] = f"{type(e).__name__}: {str(e)[:120]}"
                    if attempt < retries:
                        await asyncio.sleep(2 ** (attempt + 1))
        if out["status"] is None and "ConnectError" in (out["error"] or "") \
                and not host.startswith("www.") and host.count(".") == 1:
            alt = url.replace("://" + host, "://www." + host, 1)
            self._log(url=url, status=None, error=out["error"], retry_as=alt)
            return await self.get(alt, retries=0)
        self._log(url=url, final_url=out["final_url"], status=out["status"],
                  error=out["error"], chars=len(out["text"]))
        # Do not cache transient network failures, so --resume can retry them.
        if out["status"] is not None:
            key.write_text(json.dumps(out))
        return out


def parse_html(html: str, base: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base, a["href"].split("#")[0])
        if href.startswith("http"):
            links.append({"url": href, "text": a.get_text(" ", strip=True)[:80]})
    for t in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return {"title": title[:200], "text": text[:MAX_TEXT], "links": links[:600]}


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def quote_in_text(quote: str, text: str) -> bool:
    """True if the quote (normalized) appears in the page text. Long quotes may
    match on any 8-word window to tolerate elisions/formatting differences."""
    q, t = normalize(quote), normalize(text)
    if not q:
        return False
    if q in t:
        return True
    words = q.split()
    if len(words) < 8:
        return False
    windows = [" ".join(words[i:i + 8]) for i in range(0, len(words) - 7, 4)]
    hits = sum(1 for w in windows if w in t)
    return hits / len(windows) >= 0.5
