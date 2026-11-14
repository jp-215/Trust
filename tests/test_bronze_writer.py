import unittest
from datetime import datetime
from trust.ingestion.bronze_writer import (
    normalize_apify_item,
    normalize_newsapi_item,
    normalize_gdelt_item,
)


class TestBronzeWriter(unittest.TestCase):
    def test_normalize_apify_item(self):
        item = {
            "outlet": "CNN",
            "url": "https://cnn.com/article",
            "title": "Test Article",
            "raw_text": "This is test content",
            "published_at": "2026-11-14T10:00:00Z",
        }
        result = normalize_apify_item(item, "test-query", "apify-run-123", "job-123")

        assert result["source_type"] == "apify_scrape"
        assert result["outlet"] == "CNN"
        assert result["title"] == "Test Article"
        assert result["apify_run_id"] == "apify-run-123"
        assert result["article_id"] is not None

    def test_normalize_newsapi_item(self):
        item = {
            "source": {"name": "Fox News", "id": "fox-news"},
            "url": "https://foxnews.com/article",
            "title": "Breaking News",
            "content": "Content here",
            "author": "Author Name",
            "publishedAt": "2026-11-14T09:00:00Z",
        }
        result = normalize_newsapi_item(item, "breaking news", "job-123")

        assert result["source_type"] == "newsapi"
        assert result["outlet"] == "Fox News"
        assert result["title"] == "Breaking News"
        assert "fox-news" in result["raw_metadata"]["source_id"]

    def test_normalize_gdelt_item(self):
        item = {
            "source": "ABC News",
            "url": "https://abcnews.com/article",
            "title": "News Update",
            "content": "Content",
            "published_at": "2026-11-14T08:00:00Z",
        }
        result = normalize_gdelt_item(item, "news", "job-123")

        assert result["source_type"] == "gdelt"
        assert result["outlet"] == "ABC News"


if __name__ == "__main__":
    unittest.main()
