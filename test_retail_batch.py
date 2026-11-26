import csv
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from retail_batch import build

class RetailBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.now=datetime(2026,11,26,tzinfo=timezone.utc)

    def row(self,retailer='Store A',host='a.example.invalid',**changes):
        row=dict(retailer=retailer,name='Example lamp',url='https://'+host+'/lamp',price='100',observed_at=self.now.isoformat(),condition='new',currency='AUD',brand='Example',mpn='L1',pack='1',variant='white',width_cm='50',internal_note='not public')
        row.update(changes)
        return row

    def source(self,rows,retailer='Store A',host='a.example.invalid',file='a.csv',authorised=True):
        with (self.root/file).open('w',newline='',encoding='utf-8') as f:
            fields=list(dict.fromkeys(k for row in rows for k in row))
            writer=csv.DictWriter(f,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return dict(retailer=retailer,file=file,allowed_hosts=[host],authorised=authorised)

    def test_multi_retailer(self):
        a=self.source([self.row()])
        b=self.source([self.row('Store B','b.example.invalid',price='90')],retailer='Store B',host='b.example.invalid',file='b.csv')
        export,history,report=build([a,b],self.root,{},self.now)
        self.assertEqual(len(export['products']),2)
        self.assertEqual(len(export['matches']),1)
        self.assertEqual(len(history),2)
        self.assertEqual(report[0]['accepted'],1)
        self.assertNotIn('internal_note',export['products'][0])

    def test_stale_excluded(self):
        old=self.row(url='https://a.example.invalid/old',observed_at=(self.now-timedelta(days=8)).isoformat())
        export,_,report=build([self.source([self.row(),old])],self.root,{},self.now)
        self.assertEqual(len(export['products']),1)
        self.assertEqual(report[0]['stale_excluded'],1)

    def test_reject_all_stale(self):
        old=self.row(observed_at=(self.now-timedelta(days=8)).isoformat())
        with self.assertRaises(ValueError):
            build([self.source([old])],self.root,{},self.now)

    def test_unapproved_feed(self):
        with self.assertRaises(ValueError):
            build([self.source([self.row()],authorised=False)],self.root,{},self.now)

    def test_unapproved_domain(self):
        with self.assertRaises(ValueError):
            build([self.source([self.row(host='other.example.invalid')])],self.root,{},self.now)

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            build([self.source([self.row(),self.row()])],self.root,{},self.now)

    def test_future_price(self):
        with self.assertRaises(ValueError):
            build([self.source([self.row(observed_at=(self.now+timedelta(days=1)).isoformat())])],self.root,{},self.now)

    def test_path_escape(self):
        with self.assertRaises(ValueError):
            build([dict(retailer='Store A',file='../outside.csv',allowed_hosts=['a.example.invalid'],authorised=True)],self.root,{},self.now)

    def test_price_history(self):
        old=self.row(observed_at=(self.now-timedelta(days=1)).isoformat(),price='150')
        _,history,_=build([self.source([old])],self.root,{},self.now)
        export,_,_=build([self.source([self.row()])],self.root,history,self.now)
        self.assertEqual(export['products'][0]['price_history']['previous_price'],150)
