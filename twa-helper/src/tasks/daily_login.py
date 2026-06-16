"""每日登录 / 领取日常奖励。

这是一个示例任务，演示"找图->点击->关弹窗"的标准套路。
你需要在 templates/ 下准备对应的截图：
  - daily_reward_btn.png   每日奖励按钮
  - claim_btn.png          领取按钮
  - close_btn.png          通用关闭按钮(弹窗右上角 X)
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("daily_login")
class DailyLogin(Task):
    def run(self) -> bool:
        log.info("[daily_login] 开始领取每日奖励")

        # 先把可能挡路的弹窗关掉
        self.bot.tap_until_gone("close_btn", max_taps=5)

        # 打开每日奖励界面
        if not self.bot.tap_template("daily_reward_btn"):
            log.info("[daily_login] 没找到每日奖励入口，跳过")
            return False

        # 连续领取(有时是多个奖励)
        self.bot.tap_until_gone("claim_btn", max_taps=10)

        # 关闭界面
        self.bot.tap_until_gone("close_btn", max_taps=5)
        log.info("[daily_login] 完成")
        return True
