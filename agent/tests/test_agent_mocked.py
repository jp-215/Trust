import unittest
from unittest.mock import MagicMock, patch
from trust_agent.agent import StorySynthesisAgent
from trust_agent.tools import dispatch


class MockGoldClient:
    def query_gold_table(self, story_id: str) -> dict:
        return {
            "story_id": story_id,
            "story_title": "Test Story",
            "outlets_covering": ["CNN", "Fox News", "ABC News"],
            "claim_matrix": [
                {
                    "claim_text": "CEO stepped down",
                    "canonical_claim_id": "claim-001",
                    "outlets_reporting": ["CNN", "ABC News"],
                    "outlets_silent": ["Fox News"],
                    "agreement_status": "agree",
                }
            ],
            "contradiction_pairs": [],
        }


class TestStorySynthesisAgent(unittest.TestCase):
    def test_tool_dispatch(self):
        gold_client = MockGoldClient()
        result = dispatch("query_gold_table", {"story_id": "story-123"}, gold_client)

        assert result["success"] is True
        assert result["story_record"]["story_id"] == "story-123"

    def test_tool_dispatch_missing_args(self):
        gold_client = MockGoldClient()
        result = dispatch("query_gold_table", {}, gold_client)

        assert "error" in result

    def test_tool_dispatch_unknown_tool(self):
        gold_client = MockGoldClient()
        with self.assertRaises(ValueError):
            dispatch("unknown_tool", {}, gold_client)

    @patch("trust_agent.agent.genai.Client")
    def test_agent_tool_calling_loop(self, mock_client_class):
        gold_client = MockGoldClient()

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        from google.genai import types

        function_call = types.FunctionCall(
            name="query_gold_table",
            args={"story_id": "story-123"},
        )

        response1 = MagicMock()
        response1.candidates = [MagicMock()]
        response1.candidates[0].content.parts = [MagicMock(function_call=function_call)]

        response2 = MagicMock()
        response2.candidates = [MagicMock()]
        text_part = MagicMock()
        text_part.function_call = None
        text_part.text = "Synthesized truth: The CEO stepped down due to allegations."
        response2.candidates[0].content.parts = [text_part]

        mock_client.models.generate_content.side_effect = [response1, response2]

        agent = StorySynthesisAgent(api_key="test-key", gold_client=gold_client)
        result = agent.run("story-123", max_turns=5)

        assert "Synthesized truth" in result
        assert mock_client.models.generate_content.call_count == 2


class TestToolDispatch(unittest.TestCase):
    def test_query_gold_with_mock_client(self):
        mock_client = MockGoldClient()
        result = dispatch("query_gold_table", {"story_id": "test-story"}, mock_client)

        assert result["success"] is True
        assert "story_record" in result
        assert result["story_record"]["story_title"] == "Test Story"


if __name__ == "__main__":
    unittest.main()
