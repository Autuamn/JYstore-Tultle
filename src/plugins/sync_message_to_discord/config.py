from typing import List, Dict
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    enable_guild_id: List[str] = []
    """启用的频道ID"""
    channel_bind: Dict[str, int] = {}
    """子频道绑定"""
    discord_webhook_url: str = ""