import json
import logging
import os

from google import genai

logger = logging.getLogger(__name__)


class AIRecommendationExplainer:
    def __init__(self, api_key: str | None = None):
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            logger.warning("No GEMINI_API_KEY provided — AI explanations disabled")
        self.client = genai.Client(api_key=resolved_key)

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
        return self.client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                system_instruction="You are a box selection assistant.",
            ),
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
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            logger.exception("Gemini returned non-JSON response")
            return None
        except Exception:
            logger.exception("Gemini API call failed")
            return None
