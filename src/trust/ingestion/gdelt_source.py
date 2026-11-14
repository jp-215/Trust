import requests


class GDELTSource:
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    def search(self, keywords: str, max_records: int = 250, time_span: str = "7d") -> list[dict]:
        params = {
            "query": keywords,
            "mode": "json",
            "maxrecords": max_records,
            "timespan": time_span,
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = []
            for article in data.get("articles", []):
                articles.append(
                    {
                        "url": article.get("url", ""),
                        "title": article.get("title", ""),
                        "source": article.get("sourcecountry", "Unknown"),
                        "published_at": article.get("seendate", ""),
                    }
                )
            return articles
        except Exception as e:
            print(f"GDELT error: {e}")
            return []
