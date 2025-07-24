from collections import defaultdict, deque

from nonebot import on_command, on_message
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="cvcvcv",
    description="复读插件",
    usage="/cvopen 开启复读模式\n/cvclose 关闭复读模式",
)

history = defaultdict(lambda: deque(maxlen=10))
MAX_HISTORY = 10
repeat_mode = True


def group_message_rule(event: GroupMessageEvent) -> bool:
    return isinstance(event, GroupMessageEvent)


message_handler = on_message(rule=group_message_rule, priority=10, block=False)


@message_handler.handle()
async def handle_message(bot: Bot, event: GroupMessageEvent):
    global repeat_mode
    if not repeat_mode:
        return

    group_id = event.group_id
    try:
        msg = str(event.get_message()).strip()
    except Exception:
        await bot.send(event, "无法处理消息内容")
        return

    last_user_msg = None
    for sender, content in reversed(history[group_id]):
        if sender == "user":
            last_user_msg = content
            break

    if last_user_msg == msg:
        bot_sent = any(
            sender == "bot" and content == msg for sender, content in history[group_id]
        )
        if not bot_sent:
            await bot.send(event, msg)
            history[group_id].append(("bot", msg))
    history[group_id].append(("user", msg))


cvopen = on_command("cvopen", priority=5, block=True)


@cvopen.handle()
async def handle_cvopen(bot: Bot, event: Event):
    global repeat_mode
    repeat_mode = True
    await cvopen.finish("复读模式已开启")


cvclose = on_command("cvclose", priority=5, block=True)


@cvclose.handle()
async def handle_cvclose(bot: Bot, event: Event):
    global repeat_mode
    repeat_mode = False
    await cvclose.finish("复读模式已关闭")
