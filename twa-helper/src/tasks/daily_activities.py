"""日常活动调度，对应外挂里一大堆「称霸天下/比武大会/服战/界海探秘…」。

外挂的做法是"检测到活动开放就参加"。这里做成**数据驱动**：你在配置里
把每个活动描述成 入口->开始->(等结算)->领奖->关闭 的模板序列，本任务依次跑。
开放检测 = 入口模板能不能找到；找不到就跳过(没开放/已完成)。

options:
  activities:
    - name: 比武大会
      entry:  [activity_btn, biwu_btn]   # 依次点：活动面板 -> 比武入口
      start:  biwu_start                 # 开始/挑战按钮(可选)
      win:    biwu_win                   # 结算标志(可选，配了就等它)
      claim:  claim_btn                  # 领奖(可选)
      timeout: 120                       # 等结算超时秒
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("daily_activities")
class DailyActivities(Task):
    def run(self) -> bool:
        acts = self.options.get("activities", [])
        if not acts:
            log.info("[daily_activities] 未配置任何活动，跳过")
            return False

        done = 0
        for act in acts:
            name = act.get("name", "?")
            entries = act.get("entry", [])
            # 入口逐级点开；任一级点不到就认为没开放
            opened = True
            for i, t in enumerate(entries):
                if not self.bot.tap_template(t, wait_after=1.5):
                    if i == 0:
                        log.info("[daily_activities] %s 未开放/入口未找到，跳过", name)
                    opened = False
                    break
            if not opened:
                self.bot.tap_until_gone("close_btn", max_taps=3)
                continue

            log.info("[daily_activities] 参加: %s", name)

            if act.get("start"):
                self.bot.tap_template(act["start"], wait_after=2.0)

            if act.get("win"):
                self.bot.wait_for(act["win"], timeout=int(act.get("timeout", 120)),
                                  interval=2.0)

            if act.get("claim"):
                self.bot.tap_until_gone(act["claim"], max_taps=5)

            self.bot.tap_until_gone("close_btn", max_taps=5)
            done += 1

        log.info("[daily_activities] 完成 %d/%d 个活动", done, len(acts))
        return done > 0
