"""核心自动挂机刷图：传奇类挂机的主体。

对应外挂里最核心的逻辑：进图 -> 按优先级找 boss/怪 -> 攻击 -> 复活/回血 ->
捡装备 -> 没怪就换图。所有目标都用"模板优先级列表"驱动，和外挂的
「boss优先顺序 / 先打最近 / 没怪跳过」一个思路。

options(在 config.yaml 的 task_options.auto_grind 配)：
  maps:          [map_1, map_2]      # 地图入口模板，轮换刷
  boss_priority: [boss_1, boss_2]    # 先打谁(优先级从高到低)
  monsters:      [monster]           # 普通怪
  revive:        [revive_btn]        # 死亡复活按钮(灵符/原地复活)
  pick_loot:     true                # 捡装备
  loot_btn:      pickup              # 捡装备按钮模板
  no_target_limit: 8                 # 连续多少轮找不到目标就换图
  round_wait:    1.5                 # 每轮间隔秒
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("auto_grind")
class AutoGrind(Task):
    def run(self) -> bool:
        o = self.options
        maps = o.get("maps", [])
        bosses = o.get("boss_priority", [])
        monsters = o.get("monsters", [])
        revive = o.get("revive", ["revive_btn"])
        targets = list(bosses) + list(monsters)
        no_target_limit = int(o.get("no_target_limit", 8))
        round_wait = float(o.get("round_wait", 1.5))

        if not targets:
            log.warning("[auto_grind] 没配 boss_priority/monsters，无法刷图")
            return False

        map_idx = 0
        if maps:
            self._enter_map(maps[map_idx])

        idle = 0
        rounds = 0
        log.info("[auto_grind] 开始刷图，目标优先级: %s", targets)

        while True:
            rounds += 1

            # 1. 死了就复活
            if self.bot.tap_any(revive, wait_after=3.0):
                log.info("[auto_grind] 已复活")
                idle = 0
                continue

            # 2. 捡装备(可选，先捡再打)
            if o.get("pick_loot", False):
                self.bot.tap_template(o.get("loot_btn", "pickup"), wait_after=0.3)

            # 3. 按优先级找目标并攻击
            hit = self.bot.tap_any(targets, wait_after=round_wait)
            if hit:
                idle = 0
                if hit in bosses:
                    log.info("[auto_grind] 打 boss: %s", hit)
                continue

            # 4. 没目标：累计空转，超阈值换图
            idle += 1
            log.debug("[auto_grind] 无目标 %d/%d", idle, no_target_limit)
            self.bot.adb.sleep(round_wait)

            if idle >= no_target_limit:
                if maps:
                    map_idx = (map_idx + 1) % len(maps)
                    log.info("[auto_grind] 长时间无怪，换图 -> %s", maps[map_idx])
                    self._enter_map(maps[map_idx])
                else:
                    log.info("[auto_grind] 长时间无怪且没配地图，结束本次刷图")
                    return True
                idle = 0

            # 单次任务的轮数上限(用于轮到下一个任务)；--loop 模式下交给主循环
            if rounds >= int(o.get("max_rounds", 9999)):
                return True

    def _enter_map(self, map_template: str) -> None:
        """打开地图/传送列表并进入指定地图。这里给最简实现：直接点地图入口模板。
        不同游戏可能要先点"地图"按钮再选，按需在模板/逻辑上扩展。"""
        if self.bot.tap_template("map_btn", wait_after=1.5):
            pass  # 有的游戏需要先开地图面板
        if self.bot.tap_template(map_template, wait_after=3.0):
            log.info("[auto_grind] 进入地图: %s", map_template)
        else:
            log.warning("[auto_grind] 没找到地图入口模板: %s", map_template)
