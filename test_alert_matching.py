import unittest
from datetime import datetime,timezone,timedelta
from retail import parse
from alert_matching import target_matches,shopping_matches,newly_matched,plan_shopping_alerts

class AlertMatchingTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,26,tzinfo=timezone.utc)
        self.target=dict(enabled=True,item_type='product',item_key='test',target_price=100)
        self.offer=dict(id='test',published=True,category='retail',price=100,verified_at=self.now.isoformat(),expires_at=(self.now+timedelta(days=1)).isoformat())
        self.row=parse(dict(retailer='Example',name='Oak TV unit',url='https://example.invalid/unit',price='90',observed_at=self.now.isoformat(),condition='new',currency='AUD',brand='Example',mpn='TV1',pack='1',variant='oak',width_cm='200',depth_cm='40',height_cm='45',shipping='10',category='Furniture',clearance='yes'))

    def test_target(self):
        self.assertTrue(target_matches(self.target,self.offer,self.now))
        self.assertFalse(target_matches(self.target,dict(self.offer,price=101),self.now))
        self.assertFalse(target_matches(dict(self.target,enabled=False),self.offer,self.now))
        self.assertFalse(target_matches(dict(self.target,item_type='vehicle'),self.offer,self.now))
        self.assertFalse(target_matches(dict(self.target,item_key='other'),self.offer,self.now))

    def test_target_freshness(self):
        for changes in [dict(published=False),dict(expires_at=self.now.isoformat()),dict(verified_at=(self.now-timedelta(days=8)).isoformat()),dict(verified_at=(self.now+timedelta(days=1)).isoformat())]:
            self.assertFalse(target_matches(self.target,dict(self.offer,**changes),self.now))

    def test_shopping_match(self):
        criteria=dict(fields=dict(search='oak TV unit',retailCategory='Furniture',specBudget='100',specBasis='delivered',specMinWidth='180',specMaxWidth='210',specMaxDepth='42',specMaxHeight='50'),clearance=True)
        self.assertTrue(shopping_matches(criteria,self.row,self.now))
        for changes in [dict(shipping=None),dict(depth_cm=None),dict(depth_cm=43),dict(width_cm=179),dict(height_cm=51),dict(price=91),dict(clearance='no')]:
            self.assertFalse(shopping_matches(criteria,dict(self.row,**changes),self.now))

    def test_invalid_or_empty_request(self):
        for fields in [{},{'specBudget':'nan'},{'specBudget':'-1'},{'unknown':'value'},{'specBasis':'invalid'},{'search':123}]:
            self.assertFalse(shopping_matches(dict(fields=fields),self.row,self.now))

    def test_stale_and_unknown_identity(self):
        criteria=dict(fields=dict(search='oak'))
        for changes in [dict(observed_at=(self.now-timedelta(days=8)).isoformat()),dict(observed_at=(self.now+timedelta(days=1)).isoformat()),dict(variant=''),dict(currency='USD')]:
            self.assertFalse(shopping_matches(criteria,dict(self.row,**changes),self.now))

    def test_new_matches(self):
        self.assertEqual(newly_matched(['a','b','b','c'],['a','c']),['b'])
        self.assertEqual(newly_matched(['a'],['a']),[])

    def test_alert_plan_requires_explicit_consent(self):
        sub=dict(enabled=True,email_opt_in=True,criteria=dict(fields=dict(search='oak')))
        self.assertEqual(len(plan_shopping_alerts(sub,[self.row],[],self.now)),1)
        for changes in [dict(enabled=False),dict(email_opt_in=False),dict(email_opt_in='true'),dict(criteria={})]:
            self.assertEqual(plan_shopping_alerts(dict(sub,**changes),[self.row],[],self.now),[])

    def test_alert_plan_deduplicates_delivered_and_repeated_offers(self):
        sub=dict(enabled=True,email_opt_in=True,criteria=dict(fields=dict(search='oak')))
        older=dict(self.row,observed_at=(self.now-timedelta(days=1)).isoformat(),price=95)
        result=plan_shopping_alerts(sub,[older,self.row,self.row],[],self.now)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['offer']['price'],90)
        self.assertEqual(plan_shopping_alerts(sub,[self.row],[result[0]['offer_key']],self.now),[])
        self.assertEqual(len(plan_shopping_alerts(sub,[self.row],[],self.now)),1)

    def test_alert_plan_excludes_stale_and_over_budget(self):
        sub=dict(enabled=True,email_opt_in=True,criteria=dict(fields=dict(search='oak',specBudget='100')))
        rows=[dict(self.row,price=101),dict(self.row,observed_at=(self.now-timedelta(days=8)).isoformat())]
        self.assertEqual(plan_shopping_alerts(sub,rows,[],self.now),[])
