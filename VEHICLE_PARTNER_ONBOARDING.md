# Vehicle inventory partner onboarding

Status: exploratory only. No provider access, pricing, or commercial terms assumed.

## Provider questions
- Is an approved read-only API, CSV, or other inventory feed available to independent Australian comparison platforms?
- Which dealers must separately consent? How is consent revoked?
- What are the licensing terms for display, photos, descriptions, historical prices and deep links?
- What are the authentication method, sandbox availability, rate limits, pagination and update frequency?
- Are drive-away prices, location, availability, VIN or provider listing ID and sold/withdrawn states available?
- Are referrals or affiliate attribution supported? What costs or obligations apply?

## Integration acceptance criteria
Map stable provider/dealer/listing identifiers, make, model, variant, year, condition, odometer, price basis (drive-away or excluding charges), currency, location, availability, authorised listing URL, approved image URLs and observation timestamp. Never infer drive-away price or availability.
Validate and quarantine malformed entries. Deduplicate within provider and dealer scope. Avoid VIN-based public exposure unless necessary and permitted. Remove sold, withdrawn or revoked inventory promptly; define expiry with the partner.
Use a server-side secret store, least privilege, bounded requests, backoff, and no credential logging. Begin with synthetic fixtures and then an approved sandbox. No scraping or customer personal data.
Preview imported counts, rejected records and stale records before publishing. Never publish without permission and a verified data contract.

## Commercial gate
No paid access, subscription, exclusivity, referral obligation or provider contract without explicit owner approval.
