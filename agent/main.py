"""Composio Access Atlas research agent — CLI.

  python -m agent.main --app GitHub            # research one app (pass A)
  python -m agent.main --limit 5               # first N apps
  python -m agent.main --all [--resume]        # all 100, skipping finished ones
  python -m agent.main --all --pass b          # independent second pass
  python -m agent.main --verify                # Stage 6 + compare + reconcile + audit sample
"""
from __future__ import annotations

import argparse, asyncio, json, time
from pathlib import Path

from . import discover, llm, registry, stages
from .fetch import Fetcher
from .schema import AppRecord, Extraction

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "runs"
TRACE = ROOT / "data" / "logs" / "trace.jsonl"
MODELS = {"a": "sonnet", "b": "haiku"}


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def trace(app_id: int, pass_name: str, stage: str, msg: str, **kw):
    TRACE.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now(), "app": app_id, "pass": pass_name, "stage": stage, "msg": msg, **kw}
    with TRACE.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"[{rec['ts'][11:19]}] #{app_id:<3} {pass_name} {stage:<14} {msg}", flush=True)


def out_path(pass_name: str, app_id: int) -> Path:
    return RUNS / f"pass_{pass_name}" / f"{app_id:03d}.json"


async def research(app: dict, f: Fetcher, pass_name: str) -> AppRecord:
    t0 = time.monotonic()
    sources, meta, err = [], {}, None
    x = Extraction()
    try:
        if pass_name == "a":
            trace(app["id"], "A", "1-discovery", f"seeds={app['seeds']}")
            extra = []
            if not app["seeds"]:
                # No URL in the brief: one small LLM web-search call to find official URLs.
                found, m = await llm.complete_json(
                    "Find official URLs only. Return JSON.",
                    f"Find the official website and developer/API documentation URLs for "
                    f"'{app['name']}' ({app['hint']}, category {app['category']}). "
                    "Return up to 4 URLs you actually saw in search results.",
                    {"type": "object", "properties": {"urls": {"type": "array", "items": {"type": "string"}}},
                     "required": ["urls"]}, "haiku", tools=["WebSearch"], max_turns=6)
                extra = [u for u in found.get("urls", []) if u.startswith("http")][:4]
                meta["discovery_cost"] = m.get("cost_usd")
                trace(app["id"], "A", "1-discovery", f"web-search fallback found {extra}")
            disc = await discover.discover(app, f, extra_seeds=extra)
            trace(app["id"], "A", "1-discovery",
                  f"{len(disc['pages'])} pages fetched, {len(disc['failures'])} failed, "
                  f"{sum(1 for g in disc['github_mcp'] if 'repo' in g)} GitHub MCP candidates")
            if not disc["pages"]:
                raise RuntimeError("no documentation pages could be fetched")
            prompt, sources = stages.prompt_a(app, disc)
            sources += [{"id": "GH", "url": g["url"], "title": g["repo"], "kind": "github_search"}
                        for g in disc["github_mcp"] if "repo" in g]
            trace(app["id"], "A", "2-4-extract", f"LLM extraction over {len(disc['pages'])} sources")
            data, m = await llm.complete_json(stages.SYSTEM_A, prompt, stages.extraction_schema(),
                                              MODELS["a"], max_turns=3)
        else:
            trace(app["id"], "B", "independent", "web-search agent researching from name only")
            data, m = await llm.complete_json(stages.SYSTEM_B, stages.prompt_b(app),
                                              stages.extraction_schema(), MODELS["b"],
                                              tools=["WebSearch", "WebFetch"], max_turns=30,
                                              timeout=900)
        meta.update(m)
        x = Extraction.model_validate(data)
        trace(app["id"], pass_name.upper(), "6-evidence", f"checking {len(x.claims)} claims against source text")
        rate = await stages.verify_claims(x, f)
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:300]}"
        rate = None
        trace(app["id"], pass_name.upper(), "error", err)
    rec = AppRecord(
        id=app["id"], name=app["name"], category=app["category"], pass_name=pass_name,
        model=meta.get("model", ""), researched_at=now(),
        duration_s=round(time.monotonic() - t0, 1),
        cost_usd=round(sum(v for v in (meta.get("cost_usd"), meta.get("discovery_cost")) if v), 4) or None,
        sources=sources, extraction=x, evidence_support_rate=rate, error=err)
    if not err:
        rec.assessment = stages.assess(x, app["category"])
        trace(app["id"], pass_name.upper(), "5-verdict",
              f"{rec.assessment.verdict} | tier={x.access.tier} | auth={x.auth.methods} | "
              f"evidence {rate} | ${rec.cost_usd} | {rec.duration_s}s")
    p = out_path(pass_name, app["id"])
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rec.model_dump_json(indent=1))
    return rec


async def run(apps: list[dict], pass_name: str, resume: bool, workers: int):
    f = Fetcher()
    q: asyncio.Queue = asyncio.Queue()
    for a in apps:
        p = out_path(pass_name, a["id"])
        if resume and p.exists() and not json.loads(p.read_text()).get("error"):
            continue
        q.put_nowait(a)
    print(f"pass {pass_name}: {q.qsize()} apps to research with {workers} workers")

    async def worker():
        while not q.empty():
            a = q.get_nowait()
            await research(a, f, pass_name)
    await asyncio.gather(*(worker() for _ in range(workers)))
    await f.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", help="app name or id")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ids", help="comma-separated ids")
    ap.add_argument("--resume", action="store_true", help="skip apps with a successful saved result")
    ap.add_argument("--pass", dest="pass_name", choices=["a", "b"], default="a")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--verify", action="store_true", help="run verification + reconciliation")
    args = ap.parse_args()
    if args.verify:
        from . import verify
        verify.main()
        return
    apps = registry.load()
    if args.app:
        apps = [registry.by_name(args.app)]
    elif args.ids:
        want = {int(i) for i in args.ids.split(",")}
        apps = [a for a in apps if a["id"] in want]
    elif args.limit:
        apps = apps[: args.limit]
    elif not args.all:
        ap.error("choose --app, --ids, --limit, --all or --verify")
    asyncio.run(run(apps, args.pass_name, args.resume, args.workers))


if __name__ == "__main__":
    main()
