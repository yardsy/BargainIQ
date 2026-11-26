# Commission Factory onboarding
Research date: 2026-11-26. All candidates unapproved; rates indicative, subject to publisher type and terms.

| Priority | Merchant | Directory ID | Advertised rate | Feed |
|---|---|---|---|---|
| 1 | Crazy Sales | 12475 | 5% | Yes |
| 2 | Costway Australia | 84326 | 5% | Yes |
| 3 | Schots | 91189 | 3–10% | Yes |
| 4 | House | 89275 | 3–8% | Yes |
| 5 | MyHouse | 89274 | 3–8% | Yes |
| 6 | Newentor | 81833 | 10% | Yes |
| 7 | Emma Sleep | 70242 | Up to 8%; category/publisher restrictions | Yes |
| 8 | Bedzy | 80589 | 5% standard; coupon restrictions | On request |
| 9 | Ergoflex | 54292 | 4% | Yes |
| 10 | Ruggable | 91503 | 3–7% | Yes |
| 11 | BecexTech | 50732 | 0.8% | Yes |
| 12 | Global Shop Direct | 76774 | Confirm | Yes |
| 13 | KOO | 88123 | Up to 8% | Yes |

Directory IDs are prospect references, not approved feed IDs or API credentials.

## Integration gates
1. Obtain publisher approval and apply to individual advertisers; check comparison-site eligibility, data reuse, caching and commission rules.
2. Confirm approved merchants and sample exports before building a production mapping.
3. Official affiliate API: https://dev.commissionfactory.com/V1/Affiliate/Functions/GetDataFeeds/ . The list endpoint returns feed metadata, individual feed endpoint returns items.
4. Keep API key server-side, redact query strings from logs, restrict hosts, enforce bounded requests and backoff. Never commit a key or live feed containing private credentials.
5. Map actual SKU, title, URL, category, currency, price and image; preserve original and authorised tracking destinations separately. Missing dimensions, condition, shipping and variant remain unknown unless confirmed. Never fabricate observation timestamps or match uncertain configurations.
6. Preview authorised local snapshots through retail_batch.py, run tests, verify commercial disclosures and publication permission before release.

Field guidance: https://help.commissionfactory.com/data-feed-best-practice-guide
Affiliate exports: https://help.commissionfactory.com/exporting-creatives
No paid service or commitment without owner approval.
