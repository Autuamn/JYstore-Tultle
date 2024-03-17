from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
)


help = on_command("help", rule=to_me())


@help.handle()
async def help_handle():
    await help.finish("I can't help you.")
