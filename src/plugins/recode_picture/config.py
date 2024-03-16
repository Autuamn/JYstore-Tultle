from typing import List
from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    recode_picture_enable_guild_id: List[str] = []
    recode_picture_enable_chinnel_id: List[str] = []

plugin_config = get_plugin_config(Config)