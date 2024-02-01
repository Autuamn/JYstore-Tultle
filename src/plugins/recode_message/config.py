from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    enable_guild_id: list
    enable_chinnel_id: list
