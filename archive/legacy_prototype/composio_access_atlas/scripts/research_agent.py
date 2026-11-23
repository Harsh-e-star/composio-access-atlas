"""Two-agent research + skeptical cross-check pipeline.

Requires OPENAI_API_KEY and network access. NOT executed in the offline demo environment.
Run --limit 5 first, inspect costs, then --limit 100.
"""
import argparse, json, os, re, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
APPS=ROOT/'data'/'apps.json'
OUT=ROOT/'data'/'agent_results.json'
ALLOWED_ACCESS={'Self-serve','Conditional','Paid','Gated','Unknown'}
ALLOWED_MCP={'Yes','No','Unknown'}

SYSTEM='''You are a careful developer API research analyst. Research only the named app.
Source hierarchy: primary developer/auth/API documents > first-party support pages > official GitHub > third party.
Never invent docs links. Cite actual URLs you observed with distinct evidence URLs for auth/access/surface where possible.
Separate can-create-developer-credentials from can-use-production-API. Mark Unknown if documentation is ambiguous.
Official first-party MCP must be distinguished from community MCP. Local CLI is not a REST API.
Return ONLY JSON with keys: auth, access, surface, mcp, blocker, note, evidence (array of {url, claim}),
confidence (High/Medium/Low), and human_followup (string). Use access labels
Self-serve (free/trial creds), Conditional (account/admin/scopes/setup), Paid (paid subscription required),
Gated (explicit approval/partnership), Unknown. Use mcp Yes only with a corroborated link.
No fabricated API endpoint counts.'''


def parse_json(s):
    s=s.strip()
    if s.startswith('```'):
        s=re.sub(r'^```(?:json)?\s*','',s)
        s=re.sub(r'\s*```$','',s)
    try:return json.loads(s)
    except json.JSONDecodeError:
        dec=json.JSONDecoder()
        for m in re.finditer(r'\{', s):
            try:
                obj,_=dec.raw_decode(s[m.start():])
                if isinstance(obj,dict):return obj
            except json.JSONDecodeError:continue
    raise ValueError('Could not find a JSON object in model output')


def validated(raw):
    if not isinstance(raw,dict):raise ValueError('not a JSON object')
    evidence=[]
    for obj in raw.get('evidence',[]):
        if isinstance(obj,dict):u,claim=obj.get('url',''),obj.get('claim','')
        else:u,claim=str(obj),''
        p=urlparse(u)
        if p.scheme=='https' and p.netloc and not p.username and len(u)<1500:
            evidence.append({'url':u,'claim':str(claim)[:300]})
    result={k:str(raw.get(k,'Unknown'))[:500] for k in
            ['auth','access','surface','mcp','blocker','note','confidence','human_followup']}
    result['access']=result['access'] if result['access'] in ALLOWED_ACCESS else 'Unknown'
    result['mcp']=result['mcp'] if result['mcp'] in ALLOWED_MCP else 'Unknown'
    result['confidence']=result['confidence'] if result['confidence'] in {'High','Medium','Low'} else 'Low'
    result['evidence']=evidence[:8]
    if not evidence:result['confidence']='Low';result['access']='Unknown'
    return result


def ask(client, model, prompt):
    # OpenAI Responses API native web-search tool (may incur search charges).
    r=client.responses.create(model=model, tools=[{'type':'web_search'}],
                              input=[{'role':'system','content':SYSTEM},
                                     {'role':'user','content':prompt}],
                              max_output_tokens=1700)
    return validated(parse_json(r.output_text))


def research(client, model, app):
    prompt=(f'Research {app["app"]} ({app["category"]}). Website hint: {app["hint"]}. '
           f'Focus on auth options, how developers obtain credentials, production gating, '
           f'API protocols/surface, and FIRST-PARTY MCP. Use the latest available official docs '
           f'and identify conflicting or recently changed policies. Return concise JSON.')
    return ask(client,model,prompt)


def skeptical_check(client, model, app, first):
    prompt=(f'INDEPENDENT FACT CHECK of {app["app"]}. Hint: {app["hint"]}. '
            'Verify this proposed record against official docs; search again, do not just trust the draft. '
            f'Proposed draft: {json.dumps(first,ensure_ascii=False)}. '
            'Pay special attention to licensing, OAuth vs bearer/API key, official MCP vs community, '
            'and whether this is a hosted API or local CLI. If not substantiated set Unknown and '
            'specify exactly what needs human review. Return a complete corrected JSON record.')
    return ask(client, model, prompt)


def differences(a,b):
    return [k for k in ('auth','access','surface','mcp') if a.get(k)!=b.get(k)]


def save(rows):
    OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--limit',type=int,default=5,help='How many apps from the requested starting ID')
    p.add_argument('--start',type=int,default=1,help='App ID 1–100')
    p.add_argument('--model',default=os.getenv('RESEARCH_MODEL','gpt-4.1-mini'))
    p.add_argument('--sleep',type=float,default=1.5)
    p.add_argument('--only-unknown',action='store_true',help='Skip the hand-reviewed seed entries')
    a=p.parse_args()
    if not os.getenv('OPENAI_API_KEY'):
        raise SystemExit('Set OPENAI_API_KEY first. No network model calls were made.')
    from openai import OpenAI
    client=OpenAI()
    apps=json.loads(APPS.read_text())
    results=json.loads(OUT.read_text()) if OUT.exists() else {}
    selected=[app for app in apps if app['id']>=a.start and
              (not a.only_unknown or app['review']!='Docs reviewed')]
    selected=selected[:a.limit]
    for app in selected:
        key=str(app['id'])
        if key in results:
            print(f'Skip cached {app["id"]}: {app["app"]}')
            continue
        print(f'Researching {app["id"]:03d} {app["app"]}',flush=True)
        try:
            draft=research(client,a.model,app)
            checked=skeptical_check(client,a.model,app,draft)
            mismatch=differences(draft,checked)
            results[key]={'app':app['app'],'category':app['category'],
                          'first_pass':draft,'second_pass':checked,
                          'disagreements':mismatch,
                          'review':'Needs human' if mismatch or checked['confidence']!='High'
                             else 'Agent cross-checked (not human verified)',
                          'checked_at':datetime.now(timezone.utc).isoformat()}
        except Exception as exc:
            results[key]={'app':app['app'],'review':'Error / needs human',
                          'error':str(exc)[:400],
                          'checked_at':datetime.now(timezone.utc).isoformat()}
        save(results)
        time.sleep(a.sleep)
    print(f'Wrote {len(results)} research outputs to {OUT}. Human review remains essential.')

if __name__=='__main__':main()
