from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class CommandAlias(BaseModel):
    instance: list[str] = Field(default=["check", "详情", "status", "状态"])
    open: list[str] = Field(default=["on", "开", "start", "启动"])
    stop: list[str] = Field(default=["off", "关", "停止"])
    restart: list[str] = Field(default=["重启"])
    kill: list[str] = Field(default=["强制结束", "强制停止", "结束进程"])
    command: list[str] = Field(default=["命令", "发送命令"])
    outputlog: list[str] = Field(default=["log", "获取输出", "日志", "输出"])


class Config(BaseModel):
    mcsm_url: str
    mcsm_api_key: str
    mcsm_daemon_id: str
    mcsm_instance_id: str
    mcsm_command_alias: CommandAlias = Field(default=CommandAlias())


plugin_config = get_plugin_config(Config)
