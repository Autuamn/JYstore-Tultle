import asyncio
import os
import sqlite3

from nonebot import get_driver, logger, on, on_message
from nonebot.adapters.discord import Bot as dc_Bot
from nonebot.adapters.qq import (
    Bot as qq_Bot,
    GuildMessageEvent as qq_GuildMessageEvent,
    MessageDeleteEvent as qq_MessageDeleteEvent,
)
from nonebot.plugin import PluginMetadata

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


enable_guild_id: list[str] = plugin_config.enable_guild_id
channel_links: dict[str, DiscordConfig] = plugin_config.channel_bind
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


matcher = on_message(rule=check_message, priority=100, block=False)
delete = on(rule=check_delete, block=False)


@matcher.handle()
async def qq_handle(
    bot: qq_Bot,
    event: qq_GuildMessageEvent,
):
    c = conn.cursor()
    logger.debug("qq_handle")
    text, img_list = await get_message(bot, event)

    if reference := event.message_reference:
        embeds = await get_embeds(bot, event, reference, c, channel_links)
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
        c.execute(
            "INSERT INTO ID (DCID, QQID) VALUES (?, ?)",
            (send.id, event.id),
        )


@delete.handle()
async def delete_handel(bot: qq_Bot, event: qq_MessageDeleteEvent):
    c = conn.cursor()
    db_selected = c.execute(
        f"SELECT DCID FROM ID WHERE QQID LIKE ('%{event.message.id}%')"
    )
    for msgid in db_selected:
        message_id = int(msgid[0])
    channel_id = int(channel_links[event.message.channel_id].channel_id)
    await delete_discord_message(dc_bot, message_id, channel_id)
    c.execute(f"DELETE FROM ID WHERE DCID={message_id}")


@driver.on_shutdown
async def close_db():
    conn.commit()
    conn.close()
