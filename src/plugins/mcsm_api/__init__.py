from asyncio import gather
from collections.abc import Mapping
import json
from typing import Any

from nonebot import require
from nonebot.adapters import Bot, Event
from nonebot.internal.driver import Request
from nonebot.internal.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_State

require("nonebot_plugin_alconna")
from arclet.alconna import Alconna, Args, Arparma, MultiVar, Subcommand
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.params import _alconna_result, assign

from .config import CommandAlias, plugin_config

URL: str = plugin_config.mcsm_url + "/api"
API_KET: str = plugin_config.mcsm_api_key
DAEMON_ID: str = plugin_config.mcsm_daemon_id
INSTANCE_ID: str = plugin_config.mcsm_instance_id
AUTH: Mapping[str, str] = {
    "apikey": API_KET,
    "daemonId": DAEMON_ID,
    "uuid": INSTANCE_ID,
}
HEADERS: dict[str, str] = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
}

command_alias: CommandAlias = plugin_config.mcsm_command_alias


async def request(
    bot: Bot,
    method: str,
    url: str,
    params: Mapping[str, str | int] = {},
) -> tuple[int, dict[str, Any] | str]:
    resp = await bot.adapter.request(
        Request(method, url, params={**params, **AUTH}, headers=HEADERS)
    )
    return (
        resp.status_code,
        json.loads(resp.content)["data"] if resp.content is not None else "",
    )


def Check(paths: list[str]) -> bool:
    async def _arparma_check(
        bot: Bot, state: T_State, event: Event, matcher: Matcher
    ) -> bool:
        arp = _alconna_result(state).result
        fns = [assign(path)(event, bot, state, arp) for path in paths]
        if not (ans := any(await gather(*fns))):
            matcher.skip()
        return ans

    return Depends(_arparma_check, use_cache=False)


matcher = on_alconna(
    Alconna(
        "mcsm",
        Subcommand("instance", alias=command_alias.instance),
        Subcommand("open", alias=command_alias.open),
        Subcommand("stop", alias=command_alias.stop),
        Subcommand("restart", alias=command_alias.restart),
        Subcommand("kill", alias=command_alias.kill),
        Subcommand(
            "command", Args["command", MultiVar(str)], alias=command_alias.command
        ),
        Subcommand("outputlog", Args["size", int], alias=command_alias.outputlog),
    )
)


@matcher.handle([Check(["$main", "instance"])])
async def instance(bot: Bot):
    status_code, data = await request(bot, "get", f"{URL}/instance")
    if status_code != 200 or isinstance(data, str):
        await matcher.finish(str(status_code) + " " + str(data))
    else:
        status = data["status"]
        await matcher.finish(
            "忙碌" if status == -1 else ["停止", "停止中", "启动中", "运行中"][status]
        )


@matcher.handle([Check(["open", "stop", "restart", "kill"])])
async def switch(bot: Bot, result: Arparma):
    url = URL + "/protected_instance"
    operation: str = list(result.subcommands.keys())[0]
    status_code, data = await request(bot, "get", f"{url}/{operation}")
    if status_code != 200:
        await matcher.finish(str(status_code) + " " + str(data))
    else:
        await matcher.finish("命令已发送！")


@matcher.assign("command")
async def command(bot: Bot, command: tuple[str, ...]):
    url = URL + "/protected_instance"
    c_command = " ".join(command)
    status_code, data = await request(
        bot,
        "get",
        f"{url}/command",
        {"command": c_command},
    )
    if status_code != 200:
        await matcher.finish(str(status_code) + " " + str(data))
    else:
        _, resp = await gather(
            matcher.send("命令已发送！"),
            request(
                bot,
                "get",
                f"{url}/outputlog",
                {"size": 20480},
            ),
        )
        if resp[0] != 200 or isinstance(resp[1], dict):
            return
        logs = resp[1].replace("\u001b[m> \r\u001b[K\u001b[32m", "").split("\r\n")
        index: None | int = None
        for i, log in enumerate(logs):
            if f"\x1b[m> {c_command}\r" == log:
                index = i
        if index:
            await matcher.finish(
                "\r\n".join(logs[index + 1 : -1]).replace(
                    "\u001b[?1l\u001b>\u001b[?1000l\u001b[?2004l\u001b[?1h\u001b=\u001b[?2004h> \r\u001b[K\u001b[32m",
                    "",
                )
            )
