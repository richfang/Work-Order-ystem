"""主控制器：把 ADB / Vision / 任务串起来，提供给任务用的高层操作。"""
import logging
import time
from typing import List, Optional, Sequence

from .adb import ADB
from .vision import Vision, Match
from .notify import Notifier

log = logging.getLogger("twa")


class Bot:
    """任务可以调用的统一上下文。封装"找到就点"这类常用动作。"""

    def __init__(self, adb: ADB, vision: Vision, config: dict,
                 notifier: Optional[Notifier] = None):
        self.adb = adb
        self.vision = vision
        self.config = config
        self.loop_cfg = config.get("loop", {})
        self.notifier = notifier or Notifier({})

    def notify(self, event: str, text: str) -> None:
        self.notifier.send(event, text)

    # ---------- 截图 ----------
    def screen(self):
        return self.adb.screenshot()

    # ---------- 找图相关高层动作 ----------
    def find(self, template: str, threshold: Optional[float] = None) -> Optional[Match]:
        return self.vision.find(self.screen(), template, threshold)

    def wait_for(self, template: str, timeout: float = 15.0,
                 interval: float = 1.0) -> Optional[Match]:
        """轮询直到出现某模板或超时。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            m = self.find(template)
            if m:
                return m
            self.adb.sleep(interval)
        log.warning("等待 %s 超时(%.0fs)", template, timeout)
        return None

    def tap_template(self, template: str, threshold: Optional[float] = None,
                     wait_after: float = 1.0) -> bool:
        """找到模板就点击中心，返回是否点到。"""
        m = self.find(template, threshold)
        if not m:
            return False
        self.adb.tap(m.x, m.y)
        log.info("点击 %s (score=%.2f)", template, m.score)
        if wait_after:
            self.adb.sleep(wait_after)
        return True

    def tap_until_gone(self, template: str, max_taps: int = 10,
                       interval: float = 1.0) -> None:
        """反复点直到该模板消失(常用于关闭弹窗/连续领奖)。"""
        for _ in range(max_taps):
            if not self.tap_template(template, wait_after=interval):
                return

    def tap_xy(self, x: int, y: int, wait_after: float = 1.0) -> None:
        self.adb.tap(x, y)
        if wait_after:
            self.adb.sleep(wait_after)

    def swipe(self, x1, y1, x2, y2, duration_ms: int = 300, wait_after: float = 0.5):
        self.adb.swipe(x1, y1, x2, y2, duration_ms)
        if wait_after:
            self.adb.sleep(wait_after)

    # ---------- 多目标(优先级)匹配：传奇刷图打 boss 必备 ----------
    def find_any(self, templates: Sequence[str],
                 threshold: Optional[float] = None) -> Optional[Match]:
        """按列表顺序找，返回第一个命中的(即"优先级")。一次截图比对全部，省时。"""
        screen = self.screen()
        for name in templates:
            try:
                m = self.vision.find(screen, name, threshold)
            except FileNotFoundError:
                log.debug("模板缺失，跳过: %s", name)
                continue
            if m:
                return m
        return None

    def tap_any(self, templates: Sequence[str], threshold: Optional[float] = None,
                wait_after: float = 1.0) -> Optional[str]:
        """按优先级找到并点击，返回命中的模板名(没命中返回 None)。"""
        m = self.find_any(templates, threshold)
        if not m:
            return None
        self.adb.tap(m.x, m.y)
        log.info("点击 %s (score=%.2f)", m.name, m.score)
        if wait_after:
            self.adb.sleep(wait_after)
        return m.name

    def exists_any(self, templates: Sequence[str],
                   threshold: Optional[float] = None) -> bool:
        return self.find_any(templates, threshold) is not None
