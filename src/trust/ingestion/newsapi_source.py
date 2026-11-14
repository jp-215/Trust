import requests


class NewsAPISource:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"

    def search(self, query: str, page_size: int = 100, page: int = 1) -> list[dict]:
        params = {
            "q": query,
            "pageSize": page_size,
            "page": page,
            "apiKey": self.api_key,
        }
        try:
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
