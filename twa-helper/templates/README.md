# templates 模板图目录

这里放你从游戏画面里裁出来的小图（PNG），脚本靠它们来"认"界面上的按钮/图标。

## 怎么准备模板图

1. 启动模拟器，进入游戏到你要识别的画面。
2. 抓一张全屏截图：
   ```bash
   python main.py --shot full.png
   ```
3. 用任意图片工具（系统自带画图、QQ截图、Photoshop 等）把要识别的
   **按钮/图标** 单独裁出来，尽量裁得紧一点，只保留有辨识度的部分。
4. 按下面的命名存到本目录。

## 当前示例任务需要的模板（按需准备）

| 文件名 | 含义 |
|--------|------|
| `close_btn.png` | 通用关闭按钮（弹窗右上角 X） |
| `claim_btn.png` | 领取/领奖按钮 |
| `daily_reward_btn.png` | 每日奖励入口 |
| `battle_entry.png` | 战斗/关卡入口 |
| `battle_start.png` | 开始战斗按钮 |
| `battle_win.png` | 战斗胜利结算标志 |
| `resource_collect.png` | 可收取的资源气泡/图标 |

## 小贴士

- 模板图要和实际运行时**同一分辨率**下截取，分辨率不一致会匹配不上。
- 找不准时把 `config.yaml` 里 `vision.threshold` 调低（如 0.8），
  或打开 `log.save_debug_shots: true` 看 `logs/debug/` 里的匹配框。
- 裁图避免包含会变化的数字（如"领取x3"里的数字），只留固定不变的部分。
