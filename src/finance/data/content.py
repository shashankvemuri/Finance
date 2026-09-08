"""Public feeds and article text; availability depends on each publisher."""

import re
from urllib.parse import quote
from xml.etree import ElementTree

import pandas as pd

from finance.data.providers import ProviderError
from finance.data.web import PublicWeb


def rss_news(url: str, *, web: PublicWeb | None = None) -> pd.DataFrame:
    body = (web or PublicWeb()).text(url)
    try:
        root = ElementTree.fromstring(body)
    except ElementTree.ParseError as exc:
        raise ProviderError("Feed is not valid XML") from exc
    records = []
    for item in root.findall(".//item"):
        title, link = item.findtext("title"), item.findtext("link")
        if title and link:
            records.append({"title": title, "url": link, "published": item.findtext("pubDate")})
    if not records:
        raise ProviderError("No RSS news items found")
    result = pd.DataFrame(records).drop_duplicates("url")
    result["published"] = pd.to_datetime(result.published, utc=True, errors="raise")
    return result.reset_index(drop=True)


def article_text(url: str, *, web: PublicWeb | None = None) -> str:
    """Extract a publicly accessible article/transcript by URL; no login or paywall fallback."""
    from lxml import html

    root = html.fromstring((web or PublicWeb()).text(url))
    articles = root.xpath('//*[@id="article-body-transcript"]') or root.xpath("//article")
    if not articles:
        raise ProviderError("No article element; publisher needs a dedicated parser")
    article = max(articles, key=lambda node: len(node.text_content()))
    paragraphs = [" ".join(p.text_content().split()) for p in article.xpath(".//p")]
    result = "\n\n".join(p for p in paragraphs if p)
    if len(result) < 200:
        raise ProviderError("Article is missing or truncated")
    return result


def reddit_posts(subreddit: str, limit: int = 25, *, web: PublicWeb | None = None) -> pd.DataFrame:
    """Public recent posts; fail explicitly if Reddit requires authenticated access."""
    if not re.fullmatch(r"\w{2,30}", subreddit) or not 1 <= limit <= 100:
        raise ValueError("invalid subreddit or limit")
    payload = (web or PublicWeb()).json(
        f"https://www.reddit.com/r/{quote(subreddit)}/new.json?limit={limit}&raw_json=1"
    )
    try:
        rows = [item["data"] for item in payload["data"]["children"]]
        result = pd.DataFrame(
            [
                {
                    "id": r["id"],
                    "text": r["title"] + "\n" + r.get("selftext", ""),
                    "published": pd.to_datetime(r["created_utc"], unit="s", utc=True),
                    "score": r["score"],
                    "url": "https://www.reddit.com" + r["permalink"],
                }
                for r in rows
            ]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProviderError("Reddit response schema changed") from exc
    return result


def transcript_index(*, web: PublicWeb | None = None) -> pd.DataFrame:
    """Discover recent publicly listed Motley Fool transcripts; not a complete historical archive."""
    from urllib.parse import urljoin

    from lxml import html

    url = "https://www.fool.com/earnings-call-transcripts/"
    root = html.fromstring((web or PublicWeb()).text(url))
    records = []
    for link in root.xpath("//a[@href]"):
        href = link.get("href")
        if "/earnings/call-transcripts/" in href:
            title = " ".join(link.text_content().split())
            if title:
                records.append({"title": title, "url": urljoin(url, href)})
    if not records:
        raise ProviderError("Transcript index has no article links")
    return pd.DataFrame(records).drop_duplicates("url").reset_index(drop=True)
