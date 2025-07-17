from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import Alconna, Subcommand, on_alconna

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
)


help = on_alconna(
    Alconna(
        "help",
        Subcommand("ppapi"),
        Subcommand("status"),
        Subcommand(
            "喜加一",
            alias=[
                "epic喜+1",
                "epic喜+一",
                "epic喜＋1",
                "epic喜＋一",
                "epic喜加1",
                "epic喜加一",
                "喜+1",
                "喜+一",
                "喜＋1",
                "喜＋一",
                "喜加1",
            ],
        ),
        Subcommand("zssm"),
    ),
    block=True,
    use_cmd_start=True,
)


@help.assign("$main")
async def _():
    await help.finish(
        "/help：显示帮助\n"
        + "/ppapi：翼龙面板api\n"
        + "/status：服务器状态[*]\n"
        + "/cvopen开启复读模式\n"
        + "/cvclose关闭复读模式\n"
        + "喜加一：epic喜加一快报\n"
        + "zssm：这是什么？问一下\n"
        + "（[*]：需要@机器人）"
    )


@help.assign("ppapi")
async def _():
    await help.finish(
        "/ppapi (check|检查)：检查api状态\n"
        + "/ppapi (command|命令) [<参数>]：执行命令\n"
        + "/ppapi (log|日志) [<参数>]：输出最后10或指定行日志\n"
        + "/ppapi (开关|power) [开|关|重启|强制停止|on|off|restart|kill]\n"
        + "/ppapi (资源|resources) [cpu|状态|内存|硬盘|运行时间|state|memory|disk|uptime]"
    )


@help.assign("status")
async def _():
    await help.finish("/status：查看服务器状态（需要@机器人）")


@help.assign("喜加一")
async def _():
    await help.finish(
        "喜加一：查找限免游戏\n"
        + "喜加一[群聊|私聊]订阅：订阅游戏资讯\n"
        + "喜加一[群聊|私聊]订阅删除：取消订阅游戏资讯"
    )


@help.assign("zssm")
async def _():
    await help.finish("zssm：ai 解释，对着你想要了解的东西，回复「zssm」吧！")
