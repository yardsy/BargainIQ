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
COMMIT;
