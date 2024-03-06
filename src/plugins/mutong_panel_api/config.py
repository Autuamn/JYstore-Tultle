from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    mutong_panel_client_api: str
    mutong_panel_api_key: str

plugin_config = get_plugin_config(Config)

signal_mapping = {
    "kill": "kill",
    "restart": "restart",
    "stop": "stop",
    "start": "start",
    "开": "start",
    "关": "stop",
    "重启": "restart",
}

key_mapping = {
    "state": "current_state",
    "memory": "memory_bytes",
    "cpu": "cpu_absolute",
    "disk": "disk_bytes",
    "uptime": "uptime",
    "状态": "current_state",
    "内存": "memory_bytes",
    "硬盘": "disk_bytes",
    "运行时间": "uptime",
}
