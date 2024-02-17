from typing import Union

from nonebot import logger, get_driver, get_bot, on_message
from nonebot.rule import is_type
from nonebot.plugin import PluginMetadata
from nonebot.adapters.qq import (
    Bot as qq_Bot,
    Message as qq_Message,
    MessageSegment as qq_MessageSegment,
    GuildMessageEvent as qq_GuildMessageEvent,
    Event as qq_Event
)
from nonebot.adapters.discord import (
    Bot as ds_Bot,
    Message as ds_Message,
    MessageSegment as ds_MessageSegment,
    MessageEvent as ds_MessageEvent,
    GuildMessageCreateEvent as ds_GuildMessageCreateEvent,
    Event as ds_Event,
)

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="sync_message_to_discord",
    description="",
    usage="",
    config=Config,
)

driver = get_driver()
global_config = get_driver().config
config = Config.parse_obj(global_config)

enable_guild_id = config.enable_guild_id
channel_bind = config.channel_bind

matcher = on_message(rule=is_type(qq_GuildMessageEvent))


async def send_to_discord(message):
    if bot := get_bot("1208326638673330196"):
        await bot.send_to(channel_id=1208348399263285308, message=message)

@matcher.handle()
async def qq_handle(bot: Union[qq_Bot, ds_Bot], event: qq_GuildMessageEvent,):
    for msg in event.get_message():
        message = ds_MessageSegment.text(msg.data["text"])
    await send_to_discord(message)
