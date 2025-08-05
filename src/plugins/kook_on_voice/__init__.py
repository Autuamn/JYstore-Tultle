from nonebot import get_bot, require
from nonebot.adapters.kaiheila import Bot
from nonebot.params import Depends
from nonebot_plugin_alconna import Alconna, on_alconna

from .config import plugin_config

require("nonebot_plugin_alconna")


bot_id = str(plugin_config.kook_on_voice_bot_id)
guild_id = str(plugin_config.kook_on_voice_guild_id)


matcher = on_alconna(Alconna("kook"))


async def get_kook_bot():
    return get_bot(bot_id)


@matcher.handle()
async def kook(kook_bot: Bot = Depends(get_kook_bot)):
    message = ""

    voice_channel_list = await kook_bot.channel_list(guild_id=guild_id, type=2)
    for channel in voice_channel_list.channels if voice_channel_list.channels else []:
        if channel_id := channel.id_:
            on_voice_users = await kook_bot.channel_userList(channel_id=channel_id)
            if on_voice_users:
                message += (channel.name or "None") + "\n"
                for index, user in enumerate(on_voice_users):
                    message += (
                        (" ├" if index != (len(on_voice_users) - 1) else " └")
                        + (user.nickname or user.username or "None")
                        + "\n"
                    )
    if not message:
        message = "没有人在语音频道"

    await matcher.finish(message)
