# JYstore-Tultle

## 简介

基于[NoneBot](https://nonebot.dev/)的机器人

### 适配器使用：

- [QQ](https://github.com/nonebot/adapter-qq)
- [Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila)

### 已安装插件：

- [服务器状态查看](https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status)

### 自制插件：
- mutong_panel_api：控制[木桶面板](https://vat.yunqiaold.com/index.php)的翼龙面板api
- recode_picture：记录发送过的图片，并返回图片的直链

## 使用

本项目基于 nb-cli 脚手架运行，请先安装 nb-cli，详见[NoneBot 快速上手](https://nonebot.dev/docs/quick-start)

### 下载项目
```bash
git clone https://github.com/Autuamn/JYstore-Tultle.git
cd JYstore-Tultle
```

### 安装依赖

1. （可选）创建虚拟环境，以 venv 为例

    ```bash
    python -m venv .venv --prompt nonebot2
    # windows
    .venv\Scripts\activate
    # linux/macOS
    source .venv/bin/activate
    ```

2. 安装 nonebot2 以及驱动器

   ```bash
   pip install 'nonebot2[aiohttp]'
   ```

3. 安装适配器

    ```bash
    pip install nonebot.adapters.qq nonebot.adapters.kaiheila
    ```

4. 安装插件

    ```bash
    pip install nonebot_plugin_status
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
kaiheila_bots =[{"token": "xxx"}]
```

更多详细参数请见各适配器的说明：[QQ](https://github.com/nonebot/adapter-qq)、[Kook](https://github.com/Tian-que/nonebot-adapter-kaiheila/blob/master/MANUAL.md)

### 运行机器人

```bash
nb run
```

### 如何后台运行？

推荐使用`tmux`工具。[Linux tmux 終端機管理工具使用教學](https://blog.gtwang.org/linux/linux-tmux-terminal-multiplexer-tutorial/)

## 配置项

配置方式：直接在 NoneBot 全局配置文件中添加以下配置项即可。

### 服务器状态查看

此插件的配置详见[插件的介绍](https://github.com/cscs181/QQ-GitHub-Bot/tree/master/src/plugins/nonebot_plugin_status)

### mutong_panel_api

- panel_client_api

    ```dotenv
    panel_client_api=https://vat-panel.yunqiaold.com/api/client/servers/xxx
    ```

    翼龙面板api的链接，`xxx`为控制台网址的最后一段

    例如：<br>
    服务器控制台的地址为`https://vat-panel.yunqiaold.com/server/1a7ce997`，则`xxx`就为`1a7ce997`

- panel_api_key

    ```dotenv
    panel_api_key=xxx
    ```

    面板账户的 **API 密钥**，可在`账号设置（点击头像）- API 凭证`处获取

### recode_picture

- enable_guild_id

    ```dotenv
    enable_guild_id=["xxx", "xxx"]
    ```

    控制启用的频道

- enable_chinnel_id

    ```dotenv
    enable_chinnel_id=["xxx", "xxx"]
    ```

    控制启用的子频道

## More

[NoneBot Docs](https://nonebot.dev/)
