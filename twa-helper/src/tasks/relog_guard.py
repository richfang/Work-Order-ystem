"""卡死检测 + 定时重启保活，对应外挂的「定时重启 / 卡死处理」。

无人值守挂机最怕卡死(掉线弹窗、加载卡住、画面定格)。本任务：
连续抓几张图比对，若画面长时间几乎不动、又不在主城/战斗，判定卡死，
尝试恢复(点 back / 关弹窗)，必要时重启微信，并推送告警。

options:
  samples:        4          # 抓几张对比
  sample_gap:     2.0        # 每张间隔秒
  diff_threshold: 2.0        # 平均像素差小于此值视为"画面没动"
  restart_wechat: false      # 卡死时是否重启微信
  wechat_package: com.tencent.mm
"""
import logging

import numpy as np

from . import Task, register

log = logging.getLogger("twa")


@register("relog_guard")
class RelogGuard(Task):
    def run(self) -> bool:
        o = self.options
        n = int(o.get("samples", 4))
        gap = float(o.get("sample_gap", 2.0))
        thr = float(o.get("diff_threshold", 2.0))

        shots = []
        for _ in range(n):
            shots.append(self.bot.screen())
            self.bot.adb.sleep(gap)

        # 计算相邻帧平均像素差
        diffs = []
        for a, b in zip(shots, shots[1:]):
            if a.shape != b.shape:
                diffs.append(999.0)
            else:
                diffs.append(float(np.mean(np.abs(a.astype(int) - b.astype(int)))))
        avg = sum(diffs) / len(diffs) if diffs else 0.0
        log.debug("[relog_guard] 画面平均帧差=%.2f (阈值=%.2f)", avg, thr)

        moving = avg >= thr
        # 在主城或战斗界面，即使画面没大动也算正常
        normal = self.bot.exists_any(["main_city", "in_battle"]) if not moving else True

        if moving or normal:
            return True  # 一切正常

        log.warning("[relog_guard] 疑似卡死(帧差=%.2f)，尝试恢复", avg)
        self.bot.notify("stuck", f"挂机疑似卡死(帧差={avg:.1f})，正在尝试恢复")

        # 恢复尝试：关弹窗 -> back
        self.bot.tap_until_gone("close_btn", max_taps=5)
        self.bot.adb.back()
        self.bot.adb.sleep(2.0)

        # 仍卡死且允许重启微信
        if o.get("restart_wechat", False):
            pkg = o.get("wechat_package", "com.tencent.mm")
            self.bot.adb.app_stop(pkg)
            self.bot.adb.sleep(3.0)
            self.bot.adb.app_start(pkg)
            self.bot.adb.sleep(8.0)
            self.bot.notify("stuck", "已重启微信，需小程序自动恢复或人工进入")
        return False
