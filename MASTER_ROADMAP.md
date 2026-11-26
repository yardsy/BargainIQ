# BargainIQ master roadmap
Agreed 26 November 2026. Supersedes previous roadmaps. Routine development authorised; no additional expenditure without owner approval.
Status: [x] merged implementation (not necessarily verified production); [ ] outstanding. Mark fully released only after relevant tests and production verification. Record evidence and blockers. No fabricated inventory, reviews, imagery claims or traffic.

## 1. Complete existing development
- [x] Website design/navigation, retail and vehicle comparison frameworks, resale calculator
- [x] Accounts, watchlists, price history, specification filters, natural-language requests
- [x] Account-synchronised searches and cross-device tests (PR 10 passed and merged; production and real-account isolation verification pending)
- [x] Multi-retailer processing and scheduled preview validation (V12, PR 11 passed and merged)
- [ ] Activate authorised inventory feeds and publication
- [x] Recover and merge V11/V12 releases (PRs 10–11)
- [x] Automated validation against generated public build (PR 14)
- [ ] Independently verify production deployment
- [x] Existing mocked browser smoke tests against public build (PR 14)
- [ ] Complete production mobile, desktop and accessibility audit

## 2. Content and website quality
- [x] Buying guide library release (PR 7 merged; PR 8 merged with 12 individual pages)
- [x] 30 individual original articles (PR 9 passed and merged)
- [x] Six category landing pages (PR 9 passed and merged)
- [x] Initial three manufacturer-linked editorial comparisons (PR 15)
- [ ] Expand verified comparisons and authorised live product listings
- [x] Initial four original educational diagrams (PR 12 merged)
- [ ] Expand original or authorised product imagery
- [x] Editorial methodology (PR 9 passed and merged)
- [x] Homepage editorial navigation (PR 12 merged)
- [ ] Consolidate empty inventory sections

## 3. SEO, analytics and acquisition
- [x] Initial SEO metadata and private-beta indexing safeguards
- [x] Aggregate analytics processing and admin report import (PR 11 merged)
- [ ] Live analytics collection and admin reporting integration (browser event client implemented, disabled; backend and activation pending)
- [x] Individual article SEO (PR 9), browser retailer click hooks and privacy tests (PR 13), initial keyword and competitor research (PR 15)
- [ ] Activate and verify retailer click reporting and refine search strategy using actual traffic
- [x] Internal links, beta robots policy and offline sitemap generation (PR 12 merged)
- [ ] Publish sitemap after launch checks
- [ ] Search Console and Bing Webmaster Tools verification
- [ ] Enable public indexing only after launch checks
- [ ] Organic social strategy, performance optimisation, final brand identity

## 4. Partnerships and inventory
- [x] Initial 14 outreach attempts; affiliate shortlist and onboarding documentation developed
- [ ] Vyro (in progress), Dealer Studio (pending), direct retail partners
- [ ] Schots follow-up (drafted; original email bounced)
- [ ] Alternative affiliate networks; Commission Factory reapplication after content and genuine traffic
- [ ] Authorised API/feed access, retrieval, validated publication and accuracy monitoring

## 5. Advanced customer functionality
- [x] Price-target and shopping-request matching engine and unit tests (PR 11 merged)
- [ ] Connect matching to authorised inventory, saved preferences and notification delivery
- [ ] Notification preferences, automatic email delivery and matching product alerts
- [ ] Customer feedback

## 6. Monetisation
- [ ] Integrate approved affiliate links, attribution and disclosures
- [ ] Sponsored placements, retailer landing page and advertising packages
- [ ] Retailer performance and revenue reporting
- [ ] First revenue

## 7. Launch and growth
- [x] Live database RLS audit: 13/13 public tables protected; anonymous customer data access denied; controlled two-account saved-search, watchlist, price-target, profile and submission isolation tests passed 26 November 2026 (transaction rollback)
- [x] Local browser data clearing controls (PR 18); five customer-table deletion cascade checks passed in rollback fixture.
- [ ] Remaining security/privacy review: narrower grants, leaked-password protection, account removal and production verification
- [ ] Public launch, customer acquisition, conversion optimisation
- [ ] Commission Factory reapplication, retailer/category expansion and profitable growth

## Immediate sequence
PRs 7, 8, 9 and 10 passed tests and merged. PR 11 (V12) passed validation and merged. PR 12 passed validation and merged homepage, original diagrams and beta SEO preparation. PRs 13–15 passed validation and merged: disabled analytics client, public build tests, three editorial comparisons and initial search research. PRs 16–19 passed and merged: expanded requirements-first guides, database isolation evidence, local privacy controls and Cloudflare migration configuration. Cloudflare primary URL is https://bargainiq.pages.dev/; owner confirmed Supabase redirect settings, live deployment verification pending. Analytics backend not active. Verify live deployment: direct retrieval of production homepage, router guide and furniture category unsuccessful on 26 November 2026; not evidence of downtime. Build useful original editorial pages and imagery while awaiting approved inventory. Establish genuine analytics and public content readiness before reapplication. Prioritise release over new disconnected modules.
