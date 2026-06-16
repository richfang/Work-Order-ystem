"""主线挂机刷图（放置模型）。

依据真实界面(IMG_0483)：进图后角色**全自动战斗**，bot 不点怪，只负责：
打开挂机地图面板 -> 在左侧列表选地图 -> 点红色「进入」-> 挂一段时间
-> 期间监控死亡复活/清图 -> 到点换下一张图。

options(config.yaml: task_options.auto_grind)：
  open_grind_btn: grind_map_btn   # 打开挂机/传送地图面板的按钮
  maps:          [map_1, map_2]   # 左侧地图列表项(从模拟器截图裁)
  enter_btn:     enter_map_btn    # 红色「进入」
  revive:        [revive_btn]     # 复活弹窗按钮(死亡时出现)
  cleared_flag:  map_cleared      # (可选)清图/无怪标志，出现就提前换图
  dwell_seconds: 600              # 每张图挂多久(秒)换下一张
  check_interval: 10              # 监控间隔(查复活/清图)
  max_switches:  6                # 换几次图后让位给其它任务(--loop 下轮回)
"""
import logging
import time

from . import Task, register

log = logging.getLogger("twa")


@register("auto_grind")
class AutoGrind(Task):
    def run(self) -> bool:
        o = self.options
        maps = o.get("maps", [])
        if not maps:
            log.warning("[auto_grind] 未配置 maps，无法挂机刷图")
            return False

        enter_btn = o.get("enter_btn", "enter_map_btn")
        revive = o.get("revive", ["revive_btn"])
        cleared = o.get("cleared_flag")
        dwell = float(o.get("dwell_seconds", 600))
        interval = float(o.get("check_interval", 10))
        max_switches = int(o.get("max_switches", len(maps)))

        for n in range(max_switches):
            target_map = maps[n % len(maps)]
            if not self._enter_grind_map(o, target_map, enter_btn):
                log.warning("[auto_grind] 进图失败: %s，跳过", target_map)
                continue

            log.info("[auto_grind] 在 %s 挂机 %.0f 秒", target_map, dwell)
            self._grind_until(dwell, interval, revive, cleared)

        return True

    def _enter_grind_map(self, o, target_map, enter_btn) -> bool:
        # 打开挂机地图面板(可能本来就开着，点不到也无妨)
        self.bot.tap_template(o.get("open_grind_btn", "grind_map_btn"), wait_after=1.5)
        # 关掉可能的小弹窗
        self.bot.tap_template("close_popup", wait_after=0.3)
        # 选地图
        if not self.bot.tap_template(target_map, wait_after=1.0):
            return False
        # 点「进入」
        if not self.bot.tap_template(enter_btn, wait_after=3.0):
            log.debug("[auto_grind] 未找到进入按钮(可能已自动进图)")
        return True

    def _grind_until(self, dwell, interval, revive, cleared) -> None:
        deadline = time.time() + dwell
        while time.time() < deadline:
            # 死亡复活
            if self.bot.tap_any(revive, wait_after=2.0):
                log.info("[auto_grind] 检测到死亡，已复活")
                continue
            # 提前清图
            if cleared and self.bot.find(cleared):
                log.info("[auto_grind] 该图已清，提前换图")
                return
            self.bot.adb.sleep(interval)
