from nonebot import on_command
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
)


help = on_command("help", rule=to_me())


@help.handle()
async def help_handle():
    await help.finish(f"I can't help you.")