import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import audit
class TestDataset(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=json.loads((ROOT/'data'/'apps.json').read_text())
 def test_inventory(self):
  self.assertEqual(100,len(self.rows))
  self.assertEqual(list(range(1,101)),[r['id'] for r in self.rows])
  self.assertEqual(100,len({r['app'] for r in self.rows}))
  self.assertEqual(10,len({r['category'] for r in self.rows}))
  from collections import Counter
  self.assertTrue(all(v==10 for v in Counter(r['category'] for r in self.rows).values()))
 def test_reviewed_have_sources(self):
  reviewed=[r for r in self.rows if r['review']=='Docs reviewed']
  self.assertGreaterEqual(len(reviewed),35)
  for r in reviewed:
   self.assertTrue(r['evidence'],r['app'])
   self.assertTrue(all(u.startswith('https://') for u in r['evidence']))
   self.assertNotEqual('Unknown',r['auth'])
 def test_pending_not_falsely_verified(self):
  for r in self.rows:
   if r['review']=='Needs research':
    self.assertEqual('Unknown',r['auth'])
    self.assertFalse(r['evidence'])
 def test_audit_reproducible(self):
  a=json.loads((ROOT/'data'/'audit.json').read_text())
  self.assertEqual(a['sample_size'],len(audit.SAMPLE))
  self.assertEqual(a['total_fields'],42)
  self.assertEqual(a['baseline_hits'],17)
 def test_html_self_contained(self):
  t=(ROOT/'index.html').read_text()
  self.assertIn('const apps=',t)
  self.assertIn('const audit=',t)
  self.assertNotIn('src="https:',t)
if __name__=='__main__':unittest.main()
