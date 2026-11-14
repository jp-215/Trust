from google import genai
from google.genai import types
from trust_agent.tools import QUERY_GOLD_TOOL, dispatch
from trust_agent.prompts import SYSTEM_PROMPT


class StorySynthesisAgent:
    def __init__(self, api_key: str, gold_client, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.gold_client = gold_client
        self.model = model
        self.tool = types.Tool(function_declarations=[QUERY_GOLD_TOOL])

    def run(self, story_id: str, max_turns: int = 5) -> str:
        user_prompt = f"{SYSTEM_PROMPT}\n\nSynthesize the source-of-truth record for story_id={story_id}."

        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=user_prompt)],
            )
        ]

        for turn in range(max_turns):
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(tools=[self.tool]),
            )

            candidate = response.candidates[0]
            part = candidate.content.parts[0]

            if part.function_call:
                fc = part.function_call
                result = dispatch(fc.name, dict(fc.args), self.gold_client)

                contents.append(candidate.content)
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=fc.name,
                                response=result,
                            )
                        ],
                    )
                )
                continue

            if part.text:
                return part.text

        return "max turns reached without final answer"
