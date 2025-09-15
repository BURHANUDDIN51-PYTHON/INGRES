from fastapi import APIRouter
from ingres_api.models.request_models import ChatQuery, NLResponseRequest
from ingres_api.utils.logger import logger
from ingres_api.detect_intent.detect_intent import DetectIntent
from ingres_api.natural_response.natural_response import NaturalLanguageResponse


# Add the prefix /chatbot
router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# Intialize the AI
INTENT = DetectIntent()
NATURAL_RESPONSE = NaturalLanguageResponse()



# All the routes available
@router.get("/")
async def root():
    """
    Root endpoint returning a welcome message for INGRES.
    """
    return {"message": "Welcome to INGRES"}


@router.post("/intent")
async def detect_intent(chat_query: ChatQuery):
    """
    Basic endpoint to receive a user query and log it.
    Later, connect this to your intent recognition system.
    """
    logger.info("Intent detection endpoint called {}".format(chat_query.uuid or "no-uuid"))
    logger.info(f"Received query: {chat_query.query}")
    # Here you would call your intent recognition logic
    response = await INTENT.detect_intent(chat_query.query)
    logger.info(f"Detected intent: {response}")
    return {"query": chat_query.query, "result": response}



@router.post("/generate-response")
async def generate_natural_response(request: NLResponseRequest):
    """
    Endpoint to generate a natural language response based on intent, query, and raw_data.
    """
    logger.info(f"generate_natural_response called with intent: {request.intent}, query: {request.query}, rawData: {request.rawData}")
    response = NATURAL_RESPONSE.generate_response(
        intent=request.intent,
        query=request.query,
        rawData=request.rawData or {}
    )
    logger.info(f"Generated natural response: {response}")
    return response

