"""Reproduce a transparent heuristic-baseline vs doc-reviewed-labels audit.
This is a development-slice *adjudication* check, NOT independent generalization accuracy.
"""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SAMPLE=['Pipedrive','Zendesk','Twilio','Google Ads','LinkedIn Ads','Shopify',
        'Amazon Selling Partner','DataForSEO','Ahrefs','GitHub','Linear','Xero',
        'NotebookLM','Mermaid CLI']

# Deliberately simple rules-based first pass, generated deterministically.
def baseline(r):
    n=r['app']
    auth='OAuth2' if any(x in n for x in ['Ads','Shopify','Xero','GitHub','Linear','Pipedrive','Zendesk','NotebookLM','Amazon']) else 'API key'
    access='Self-serve' if n!='NotebookLM' else 'Self-serve'  # ignores production gates
    surface='REST'
    return {'auth':auth,'access':access,'surface':surface}

def assess():
    rows={r['app']:r for r in json.loads((ROOT/'data'/'apps.json').read_text())}
    audit=[];hits=0
    for n in SAMPLE:
        r=rows[n];b=baseline(r)
        gold={k:r[k] for k in ('auth','access','surface')}
        correct=[k for k in gold if gold[k]==b[k]]
        hits+=len(correct)
        audit.append({'app':n,'category':r['category'],'first':b,'reviewed':gold,
                      'hits':correct,'misses':[k for k in gold if k not in correct],
                      'evidence':r['evidence'][:2], 'note':r['note']})
    result={'sample_size':len(SAMPLE),'fields_per_app':3,'total_fields':len(SAMPLE)*3,
            'baseline_hits':hits,'baseline_agreement':round(100*hits/(len(SAMPLE)*3),1),
            'post_adjudication_fields':len(SAMPLE)*3,
            'post_adjudication_accuracy_claim':'Not independent: same sample was adjudicated by hand',
            'method':'Deterministic rule-based baseline compared with first-party-doc-reviewed annotations. No live AI-agent execution claimed.',
            'items':audit}
    (ROOT/'data'/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(f'Sample: {len(SAMPLE)} apps, {len(SAMPLE)*3} fields. Baseline {hits}/{len(SAMPLE)*3} = {result["baseline_agreement"]}% agreement; human-corrected same-sample cells {len(SAMPLE)*3}/{len(SAMPLE)*3} (NOT a holdout).')
    return result
if __name__=='__main__':assess()
