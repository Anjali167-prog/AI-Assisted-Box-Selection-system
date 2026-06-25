import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from google import genai

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Test the Gemini API key and generate a sample explanation"

    def handle(self, *args, **options):
        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            self.stderr.write(self.style.ERROR(
                "GEMINI_API_KEY is not set in settings or .env file.\n"
                "Check that box_selector/.env contains: GEMINI_API_KEY=your-key"
            ))
            return

        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "(too short)"
        self.stdout.write(f"GEMINI_API_KEY found: {masked}")

        client = genai.Client(api_key=api_key)

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents="Say hello in one word.",
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            self.stdout.write(self.style.SUCCESS(f"Gemini API responded: {response.text}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gemini API call failed: {e}"))
            return

        prompt = (
            "A customer needs a box for 3 product(s) with total weight 600g "
            "and total volume 1200cm³. The recommended box is 'Medium Box' "
            "with max weight 3000g, volume 9000cm³, and cost $4.00. "
            "Explain why this box was selected in one sentence. "
            "Respond in JSON with keys 'recommended_box' and 'reason'."
        )
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    system_instruction="You are a box selection assistant.",
                ),
            )
            result = json.loads(response.text)
            self.stdout.write(self.style.SUCCESS(f"Explanation: {json.dumps(result, indent=2)}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Explanation generation failed: {e}"))
