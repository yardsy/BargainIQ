"""Pure matching logic for verified offers and authorised retail snapshots.
No account reads, network requests or notification delivery.
"""
import math
from datetime import datetime,timezone,timedelta
from retail import observation_time,offer_key

def positive(value):
    if isinstance(value,bool): return None
    try: n=float(value)
    except (TypeError,ValueError,OverflowError): return None
    return n if math.isfinite(n) and n>0 else None

def timestamp(value):
    try: return observation_time(value)
    except (TypeError,ValueError,OverflowError): return None

def target_matches(target,offer,now=None):
    now=now or datetime.now(timezone.utc)
    if target.get('enabled') is not True or offer.get('published') is not True: return False
    expiry=timestamp(offer.get('expires_at'))
    verified=timestamp(offer.get('verified_at'))
    if not expiry or not verified or expiry<=now or verified>now or verified<now-timedelta(days=7): return False
    kind={'retail':'product','vehicle':'vehicle'}.get(offer.get('category'))
    if not kind or target.get('item_type')!=kind or target.get('item_key')!=str(offer.get('id')): return False
    goal=positive(target.get('target_price'))
    price=positive(offer.get('price'))
    return goal is not None and price is not None and price<=goal

def shopping_matches(criteria,row,now=None):
    now=now or datetime.now(timezone.utc)
    if not isinstance(criteria,dict) or not isinstance(criteria.get('fields'),dict): return False
    fields=criteria['fields']
    allowed={'search','retailCategory','retailSort','specBudget','specBasis','specCondition','specMinWidth','specMaxWidth','specMaxDepth','specMaxHeight'}
    if set(fields)-allowed or any(not isinstance(v,str) for v in fields.values()): return False
    if row.get('currency')!='AUD' or row.get('condition') not in ('new','used','refurbished','exdisplay'): return False
    at=timestamp(row.get('observed_at'))
    if not at or at>now or at<now-timedelta(days=7): return False
    price=positive(row.get('price'))
    if price is None: return False
    if not offer_key(row): return False
    query=fields.get('search','').strip().casefold()
    category=fields.get('retailCategory','').strip()
    condition=fields.get('specCondition','')
    basis=fields.get('specBasis','item')
    if basis not in ('item','delivered'): return False
    if category and category!=str(row.get('category') or 'Other').strip(): return False
    if condition and condition!=row.get('condition'): return False
    haystack=' '.join(str(row.get(k) or '') for k in ('name','retailer','brand','mpn','category')).casefold()
    if query and query not in haystack: return False
    if criteria.get('clearance') is True and str(row.get('clearance')).lower() not in ('yes','true','1'): return False
    budget=fields.get('specBudget','')
    if budget:
        cap=positive(budget)
        if cap is None: return False
        if basis=='delivered':
            shipping=row.get('shipping')
            if isinstance(shipping,bool) or not isinstance(shipping,(int,float)) or not math.isfinite(shipping) or shipping<0: return False
            price+=shipping
        if price>cap: return False
    for field,key,minimum in [('width_cm','specMinWidth',True),('width_cm','specMaxWidth',False),('depth_cm','specMaxDepth',False),('height_cm','specMaxHeight',False)]:
        if fields.get(key,''):
            bound=positive(fields[key])
            value=positive(row.get(field))
            if bound is None or value is None or (value<bound if minimum else value>bound): return False
    # Empty requests must not subscribe to every listing.
    return bool(query or category or condition or budget or criteria.get('clearance') is True or any(fields.get(k) for k in ('specMinWidth','specMaxWidth','specMaxDepth','specMaxHeight')))

def newly_matched(current,previous_keys):
    """Return stable offer identities not present in the previous successful check."""
    old=set(previous_keys)
    return sorted(set(current)-old)
