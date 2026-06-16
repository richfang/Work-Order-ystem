"""自动合成 / 锻造，对应外挂的「自动合成(只合终极) / 自动锻造」。

思路：打开背包/合成界面 -> 反复点合成/锻造直到没有可合的 -> 关闭。

options:
  open_btns:   [bag_btn, craft_btn]   # 依次点开背包->合成界面
  craft_btn:   do_craft               # 合成/锻造执行按钮
  confirm_btn: confirm                # 弹窗确认
  only_ultimate: true                 # 只合终极(需要 only_ultimate_btn 模板先勾选)
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("auto_craft")
class AutoCraft(Task):
    def run(self) -> bool:
        o = self.options
        log.info("[auto_craft] 开始自动合成/锻造")

        for b in o.get("open_btns", ["bag_btn", "craft_btn"]):
            self.bot.tap_template(b, wait_after=1.5)

        if o.get("only_ultimate", False):
            self.bot.tap_template("only_ultimate_btn", wait_after=0.5)

        craft = o.get("craft_btn", "do_craft")
        confirm = o.get("confirm_btn", "confirm")
        for _ in range(int(o.get("max_craft", 30))):
            if not self.bot.tap_template(craft, wait_after=1.0):
                break
            self.bot.tap_template(confirm, wait_after=1.0)

        self.bot.tap_until_gone("close_btn", max_taps=5)
        log.info("[auto_craft] 完成")
        return True
