"""摆摊回收 / 回仓，对应外挂的「摆摊回收 / 回仓 / 回城」。

把背包里的垃圾装备一键回收(或卖店)、贵重的存仓库，防止背包满了停挂。

options:
  open_btns:   [bag_btn]       # 打开背包
  recycle_btn: recycle         # 一键回收/分解
  confirm_btn: confirm
  store_btn:   store           # 存仓库(可选)
  back_city:   false           # 结束后是否回城
  back_city_btn: back_city_btn
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("stall_recycle")
class StallRecycle(Task):
    def run(self) -> bool:
        o = self.options
        log.info("[stall_recycle] 背包回收/回仓")

        for b in o.get("open_btns", ["bag_btn"]):
            self.bot.tap_template(b, wait_after=1.2)

        # 一键回收 + 确认(可能多轮)
        for _ in range(int(o.get("max_recycle", 5))):
            if not self.bot.tap_template(o.get("recycle_btn", "recycle"), wait_after=1.0):
                break
            self.bot.tap_template(o.get("confirm_btn", "confirm"), wait_after=1.0)

        # 存仓库(可选)
        if o.get("store_btn"):
            self.bot.tap_template(o["store_btn"], wait_after=1.0)

        self.bot.tap_until_gone("close_btn", max_taps=5)

        if o.get("back_city", False):
            self.bot.tap_template(o.get("back_city_btn", "back_city_btn"), wait_after=3.0)

        log.info("[stall_recycle] 完成")
        return True
