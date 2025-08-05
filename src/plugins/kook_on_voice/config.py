from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    kook_on_voice_bot_id: int
    kook_on_voice_guild_id: int


plugin_config = get_plugin_config(Config)
