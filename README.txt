BargainIQ / CarRadar V5 — GitHub cloud pilot

1. Create a new public repository at https://github.com/new (suggested name bargainiq). Public means code and stock data are public; never upload credentials or private dealer data.
2. Extract this archive. Upload index.html, stock.json, adapter.py, collector.py, test_collector.py and README.txt to the repository root. Commit.
3. In the repository, choose Add file > Create new file. Name it .github/workflows/refresh.yml and paste the contents of the supplied workflow file. Commit. (The hidden folder may not be visible by default; an identical copy named workflow-copy.txt is provided.)
4. Settings > Pages > Build and deployment > Source: GitHub Actions.
5. Actions > CarRadar stock refresh > Run workflow. The deployment step will show the website URL. The initial site displays historical stock only.
6. Enable collection only after confirming permission and redistribution rights for each source. Settings > Secrets and variables > Actions > Variables > New repository variable. Name APPROVED_DEALERS; value is a space-separated list of approved slugs: essendonhyundai sheppartonhyundai sydneycityhyundai wayvillehyundai johnhugheshyundai. Include only approved dealers. Run workflow again and inspect logs. No local Python needed.
7. The workflow is scheduled approximately every four hours, subject to GitHub scheduling and inactivity rules. On failed collection, old listings are retained and marked unconfirmed. The collector handles first pages only, not nationwide inventory. No live end-to-end verification yet. The URL fallback requires a stable individual listing URL, not the generic search page. Check actual output before using for purchasing decisions.

No Supabase or Cloudflare account is needed for this pilot. No credentials should be committed. All non-car sections remain demonstration data. Do not sell access or publish third-party inventory without necessary rights.
