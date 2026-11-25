import unittest
from retail import parse,groups,profit,gtin
class RetailTests(unittest.TestCase):
 def row(self,**kw):
  r=dict(retailer='A',name='Test item',url='https://example.com/item',price='100',observed_at='2026-11-25',condition='new',currency='AUD',brand='Brand',mpn='ABC',pack='1',variant='black')
  r.update(kw);return parse(r)
 def test_match(self):
  self.assertEqual(len(groups([self.row(),self.row(retailer='B',price='90')])),1)
 def test_variant(self):
  self.assertFalse(groups([self.row(),self.row(retailer='B',variant='white')]))
 def test_condition(self):
  self.assertFalse(groups([self.row(),self.row(retailer='B',condition='used')]))
 def test_currency(self):
  with self.assertRaises(ValueError):self.row(currency='USD')
 def test_nan(self):
  with self.assertRaises(ValueError):self.row(price='nan')
 def test_gtin(self):
  self.assertEqual(gtin('4006381333931'),'04006381333931')
  self.assertIsNone(gtin('4006381333932'))
 def test_profit(self):
  self.assertEqual(profit(100,150,10,5),30)
