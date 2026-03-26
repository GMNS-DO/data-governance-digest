#!/usr/bin/env python3
“””
Data Governance Digest — Article Fetcher
Runs via GitHub Actions on schedule.
Fetches RSS feeds, categorizes with Claude, writes articles.json
“””

import json
import os
import re
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ── SOURCES ──────────────────────────────────────────────────────────────────

SOURCES = [
# (name, rss_url, default_section)
(“DATAVERSITY”,          “https://www.dataversity.net/category/data-governance/feed/”, “news”),
(“Collibra Blog”,        “https://www.collibra.com/blog/rss”,                          “news”),
(“Nicola Askham”,        “https://www.nicolaaskham.com/blog?format=rss”,               “opinions”),
(“TDAN.com”,             “https://tdan.com/category/data-topics/data-governance/feed/”,“news”),
(“LightsOnData”,         “https://lightsondata.com/feed/”,                             “tools”),
(“Netwrix (DG)”,         “https://blog.netwrix.com/tag/data-governance/feed/”,         “news”),
(“Henrik Liliendahl”,    “https://liliendahl.com/feed/”,                               “opinions”),
(“IT Governance UK”,     “https://www.itgovernance.co.uk/blog/category/data-protection-and-privacy/feed”, “regulation”),
(“Privacy International”,“https://privacyinternational.org/rss.xml”,                   “regulation”),
(“Merudata Blog”,        “https://merudata.com/blog-feed.xml”,                         “news”),
(“InformationBytes”,     “https://informationbytes.com/feed/”,                         “regulation”),
(“Perficient (DG)”,      “https://blogs.perficient.com/tag/data-governance/feed/”,     “tools”),
]

MAX_ARTICLES = 5   # per source
TOTAL_CAP    = 30  # total articles cap

ANTHROPIC_API_KEY = os.environ.get(“ANTHROPIC_API_KEY”, “”)

# ── RSS PARSING ───────────────────────────────────────────────────────────────

def fetch_rss(url, timeout=10):
try:
req = urllib.request.Request(url, headers={“User-Agent”: “DataGovernanceDigest/1.0”})
with urllib.request.urlopen(req, timeout=timeout) as resp:
return resp.read()
except Exception as e:
print(f”  [WARN] Could not fetch {url}: {e}”)
return None

def parse_rss(xml_bytes, source_name, default_section):
articles = []
try:
root = ET.fromstring(xml_bytes)
ns = {“atom”: “http://www.w3.org/2005/Atom”}
channel = root.find(“channel”)
if channel is None:
# Atom feed fallback
entries = root.findall(“atom:entry”, ns) or root.findall(“entry”)
for entry in entries[:MAX_ARTICLES]:
title = (entry.findtext(“atom:title”, namespaces=ns) or entry.findtext(“title”) or “”).strip()
url   = “”
link  = entry.find(“atom:link”, ns) or entry.find(“link”)
if link is not None:
url = link.get(“href”) or link.text or “”
summary = (entry.findtext(“atom:summary”, namespaces=ns) or
entry.findtext(“atom:content”, namespaces=ns) or
entry.findtext(“summary”) or “”).strip()
date_str = (entry.findtext(“atom:updated”, namespaces=ns) or
entry.findtext(“atom:published”, namespaces=ns) or
entry.findtext(“updated”) or “”).strip()
articles.append({
“title”: strip_html(title),
“url”: url.strip(),
“raw_summary”: strip_html(summary)[:600],
“date”: format_date(date_str),
“source”: source_name,
“section”: default_section,
})
return articles

```
    for item in channel.findall("item")[:MAX_ARTICLES]:
        title   = strip_html(item.findtext("title", "")).strip()
        url     = (item.findtext("link") or item.findtext("{http://www.w3.org/2005/Atom}link") or "").strip()
        summary = strip_html(item.findtext("description", "") or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded", "")).strip()[:600]
        date_str = item.findtext("pubDate", "").strip()
        articles.append({
            "title": title,
            "url": url,
            "raw_summary": summary,
            "date": format_date(date_str),
            "source": source_name,
            "section": default_section,
        })
except ET.ParseError as e:
    print(f"  [WARN] XML parse error for {source_name}: {e}")
return articles
```

def strip_html(text):
text = re.sub(r’<[^>]+>’, ’ ‘, text or ‘’)
text = re.sub(r’ ’, ’ ‘, text)
text = re.sub(r’&’, ‘&’, text)
text = re.sub(r’<’, ‘<’, text)
text = re.sub(r’>’, ‘>’, text)
text = re.sub(r’"’, ‘”’, text)
text = re.sub(r’&#\d+;’, ‘’, text)
text = re.sub(r’\s+’, ’ ’, text)
return text.strip()

def format_date(date_str):
if not date_str:
return datetime.now(timezone.utc).strftime(”%d %b %Y”)
try:
dt = parsedate_to_datetime(date_str)
return dt.strftime(”%d %b %Y”)
except Exception:
pass
try:
for fmt in (”%Y-%m-%dT%H:%M:%SZ”, “%Y-%m-%dT%H:%M:%S%z”, “%Y-%m-%d”):
try:
dt = datetime.strptime(date_str[:19], fmt[:len(date_str[:19])])
return dt.strftime(”%d %b %Y”)
except Exception:
continue
except Exception:
pass
return date_str[:16]

# ── AI ENRICHMENT ─────────────────────────────────────────────────────────────

def enrich_with_claude(articles):
“”“Use Claude to generate clean summaries and assign tags.”””
if not ANTHROPIC_API_KEY:
print(”[INFO] No ANTHROPIC_API_KEY — skipping AI enrichment, using raw summaries”)
for a in articles:
a[“summary”] = a[“raw_summary”] or “Read the full article for details.”
a[“tags”] = []
return articles

```
enriched = []
# Batch articles to reduce API calls
batch_size = 6
for i in range(0, len(articles), batch_size):
    batch = articles[i:i+batch_size]
    batch_text = "\n\n".join([
        f"ARTICLE {j+1}:\nTitle: {a['title']}\nSource: {a['source']}\nSection: {a['section']}\nRaw summary: {a['raw_summary']}"
        for j, a in enumerate(batch)
    ])
    prompt = f"""You are an editor for a Data Governance Digest newsletter.
```

For each article below, return a JSON array with one object per article containing:

- summary: A crisp 1-2 sentence summary (max 180 chars). Professional, no fluff.
- tags: Array of 2-3 short tags (e.g. “Data Quality”, “GDPR”, “AI Governance”, “MDM”, “Regulation”, “Best Practice”, “Framework”, “Privacy”, “Compliance”)
- section: One of: news, opinions, tools, regulation (use the given section unless clearly wrong)

Return ONLY a valid JSON array, no preamble, no markdown fences.

{batch_text}
“””
try:
payload = json.dumps({
“model”: “claude-sonnet-4-5-20250929”,
“max_tokens”: 2000,
“messages”: [{“role”: “user”, “content”: prompt}]
}).encode()
req = urllib.request.Request(
“https://api.anthropic.com/v1/messages”,
data=payload,
headers={
“Content-Type”: “application/json”,
“x-api-key”: ANTHROPIC_API_KEY,
“anthropic-version”: “2023-06-01”,
}
)
with urllib.request.urlopen(req, timeout=30) as resp:
result = json.loads(resp.read())
text = result[“content”][0][“text”].strip()
# Strip markdown fences robustly
text = re.sub(r’^`(?:json)?\s*', '', text, flags=re.MULTILINE) text = re.sub(r'\s*`\s*$’, ‘’, text, flags=re.MULTILINE)
text = text.strip()
parsed = json.loads(text)
# Handle if Claude wraps in a dict like {“articles”: […]}
enrichments = parsed if isinstance(parsed, list) else parsed.get(“articles”, parsed.get(“items”, []))
for j, a in enumerate(batch):
if j < len(enrichments):
a[“summary”] = enrichments[j].get(“summary”, a[“raw_summary”])[:220]
a[“tags”]    = enrichments[j].get(“tags”, [])[:3]
a[“section”] = enrichments[j].get(“section”, a[“section”])
else:
a[“summary”] = a[“raw_summary”] or “”
a[“tags”] = []
enriched.extend(batch)
except Exception as e:
print(f”  [WARN] Claude enrichment failed for batch: {e}”)
for a in batch:
a[“summary”] = a[“raw_summary”] or “”
a[“tags”] = []
enriched.extend(batch)
time.sleep(0.5)  # gentle rate limiting
return enriched

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
print(f”[{datetime.now().isoformat()}] Starting Data Governance Digest fetch…”)
all_articles = []

```
for (name, url, section) in SOURCES:
    print(f"  Fetching: {name}")
    xml = fetch_rss(url)
    if xml:
        arts = parse_rss(xml, name, section)
        print(f"    → {len(arts)} articles")
        all_articles.extend(arts)
    time.sleep(0.3)

# Deduplicate by URL
seen = set()
deduped = []
for a in all_articles:
    if a["url"] and a["url"] not in seen:
        seen.add(a["url"])
        deduped.append(a)

# Cap total
deduped = deduped[:TOTAL_CAP]
print(f"  Total unique articles: {len(deduped)}")

# AI enrichment
print("  Enriching with Claude…")
enriched = enrich_with_claude(deduped)

# Clean up raw_summary field
for a in enriched:
    a.pop("raw_summary", None)

output = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "article_count": len(enriched),
    "articles": enriched
}

with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"  ✓ Written articles.json with {len(enriched)} articles")
```

if **name** == “**main**”:
main()