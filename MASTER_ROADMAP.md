# BargainIQ master roadmap — retail only
Updated 27 November 2026. Routine development authorised; no expenditure without owner approval. Merged code is not proof of production deployment. Preserve verified history and customer records. Never fabricate inventory, discounts, reviews or traffic.

## P0 — customer experience and release integrity
- [x] Independent retail site; automotive moved to CarRadar (PR 28).
- [x] Retail account interface and legacy automotive record preservation (PR 29); underlying database grants unchanged.
- [x] Clean public build, 25 retail guides, five categories, requirements-first search, matching cards and account-synchronised saved requests.
- [x] Personal discovery criteria displayed (PR 30).
- [ ] Balanced retail homepage and responsive navigation (current layout branch).
- [ ] Independently verify live deployment, authentication, mobile/desktop accessibility and actual user journeys.
- [ ] Resolve open PR 24 stale-price candidate issue before enabling alerts; reconcile overlapping PR 26 with current main.
- [ ] Remove legacy automotive source files only after dependency audit; retain historical records safely. CarRadar referral link remains.

## P1 — product discovery and supply
- [x] Retail feed validation, matching by identifiers/variant/condition, recorded price history, approved-source preview processing.
- [ ] Authorised retailer or affiliate feed access; Awin enquiry sent, Commission Factory declined early application. No approved live feed established.
- [ ] Establish a useful first category (furniture/homewares preferred subject to feed access), confirm delivery/stock/variant accuracy and publication rights.
- [ ] Automated approved-feed retrieval, validation, freshness/withdrawal handling, monitored publication.
- [ ] Personal shopping dashboard: saved requirements, matching products, delivered prices, recorded drops, cross-device recommendations.
- [ ] Repair and validate opt-in alert candidate logic, then notification preferences, deduplication, delivery and unsubscribe. No active automated alerts yet.

## P2 — acquisition and trust
- [x] Editorial methodology, original diagrams, beta noindex, offline sitemap, aggregate analytics infrastructure and privacy controls.
- [ ] Production security review, account removal, protected analytics endpoint, abuse controls, retention and real-admin verification. No analytics collection activated.
- [ ] Verify useful inventory and customer experience before enabling indexing, sitemap and search console.
- [ ] Expand independently useful buying guides and original/authorised images, test organic acquisition with real traffic.

## P3 — commercial validation
- [ ] Approved affiliate tracking and disclosures; measure qualified clicks and conversion.
- [ ] Validate repeat use, first revenue, unit economics and retailer demand before paid expansion.
- [ ] Sponsored placement disclosures, retailer reporting and commercial packages only after demonstrated demand.
- [ ] Scale categories and partnerships based on verified performance.

## Operating rules
Each release: scoped branch, regression tests, merge only after green checks, verify production separately. No paid subscriptions or domains without approval. Separate CarRadar development in yardsy/CarRadar. Historical roadmap retained in Git history; prior DB isolation audit passed rollback fixtures on 26 November, but production auth and data permissions need ongoing verification.
