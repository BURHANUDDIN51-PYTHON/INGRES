import json
import re
import groq
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
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
        
        # ====== CONFIG FOR RAG ======
        self.INDEX_FILE = r"ingres_api/detect_intent/rag_store/faiss_index.bin"
        self.METADATA_FILE = r"ingres_api/detect_intent/rag_store/faiss_metadata.json"
        
        self.rag_index = faiss.read_index(self.INDEX_FILE)
        with open(self.METADATA_FILE, "r", encoding="utf-8") as f:
            self.rag_metadata = json.load(f)

        # ====== INIT EMBEDDING MODEL ======
        self.rag_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        
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
GroundwaterRechargeData(
    id,
    state_name,
    district_name,
    monsoon_recharge_from_rainfall,
    monsoon_recharge_from_other_sources,
    non_monsoon_recharge_from_rainfall,
    non_monsoon_recharge_from_other_sources,
    total_annual_groundwater_recharge,
    total_natural_discharge,
    annual_extractable_groundwater_resource,
    irrigation_annual_extraction,
    industrial_annual_extraction,
    domestic_annual_extraction,
    total_annual_extraction,
    annual_gw_allocation_for_domestic_use,
    net_gw_availability_for_future,
    stage_of_gw_extraction,
    ground_water_depth
)
Keyword Mapping (for intent/entity extraction):
- "groundwater data", "total recharge" → total_annual_groundwater_recharge
- "monsoon rainfall recharge" → monsoon_recharge_from_rainfall
- "monsoon recharge other sources" → monsoon_recharge_from_other_sources
- "non-monsoon rainfall recharge" → non_monsoon_recharge_from_rainfall
- "non-monsoon recharge other sources" → non_monsoon_recharge_from_other_sources
- "natural discharge" → total_natural_discharge
- "annual extractable resources" → annual_extractable_groundwater_resource
- "irrigation extraction" → irrigation_annual_extraction
- "industrial extraction" → industrial_annual_extraction
- "domestic extraction" → domestic_annual_extraction
- "total extraction" → total_annual_extraction
- "allocation for domestic use" → annual_gw_allocation_for_domestic_use
- "net availability" → net_gw_availability_for_future
- "stage of extraction" → stage_of_gw_extraction
- "groundwater depth", "water level" → ground_water_depth

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
            
            # ====== Step 1: Retrieve relevant RAG examples ======
            query_vector = self.rag_embedding_model.encode([query], normalize_embeddings=True)
            query_vector_np = np.array(query_vector, dtype=np.float32)
            distances, indices = self.rag_index.search(query_vector_np, 5) # top_k=5

            retrieved_examples = []
            for idx, score in zip(indices[0], distances[0]):
                if idx == -1:
                    continue
                entry = self.rag_metadata[idx]
                retrieved_examples.append(entry)

            # Convert retrieved examples to string for injection
            if retrieved_examples:
                rag_examples_text = json.dumps(retrieved_examples, indent=2, ensure_ascii=False)
            else:
                rag_examples_text = "[]"
                
            logger.info(f"Retrieved {len(retrieved_examples)} RAG examples for context.")

            prompt = f"Query: {query}\nRespond with ONLY JSON as specified."
            dynamic_system_prompt = f"{self.system_prompt}\n\n**RAG-Retrieved Few-shot Examples:**\n{rag_examples_text}"
        
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": dynamic_system_prompt},
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
