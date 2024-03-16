import aiohttp
import json
from io import StringIO

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata

from .config import plugin_config, Config, signal_mapping, key_mapping

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


mcsm_power = on_command("mcsmPower", rule=to_me(), priority=0, block=True)
mcsm_usage = on_command("mcsmUsage", rule=to_me(), priority=0, block=True)
mcsm_log = on_command("mcsmLog", rule=to_me(), priority=0, block=True)
mcsm_apiChack = on_command("mcsmApiChack", rule=to_me(), priority=0, block=True)
mcsm_command = on_command("mcsmCommand", rule=to_me(), priority=0, block=True)


@mcsm_power.handle()
async def mcsm_power_function(args: Message = CommandArg()):
    power_api = f"{CLIENT_API}/power"
    data = {"signal": signal_mapping.get(args.extract_plain_text(), None)}
    if data["signal"] is None:
        await mcsm_usage_function(args="state")
    status_code, response_text = await http_post(power_api, HEADEARS, data)
    message = f"{status_code} Successful" if status_code == 204 else str(status_code)
    await mcsm_power.send(message)
    if response_text:
        await mcsm_power.finish(response_text)


@mcsm_usage.handle()
async def mcsm_usage_function(args: Message = CommandArg()):
    usage_api = f"{CLIENT_API}/resources"
    status_code, response_text = await http_get(usage_api, HEADEARS)
    await mcsm_usage.finish(f"{status_code}\n{response_text}") if status_code != 200 else None
    response_json = json.loads(response_text)
    specified_key = key_mapping.get(args if isinstance(args, str) else args.extract_plain_text(), None)
    if specified_key is None:
        await mcsm_usage.finish(response_text)
    else:
        resource_attributes = response_json["attributes"]["resources"]
        specified_value = resource_attributes.get(
            specified_key, response_json["attributes"].get(specified_key, None)
        )
        await mcsm_usage.finish(str(specified_value))


@mcsm_log.handle()
async def mcsm_log_function(args: Message = CommandArg()):
    file_contents_api = f"{CLIENT_API}/files/contents"
    file_dir = "/logs/latest.log"
    _, response_file = await http_get(f"{file_contents_api}?file={file_dir}", HEADEARS)
    if args:
        try:
            n = int(args.extract_plain_text())
            last_n_lines = list(StringIO(response_file).readlines()[-n:])
            await mcsm_log.send("".join(last_n_lines))
        except ValueError:
            await mcsm_log.finish("error")
    else:
        try:
            await mcsm_log.send(f"{file_contents_api}?file={file_dir}")
        except Exception as e:
            await mcsm_log.finish(f"{e}")


@mcsm_apiChack.handle()
async def mcsm_apiChack_function():
    status_code, response_text = await http_get(CLIENT_API, HEADEARS)
    message = f"{status_code} OK" if status_code == 200 else response_text
    await mcsm_apiChack.send(message)


@mcsm_command.handle()
async def mcsm_command_function(args: Message = CommandArg()):
    command_api = f"{CLIENT_API}/command"
    data = {"command": args.extract_plain_text()}
    status_code, response_text = await http_post(command_api, HEADEARS, data)
    if status_code == 204:
        await mcsm_command.finish(f"{status_code} Successful")
    elif status_code == 502:
        await mcsm_command.finish(f"{status_code} Server offline")
    else:
        await mcsm_command.finish(response_text)
