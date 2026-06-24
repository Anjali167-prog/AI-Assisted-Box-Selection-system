import json
import os

from openai import OpenAI


class AIRecommendationExplainer:
    def __init__(self, api_key: str | None = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1",
        )

    def _build_prompt(
        self,
        box_name: str,
        cost: str,
        total_items: int,
        total_weight: float,
        total_volume: float,
        box_volume: float,
        box_max_weight: float,
    ) -> str:
        return (
            f"A customer needs a box for {total_items} product(s) "
            f"with total weight {total_weight}g and total volume {total_volume}cm³. "
            f"The recommended box is '{box_name}' with max weight {box_max_weight}g, "
            f"volume {box_volume}cm³, and cost ${cost}. "
            f"Explain why this box was selected in one sentence. "
            f"Respond in JSON with keys 'recommended_box' and 'reason'."
        )

    def _call_api(self, prompt: str):
        return self.client.chat.completions.create(
            model="grok-4.3",
            messages=[
                {"role": "system", "content": "You are a box selection assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

    def explain(
        self,
        box_name: str,
        cost: str,
        total_items: int,
        total_weight: float,
        total_volume: float,
        box_volume: float,
        box_max_weight: float,
    ) -> dict | None:
        prompt = self._build_prompt(
            box_name=box_name,
            cost=cost,
            total_items=total_items,
            total_weight=total_weight,
            total_volume=total_volume,
            box_volume=box_volume,
            box_max_weight=box_max_weight,
        )
        try:
            response = self._call_api(prompt=prompt)
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception:
            return None
