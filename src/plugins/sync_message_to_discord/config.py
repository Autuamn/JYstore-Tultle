import json
from typing import List, Dict
from pydantic import BaseModel, Extra, Field


class Config(BaseModel, extra=Extra.ignore):
    enable_guild_id: List[str] = []
    """启用的频道ID"""
    channel_bind: str = ""
    """子频道绑定"""
    try:
        channel_links = json.loads(channel_bind)
    except:
        channel_links = {}