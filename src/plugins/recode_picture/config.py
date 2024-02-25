from typing import List
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    recode_picture_enable_guild_id: List[str] = []
    recode_picture_enable_chinnel_id: List[str] = []
