from pydantic import BaseModel

class BotStatusResponse(BaseModel):
    is_running: bool
    symbol: str  
    
class ActionResponse(BaseModel):
    status: str
    message: str


class CandleResponse(BaseModel):
    time: int       # Timestamp (Unix)
    open: float
    high: float
    low: float
    close: float
    tick_volume: int