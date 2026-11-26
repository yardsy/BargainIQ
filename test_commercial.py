import unittest
from datetime import datetime,timezone,timedelta
from commercial import approved_link,sponsored_offer

class CommercialTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,26,tzinfo=timezone.utc)
        self.original='https://shop.example.invalid/item'
        self.meta=dict(approved=True,original_url=self.original,affiliate_url='https://partner.example.invalid/item',allowed_hosts=['partner.example.invalid'],expires_at=(self.now+timedelta(days=1)).isoformat())

    def test_affiliate_approved(self):
        self.assertEqual(approved_link(self.original,self.meta,self.now),(self.meta['affiliate_url'],True))

    def test_fallback(self):
        for change in [dict(approved=False),dict(original_url='wrong'),dict(affiliate_url='http://partner.example.invalid/item'),dict(affiliate_url='https://other.example.invalid/item'),dict(expires_at=self.now.isoformat())]:
            self.assertEqual(approved_link(self.original,dict(self.meta,**change),self.now),(self.original,False))

    def test_sponsored(self):
        offer=dict(approved=True,published=True,title='Example offer',url=self.original,expires_at=self.meta['expires_at'])
        self.assertEqual(sponsored_offer(offer,self.now)['label'],'Sponsored advertisement')
        self.assertIsNone(sponsored_offer(dict(offer,approved=False),self.now))
        self.assertIsNone(sponsored_offer(dict(offer,published=False),self.now))
        self.assertIsNone(sponsored_offer(dict(offer,expires_at=self.now.isoformat()),self.now))
