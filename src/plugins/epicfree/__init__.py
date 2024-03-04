# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 16:58:31 2024

@author: zxz00
"""

from nonebot import get_driver, on_command, on_message
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.qq import Bot, Message, GuildMessageEvent


__plugin_meta__ = PluginMetadata(
    name="epic",
    description="",
    usage="",
)

epic = on_command("epic", rule=to_me())


from .data_source import get_epic_free  # noqa: E402

@epic.handle()
async def epic_handle(bot: Bot, event: GuildMessageEvent):
    free = await get_epic_free()
    await epic.finish(free)  # type: ignore

    