from typing import List, Any
from pydantic import BaseModel


class AccountRecord(BaseModel):
    id: str
    created_at: str
    screen_name: str


class PostRecord(BaseModel):
    id: str
    created_at: str
    author_id: str
    is_repost: bool
    text: str
    hashtags: str


class PuppetPosterRequest(BaseModel):
    hashtag: Any
    posts_data: List[PostRecord]
    accounts_data: List[AccountRecord]

class PuppetPosterResponse(BaseModel):
    count: int