import asyncio
from sqlite3 import Cursor
from typing import Optional

import aiohttp
import filetype
from nonebot import logger
from nonebot.adapters.discord import Bot as dc_Bot
from nonebot.adapters.discord.api import Embed, EmbedAuthor, File, MessageGet
from nonebot.adapters.qq import Bot as qq_Bot, GuildMessageEvent as qq_GuildMessageEvent
from nonebot.adapters.qq.models import MessageReference

from .config import DiscordConfig
from .qq_emoji_dict import qq_emoji_dict


async def get_member_name(
    bot: qq_Bot, event: qq_GuildMessageEvent, user_id: str
) -> str:
    if event.author.id == user_id:
        return event.author.username or ""
    else:
        member = await bot.get_member(guild_id=event.guild_id, user_id=user_id)
        return member.nick or ""


async def get_image_file(url: str) -> File:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img_bytes = await response.read()
            match = filetype.match(img_bytes)
            kind = match.extension if match else ""
    return File(content=img_bytes, filename=f"{str(url.split('/')[-1])}.{kind}")


async def get_message(
    bot: qq_Bot, event: qq_GuildMessageEvent
) -> tuple[str, list[str]]:
    logger.debug("get_message")
    text = ""
    img_list: list[str] = []
    for msg in event.get_message():
        if msg.type == "text":
            # 文本
            text += str(msg.data["text"])
        elif msg.type == "emoji":
            # 表情
            text += f"[{qq_emoji_dict.get(msg.data['id'], 'N/A')}]"
        elif msg.type == "mention_user":
            # @人
            text += (
                f"@[ID:{msg.data['user_id']}]"
                + await get_member_name(bot, event, msg.data["user_id"])
                + " "
            )
        elif msg.type == "image":
            # 图片
            img_list.append(msg.data["url"])
    logger.debug("got")
    return text, img_list


async def get_embeds(
    bot: qq_Bot,
    event: qq_GuildMessageEvent,
    reference: MessageReference,
    c: Cursor,
    channel_links: dict[str, DiscordConfig],
) -> list[Embed]:
    reference_message = await bot.get_message_of_id(
        channel_id=event.channel_id, message_id=reference.message_id
    )
    reference_member = await bot.get_member(
        guild_id=reference_message.guild_id, user_id=reference_message.author.id
    )

    db_selected = c.execute(
        f"SELECT DCID FROM ID WHERE QQID LIKE ('%{reference.message_id}%')"
    )
    for selected in db_selected:
        reference_id = selected[0]

    channel_id = channel_links[event.channel_id].channel_id

    author = EmbedAuthor(
        name=f"{reference_message.author.username or ''} [ID:{reference_message.author.id}]",
        icon_url=(reference_member.user.avatar if reference_member.user else "") or "",
    )
    description = (
        f"{reference_message.content}\n\n"
        + (
            f"<t:{int(reference_message.timestamp.timestamp())}:R>"
            if reference_message.timestamp
            else ""
        )
        + (
            f"[[ ↑ ]](https://discord.com/channels/1171294052839333910/{channel_id}/{reference_id})"
            if reference_id
            else "[ ? ]"
        )
    )

    embeds = [
        Embed(
            author=author,
            description=description,
        )
    ]
    return embeds


async def send_to_discord(
    bot: dc_Bot,
    webhook_id: int,
    token: str,
    text: Optional[str],
    img_list: Optional[list[str]],
    embed: Optional[list[Embed]],
    username: Optional[str],
    avatar_url: Optional[str],
) -> MessageGet:
    logger.debug("send_to_discord")

    if img_list:
        get_img_tasks = [get_image_file(img) for img in img_list]
        files = await asyncio.gather(*get_img_tasks)
    else:
        files = None

    # try_times = 0

    # while try_times < 3:
    #    try:
    send = await bot.execute_webhook(
        webhook_id=webhook_id,
        token=token,
        content=text or "",
        files=files,
        embeds=embed,
        username=username,
        avatar_url=avatar_url,
        wait=True,
    )
    #        break
    """    except:
            await asyncio.sleep(5)
            try_times += 1
            if try_times == 3:
                send = await bot.execute_webhook(
                    webhook_id=webhook_id,
                    token=token,
                    content=text or "",
                    files=files,
                    embeds=embed,
                    username=username,
                    avatar_url=avatar_url,
                    wait=True,
                )"""

    logger.debug("send")
    return send


async def delete_discord_message(bot: dc_Bot, message_id: int, channel_id: int):
    await bot.delete_message(message_id=message_id, channel_id=channel_id)
