from databricks import sql


class GoldClient:
    def __init__(self, server_hostname: str, http_path: str, access_token: str):
        self._conn_kwargs = {
            "server_hostname": server_hostname,
            "http_path": http_path,
            "access_token": access_token,
        }

    def query_gold_table(self, story_id: str) -> dict | None:
        query = "SELECT * FROM gold.story_records WHERE story_id = %(story_id)s"
        try:
            with sql.connect(**self._conn_kwargs) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, {"story_id": story_id})
                    row = cur.fetchone()
                    if row:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, row))
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to query gold table: {e}")

    def write_synthesis(self, story_id: str, synthesized_truth: str, metadata: dict | None = None) -> None:
        from datetime import datetime

        metadata = metadata or {}
        query = """
        INSERT INTO gold.story_synthesis (story_id, synthesized_truth, synthesis_metadata, synthesized_at)
        VALUES (%(story_id)s, %(synthesized_truth)s, %(metadata)s, %(synthesized_at)s)
        """
        try:
            with sql.connect(**self._conn_kwargs) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        query,
                        {
                            "story_id": story_id,
                            "synthesized_truth": synthesized_truth,
                            "metadata": metadata,
                            "synthesized_at": datetime.utcnow().isoformat(),
                        },
                    )
        except Exception as e:
            raise RuntimeError(f"Failed to write synthesis: {e}")
