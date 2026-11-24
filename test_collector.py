import unittest
from collector import merge
from adapter import parse
class Tests(unittest.TestCase):
 def test_history_and_failure(self):
  r={'dealer':'A','stock':'1','id':'a','price':40000}; old={'vehicles':[r]}; first,h=merge(old,{'vehicles':[r],'report':[]},[],'2026-11-24T00:00:00Z');self.assertEqual(len(h),1)
  second,h=merge(first,{'vehicles':[dict(r,price=39000)],'report':[]},h,'2026-11-24T04:00:00Z');self.assertEqual(second['vehicles'][0]['price_change'],-1000);self.assertEqual(len(h),2)
  third,h=merge(second,{'vehicles':[],'report':[]},h,'2026-11-24T08:00:00Z');self.assertEqual(third['vehicles'][0]['price'],39000);self.assertIn('not confirmed',third['vehicles'][0]['status'])
 def test_parser(self):
  r=parse('2026 Hyundai Kona Hybrid SX2.V3 new SUV 10 km Front Wheel Drive Stock No: 123 $39,990 Drive Away','A','VIC','https://example.com');self.assertEqual(r['price'],39990);self.assertEqual(r['drive'],'FWD')
if __name__=='__main__':unittest.main()

class MissingStockTests(unittest.TestCase):
 def test_url_identity(self):
  text='2026 Hyundai Kona Hybrid new SUV 10 km $39,990 Drive Away'
  a=parse(text,'A','SA','https://example.com/cars/123')
  b=parse(text.replace('39,990','38,990'),'A','SA','https://example.com/cars/123?ref=abc')
  self.assertEqual(a['id'],b['id']);self.assertIsNone(a['stock'])
  first,h=merge({'vehicles':[]},{'vehicles':[a],'report':[]},[],'one')
  second,h=merge(first,{'vehicles':[b],'report':[]},h,'two')
  self.assertEqual(len(second['vehicles']),1);self.assertEqual(second['vehicles'][0]['price_change'],-1000)
 def test_reject_generic_link(self):
  self.assertIsNone(parse('2026 Hyundai Kona Hybrid new SUV $39,990 Drive Away','A','SA','https://example.com/search/new-cars'))
