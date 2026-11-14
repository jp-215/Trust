from typing import Any
from apify_client import ApifyClient


class ApifySource:
    def __init__(self, api_token: str, actor_id: str):
        self.client = ApifyClient(api_token)
        self.actor_id = actor_id

    def run_and_fetch(self, run_input: dict) -> list[dict]:
        run = self.client.actor(self.actor_id).call(run_input=run_input)
        dataset_id = run["defaultDatasetId"]
        return list(self.client.dataset(dataset_id).iterate_items())
