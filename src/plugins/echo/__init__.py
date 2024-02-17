from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot.adapters.discord.api import StringOption
from nonebot.adapters.discord.commands import (
    CommandOption,
    on_slash_command,
)

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="echo",
    description="",
    usage="",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)


matcher = on_slash_command(
    name="echo",
    description="返回输入的字符串",
    options=[
        StringOption(
            name="字符串",
            description="任意字符串",
            required=True,
        ),
    ]
)


@matcher.handle()
async def handel_echo(字符串: CommandOption[str]):
    await matcher.send(字符串)
