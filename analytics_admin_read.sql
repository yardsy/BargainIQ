-- Only existing administrator members may read daily aggregates.
GRANT SELECT ON public.engagement_daily TO authenticated;
CREATE POLICY engagement_admin_read ON public.engagement_daily
 FOR SELECT TO authenticated
 USING (EXISTS (SELECT 1 FROM public.admin_members WHERE user_id=(SELECT auth.uid())));
