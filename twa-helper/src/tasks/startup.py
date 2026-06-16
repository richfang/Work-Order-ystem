"""开局处理：把游戏带到"可以开始挂机"的状态。

对应外挂里的「选择角色 / 雷电黑框 / 关弹窗」那一类。
传奇类小程序常见开局：模拟器/小程序黑框 -> 公告/活动弹窗 -> 选区选角 -> 进入主城。

需要的模板(按你游戏截)：
  close_btn        通用关闭(弹窗右上角 X)
  enter_game       进入游戏/开始游戏按钮
  select_role      选择角色/确认进入
  main_city        主城标志(用来确认已进入游戏)
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("startup")
class Startup(Task):
    def run(self) -> bool:
        log.info("[startup] 处理开局")

        # 连续关弹窗(公告/活动/签到弹窗)
        self.bot.tap_until_gone("close_btn", max_taps=8, interval=1.0)

        # 进入游戏 / 选区选角
        self.bot.tap_template("enter_game", wait_after=3.0)
        self.bot.tap_template("select_role", wait_after=3.0)

        # 再清一遍进游戏后的弹窗
        self.bot.tap_until_gone("close_btn", max_taps=8, interval=1.0)

        # 确认是否到主城
        if self.bot.wait_for("main_city", timeout=20, interval=2.0):
            log.info("[startup] 已进入主城")
            return True
        log.warning("[startup] 没确认到主城，可能模板缺失或卡在加载")
        self.bot.notify("stuck", "开局卡住：没进到主城")
        return False
