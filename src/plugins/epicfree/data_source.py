from datetime import datetime
import json
from pathlib import Path
from traceback import format_exc
from typing import Literal, Union

from aiohttp import ClientSession
from nonebot import get_driver
from nonebot.adapters import MessageSegment
from nonebot.log import logger
from pytz import timezone

RES_PARENT = getattr(get_driver().config, "resources_dir", None)
if RES_PARENT and Path(RES_PARENT).exists():
    res_path = Path(RES_PARENT) / "epicfree"
else:
    res_path = Path("data/epicfree")
res_path.mkdir(parents=True, exist_ok=True)
CACHE = res_path / "status.json"
PUSHED = res_path / "last_pushed.json"


async def subscribe_helper(
    method: Literal["读取", "启用", "删除"] = "读取",
    sub_type: str = "",
    subject: str = "",
) -> Union[dict, str]:
    """写入与读取订阅配置"""

    if CACHE.exists():
        status_data = json.loads(CACHE.read_text(encoding="UTF-8"))
    else:
        status_data = {"群聊": [], "私聊": []}
        CACHE.write_text(
            json.dumps(status_data, ensure_ascii=False, indent=2), encoding="UTF-8"
        )
    # 读取时，返回订阅状态字典
    if method == "读取":
        return status_data
    # 启用订阅时，将新的用户按类别写入至指定数组
    elif method == "启用":
        if subject in status_data[sub_type]:
            return f"{sub_type}{subject} 已经订阅过 Epic 限免游戏资讯了哦！"
        status_data[sub_type].append(subject)
    # 删除订阅
    elif method == "删除":
        if subject not in status_data[sub_type]:
            return f"{sub_type}{subject} 未曾订阅过 Epic 限免游戏资讯！"
        status_data[sub_type].remove(subject)
    try:
        CACHE.write_text(
            json.dumps(status_data, ensure_ascii=False, indent=2), encoding="UTF-8"
        )
        return f"{sub_type}{subject} Epic 限免游戏资讯订阅已{method}！"
    except Exception as e:
        logger.error(f"写入 Epic 订阅 JSON 错误 {e.__class__.__name__}\n{format_exc()}")
        return f"{sub_type}{subject} Epic 限免游戏资讯订阅{method}失败惹.."


async def query_epic_api() -> list:
    """
    获取所有 Epic Game Store 促销游戏

    参考 RSSHub ``/epicgames`` 路由 https://github.com/DIYgod/RSSHub/blob/master/lib/v2/epicgames/index.js
    """
    async with ClientSession(
        headers={
            "Referer": "https://www.epicgames.com/store/zh-CN/",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"
            ),
        }
    ) as session:
        try:
            async with session.get(
                "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions",
                params={"locale": "zh-CN", "country": "CN", "allowCountries": "CN"},
                timeout=10.0,
            ) as response:
                res_json = await response.json()
                return res_json["data"]["Catalog"]["searchStore"]["elements"]
        except Exception as e:
            logger.error(
                f"请求 Epic Store API 错误 {e.__class__.__name__}\n{format_exc()}"
            )
            return []


async def get_epic_free() -> str:
    """
    获取 Epic Game Store 免费游戏信息

    参考 pip 包 epicstore_api 示例 https://github.com/SD4RK/epicstore_api/blob/master/examples/free_games_example.py
    """

    games = await query_epic_api()
    if not games:
        return "Epic 可能又抽风啦，请稍后再试（"

    else:
        logger.debug(
            f"获取到 {len(games)} 个游戏数据：\n{('、'.join(game['title'] for game in games))}"
        )
        game_cnt, msg = 0, ""
        for game in games:
            game_name = game.get("title", "未知")
            try:
                if not game.get("promotions"):
                    continue
                game_promotions = game["promotions"]["promotionalOffers"]
                upcoming_promotions = game["promotions"]["upcomingPromotionalOffers"]
                original_price = game["price"]["totalPrice"]["fmtPrice"][
                    "originalPrice"
                ]
                discount_price = game["price"]["totalPrice"]["fmtPrice"][
                    "discountPrice"
                ]
                if not game_promotions:
                    if upcoming_promotions:
                        logger.info(
                            f"跳过即将推出免费游玩的游戏：{game_name}({discount_price})"
                        )
                    continue  # 仅返回正在推出免费游玩的游戏
                elif game["price"]["totalPrice"]["fmtPrice"]["discountPrice"] != "0":
                    logger.info(
                        f"跳过促销但不免费的游戏：{game_name}({discount_price})"
                    )
                    continue
                # 处理游戏发行信息
                game_dev, game_pub = game["seller"]["name"], game["seller"]["name"]
                for pair in game["customAttributes"]:
                    if pair["key"] == "developerName":
                        game_dev = pair["value"]
                    elif pair["key"] == "publisherName":
                        game_pub = pair["value"]
                dev_com = f"{game_dev} 开发、" if game_dev != game_pub else ""
                companies = (
                    f"由 {dev_com}{game_pub} 发行，"
                    if game_pub != "Epic Dev Test Account"
                    else ""
                )
                # 处理游戏限免结束时间
                date_rfc3339 = game_promotions[0]["promotionalOffers"][0]["endDate"]
                end_date = (
                    datetime.strptime(date_rfc3339, "%Y-%m-%dT%H:%M:%S.%f%z")
                    .astimezone(timezone("Asia/Shanghai"))
                    .strftime("%m {m} %d {d} %H:%M")
                    .format(m="月", d="日")
                )

                game_cnt += 1
                msg += f"{game_name} ({original_price})游戏{companies}，将在 {end_date} 结束免费领取~\n"

            except (AttributeError, IndexError, TypeError):
                logger.debug(
                    f"处理游戏 {game_name} 时遇到应该忽略的错误\n{format_exc()}"
                )
                pass
            except Exception as e:
                logger.error(
                    f"组织 Epic 订阅消息错误 {e.__class__.__name__}\n{format_exc()}"
                )
        # 返回整理为 CQ 码的消息字符串
        msg = (
            f"{game_cnt} 款游戏现在免费！\n"
            if game_cnt
            else "暂未找到正在促销的游戏..."
        ) + msg
        return msg


def check_push(msg: list[MessageSegment]) -> bool:
    """检查是否需要重新推送"""

    last_text: list[str] = (
        json.loads(PUSHED.read_text(encoding="UTF-8")) if PUSHED.exists() else []
    )
    _msg_text = [x.data["content"][0].data.get("text") for x in msg]
    this_text = [s for s in _msg_text if s]

    need_push = this_text != last_text
    if need_push:
        PUSHED.write_text(
            json.dumps(this_text, ensure_ascii=False, indent=2), encoding="UTF-8"
        )
    return need_push
