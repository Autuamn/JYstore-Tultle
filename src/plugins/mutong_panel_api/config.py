from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    mutong_panel_client_api: str
    mutong_panel_api_key: str


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
