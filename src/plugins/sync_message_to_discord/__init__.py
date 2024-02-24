import io
from typing import List
import aiohttp
import filetype

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
import nonebot.adapters.discord.api as dc_api
import discord

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
channel_links = config.channel_links


async def check_message(bot: qq_Bot, event: qq_GuildMessageEvent) -> bool:
    logger.debug("check_message")
    return (
        isinstance(event, qq_GuildMessageEvent)
        and event.guild_id in enable_guild_id
        and event.channel_id in channel_links.keys()
    )

matcher = on_message(check_message, block=False)


async def get_member_name(bot: qq_Bot, event: qq_GuildMessageEvent, user_id: str) -> str:
    if event.author.id == user_id:
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
    text: str = ""
    imgList: list[str] = []
    for msg in event.get_message():
        if msg.type == "text":
            # 文本
            text += msg.data['text']
        elif msg.type == "emoji":
            # 表情
            text += f"[{qq_emoji_dict.get(msg.data['id'], "N/A")}]"
        elif msg.type == "image":
            # 图片
            imgList.append(msg.data["url"])
        elif msg.type == "mention_user":
            # @人
            text += (
                f"@[ID:{msg.data["user_id"]}]"
                + await get_member_name(bot, event, msg.data["user_id"])
                + " "
            )
    logger.debug("got")
    return text, imgList


async def send_to_discord(
    webhook_url: str, text: str|None, imgList:list[str]|None , username: str, avatar_url: str|None
):
    logger.debug("send_to_discord")

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(60)) as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        webhook.proxy = "scoks5://127.0.0.1:7890"
        if text:
            await webhook.send(
                text,
                username=username,
                avatar_url=avatar_url
            )
        if imgList:
            for img in imgList:
                img_bytes = await get_image_bytes(img)
                img_io = io.BytesIO(img_bytes)
                kind = filetype.match(img_bytes).extension
                await webhook.send(
                    file=discord.File(img_io, f"{str(img.split('/')[-1])}.{kind}"),
                    username=username,
                    avatar_url=avatar_url
                )

    logger.debug("send")


@matcher.handle()
async def qq_handle(bot: qq_Bot, event: qq_GuildMessageEvent,):
    logger.debug("qq_handle")
    text, imgList = await get_message(bot, event)
    webhook_url = channel_links.get(event.channel_id,{}).get("webhook_url","0")
    username = f"[ID:{event.author.id}] {event.author.username}"
    avatar = event.author.avatar
    await send_to_discord(webhook_url, text, imgList, username, avatar)
