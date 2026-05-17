# Meta ad comment → objection classifier

`fetch_meta_comments.py` pulls comments from Meta ad posts and bins them
by objection category (price, accuracy skepticism, app/connectivity,
shipping, competitors, refund/warranty, support, health-claim skepticism,
DEXA comparison, weight-loss concern, positive, intent, etc.). Categories
are tuned for the Hume Body Pod smart-scale context.

## Setup

1. Create a System User token (or use a temporary Graph API Explorer token) with:
   - `ads_read`
   - `pages_read_engagement`
   - `pages_show_list`
   - access to the page owning the ad posts
2. Export env vars:
   ```
   export META_ACCESS_TOKEN=EAAG...
   export AD_ACCOUNT_ID=act_3630696143872779
   # optional, enables LLM fallback for low-confidence rule matches
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

## Run

```bash
python3 scripts/fetch_meta_comments.py --days 30 --min-comments 10 --limit-ads 25
# add --use-claude to enable the Claude fallback
```

Outputs:
- `meta_comments.json` — every classified comment with ad/campaign/post metadata.
- `meta_objections_summary.json` — counts per category, per ad and overall.

## Adjusting categories

Edit `OBJECTION_RULES` in `fetch_meta_comments.py`. The list is ordered:
the first matching pattern wins.
