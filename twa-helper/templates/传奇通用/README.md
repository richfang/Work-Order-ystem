# 传奇通用 模板图清单（按真实界面整理）

> ⚠️ 你发的是 **iPhone 截图**，只能当"长啥样"的参考。挂机跑在**安卓模拟器**上，
> 分辨率/缩放不同，**模板图必须用 `python main.py --shot` 从模拟器里截再裁**，
> 否则匹配不上。

抓图：`python main.py --shot full.png`，再把下列按钮裁成小 png 放本目录。
缺哪张，对应任务/活动会自动跳过，所以可以先做核心几张跑起来。

## 通用（每张子界面都有）
| 文件名 | 含义 | 参考图 |
|--------|------|--------|
| `close_btn.png` | 右上角红色 X 关闭 | 全部 |
| `close_popup.png` | 中间小弹窗的关闭/空白处(可选) | — |
| `claim_btn.png` | 领取/领奖 | — |
| `confirm.png` | 通用"确认" | — |
| `main_city.png` | 主城/挂机主界面标志 | IMG_0472 |
| `in_battle.png` | 战斗中标志(卡死检测用) | IMG_0472 |

## startup（开局）
| `enter_game.png` | 进入/开始游戏 |
| `select_role.png` | 选区/选角确认 |

## auto_grind（主线挂机刷图，核心）— 参考 IMG_0483
| `grind_map_btn.png` | 打开挂机/传送地图面板的按钮 |
| `map_1.png` `map_2.png` `map_3.png` | 左侧地图列表项(夺命无忌/远昇… 各裁一张) |
| `enter_map_btn.png` | 红色「进入」 |
| `revive_btn.png` | 死亡复活弹窗按钮(「复活提醒」相关) |
| `map_cleared.png` | (可选)清图/无怪标志，如"剩余精英怪 0/15"那块 |

## daily_activities（每日活动）— 参考 IMG_0473 总地图
| `world_map_btn.png` | 打开副本/活动总地图的按钮 |
| `act_yuangu.png` | 总地图上「远古荒原」入口 |
| `act_kuangbao.png` | 「狂暴战场」入口 |
| `act_biwu.png` | 「比武大会」入口 |
| `act_tiankong.png` | 「天空之城」入口 |
| `act_jindi.png` | 「禁地福利」入口 |
| `act_wanyao.png` | 「万妖牢狱」入口 |
| `enter_map_btn.png` | 红色「进入」(复用) |
| `challenge_btn.png` | 红色「前往挑战」(IMG_0475/0478) |
| `match_btn.png` | 「匹配对手」(IMG_0481 比武) |
| `onekey_btn.png` | 「一键挑战」(IMG_0474 天空之城) |

## auto_craft（合成锻造）
| `bag_btn.png` | 背包 |
| `craft_btn.png` | 合成/锻造入口 |
| `do_craft.png` | 执行合成/锻造 |
| `only_ultimate_btn.png` | "只合终极"勾选(可选) |

## stall_recycle（回收回仓）
| `recycle.png` | 一键回收/分解 |
| `back_city_btn.png` | 回城(可选) |

## 裁图提示
- 只留**固定不变**的部分，避开会变的数字(战力/次数/血条)。
- 识别不到：调低 `config.yaml` 的 `vision.threshold`，或开 `save_debug_shots` 看 `logs/debug/`。
