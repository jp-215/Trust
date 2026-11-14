import argparse
import os
from dotenv import load_dotenv
from trust_agent.agent import StorySynthesisAgent
from trust_agent.gold_client import GoldClient


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Synthesize story truth from aggregated news coverage")
    parser.add_argument("--story-id", required=True, help="The story ID to synthesize")
    args = parser.parse_args()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not set in environment")

    db_host = os.environ.get("DATABRICKS_SERVER_HOSTNAME")
    db_path = os.environ.get("DATABRICKS_HTTP_PATH")
    db_token = os.environ.get("DATABRICKS_TOKEN")

    if not all([db_host, db_path, db_token]):
        raise ValueError("Missing Databricks credentials in environment")

    gold_client = GoldClient(
        server_hostname=db_host,
        http_path=db_path,
        access_token=db_token,
    )

    agent = StorySynthesisAgent(api_key=gemini_key, gold_client=gold_client)
    synthesis = agent.run(args.story_id)

    print("\n" + "=" * 80)
    print(f"SYNTHESIZED TRUTH FOR STORY: {args.story_id}")
    print("=" * 80)
    print(synthesis)
    print("=" * 80)

    # TODO: Write synthesis back to gold.story_synthesis table
    # gold_client.write_synthesis(args.story_id, synthesis, metadata={"agent": "gemini", "model": "gemini-2.0-flash"})


if __name__ == "__main__":
    main()
