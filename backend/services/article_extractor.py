import requests
from newspaper import Article
from bs4 import BeautifulSoup


def extract_title_from_soup(soup, fallback_title="제목 없음"):
    og_title = soup.find("meta", property="og:title")

    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    twitter_title = soup.find("meta", attrs={"name": "twitter:title"})

    if twitter_title and twitter_title.get("content"):
        return twitter_title["content"].strip()

    h1 = soup.find("h1")

    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    if fallback_title:
        return fallback_title.strip()

    return "제목 없음"


def extract_article(url: str):
    """
    Extract title and body text from a news article URL.
    It tries newspaper3k first, then uses BeautifulSoup for a more accurate title.
    """
    newspaper_title = ""
    newspaper_text = ""

    try:
        article = Article(url, language="ko")
        article.download()
        article.parse()

        newspaper_title = article.title or ""
        newspaper_text = article.text or ""

    except Exception as e:
        print("newspaper3k failed:", e)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = extract_title_from_soup(soup, fallback_title=newspaper_title)

        if newspaper_text and len(newspaper_text) > 300:
            return {
                "title": title,
                "text": newspaper_text,
                "url": url
            }

        paragraphs = soup.find_all("p")
        text = "\n".join(
            p.get_text(strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )

        return {
            "title": title,
            "text": text,
            "url": url
        }

    except Exception as e:
        print("BeautifulSoup failed:", e)

        return {
            "title": newspaper_title if newspaper_title else "기사 추출 실패",
            "text": newspaper_text,
            "url": url
        }