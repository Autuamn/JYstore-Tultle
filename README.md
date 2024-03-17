# JYstore-Tultle

## 简介

基于[NoneBot](https://nonebot.dev/)的机器人

### 适配器使用：

- [QQ](https://github.com/nonebot/adapter-qq)
- [Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila)
- [Discord](https://github.com/nonebot/adapter-discord)

### 已安装插件：

- [服务器状态查看](https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status)

### 自制插件：
- epicfree：获取 Epic Game 免费游戏
- mutong_panel_api：控制[木桶面板](https://vat.yunqiaold.com/index.php)的翼龙面板api
- recode_picture：记录发送过的图片，并返回图片的直链
- sync_message_to_discord：向 Discord 同步消息（单向）

## 使用
本项目基于 nb-cli 脚手架运行，请先安装 nb-cli ，详见[NoneBot 快速上手](https://nonebot.dev/docs/quick-start)

### 下载项目
```bash
git clone https://github.com/Autuamn/JYstore-Tultle.git
cd JYstore-Tultle
```

### 安装依赖
本项目使用 poetry 管理依赖，请确保安装了 poetry


1. （可选）创建虚拟环境，以 venv 为例

    ```bash
    python -m venv .venv --prompt JYT
    # windows
    .venv\Scripts\activate
    # linux/macOS
    source .venv/bin/activate
    ```

2. 使用 poetry 安装依赖

   ```bash
   poetry shell
   poetry install
   ```

### 创建配置文件

在**项目文件夹**创建一个`.env`文件，并写入以下内容：
```dotenv
DRIVER=~aiohttp
QQ_BOTS='
[
  {
    "id": "xxx",
    "token": "xxx",
    "secret": "xxx",
    "intent": {
      "guild_messages": true,
      "at_messages": false,
      "direct_message": true
    }
  }
]
'
DISCORD_BOTS='
[
  {
    "token": "xxx",
    "intent": {
      "guild_messages": true,
      "direct_messages": true
    },
    "application_commands": {"*": ["*"]}
  }
]
'
kaiheila_bots =[{"token": "xxx"}]
```
如果无法直接访问Discord还需加上`DISCORD_PROXY`设置代理

更多详细参数请见各适配器的说明：[QQ](https://github.com/nonebot/adapter-qq)、[Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila/blob/master/MANUAL.md)、[Discord](https://github.com/nonebot/adapter-discord)

### 运行机器人

```bash
nb run
```

### 如何后台运行？

推荐使用 tmux 工具<br>[Linux tmux 終端機管理工具使用教學](https://blog.gtwang.org/linux/linux-tmux-terminal-multiplexer-tutorial/)

## 配置项

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可

### 服务器状态查看

此插件的配置详见[插件的介绍](https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status)

### mutong_panel_api

- mutong_panel_client_api

    ```dotenv
    mutong_panel_client_api=https://vat-panel.yunqiaold.com/api/client/servers/xxx
    ```

    翼龙面板api的链接，`xxx`为控制台网址的最后一段

    例如：<br>
    服务器控制台的地址为`https://vat-panel.yunqiaold.com/server/1a7ce997`，则`xxx`就为`1a7ce997`

- mutong_panel_api_key

    ```dotenv
    mutong_panel_api_key=xxx
    ```

    面板账户的 **API 密钥**，可在“账号设置（点击头像）- API 凭证”处获取

### recode_picture

- recode_picture_enable_guild_id

    ```dotenv
    recode_picture_enable_guild_id=["123", "456"]
    ```

    控制启用的频道

- recode_picture_enable_chinnel_id

    ```dotenv
    recode_picture_enable_chinnel_id=["123", "456"]
    ```

    控制启用的子频道

### sync_message_to_discord

- enable_guild_id
    
    ```dotenv
    enable_guild_id=["123", "456"]
    ```

    控制启用的频道

- channel_bind

    ```dotenv
    channel_bind='{
        "123": {
            "channel_id": 123,
            "webhook_id": 123,
            "webhook_token": "xxx"
        },
        "456": {
            "channel_id": 456,
            "webhook_id": 456,
            "webhook_token": "xxx"
        }
    }'
    ```

    绑定QQ子频道和Discode频道，需要自行准备好 [WebHook](https://discord.com/developers/docs/resources/webhook)

## More

[NoneBot Docs](https://nonebot.dev/)
