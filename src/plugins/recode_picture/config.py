from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    recode_picture_recode_file_url: str = ""
    recode_picture_enable_guild_id: list[str] = []
    recode_picture_enable_chinnel_id: list[str] = []


plugin_config = get_plugin_config(Config)
