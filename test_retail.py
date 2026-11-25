import unittest
from retail import parse,groups,profit,gtin,record_history,price_context
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

 def test_delivery(self):
  self.assertIsNone(self.row()['shipping'])
  self.assertEqual(self.row(shipping='0')['shipping'],0)
  self.assertEqual(self.row(shipping='12.50')['shipping'],12.5)
  for value in ('nan','inf','-1'):
   with self.assertRaises(ValueError):self.row(shipping=value)
 def test_image(self):
  self.assertEqual(self.row(image_url='https://example.com/image.png')['image_url'],'https://example.com/image.png')
  for value in ('http://example.com/a','javascript:alert(1)','https://user:pass@example.com/a'):
   with self.assertRaises(ValueError):self.row(image_url=value)

 def test_history(self):
  a=self.row(price='120',observed_at='2026-11-20')
  b=self.row(price='90',observed_at='2026-11-25')
  h=record_history([a,b],{})
  c=price_context(b,h)
  self.assertEqual(c['previous_price'],120)
  self.assertEqual(c['lowest_observed'],90)
  self.assertEqual(len(c['observations']),2)
  self.assertEqual(record_history([b],h),h)
  self.assertIsNone(price_context(a,h)['previous_price'])
 def test_history_separation(self):
  a=self.row(price='120')
  b=self.row(price='90',variant='white')
  c=self.row(price='80',retailer='B')
  h=record_history([a,b,c],{})
  self.assertEqual(len(h),3)
  self.assertIsNone(price_context(b,h)['previous_price'])
 def test_history_conflict(self):
  with self.assertRaises(ValueError):record_history([self.row(price='120'),self.row(price='90')],{})
 def test_history_missing_identity(self):
  self.assertEqual(record_history([self.row(variant='')],{}),{})

 def test_dimensions(self):
  self.assertEqual(self.row(width_cm='50.5')['width_cm'],50.5)
  self.assertIsNone(self.row()['depth_cm'])
  for value in ('nan','inf','0','-1'):
   with self.assertRaises(ValueError):self.row(width_cm=value)
 def test_invalid_observation_date(self):
  with self.assertRaises(ValueError):self.row(observed_at='not-a-date')
