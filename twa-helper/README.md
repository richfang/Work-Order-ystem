# 全战觉醒 挂机助手 (twa-helper)

一个基于 **ADB + OpenCV 找图** 的微信小程序游戏《全战觉醒》自动化脚本框架。
原理是"模拟人手点屏幕"：截屏 → 识别按钮 → 模拟点击，**不破解游戏、不抓包、不绕反作弊**。

> ⚠️ **风险提醒**：自动挂机/模拟操作通常**违反微信及游戏用户协议**，存在**封号风险**。
> 请使用你能接受损失的账号，自行承担风险。本项目仅供学习自动化技术之用。

## 工作原理

```
安卓模拟器(雷电/MuMu) 跑微信 → 打开《全战觉醒》小程序
        │  ADB
        ▼
  截图(screencap) ──► OpenCV 模板匹配找按钮 ──► input tap 点击
        ▲                                          │
        └──────────────  任务循环(状态机) ◄────────┘
```

## 环境准备

1. **安卓模拟器**：装雷电 / MuMu / 夜神，在里面装微信并能正常打开小程序。
2. **ADB**：装 Android Platform Tools，确保命令行 `adb devices` 能看到模拟器。
   - 雷电常见地址 `127.0.0.1:5555`、MuMu `127.0.0.1:7555`、夜神 `127.0.0.1:62001`
   - 网络型需要先 `adb connect 127.0.0.1:7555`
3. **Python 3.9+** 并安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

```bash
# 1. 确认设备连上
python main.py --devices

# 2. 进游戏到目标画面，抓一张截图，用来裁模板
python main.py --shot full.png

# 3. 把按钮裁成小图放进 templates/（命名见 templates/README.md）

# 4. 跑一轮所有任务
python main.py

# 5. 持续挂机（Ctrl+C 退出）
python main.py --loop

# 只跑某个任务
python main.py --once daily_login
```

## 配置

所有行为在 `config.yaml` 里调：设备序列号、找图阈值、任务列表与各任务参数、日志等级等。

## 目录结构

```
twa-helper/
├── main.py              # 入口（命令行）
├── config.yaml          # 配置
├── requirements.txt
├── src/
│   ├── adb.py           # ADB 控制：截图/点击/滑动
│   ├── vision.py        # OpenCV 模板匹配找图
│   ├── bot.py           # 高层动作：wait_for / tap_template ...
│   ├── logger.py
│   └── tasks/           # 任务模块（可自行增减）
│       ├── __init__.py        # 任务注册表
│       ├── daily_login.py     # 每日奖励
│       ├── auto_battle.py     # 自动战斗
│       └── collect_resource.py# 收资源
├── templates/           # 你自己裁的按钮模板图
└── logs/
```

## 写一个新任务

在 `src/tasks/` 下新建文件，注册即可：

```python
from . import Task, register

@register("my_task")
class MyTask(Task):
    def run(self) -> bool:
        if self.bot.tap_template("some_button"):
            self.bot.wait_for("result_flag", timeout=30)
            self.bot.tap_until_gone("close_btn")
        return True
```

然后把 `my_task` 加进 `config.yaml` 的 `tasks` 列表。

## 常见问题

- **找不到设备**：先开模拟器，再 `adb connect <地址>`，确认 `adb devices` 有 `device` 状态。
- **点不准/识别不到**：模板图必须和运行时同一分辨率截取；调低 `vision.threshold`；
  打开 `log.save_debug_shots: true` 看 `logs/debug/` 的匹配框定位问题。
- **画面有动画导致漏点**：适当加大 `wait_after` / `interval`。
