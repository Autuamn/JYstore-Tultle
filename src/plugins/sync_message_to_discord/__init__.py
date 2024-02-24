import aiohttp
import filetype
from typing import List, Dict, Union

from nonebot import logger, get_driver, get_bot, on_message
from nonebot.rule import is_type, Rule
from nonebot.plugin import PluginMetadata
from nonebot.adapters.qq import (
    Bot as qq_Bot,
    Message as qq_Message,
    MessageSegment as qq_MessageSegment,
    GuildMessageEvent as qq_GuildMessageEvent,
    Event as qq_Event
)
from nonebot.adapters.discord import (
    Bot as dc_Bot,
    Message as dc_Message,
    MessageSegment as dc_MessageSegment,
    MessageEvent as dc_MessageEvent,
    GuildMessageCreateEvent as dc_GuildMessageCreateEvent,
    Event as dc_Event,
)

from .qq_emoji_dict import qq_emoji_dict
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

enable_guild_id: List[str] = config.enable_guild_id
channel_bind: Dict[str, int] = config.channel_bind
discord_webhook_url: str = config.discord_webhook_url

async def check_message(bot: qq_Bot, event: qq_GuildMessageEvent) -> bool:
    logger.debug("check_message")
    return (
        isinstance(event, qq_GuildMessageEvent)
        and event.guild_id in enable_guild_id
        and event.channel_id in channel_bind.keys()
    )

matcher = on_message(check_message, block=False)


async def get_member_name(bot: qq_Bot, event: qq_GuildMessageEvent, user_id: str) -> str:
    if event.author.username == user_id:
        return event.author.username if event.author.username else ""
    else:
        member =  await bot.get_member(guild_id=event.guild_id, user_id=user_id)
        return member.nick if member.nick else ""

async def get_image_bytes(url) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_bytes = await response.read()
    return image_bytes

async def get_message(bot: qq_Bot, event: qq_GuildMessageEvent):
    logger.debug("get_message")
    msgList: dc_Message = dc_MessageSegment.text(
            f"[ID:{event.author.id}]"
            + await get_member_name(bot, event, event.author.id)
        ) + "\n"
    for msg in event.get_message():
        if msg.type == "text":
            # 文本
            msgData = dc_MessageSegment.text(msg.data['text'])
        elif msg.type == "emoji":
            # 表情
            msgData = dc_MessageSegment.text(f"[{qq_emoji_dict.get(msg.data['id'], "N/A")}]")
        elif msg.type == "image":
            # 图片
            content = await get_image_bytes(msg.data["url"])
            kind = filetype.match(content).extension
            msgData = dc_MessageSegment.attachment(
                f"{str(msg.data["url"].split('/')[-1])}.{kind}",
                content = content
                )
        elif msg.type == "mention_user":
            # @人
            msgData = dc_MessageSegment.text(
                await get_member_name(bot, event, msg.data["user_id"])
            )
        elif msg.type == "mention_everyone":
            # @全体
            msgData = dc_MessageSegment.mention_everyone()
        msgList += msgData
    logger.debug("got")
    return msgList


async def send_to_discord(
    channel_id: int, message: Union[str, dc_Message, dc_MessageSegment]
):
    logger.debug("send_to_discord")
    if bot := get_bot("1208326638673330196"):
        await bot.send_to(channel_id=channel_id, message=message)
        logger.debug("send")


@matcher.handle()
async def qq_handle(bot: qq_Bot, event: qq_GuildMessageEvent,):
    logger.debug("qq_handle")
    message = await get_message(bot, event)
    channel_id = channel_bind.get(event.channel_id,0)
    await send_to_discord(channel_id, message)
