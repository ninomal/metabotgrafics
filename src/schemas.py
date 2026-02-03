from pydantic import BaseModel

class BotStatusResponse(BaseModel):
    is_running: bool
    symbol: str  
    
class ActionResponse(BaseModel):
    status: str
    message: str