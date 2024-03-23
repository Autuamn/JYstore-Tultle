from typing import Optional

from nonebot import get_plugin_config
from pydantic import BaseModel


class DiscordConfig(BaseModel):
    channel_id: int
    webhook_id: int
    webhook_token: str


class Config(BaseModel):
    smd_enable_guild_id: list[str] = []
    """启用的频道ID"""
    smd_channel_bind: dict[str, DiscordConfig] = {}
    """子频道绑定"""
    discord_proxy: Optional[str] = None


plugin_config = get_plugin_config(Config)
