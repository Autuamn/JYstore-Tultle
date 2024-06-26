from typing import Optional

from nonebot import get_plugin_config
from pydantic import BaseModel


class Link(BaseModel):
    qq_guild_id: str
    dc_guild_id: int
    qq_channel_id: str
    dc_channel_id: int
    webhook_id: int
    webhook_token: str


class Config(BaseModel):
    smd_channel_links: list[Link] = []
    """子频道绑定"""
    smd_unmatch_beginning: list[str] = ["/"]
    discord_proxy: Optional[str] = None


plugin_config = get_plugin_config(Config)
