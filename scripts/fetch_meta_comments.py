#!/usr/bin/env python3
"""Pull comments from Meta ad posts and classify them by objection.

Usage:
    META_ACCESS_TOKEN=EAA... AD_ACCOUNT_ID=act_3630696143872779 \
        python3 scripts/fetch_meta_comments.py [--days 30] [--min-comments 5] [--limit-ads 50]

Optional:
    ANTHROPIC_API_KEY=sk-ant-...   Enables Claude fallback for ambiguous comments.

The script:
  1. Lists ads from the account with `effective_object_story_id`.
  2. Pulls insights to find ads with the most post comments.
  3. Fetches `/{post_id}/comments` (paginated) for the top ads.
  4. Classifies each comment by objection category (regex first; Claude fallback
     when ANTHROPIC_API_KEY is set and the rules can't confidently match).
  5. Writes `meta_comments.json` (raw) and `meta_objections_summary.json`
     (counts by category, per ad and overall) to the working directory.

Required Meta permissions on the access token:
  - ads_read
  - pages_read_engagement
  - pages_show_list  (to read post-level comments on owned pages)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from typing import Iterable

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def graph_get(path: str, params: dict, token: str, retries: int = 3) -> dict:
    qs = urllib.parse.urlencode({**params, "access_token": token})
    url = f"{GRAPH_BASE}/{path.lstrip('/')}?{qs}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 or e.code >= 500:
                wait = 2 ** attempt
                print(f"  retrying after {wait}s ({e.code})", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"Graph API {e.code}: {body}") from e
        except urllib.error.URLError as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed after {retries} retries: {path}")


def graph_paginate(path: str, params: dict, token: str, max_pages: int = 20) -> Iterable[dict]:
    next_url = None
    page = 0
    while page < max_pages:
        if next_url:
            with urllib.request.urlopen(next_url, timeout=30) as resp:
                data = json.loads(resp.read())
        else:
            data = graph_get(path, params, token)
        for row in data.get("data", []):
            yield row
        next_url = data.get("paging", {}).get("next")
        if not next_url:
            return
        page += 1


# ---------------------------------------------------------------------------
# Objection classification
# ---------------------------------------------------------------------------

# Tuned for a smart-scale / body composition product (Hume Body Pod).
# Order matters: the first matching pattern wins, so put narrow/strong signals
# (positive sentiment, DEXA comparison) before broader buckets that share
# keywords (weight_loss_concern, competitors).
OBJECTION_RULES: list[tuple[str, re.Pattern]] = [
    ("positive", re.compile(
        r"\b(love\s+(it|this|mine|my)|amazing|best\s+(scale|purchase|buy)|"
        r"great\s+product|highly\s+recommend|game[\s-]?chang(er|ing)|"
        r"life[\s-]?sav(er|ing)|obsessed)\b", re.I)),
    ("comparison_dexa", re.compile(
        r"\b(compared?\s+to\s+(a\s+)?dexa|vs\.?\s*dexa|like\s+a\s+dexa|"
        r"dexa\s+scan)\b", re.I)),
    ("refund_warranty", re.compile(
        r"\b(refund|return(ed|ing|s)?\s+(it|policy)?|warrant(y|ies)|"
        r"brok(e|en)\s+(after|down)|stopped\s+work|defective|"
        r"replace(ment)?|cancel(led|ling)?)\b", re.I)),
    ("accuracy_skepticism", re.compile(
        r"\b(accura(te|cy)|scam|fake|bogus|\blie\b|liar|hoax|legit|"
        r"real(\??|ly)\?|trust(ed|worthy)?|believ|doesn'?t\s+work|"
        r"don'?t\s+work|gimmick|snake\s*oil)\b", re.I)),
    ("app_connectivity", re.compile(
        r"\b(\bapp\b|bluetooth|blue\s*tooth|wifi|wi[-\s]?fi|sync(ing|ed)?|"
        r"connect(ing|ion|ivity)?|android|ios|iphone|pair(ing|ed)?|"
        r"crash(es|ed|ing)?|firmware)\b", re.I)),
    ("shipping_delivery", re.compile(
        r"\b(ship(ping|ped)?|deliver(y|ed)?|arriv(e|ed|ing)|tracking|"
        r"wait(ing)?\s+(on|for|to\s+receive)\s+my|still\s+wait(ing)?|"
        r"where['s\s]+my\s+order|haven'?t\s+(received|got|gotten))\b", re.I)),
    ("competitors", re.compile(
        r"\b(withings|renpho|tanita|inbody|fitbit|garmin|oura|whoop|"
        r"apple\s*health|google\s*fit|myfitnesspal|eufy|wyze|happy\s*scale)\b",
        re.I)),
    ("customer_support", re.compile(
        r"\b(customer\s+(service|support)|support\s+team|no\s+(reply|response)|"
        r"never\s+(reply|respond|answers)|ticket|no\s+one\s+(answers|responds))\b",
        re.I)),
    ("health_claim_skepticism", re.compile(
        r"\b(body\s*fat|muscle\s+mass|metabolic\s+age|\bbmi\b|visceral|"
        r"hydration|bone\s+mass|basal|bmr)\b.*\b(accura|wrong|off|true|"
        r"correct|believ|trust)\b", re.I)),
    ("price", re.compile(
        r"(\$\d+|\b(price|pricing|cost(s|ly)?|expensive|cheap|afford|"
        r"too\s+much|how\s+much|can'?t\s+afford|budget|worth\s+(it|the\s+price)|"
        r"overpriced|cheaper)\b)", re.I)),
    ("weight_loss_concern", re.compile(
        r"\b(weight\s+loss|losing\s+weight|gain(ing|ed)?\s+weight|"
        r"plateau|diet(ing)?|calorie|deficit)\b", re.I)),
    ("interest_intent", re.compile(
        r"\b(where\s+can\s+i\s+(buy|get)|how\s+do\s+i\s+(buy|get|order)|"
        r"link\s+please|link\??$|interested|sign\s+me\s+up|want\s+one|"
        r"need\s+(this|one))\b", re.I)),
]


def classify_with_rules(message: str) -> tuple[str, float]:
    """Return (category, confidence). Confidence 1.0 for clear rule match,
    0.6 for question-only, 0.0 for unmatched."""
    if not message or not message.strip():
        return ("empty", 1.0)
    matched = []
    for label, pat in OBJECTION_RULES:
        if pat.search(message):
            matched.append(label)
    if matched:
        # Prefer the first (highest-priority) match; surface multi-match in metadata.
        return (matched[0], 1.0 if len(matched) == 1 else 0.85)
    if message.strip().endswith("?"):
        return ("question_other", 0.6)
    return ("unclassified", 0.0)


CLAUDE_PROMPT = """Classify this Meta ad comment into ONE objection category.

Comment: {comment}

Categories:
- price (cost, affordability)
- accuracy_skepticism (does the product work, is it real)
- app_connectivity (app, bluetooth, sync issues)
- shipping_delivery (delivery time, tracking)
- competitors (mentions of competing products)
- refund_warranty (returns, broken units, warranty)
- customer_support (service complaints)
- health_claim_skepticism (doubts about body fat, BMI, metabolic age)
- comparison_dexa (comparing to DEXA scans)
- weight_loss_concern (weight goals, dieting)
- positive (praise, love it)
- interest_intent (asking how to buy)
- question_other (a question not in other categories)
- spam (giveaway tagging, off-topic spam)
- other

Respond with JSON only: {{"category": "<one_of_above>", "confidence": <0-1>, "reason": "<5 word reason>"}}
"""


def classify_with_claude(message: str, api_key: str) -> tuple[str, float, str] | None:
    payload = {
        "model": "claude-haiku-4-5",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": CLAUDE_PROMPT.format(comment=message[:500])}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        text = data["content"][0]["text"].strip()
        # Strip code fences if Claude added them.
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
        parsed = json.loads(text)
        return (parsed["category"], float(parsed.get("confidence", 0.8)),
                parsed.get("reason", ""))
    except Exception as e:
        print(f"  claude classify failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def list_top_ads(account_id: str, token: str, days: int, min_comments: int,
                 limit_ads: int) -> list[dict]:
    """Return ads sorted by post comment count, with effective_object_story_id."""
    since = time.strftime("%Y-%m-%d", time.gmtime(time.time() - days * 86400))
    until = time.strftime("%Y-%m-%d")
    print(f"fetching ads {since} → {until} ...", file=sys.stderr)

    insights = list(graph_paginate(
        f"{account_id}/insights",
        {
            "level": "ad",
            "fields": "ad_id,ad_name,campaign_name,spend,actions",
            "time_range": json.dumps({"since": since, "until": until}),
            "limit": 200,
        },
        token,
        max_pages=10,
    ))

    rows = []
    for row in insights:
        comment_count = 0
        for action in row.get("actions") or []:
            if action.get("action_type") == "comment":
                comment_count = int(action.get("value", 0))
                break
        if comment_count < min_comments:
            continue
        rows.append({
            "ad_id": row.get("ad_id"),
            "ad_name": row.get("ad_name"),
            "campaign_name": row.get("campaign_name"),
            "spend": float(row.get("spend", 0)),
            "comment_count": comment_count,
        })
    rows.sort(key=lambda r: -r["comment_count"])
    rows = rows[:limit_ads]

    print(f"  resolving post IDs for {len(rows)} ads ...", file=sys.stderr)
    for r in rows:
        try:
            ad = graph_get(r["ad_id"],
                           {"fields": "creative{effective_object_story_id,object_story_id}"},
                           token)
            creative = ad.get("creative", {}) or {}
            r["post_id"] = (creative.get("effective_object_story_id")
                            or creative.get("object_story_id"))
        except Exception as e:
            print(f"  skip {r['ad_id']}: {e}", file=sys.stderr)
            r["post_id"] = None
    return rows


def fetch_comments(post_id: str, token: str, max_comments: int = 500) -> list[dict]:
    out = []
    for c in graph_paginate(
        f"{post_id}/comments",
        {"fields": "id,message,from,created_time,comment_count,like_count",
         "limit": 100, "order": "reverse_chronological"},
        token,
        max_pages=max(1, max_comments // 100),
    ):
        out.append(c)
        if len(out) >= max_comments:
            break
    return out


def get_page_token(page_id: str, user_token: str, cache: dict) -> str | None:
    """Exchange the user token for a Page access token (cached per page)."""
    if page_id in cache:
        return cache[page_id]
    try:
        data = graph_get(page_id, {"fields": "access_token"}, user_token)
        tok = data.get("access_token")
        cache[page_id] = tok
        return tok
    except Exception as e:
        print(f"  no page token for {page_id}: {e}", file=sys.stderr)
        cache[page_id] = None
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--min-comments", type=int, default=5)
    p.add_argument("--limit-ads", type=int, default=25)
    p.add_argument("--max-comments-per-ad", type=int, default=300)
    p.add_argument("--out", default="meta_comments.json")
    p.add_argument("--summary-out", default="meta_objections_summary.json")
    p.add_argument("--use-claude", action="store_true",
                   help="Fall back to Claude for unclassified comments (needs ANTHROPIC_API_KEY).")
    args = p.parse_args()

    token = os.environ.get("META_ACCESS_TOKEN")
    account_id = os.environ.get("AD_ACCOUNT_ID")
    if not token or not account_id:
        print("error: set META_ACCESS_TOKEN and AD_ACCOUNT_ID env vars", file=sys.stderr)
        return 2
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY") if args.use_claude else None
    if args.use_claude and not anthropic_key:
        print("warn: --use-claude set but ANTHROPIC_API_KEY missing; skipping LLM fallback",
              file=sys.stderr)

    ads = list_top_ads(account_id, token, args.days, args.min_comments, args.limit_ads)
    print(f"found {len(ads)} ads with >= {args.min_comments} comments", file=sys.stderr)

    all_comments = []
    per_ad_counts: dict[str, Counter] = defaultdict(Counter)
    global_counts: Counter = Counter()
    page_token_cache: dict[str, str | None] = {}

    for ad in ads:
        if not ad.get("post_id"):
            continue
        page_id = ad["post_id"].split("_", 1)[0]
        page_token = get_page_token(page_id, token, page_token_cache) or token
        print(f"  fetching comments for ad {ad['ad_id']} (post {ad['post_id']}) ...",
              file=sys.stderr)
        try:
            comments = fetch_comments(ad["post_id"], page_token, args.max_comments_per_ad)
        except Exception as e:
            print(f"    failed: {e}", file=sys.stderr)
            continue
        print(f"    got {len(comments)} comments", file=sys.stderr)

        for c in comments:
            msg = c.get("message", "") or ""
            category, confidence = classify_with_rules(msg)
            reason = ""
            classifier = "rules"
            if confidence < 0.6 and anthropic_key and msg.strip():
                llm = classify_with_claude(msg, anthropic_key)
                if llm:
                    category, confidence, reason = llm
                    classifier = "claude"

            record = {
                "ad_id": ad["ad_id"],
                "ad_name": ad["ad_name"],
                "campaign_name": ad.get("campaign_name"),
                "post_id": ad["post_id"],
                "comment_id": c.get("id"),
                "message": msg,
                "created_time": c.get("created_time"),
                "like_count": c.get("like_count"),
                "reply_count": c.get("comment_count"),
                "category": category,
                "confidence": confidence,
                "classifier": classifier,
                "reason": reason,
            }
            all_comments.append(record)
            per_ad_counts[ad["ad_id"]][category] += 1
            global_counts[category] += 1

    with open(args.out, "w") as f:
        json.dump(all_comments, f, indent=2, ensure_ascii=False)

    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lookback_days": args.days,
        "total_comments_classified": len(all_comments),
        "global_objection_counts": dict(global_counts.most_common()),
        "per_ad": [
            {
                "ad_id": ad["ad_id"],
                "ad_name": ad["ad_name"],
                "campaign_name": ad.get("campaign_name"),
                "spend": ad.get("spend"),
                "comment_count_reported": ad.get("comment_count"),
                "objection_counts": dict(per_ad_counts[ad["ad_id"]].most_common()),
            }
            for ad in ads if ad.get("post_id")
        ],
    }
    with open(args.summary_out, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nwrote {args.out} ({len(all_comments)} comments)", file=sys.stderr)
    print(f"wrote {args.summary_out}", file=sys.stderr)
    print("\ntop objections overall:", file=sys.stderr)
    for cat, n in global_counts.most_common(10):
        print(f"  {cat:30s} {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
