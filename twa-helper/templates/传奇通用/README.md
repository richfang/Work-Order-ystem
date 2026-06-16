# 传奇通用 模板图清单

全战觉醒 / 英雄铁魂 / 奇光霸业 / 龙迹之城 等换皮游戏共用这套图。
用 `python main.py --shot full.png` 抓全屏，再把下面这些按钮/图标裁成小 png 放这里。
（先准备到哪个任务的图，就能先跑哪个任务；缺图的任务会自动跳过。）

## 通用
| 文件名 | 含义 |
|--------|------|
| `close_btn.png` | 弹窗右上角关闭 X |
| `main_city.png` | 主城界面标志(判断已进游戏) |
| `in_battle.png` | 战斗中标志(卡死检测用) |
| `confirm.png` | 通用"确认"按钮 |
| `claim_btn.png` | 领取/领奖 |

## startup（开局）
| `enter_game.png` | 进入/开始游戏 |
| `select_role.png` | 选择角色/确认进入 |

## auto_grind（刷图，核心）
| `map_btn.png` | 打开地图/传送面板(可选) |
| `map_1.png` `map_2.png` | 要刷的地图入口(可多个，轮换) |
| `boss_1.png` `boss_2.png` | boss(按优先级，先打 boss_1) |
| `monster.png` | 普通怪 |
| `revive_btn.png` | 死亡复活(灵符/原地复活) |
| `pickup.png` | 捡装备 |

## auto_craft（合成锻造）
| `bag_btn.png` | 背包 |
| `craft_btn.png` | 合成/锻造入口 |
| `do_craft.png` | 执行合成/锻造 |
| `only_ultimate_btn.png` | "只合终极"勾选(可选) |

## stall_recycle（回收回仓）
| `recycle.png` | 一键回收/分解 |
| `back_city_btn.png` | 回城(可选) |

## daily_activities（日常活动，按 config 里配的）
| `activity_btn.png` | 活动面板入口 |
| `biwu_btn.png` `biwu_start.png` | 比武入口/开始 |
| `czts_btn.png` | 称霸天下入口 |
| …按你在 config.yaml 里加的活动继续补 |

## 提示
- 模板必须和运行时**同分辨率**截取。
- 识别不到就调低 `config.yaml` 的 `vision.threshold`，或开 `save_debug_shots` 看 `logs/debug/`。
- 裁图只留固定不变的部分，避开会变的数字/血条。
