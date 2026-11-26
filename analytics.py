"""Validate aggregate analytics events. No tracking identifiers or network I/O."""
from collections import Counter

EVENTS={'page_view','retailer_click','search_run','request_saved'}
VIEWS={'home','all','same','clearance','flip','car','watch','account'}
CATEGORIES={'retail','vehicle','unknown'}

def clean_event(event):
    if not isinstance(event,dict):
        raise ValueError('Invalid event')
    if set(event)-{'event','view','category'}:
        raise ValueError('Unexpected analytics fields')
    kind=event.get('event')
    view=event.get('view')
    category=event.get('category','unknown')
    if kind not in EVENTS or view not in VIEWS or category not in CATEGORIES:
        raise ValueError('Unknown analytics event')
    return kind,view,category

def aggregate(events):
    counts=Counter(clean_event(e) for e in events)
    return [{'event':k[0],'view':k[1],'category':k[2],'count':n} for k,n in sorted(counts.items())]
