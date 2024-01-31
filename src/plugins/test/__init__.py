from pathlib import Path

from nonebot import on_command
from nonebot.adapters.qq import (
    Bot as qq_Bot,
    Message as qq_Message,
    MessageSegment as qq_MessageSegment,
    Event as qq_Event
)
from nonebot.adapters.kaiheila import(
    Bot as kook_Bot,
    Message as kook_Message,
    MessageSegment as kook_MessageSegment,
    Event as kook_Event
)
from nonebot.adapters import Adapter
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="test",
    description="",
    usage="",
)
test = on_command("test")

@test.handle()
async def test_qq(bot: qq_Bot, event: qq_Event):
    await bot.send(event, qq_MessageSegment.text("QQ"))

@test.handle()
async def test_kook(bot: kook_Bot, event: kook_Event):
    await bot.send(event, kook_MessageSegment.text("Kook"))