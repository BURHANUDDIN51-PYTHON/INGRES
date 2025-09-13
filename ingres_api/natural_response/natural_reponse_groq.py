import json
import groq
from ingres_api.config import settings
from ingres_api.utils.logger import logger
from ingres_api.natural_response.few_shot_nl import FEW_SHOT_EXAMPLES

class NaturalLanguageResponse:
    def __init__(self):
        """
        Initializes the NaturalLanguageResponse class.
        - Creates Groq client
        - Loads system prompt
        - Warms up model to avoid latency
        - Initializes history
        """
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")

        # Initialize Groq client
        self.client = groq.Client(api_key=settings.GROQ_API_KEY)
        
        self.history = []
        self.model = "llama-3.3-70b-versatile"  # Or any Groq-supported LLM
        self.system_prompt = self._build_system_prompt()
        self._warm_up_model()

    def _warm_up_model(self):
        """
        Sends a dummy request to warm up the model and reduce cold-start latency.
        """
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": "Hello! This is a warm-up request."}
                ],
                max_tokens=50,
                temperature=0.1
            )
            logger.info('Model Warm up for the natural language response is Completed')
        except Exception as e:
            logger.error(f"Warm-up failed: {e}")

    def _build_system_prompt(self):
        """
        Builds the system prompt to ensure consistent response format, including few-shot examples.
        """
        
        prompt = (
            "You are a Natural Language Response Generator for a groundwater chatbot. "
            "Your job is to read the intent, user query, and raw data (if available) "
            "and respond with a clear natural language summary. "
            "Output strictly in JSON format:\n"
            "{\n"
            "  \"nl_response\": \"A clear, human-readable summary of the answer.\",\n"
            "  \"visualization_data\": {\n"
            "    \"type\": \"bar | line | pie | doughnut\",\n"
            "    \"labels\": [\"Label 1\", \"Label 2\"],\n"
            "    \"data\": [numeric_values],\n"
            "    \"x_axis\": \"X Axis Label\",\n"
            "    \"y_axis\": \"Y Axis Label\"\n"
            "  }\n"
            "}\n"
            "If no visualization is needed, set visualization_data as an empty object {}. "
            "Never output extra text or explanation outside JSON. "
            "\nFew-shot examples for guidance:\n" + json.dumps(FEW_SHOT_EXAMPLES, indent=2)
        )
        return prompt

    def generate_response(self, intent: str, query: str, rawData: dict = None):
        """
        Generates a natural language response based on intent, query, and raw data.
        Maintains conversation history.
        """
        user_message = {
            "intent": intent,
            "query": query,
            "rawData": rawData if rawData else {}
        }

        self.history.append(user_message)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *[
                        {"role": "user", "content": json.dumps(h)} for h in self.history
                    ]
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}  # Strict JSON output
            )

            output = response.choices[0].message.content
            
            try:
                parsed_output = json.loads(output)
            except json.JSONDecodeError as jde:
                # Log the error and return a clear message
                logger.info(f"JSON decode error: {jde}. Output: {output}")
                return {
                    "nl_response": f"Faced error in processing your request",
                    "visualization_data": {}
                }

            # Ensure required keys exist even if missing from LLM
            if "nl_response" not in parsed_output:
                parsed_output["nl_response"] = "No response generated."
            if "visualization_data" not in parsed_output:
                parsed_output["visualization_data"] = {}


            return parsed_output

        except Exception as e:
            return {
                "nl_response": f"Error generating response: {e}",
                "visualization_data": {}
            }

