"""ADB 设备控制：截图、点击、滑动。

通过命令行 adb 与安卓模拟器/真机通信，不依赖第三方 adb 库，
方便在任意环境部署。
"""
import logging
import subprocess
import time
from typing import List, Optional

import numpy as np
import cv2

log = logging.getLogger("twa")


class ADBError(RuntimeError):
    pass


class ADB:
    def __init__(self, adb_path: str = "adb", serial: str = ""):
        self.adb_path = adb_path
        self.serial = serial or self._auto_detect_serial()
        log.info("使用 ADB 设备: %s", self.serial)

    # ---------- 底层命令 ----------
    def _base_cmd(self) -> List[str]:
        cmd = [self.adb_path]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def _run(self, args: List[str], binary: bool = False) -> bytes:
        cmd = self._base_cmd() + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, timeout=30, check=True
            )
        except FileNotFoundError as e:
            raise ADBError(f"找不到 adb 可执行文件: {self.adb_path}") from e
        except subprocess.CalledProcessError as e:
            raise ADBError(
                f"adb 命令失败: {' '.join(args)}\n{e.stderr.decode(errors='ignore')}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise ADBError(f"adb 命令超时: {' '.join(args)}") from e
        return result.stdout if binary else result.stdout.decode(errors="ignore")

    def _auto_detect_serial(self) -> str:
        try:
            out = subprocess.run(
                [self.adb_path, "devices"], capture_output=True, timeout=10
            ).stdout.decode(errors="ignore")
        except FileNotFoundError as e:
            raise ADBError(f"找不到 adb 可执行文件: {self.adb_path}") from e
        devices = [
            line.split("\t")[0]
            for line in out.splitlines()[1:]
            if line.strip() and line.strip().endswith("device")
        ]
        if not devices:
            raise ADBError(
                "没有检测到已连接的 ADB 设备。请先启动模拟器，"
                "并确认 `adb devices` 能看到它。"
            )
        return devices[0]

    def connect(self, address: str) -> None:
        """对网络型模拟器(如 127.0.0.1:7555)主动连接。"""
        out = self._run(["connect", address])
        log.debug("adb connect %s -> %s", address, out.strip())

    # ---------- 操作 ----------
    def screenshot(self) -> np.ndarray:
        """返回 BGR 格式的 numpy 图像。"""
        raw = self._run(["exec-out", "screencap", "-p"], binary=True)
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ADBError("截图解码失败，可能是 adb 输出被污染")
        return img

    def tap(self, x: int, y: int) -> None:
        log.debug("tap (%d, %d)", x, y)
        self._run(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        log.debug("swipe (%d,%d)->(%d,%d) %dms", x1, y1, x2, y2, duration_ms)
        self._run(
            ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)]
        )

    def back(self) -> None:
        self._run(["shell", "input", "keyevent", "4"])

    def app_stop(self, package: str) -> None:
        log.info("强停应用: %s", package)
        self._run(["shell", "am", "force-stop", package])

    def app_start(self, package: str) -> None:
        log.info("启动应用: %s", package)
        self._run(["shell", "monkey", "-p", package,
                   "-c", "android.intent.category.LAUNCHER", "1"])

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
