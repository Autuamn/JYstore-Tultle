from typing import List, Dict, Optional
from nonebot import get_plugin_config
from pydantic import BaseModel

class DiscordConfig(BaseModel):
    channel_id: int
    webhook_id: int
    webhook_token: str

class Config(BaseModel):
    enable_guild_id: List[str] = []
    """启用的频道ID"""
    channel_bind: Dict[str, DiscordConfig] = {}
    """子频道绑定"""
    discord_proxy: Optional[str] = None

plugin_config = get_plugin_config(Config)
