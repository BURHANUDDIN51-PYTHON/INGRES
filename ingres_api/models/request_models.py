from pydantic import BaseModel

class ChatQuery(BaseModel):
    query: str
    uuid: str | None = None
    
class NLResponseRequest(BaseModel):
    intent: str
    query: str
    rawData: dict | None = None
    uuid: str