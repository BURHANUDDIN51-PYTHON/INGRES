import json
import re
import groq
from ingres_api.config import settings
from ingres_api.utils.logger import logger
from ingres_api.detect_intent.fewshots import FEW_SHOT_EXAMPLE

class DetectIntent:
    def __init__(self):
        """
        Initializes the Groq model with a system prompt.
        """
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")

        # Initialize Groq client
        self.client = groq.Client(api_key=settings.GROQ_API_KEY)

        # System prompt (same as Gemini)
        self.system_prompt = f"""  
You are an intent detection and entity extraction system for a groundwater data chatbot. Your task is to classify a user query into one of the following intents and extract relevant entities.

**Available Intents:**
- `list_units_by_category`: Find units (districts, blocks) by category.
- `list_units_by_condition`: Find units by a specific condition.
- `compare_states_extraction`: Compare extraction data between states.
- `compare_categories_in_state`: Compare categories within a state.
- `get_historical_data`: Get historical data for a unit.
- `get_state_metric`: Get a specific metric for a state.
- `find_units_by_metric_value`: Find units based on a metric value.
- `get_data_for_unit`: Get a single data point for a unit.
- `compare_data`: Compare data points.
- `definition`: Provide a definition.
- `general_greeting`: User is saying hello.
- `general_help`: User needs general help.
- `thank_you`: User is expressing gratitude.
- `unsupported`: The query is out of scope.

**Database Schema:**
- `AssessmentUnit(state, district, block_name, unit_code)`
- `GroundwaterData(year, annual_recharge, annual_extractable_resources, annual_extraction, stage_of_extraction, category)`

**Few-shot Examples:**
{FEW_SHOT_EXAMPLE}

**Rules:**
- Respond with **valid JSON only**.
- Never include natural language explanations.
- If an entity is not found, do not include its key in the `entities` object.
- Include a confidence score between 0 and 1.       
"""

        self.model = "llama-3.1-8b-instant"  # Groq model (fast + good for structured output)

        self._warmup_model()

    def _warmup_model(self):
        """
        Warms up the Groq model by sending a dummy request with the system prompt.
        This primes the model and reduces latency for the first real request.
        """
        try:
            dummy_query = "Warm up the model. Respond with an empty JSON object."
            _ = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Query: {dummy_query}\nRespond with ONLY JSON as specified."}
                ],
                max_tokens=50,
                temperature=0
            )
            logger.info("Groq model warmup completed.")
        except Exception as e:
            logger.warning(f"Model warmup failed: {e}")

    def _clean_response(self, text: str) -> str:
        """
        Removes Markdown code fences (```json ... ```) if present,
        and returns only the raw JSON string.
        """
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
        return cleaned.strip()

    async def detect_intent(self, query: str) -> dict:
        """
        Analyze the user query, detect intent, extract entities,
        and return a JSON-like Python dict.
        """
        try:
            logger.info(f"Analyzing query: {query}")

            prompt = f"Query: {query}\nRespond with ONLY JSON as specified."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0
            )

            if not response or not response.choices:
                logger.error("Empty response from Groq model.")
                return {
                    "intent": "unknown",
                    "entities": {},
                    "confidence": 0.0
                }

            text_output = response.choices[0].message.content
            
            logger.info(f"Raw Groq response: {text_output}")
            
            cleaned_text = self._clean_response(text_output)
            parsed = json.loads(cleaned_text)
            return parsed

        except json.JSONDecodeError:
            logger.error(f"Failed to parse Groq response as JSON: {text_output if 'text_output' in locals() else ''}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0
            }
        except Exception as e:
            logger.error(f"Error during intent detection: {e}")
            return {
                "intent": "error",
                "entities": {},
                "confidence": 0.0
            }
