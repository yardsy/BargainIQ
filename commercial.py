"""Commercial metadata validation; never generate affiliate URLs or activate ads."""
from urllib.parse import urlsplit
from retail import observation_time
from datetime import datetime,timezone

def approved_link(original, metadata, now=None):
    """Return original URL unless an explicitly approved affiliate link is valid."""
    now=now or datetime.now(timezone.utc)
    if not isinstance(metadata,dict) or metadata.get('approved') is not True:
        return original,False
    try:
        url=metadata['affiliate_url']
        u=urlsplit(url)
        if metadata['original_url']!=original or u.scheme!='https' or not u.hostname or u.username or u.password:
            return original,False
        if u.hostname not in metadata['allowed_hosts'] or observation_time(metadata['expires_at'])<=now:
            return original,False
        return url,True
    except (ValueError,TypeError,KeyError,AttributeError):
        return original,False

def sponsored_offer(offer, now=None):
    """Separate paid placements from organic ranking, fail closed."""
    now=now or datetime.now(timezone.utc)
    try:
        if offer.get('approved') is not True or offer.get('published') is not True:
            return None
        if observation_time(offer['expires_at'])<=now:
            return None
        u=urlsplit(offer['url'])
        if u.scheme!='https' or not u.hostname or u.username or u.password:
            return None
        title=offer['title']
        if not isinstance(title,str) or not 1<=len(title.strip())<=200:
            return None
        return {'title':title,'url':offer['url'],'label':'Sponsored advertisement'}
    except (ValueError,TypeError,KeyError,AttributeError):
        return None
