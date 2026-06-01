from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import requests
import re

app = FastAPI(
    title="Siyatha News API",
    description="Live scraper API for siyathanews.lk"
)

@app.get("/")
async def root():
    return {
        "success": True,
        "creator": "WhiteShadow",
        "message": "Siyatha News API",
        "endpoint": "/api/news"
    }

@app.get("/api/news")
async def get_news():
    url = "https://siyathanews.lk"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news: {str(e)}"
        )

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    news_containers = soup.find_all("div", class_="td-module-container")

    for container in news_containers:
        title_tag = container.find("h3", class_="entry-title")

        if not title_tag:
            continue

        link_tag = title_tag.find("a")

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        link = link_tag.get("href", "")

        summary = ""
        excerpt = container.find("div", class_="td-excerpt")

        if excerpt:
            summary = excerpt.get_text(strip=True)

        image_url = ""

        thumb = container.find("span", class_="entry-thumb td-thumb-css")

        if thumb and thumb.get("style"):
            match = re.search(
                r'url\([\'"]?(.*?)[\'"]?\)',
                thumb["style"]
            )

            if match:
                image_url = match.group(1)

        if not image_url:
            img = container.find("img")

            if img:
                image_url = (
                    img.get("src")
                    or img.get("data-src")
                    or ""
                )

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "image_url": image_url
        })

        if len(articles) >= 5:
            break

    return {
        "success": True,
        "creator": "WhiteShadow",
        "count": len(articles),
        "result": articles
    }
