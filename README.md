# JYstore-Tultle

## 简介

基于[NoneBot](https://nonebot.dev/)的机器人

### 适配器使用：

- [QQ](https://github.com/nonebot/adapter-qq)
- [Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila)
- [Discord](https://github.com/nonebot/adapter-discord)

### 已安装插件：

- [本地数据存储](https://github.com/nonebot/plugin-localstore)
- [定时任务](https://github.com/nonebot/plugin-apscheduler)
- [服务器状态查看](https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status)
- [Epic 限免游戏资讯](https://github.com/monsterxcn/nonebot_plugin_epicfree)

### 自制插件：
- mutong_panel_api：控制[木桶面板](https://vat.yunqiaold.com/index.php)的翼龙面板api
- recode_picture：记录发送过的图片，并返回图片的直链

## 使用
本项目基于 nb-cli 脚手架运行，请先安装 nb-cli ，详见[NoneBot 快速上手](https://nonebot.dev/docs/quick-start)

### 下载项目
```bash
git clone https://github.com/Autuamn/JYstore-Tultle.git
cd JYstore-Tultle
```

### 安装依赖
本项目使用 poetry 管理依赖，请确保安装了 poetry

   ```bash
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
如果无法直接访问 Discord 还需加上`DISCORD_PROXY`设置代理

更多详细参数请见各适配器的说明：[QQ](https://github.com/nonebot/adapter-qq)、[Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila/blob/master/MANUAL.md)、[Discord](https://github.com/nonebot/adapter-discord)

### 运行机器人

```bash
nb run
```

### 如何后台运行？

推荐使用 tmux 工具<br>[Linux tmux 終端機管理工具使用教學](https://blog.gtwang.org/linux/linux-tmux-terminal-multiplexer-tutorial/)

## 配置项

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可

### 非自制插件的配置项请参考插件的主页

需要注意的是，本项目的自制插件使用[本地数据存储](https://github.com/nonebot/plugin-localstore)存储数据。如需更改目录请在配置文件中加入
```dotenv
localstore_cache_dir=""   # 缓存目录
localstore_config_dir=""  # 配置目录
localstore_data_dir=""    # 数据目录
```

### mutong_panel_api

- mutong_panel_client_api

    ```dotenv
    mutong_panel_client_api=https://vat-panel.yunqiaold.com/api/client/servers/xxx
    ```

    翼龙面板 api 的链接，`xxx`为控制台网址的最后一段

    例如：<br>
    服务器控制台的地址为`https://vat-panel.yunqiaold.com/server/1a7ce997`，则`xxx`就为`1a7ce997`

- mutong_panel_api_key

    ```dotenv
    mutong_panel_api_key=xxx
    ```

    面板账户的 **API 密钥**，可在“账号设置（点击头像）- API 凭证”处获取

### recode_picture

- recode_picture_recode_file_url

    ```dotenv
    recode_picture_recode_file_url="http://114.514.19.19:810"
    ```

    QQ官方机器人不能发域名 url，只能用ip访问



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

## More

[NoneBot Docs](https://nonebot.dev/)
