from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    enable_guild_id: list = []
    """启用的频道ID"""
    channel_bind: dict = {}
    """子频道绑定"""