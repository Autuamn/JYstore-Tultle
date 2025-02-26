import json

import aiohttp
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from .config import Config, key_mapping, plugin_config, signal_mapping

__plugin_meta__ = PluginMetadata(
    name="mutong-panel_api",
    description="",
    usage="",
    config=Config,
)


CLIENT_API = plugin_config.mutong_panel_client_api
API_KEY = plugin_config.mutong_panel_api_key
HEADEARS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "Application/vnd.pterodactyl.v1+json",
    "Content-Type": "application/json",
}


async def http_get(url, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            return response.status, await response.text()


async def http_post(url, headers, data):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json=data) as response:
            return response.status, await response.text()


async def milliseconds_to_time(milliseconds: int) -> str:
    seconds = milliseconds // 1000
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    timer_parts = []
    if days > 0:
        timer_parts.append(f"{days}d")
    if hours % 24 > 0 or days > 0:
        timer_parts.append(f"{hours % 24}h")
    if minutes % 60 > 0 or hours % 24 > 0 or days > 0:
        timer_parts.append(f"{minutes % 60}m")
    if seconds % 60 >= 0:  # Always include seconds
        timer_parts.append(f"{seconds % 60}s")

    timer_str = " ".join(timer_parts)
    return timer_str


async def bytes_to_size(bytes_count: int) -> str:
    bytes = bytes_count
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}"
        bytes /= 1024
    return f"{bytes:.2f}TiB"


ppapi_power = on_command("ppapi power", aliases={"ppapi 开关"})
ppapi_resources = on_command("ppapi resources", aliases={"aapai 资源"})
ppapi_log = on_command("ppapi log", aliases={"ppapi 日志"})
ppapi_api_chack = on_command("ppapi chack", aliases={"ppapi 检查"})
ppapi_command = on_command("ppapi command", aliases={"ppapi 命令"})


@ppapi_power.handle()
async def ppapi_power_function(args: Message = CommandArg()):
    power_api = f"{CLIENT_API}/power"
    data = {"signal": signal_mapping.get(args.extract_plain_text(), None)}
    if data["signal"] is None:
        await ppapi_resources_function(args="state")
    status_code, response_text = await http_post(power_api, HEADEARS, data)
    message = f"{status_code} Successful" if status_code == 204 else str(status_code)
    await ppapi_power.send(message)
    if response_text:
        await ppapi_power.finish(response_text)


@ppapi_resources.handle()
async def ppapi_resources_function(args: Message = CommandArg()):
    resources_api = f"{CLIENT_API}/resources"
    status_code, response_text = await http_get(resources_api, HEADEARS)
    (
        await ppapi_resources.finish(f"{status_code}\n{response_text}")
        if status_code != 200
        else None
    )
    response_json = json.loads(response_text)
    specified_key = key_mapping.get(
        args if isinstance(args, str) else args.extract_plain_text(), None
    )
    resource_attributes = response_json["attributes"]["resources"]
    if specified_key:
        specified_value = resource_attributes.get(
            specified_key,
            response_json["attributes"].get(specified_key, "不支持的参数"),
        )
        if specified_value == "不支持的参数" or specified_key == "current_state":
            stats_text = specified_key
        elif specified_key == "cpu_absolute":
            stats_text = f"{specified_value}%"
        elif specified_key == "uptime":
            stats_text = await milliseconds_to_time(specified_value)
        elif specified_key in ["memory_bytes", "disk_bytes"]:
            stats_text = await bytes_to_size(specified_value)
    else:
        stats_text = f'当前状态：{response_json["attributes"]["current_state"]}'
        if response_json["attributes"]["current_state"] == "offline":
            stats_text += (
                f'\n硬盘：{await bytes_to_size(resource_attributes["disk_bytes"])}'
            )
        else:
            uptime_str = await milliseconds_to_time(resource_attributes["uptime"])
            stats_text += (
                f"\n在线时间：{uptime_str}"
                + f'\nCPU负载：{resource_attributes["cpu_absolute"]}%'
                + f'\n内存：{await bytes_to_size(resource_attributes["memory_bytes"])}'
                + f'\n硬盘：{await bytes_to_size(resource_attributes["disk_bytes"])}'
                + f'\n网络 (接收)：{await bytes_to_size(resource_attributes["network_rx_bytes"])}'
                + f'\n网络 (发送)：{await bytes_to_size(resource_attributes["network_tx_bytes"])}'
            )
    await ppapi_resources.finish(stats_text)


@ppapi_log.handle()
async def ppapi_log_function(args: Message = CommandArg()):
    file_contents_api = f"{CLIENT_API}/files/contents"
    file_dir = "/logs/latest.log"
    _, response_file = await http_get(f"{file_contents_api}?file={file_dir}", HEADEARS)
    if args:
        try:
            n = int(args.extract_plain_text())
            last_n_lines = response_file.split("\n")[-(n + 1) : -1]
            await ppapi_log.send("\n".join(last_n_lines))
        except ValueError as e:
            await ppapi_log.finish(f"error: {e}")
    else:
        try:
            await ppapi_log.send(f"{file_contents_api}?file={file_dir}")
        except Exception as e:
            await ppapi_log.finish(f"{e}")


@ppapi_api_chack.handle()
async def ppapi_api_chack_function():
    status_code, response_text = await http_get(CLIENT_API, HEADEARS)
    message = f"{status_code} OK" if status_code == 200 else response_text
    await ppapi_api_chack.send(message)


@ppapi_command.handle()
async def ppapi_command_function(args: Message = CommandArg()):
    file_contents_api = f"{CLIENT_API}/files/contents"
    file_dir = "/logs/latest.log"
    _, response_file_before = await http_get(
        f"{file_contents_api}?file={file_dir}", HEADEARS
    )

    command_api = f"{CLIENT_API}/command"
    data = {"command": args.extract_plain_text()}
    status_code, response_text = await http_post(command_api, HEADEARS, data)
    if status_code == 204:
        _, response_file_after = await http_get(
            f"{file_contents_api}?file={file_dir}", HEADEARS
        )
        log_before = response_file_before.split("\n")[0:-1]
        new_log = response_file_after.split("\n")[len(log_before) : -1]
        if new_log:
            await ppapi_command.finish("\n".join(new_log))
        else:
            await ppapi_command.finish(f"{status_code} Successful")
    elif status_code == 502:
        await ppapi_command.finish(f"{status_code} Server offline")
    else:
        await ppapi_command.finish(response_text)
