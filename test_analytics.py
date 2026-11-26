import unittest
from analytics import aggregate,clean_event

class AnalyticsTests(unittest.TestCase):
    def test_counts(self):
        e=dict(event='retailer_click',view='same',category='retail')
        self.assertEqual(aggregate([e,e]),[dict(e,count=2)])
    def test_reject_identifiers(self):
        for key in ('email','user_id','ip','query','url','session_id'):
            with self.assertRaises(ValueError):
                clean_event(dict(event='search_run',view='home',**{key:'private'}))
    def test_invalid_event(self):
        with self.assertRaises(ValueError):
            clean_event(dict(event='unknown',view='home'))
