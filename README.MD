# 📰 The Data Governance Digest

### Curated by GMNS Data Office
A beautiful, auto-refreshing data governance intelligence digest — hosted free on GitHub Pages, powered by real RSS feeds and Claude AI summaries.

-----

## 🚀 Setup in 5 Steps

### Step 1 — Create a GitHub Repository

1. Go to [github.com](https://github.com) → click **New repository**
1. Name it: `data-governance-digest` (or anything you like)
1. Set it to **Public** (required for free GitHub Pages)
1. Click **Create repository**

-----

### Step 2 — Upload These Files

Upload all files from this folder to the root of your repository:

```
/
├── index.html            ← The digest website
├── fetch_articles.py     ← Article fetcher script
├── articles.json         ← Auto-generated (commit an empty version first)
└── .github/
    └── workflows/
        └── refresh.yml   ← GitHub Actions automation
```

For `articles.json`, commit this placeholder first:

```json
{"generated_at": "", "article_count": 0, "articles": []}
```

-----

### Step 3 — Add Your Anthropic API Key

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
1. Click **New repository secret**
1. Name: `ANTHROPIC_API_KEY`
1. Value: your key from [console.anthropic.com](https://console.anthropic.com)
1. Click **Add secret**

> **Note:** Without this key the digest still works — it just shows raw summaries instead of AI-polished ones.

-----

### Step 4 — Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
1. Under **Source**, select `Deploy from a branch`
1. Branch: `main` · Folder: `/ (root)`
1. Click **Save**

After ~2 minutes your digest is live at:

```
https://YOUR-USERNAME.github.io/data-governance-digest/
```

-----

### Step 5 — Run the First Fetch

1. Go to your repo → **Actions** tab
1. Click **Refresh Data Governance Digest**
1. Click **Run workflow** → **Run workflow**

Articles will appear on your page within ~60 seconds! 🎉

-----

## 🔄 Refresh Schedule

|Type          |When                    |What                             |
|--------------|------------------------|---------------------------------|
|**Daily News**|Every day at 6:00 AM UTC|Top articles from all RSS sources|
|**Manual**    |Anytime via Actions tab |On-demand refresh                |

You can also change the cron schedule in `.github/workflows/refresh.yml`.

-----

## 📡 Curated Sources

|Source                  |Category                 |
|------------------------|-------------------------|
|DATAVERSITY             |Education / Articles     |
|Collibra Blog           |Practitioner / Vendor    |
|Nicola Askham (DG Coach)|Expert Blog              |
|TDAN.com                |Newsletter / Practitioner|
|LightsOnData            |Data Quality & Governance|
|Netwrix Blog            |Security / Governance    |
|Henrik Liliendahl Blog  |MDM / Data Quality       |
|IT Governance UK        |GDPR / Compliance        |
|Privacy International   |Regulation / Policy      |
|Merudata Blog           |IG Programs              |
|InformationBytes        |Data Privacy Law         |
|erwin (Quest) Blog      |Enterprise DG            |

To add/remove sources, edit the `SOURCES` list in `fetch_articles.py`.

-----

## 💡 Sharing Your Digest

Once live, just share the GitHub Pages URL:

```
https://YOUR-USERNAME.github.io/data-governance-digest/
```

No login required. Anyone with the link can read it.

-----

## 🛠 Customization

- **Change curator name**: Edit `index.html` — search for “Richard Horst”
- **Add a new source**: Add a tuple to `SOURCES` in `fetch_articles.py`
- **Change refresh time**: Edit the `cron` line in `refresh.yml`
- **Add more sections**: Extend the section filter logic in `index.html`

-----

*Built with GitHub Pages + GitHub Actions + Claude AI*
