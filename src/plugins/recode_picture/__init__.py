from nonebot import on_command, on_message
from nonebot.adapters.qq import Bot, GuildMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import Config, plugin_config

__plugin_meta__ = PluginMetadata(
    name="recode_message",
    description="",
    usage="",
    config=Config,
)


enable_guild_id = plugin_config.recode_picture_enable_guild_id
enable_chinnel_id = plugin_config.recode_picture_enable_chinnel_id
pic_map: list[str] = []  # 保存图片url


async def check_pic(bot: Bot, event: GuildMessageEvent) -> bool:
    """检查消息"""
    return (
        event.guild_id in enable_guild_id
        and event.channel_id in enable_chinnel_id
        and any(msg.type == "image" for msg in event.get_message())
    )


notice_pic = on_message(check_pic, block=False)


@notice_pic.handle()
async def handle_pic(bot: Bot, event: GuildMessageEvent):
    """记录图片url"""
    try:
        for msg in event.get_message():
            pic_map.append(msg.data["url"]) if msg.type == "image" else None
    except AttributeError:
        pass


pic_url = on_command("图片直链", aliases={"pic_url"}, rule=to_me())


def save_pic_map(pic_map_needsave):
    with open("record.txt", "w") as file:
        items = (
            f"{item}\n" if i % 8 != 7 else f"{item}\n\n"  # 每8项插入一个空行
            for i, item in enumerate(pic_map_needsave)
        )
        file.writelines(items)


@pic_url.handle()
async def send_pic_url(bot: Bot, args: Message = CommandArg()):
    if pic_map == []:
        await pic_url.finish("目前没有存图")
    else:
        if args.extract_plain_text() == "":  # 没参数发全部
            save_pic_map(pic_map)
            pic_map.clear()
        elif args.extract_plain_text() in ["clear", "清除"]:  # 清除保存的图片url
            pic_map.clear()
            await pic_url.finish("cleared!")
        else:  # 有参数发最后n张
            try:
                n = int(args.extract_plain_text())
                if n > 0:
                    save_pic_map(pic_map[-n:])
                    del pic_map[-n:]
                else:
                    raise ValueError
            except ValueError:
                await pic_url.finish("参数错误")
        await pic_url.send("http://47.107.89.48:25565")
