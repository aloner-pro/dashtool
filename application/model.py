from pydantic import BaseModel
from typing import Optional, List

class UploadResponse(BaseModel):
    detail: str
    
class GameData(BaseModel):
    AppID: int
    Name: str
    Release_date: str
    Required_age: int
    Price: float
    DLC_count: int
    About_the_game: str
    Supported_languages: List[str]
    Windows: int
    Mac: int
    Linux: int
    Positive: int
    Negative: int
    Score_rank: Optional[int]
    Developers: str
    Publishers: str
    Categories: List[str]
    Genres: List[str]
    Tags: List[str]

class SearchResponse(BaseModel):
    count: int
    results: List[GameData]

class ErrorResponse(BaseModel):
    detail: str