"""自动战斗 / 扫荡。

示例逻辑：进入战斗界面 -> 点开始 -> 等待结算 -> 领奖 -> 重复 N 次。
需要的模板(按你实际界面截)：
  - battle_entry.png    战斗/关卡入口
  - battle_start.png    开始战斗按钮
  - battle_win.png      战斗胜利标志(用于判断结算出现)
  - claim_btn.png       领奖按钮
  - close_btn.png       关闭按钮
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("auto_battle")
class AutoBattle(Task):
    def run(self) -> bool:
        repeat = int(self.options.get("repeat", 5))
        log.info("[auto_battle] 计划自动战斗 %d 次", repeat)

        done = 0
        for i in range(repeat):
            log.info("[auto_battle] 第 %d/%d 次", i + 1, repeat)

            self.bot.tap_until_gone("close_btn", max_taps=3)

            if not self.bot.tap_template("battle_entry"):
                log.warning("[auto_battle] 找不到战斗入口，停止")
                break

            if not self.bot.tap_template("battle_start", wait_after=2.0):
                log.warning("[auto_battle] 找不到开始按钮，停止")
                break

            # 等待战斗结算
            if not self.bot.wait_for("battle_win", timeout=120, interval=2.0):
                log.warning("[auto_battle] 等待结算超时，可能战败或卡住")
                self.bot.adb.back()
                continue

            # 领奖 + 关闭
            self.bot.tap_until_gone("claim_btn", max_taps=5)
            self.bot.tap_until_gone("close_btn", max_taps=5)
            done += 1

        log.info("[auto_battle] 完成 %d/%d 次", done, repeat)
        return done > 0
