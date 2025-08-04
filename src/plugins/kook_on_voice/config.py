from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    kook_bot_id: int
    guild_id: int


plugin_config = get_plugin_config(Config)
