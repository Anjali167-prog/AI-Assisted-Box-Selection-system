import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from ..services.ai_explainer import AIRecommendationExplainer


class AIRecommendationExplainerTest(SimpleTestCase):
    def test_explain_returns_expected_structure(self):
        mock_content = json.dumps({
            "recommended_box": "Medium",
            "reason": "Medium box fits all items, supports total weight and has lowest cost."
        })
        mock_choice = MagicMock()
        mock_choice.message.content = mock_content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(AIRecommendationExplainer, "_call_api", return_value=mock_response):
            explainer = AIRecommendationExplainer(api_key="sk-test")
            result = explainer.explain(
                box_name="Medium",
                cost="4.00",
                total_items=3,
                total_weight=600.0,
                total_volume=1200.0,
                box_volume=9000.0,
                box_max_weight=3000.0,
            )
            self.assertIn("recommended_box", result)
            self.assertIn("reason", result)
            self.assertEqual(result["recommended_box"], "Medium")
            self.assertEqual(
                result["reason"],
                "Medium box fits all items, supports total weight and has lowest cost."
            )

    def test_explain_prompt_contains_key_context(self):
        recorded_kwargs = {}

        def capture(prompt=""):
            recorded_kwargs["prompt"] = prompt
            mock_choice = MagicMock()
            mock_choice.message.content = json.dumps({
                "recommended_box": "Medium",
                "reason": "It fits."
            })
            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            return mock_response

        with patch.object(AIRecommendationExplainer, "_call_api", side_effect=capture):
            explainer = AIRecommendationExplainer(api_key="sk-test")
            explainer.explain(
                box_name="Medium",
                cost="4.00",
                total_items=3,
                total_weight=600.0,
                total_volume=1200.0,
                box_volume=9000.0,
                box_max_weight=3000.0,
            )

            prompt = recorded_kwargs["prompt"]
            self.assertIn("Medium", prompt)
            self.assertIn("600.0g", prompt)
            self.assertIn("1200.0cm", prompt)
            self.assertIn("3 product(s)", prompt)
            self.assertIn("$4.00", prompt)

    def test_uses_grok_base_url_and_env_var(self):
        with patch("recommendation.services.ai_explainer.OpenAI") as mock_openai:
            AIRecommendationExplainer()
            mock_openai.assert_called_once()
            _, kwargs = mock_openai.call_args
            self.assertEqual(kwargs["base_url"], "https://api.x.ai/v1")
            self.assertIn("api_key", kwargs)
