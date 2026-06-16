"""基于 OpenCV 模板匹配的找图。

模板图就是你从游戏画面里截下来的小图(按钮/图标)，放到 templates/ 下。
"""
import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

import cv2
import numpy as np

log = logging.getLogger("twa")


@dataclass
class Match:
    name: str
    x: int          # 中心点 x
    y: int          # 中心点 y
    score: float    # 相似度
    w: int
    h: int


class Vision:
    def __init__(self, template_dir: str, threshold: float = 0.85,
                 save_debug_shots: bool = False, debug_dir: str = "logs/debug"):
        self.template_dir = template_dir
        self.threshold = threshold
        self.save_debug_shots = save_debug_shots
        self.debug_dir = debug_dir
        self._cache: Dict[str, np.ndarray] = {}
        if save_debug_shots:
            os.makedirs(debug_dir, exist_ok=True)

    def _load_template(self, name: str) -> np.ndarray:
        if name in self._cache:
            return self._cache[name]
        path = name if os.path.isabs(name) else os.path.join(self.template_dir, name)
        if not path.lower().endswith((".png", ".jpg", ".jpeg")):
            path += ".png"
        tpl = cv2.imread(path, cv2.IMREAD_COLOR)
        if tpl is None:
            raise FileNotFoundError(f"模板图不存在或无法读取: {path}")
        self._cache[name] = tpl
        return tpl

    def find(self, screen: np.ndarray, template_name: str,
             threshold: Optional[float] = None) -> Optional[Match]:
        """在 screen 中找 template，找到返回 Match，否则 None。"""
        thr = self.threshold if threshold is None else threshold
        tpl = self._load_template(template_name)
        th, tw = tpl.shape[:2]

        result = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        log.debug("find %s -> score=%.3f (thr=%.2f)", template_name, max_val, thr)
        if self.save_debug_shots:
            self._dump_debug(screen, template_name, max_loc, tw, th, max_val)

        if max_val < thr:
            return None
        return Match(
            name=template_name,
            x=max_loc[0] + tw // 2,
            y=max_loc[1] + th // 2,
            score=float(max_val),
            w=tw, h=th,
        )

    def exists(self, screen: np.ndarray, template_name: str,
               threshold: Optional[float] = None) -> bool:
        return self.find(screen, template_name, threshold) is not None

    def _dump_debug(self, screen, name, loc, w, h, score):
        vis = screen.copy()
        cv2.rectangle(vis, loc, (loc[0] + w, loc[1] + h), (0, 0, 255), 2)
        safe = name.replace("/", "_").replace("\\", "_")
        cv2.imwrite(os.path.join(self.debug_dir, f"{safe}_{score:.2f}.png"), vis)
