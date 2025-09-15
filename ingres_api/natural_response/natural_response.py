import json
import groq
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
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
        """
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")

        # Initialize Groq client
        self.client = groq.Client(api_key=settings.GROQ_API_KEY)
        
        self.INDEX_FILE = r"ingres_api/natural_response/rag_store_nl/faiss_index.bin"
        self.METADATA_FILE = r"ingres_api/natural_response/rag_store_nl/faiss_metadata.json"
        
        # Load FAISS index + metadata
        self.rag_index = faiss.read_index(self.INDEX_FILE)
        with open(self.METADATA_FILE, "r", encoding="utf-8") as f:
            self.rag_metadata = json.load(f)

        # Initialize embedding model
        self.rag_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        self.model = "llama-3.1-8b-instant"
        self.system_prompt = self._build_system_prompt()  # Static system prompt
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
        Builds the static system prompt (no history).
        """
        return f"""
            You are a Natural Language Response Generator for a groundwater chatbot.

Your job:
- Read the **intent**, **user query**, and **raw_data** (if available).
- Use the raw_data fields intelligently to generate a natural language answer.
- Understand the database schema and map query terms to the correct fields.
- Generate a concise, human-readable, factual summary based strictly on raw_data.

Database Schema:
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

Keyword Mapping for Understanding:
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

Your Output Format (strict JSON only):
{{
  "nl_response": "A clear, concise, human-readable summary of the result based on raw_data.",
  "visualization_data": {{
    "type": "bar | line | pie | doughnut",
    "labels": ["Label 1", "Label 2"],
    "data": [numeric_values],
    "x_axis": "X Axis Label",
    "y_axis": "Y Axis Label"
  }}
}}

Few-shot examples for guidance:
{json.dumps(FEW_SHOT_EXAMPLES, indent=2)}
            
Rules:
- If no visualization is needed, set visualization_data to an empty object {{}}.
- Never output extra text or explanation outside JSON.
- If raw_data is empty or intent is unsupported, respond gracefully with an informative message in nl_response.
- Use field names from raw_data to make the answer accurate. If multiple records are present, summarize them meaningfully (aggregating or listing as needed).
- If numeric data is present, format clearly (e.g., "1500 MCM" or "45%").
- If query explicitly asks for a chart/graph, populate visualization_data with suitable chart type and labels.
- Be precise, concise, and factual. Avoid speculation.
"""


    def generate_response(self, intent: str, query: str, rawData: dict = None):
        """
        Generates a natural language response based on intent, query, and raw data.
        No conversation history is kept — each request is independent.
        """
        # Step 1: Retrieve relevant RAG examples
        query_vector = self.rag_embedding_model.encode([query], normalize_embeddings=True)
        query_vector_np = np.array(query_vector, dtype=np.float32)
        distances, indices = self.rag_index.search(query_vector_np, 5)

        retrieved_examples = []
        for idx, score in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            retrieved_examples.append(self.rag_metadata[idx])

        rag_examples_text = json.dumps(retrieved_examples, indent=2, ensure_ascii=False) if retrieved_examples else "[]"
        logger.info(f"Retrieved {len(retrieved_examples)} RAG examples for context.")

        # Step 2: Build final system prompt with RAG examples
        dynamic_system_prompt = f"{self.system_prompt}\n\n**RAG-Retrieved Few-shot Examples:**\n{rag_examples_text}"

        user_message = json.dumps({
            "intent": intent,
            "query": query,
            "rawData": rawData if rawData else {}
        })
        
        query = f"Intent: {intent}\nQuery: {query}\nRaw Data: {json.dumps(rawData) if rawData else '{}'}\nRespond with ONLY JSON as specified."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": dynamic_system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            output = response.choices[0].message.content

            try:
                parsed_output = json.loads(output)
            except json.JSONDecodeError as jde:
                logger.error(f"JSON decode error: {jde}. Output: {output}")
                return {
                    "nl_response": "Faced error in processing your request",
                    "visualization_data": {}
                }

            # Ensure keys always exist
            parsed_output.setdefault("nl_response", "No response generated.")
            parsed_output.setdefault("visualization_data", {})

            return parsed_output

        except Exception as e:
            logger.error(f"Error during response generation: {e}")
            return {
                "nl_response": f"Error generating response: {e}",
                "visualization_data": {}
            }
