-- Proposed migration only. Do not apply until reviewed and tested.
BEGIN;
CREATE TABLE public.engagement_daily (
 day date NOT NULL,
 event text NOT NULL CHECK (event IN ('page_view','retailer_click','search_run','request_saved')),
 view_name text NOT NULL CHECK (view_name IN ('home','all','same','clearance','flip','car','watch','account')),
 category text NOT NULL CHECK (category IN ('retail','vehicle','unknown')),
 count bigint NOT NULL DEFAULT 1 CHECK (count > 0),
 PRIMARY KEY (day,event,view_name,category)
);
ALTER TABLE public.engagement_daily ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.engagement_daily FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE ON public.engagement_daily TO service_role;
CREATE FUNCTION public.increment_engagement(p_event text,p_view text,p_category text)
RETURNS void LANGUAGE sql SECURITY INVOKER SET search_path = '' AS $$
 INSERT INTO public.engagement_daily(day,event,view_name,category,count)
 VALUES ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date,p_event,p_view,p_category,1)
 ON CONFLICT (day,event,view_name,category)
 DO UPDATE SET count=public.engagement_daily.count+1;
$$;
REVOKE ALL ON FUNCTION public.increment_engagement(text,text,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.increment_engagement(text,text,text) TO service_role;
-- Global UTC-day cap, enforced atomically even under concurrent requests.
-- The cap limits accepted writes, not hosting invocations or attempted database calls.
CREATE TABLE public.engagement_daily_budget (
 day date PRIMARY KEY,
 accepted integer NOT NULL CHECK (accepted BETWEEN 1 AND 5000)
);
ALTER TABLE public.engagement_daily_budget ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.engagement_daily_budget FROM PUBLIC, anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.engagement_daily_budget TO service_role;
GRANT DELETE ON public.engagement_daily TO service_role;
-- Replace the preliminary counter with a capped counter in the same transaction.
DROP FUNCTION public.increment_engagement(text,text,text);
CREATE FUNCTION public.increment_engagement(p_event text,p_view text,p_category text)
RETURNS boolean LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $
DECLARE
 d date := (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date;
BEGIN
 IF p_event IS NULL OR p_event NOT IN ('page_view','retailer_click','search_run','request_saved')
 OR p_view IS NULL OR p_view NOT IN ('home','all','same','clearance','flip','car','watch','account')
 OR p_category IS NULL OR p_category NOT IN ('retail','vehicle','unknown') THEN
  RAISE EXCEPTION 'Invalid engagement event';
 END IF;
 INSERT INTO public.engagement_daily_budget(day,accepted) VALUES(d,1)
 ON CONFLICT(day) DO UPDATE SET accepted=public.engagement_daily_budget.accepted+1
 WHERE public.engagement_daily_budget.accepted < 5000;
 IF NOT FOUND THEN RETURN false; END IF;
 INSERT INTO public.engagement_daily(day,event,view_name,category,count)
 VALUES(d,p_event,p_view,p_category,1)
 ON CONFLICT(day,event,view_name,category) DO UPDATE SET count=public.engagement_daily.count+1;
 RETURN true;
END;
$;
REVOKE ALL ON FUNCTION public.increment_engagement(text,text,text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.increment_engagement(text,text,text) TO service_role;
CREATE FUNCTION public.prune_engagement()
RETURNS void LANGUAGE sql SECURITY INVOKER SET search_path = '' AS $
 DELETE FROM public.engagement_daily WHERE day < (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 89;
 DELETE FROM public.engagement_daily_budget WHERE day < (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - 89;
$;
REVOKE ALL ON FUNCTION public.prune_engagement() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.prune_engagement() TO service_role;
COMMIT;
