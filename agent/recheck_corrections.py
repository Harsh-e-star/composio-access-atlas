"""Re-fetch the official source of each externally proposed (AI-reviewed) correction and
check that the page text contains the terms the proposed value depends on.
This is a keyword-presence check, not a semantic proof; results are recorded as such."""
import asyncio, csv
from pathlib import Path
from .fetch import Fetcher

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "audit" / "external_ai_review"
CHECK = {
 ("Salesforce","auth_methods"):["oauth"], ("Salesforce","protocols"):["soap","rest"],
 ("Zoho CRM","protocols"):["rest"], ("Zoho CRM","api_breadth"):["bulk","records"],
 ("Zoho CRM","official_mcp"):["mcp"], ("Freshdesk","auth_methods"):["api key","password"],
 ("Help Scout","auth_methods"):["oauth"], ("Help Scout","protocols"):["rest"],
 ("Gladly","auth_methods"):["basic"], ("Zoho Cliq","auth_methods"):["oauth"],
 ("Zoho Cliq","protocols"):["rest"], ("Zoho Cliq","official_mcp"):["mcp"],
 ("Google Ads","protocols"):["grpc","rest"], ("Mailchimp","official_mcp"):["mcp"],
 ("Airtable","protocols"):["rest"], ("Jira","auth_methods"):["basic","api token"],
 ("Jira","protocols"):["rest"], ("Jira","api_breadth"):["issue","project"],
 ("Monday.com","protocols"):["graphql"], ("QuickBooks","access_tier"):["sandbox"],
 ("QuickBooks","protocols"):["rest"],
}

async def main():
    rows = list(csv.DictReader(open(D / "composio_source_checked_corrections.csv", encoding="utf-8-sig")))
    f = Fetcher(); out = []
    for r in rows:
        page = await f.get(r["new_official_source"]); t = page["text"].lower()
        kws = CHECK.get((r["app"], r["field"]), [])
        hit = [k for k in kws if k in t]
        if len(t) < 200:
            st = f"fetch_failed:{page['error'] or 'empty/JS page'}"
        elif len(hit) == len(kws):
            st = "keywords_found"
        else:
            st = "missing:" + ",".join(sorted(set(kws) - set(hit)))
        out.append({**r, "recheck_status": st, "page_chars": len(t)})
        print(f"{r['app']:12} {r['field']:13} -> {r['suggested_reference_value']:26} {st}")
    await f.close()
    with open(D / "correction_source_recheck.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out[0])); w.writeheader(); w.writerows(out)

if __name__ == "__main__":
    asyncio.run(main())
