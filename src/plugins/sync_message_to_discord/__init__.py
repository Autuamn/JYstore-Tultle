import asyncio
import os
import sqlite3

from nonebot import get_driver, logger, on, on_message, on_regex
from nonebot.adapters.discord import Bot as dc_Bot
from nonebot.adapters.qq import (
    Bot as qq_Bot,
    GuildMessageEvent as qq_GuildMessageEvent,
    MessageDeleteEvent as qq_MessageDeleteEvent,
)
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import Config, DiscordConfig, plugin_config
from .init_db import init_db
from .utils import delete_discord_message, get_embeds, get_message, send_to_discord

__plugin_meta__ = PluginMetadata(
    name="sync_message_to_discord",
    description="",
    usage="",
    config=Config,
)

driver = get_driver()


@driver.on_bot_connect
async def get_dc_bot(bot: dc_Bot):
    global dc_bot
    dc_bot = bot


enable_guild_id: list[str] = plugin_config.smd_enable_guild_id
channel_links: dict[str, DiscordConfig] = plugin_config.smd_channel_bind
discord_proxy = plugin_config.discord_proxy


@driver.on_startup
async def connect_db():
    global conn
    dbpath = os.path.abspath("./msgid.db")
    conn = (
        await init_db(dbpath) if not os.path.exists(dbpath) else sqlite3.connect(dbpath)
    )


async def check_message(bot: qq_Bot, event: qq_GuildMessageEvent) -> bool:
    logger.debug("check_message")
    return (
        isinstance(event, qq_GuildMessageEvent)
        and event.guild_id in enable_guild_id
        and event.channel_id in channel_links.keys()
    )


async def check_delete(bot: qq_Bot, event: qq_MessageDeleteEvent) -> bool:
    logger.debug("check_delete")
    return (
        isinstance(event, qq_MessageDeleteEvent)
        and event.message.guild_id in enable_guild_id
        and event.message.channel_id in channel_links.keys()
    )


unmatcher = on_regex(r"/.*", rule=to_me(), priority=1, block=True)
matcher = on_message(rule=check_message, priority=10, block=False)
delete = on(rule=check_delete)


@unmatcher.handle()
async def unmatcher_handle():
    pass


@matcher.handle()
async def qq_handle(
    bot: qq_Bot,
    event: qq_GuildMessageEvent,
):
    logger.debug("qq_handle")
    text, img_list = await get_message(bot, event)

    if reference := event.message_reference:
        embeds = await get_embeds(bot, event, reference, conn, channel_links)
    else:
        embeds = None

    webhook_id = channel_links[event.channel_id].webhook_id
    webhook_token = channel_links[event.channel_id].webhook_token
    username = f"{event.author.username} [ID:{event.author.id}]"
    avatar = event.author.avatar

    try_times = 0
    while True:
        try:
            send = await send_to_discord(
                dc_bot,
                webhook_id,
                webhook_token,
                text,
                img_list,
                embeds,
                username,
                avatar,
            )
            break
        except NameError:
            try_times += 1
            logger.warning(f"retry {try_times}")
            if try_times == 3:
                raise NameError
            await asyncio.sleep(5)

    if send:
        conn.execute(
            "INSERT INTO ID (DCID, QQID) VALUES (?, ?)",
            (send.id, event.id),
        )


@delete.handle()
async def delete_handel(bot: qq_Bot, event: qq_MessageDeleteEvent):
    try_times = 0
    while True:
        try:
            db_selected = conn.execute(
                f"SELECT DCID FROM ID WHERE QQID LIKE ('%{event.message.id}%')"
            )
            msgids = db_selected.fetchone()
            for msgid in msgids:
                channel_id = channel_links[event.message.channel_id].channel_id
                await delete_discord_message(dc_bot, msgid, channel_id)
                conn.execute(f"DELETE FROM ID WHERE DCID={msgid}")
            break
        except [UnboundLocalError | TypeError] as e:
            try_times += 1
            if try_times == 3:
                raise e
            await asyncio.sleep(5)


@driver.on_shutdown
async def close_db():
    conn.commit()
    conn.close()
