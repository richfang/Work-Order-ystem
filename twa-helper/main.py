#!/usr/bin/env python3
"""全战觉醒挂机助手 入口。

用法:
    python main.py                  # 跑一轮 config.yaml 里的所有任务
    python main.py --loop           # 循环跑(挂机)，Ctrl+C 退出
    python main.py --once daily_login   # 只跑某一个任务
    python main.py --shot a.png     # 抓一张当前画面，方便你裁模板图
    python main.py --devices        # 列出 adb 设备

注意：仅用于 UI 自动化(模拟人手点击)，请知悉游戏协议与封号风险。
"""
import argparse
import sys
import time

import yaml

from src.logger import setup_logger
from src.adb import ADB, ADBError
from src.vision import Vision
from src.bot import Bot
from src import tasks as task_pkg


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_bot(cfg: dict) -> Bot:
    dev = cfg.get("device", {})
    adb = ADB(adb_path=dev.get("adb_path", "adb"), serial=dev.get("serial", ""))

    vcfg = cfg.get("vision", {})
    lcfg = cfg.get("log", {})
    vision = Vision(
        template_dir=vcfg.get("template_dir", "templates"),
        threshold=vcfg.get("threshold", 0.85),
        save_debug_shots=lcfg.get("save_debug_shots", False),
    )
    return Bot(adb, vision, cfg)


def run_tasks(bot: Bot, cfg: dict, only: str = None) -> None:
    task_pkg.load_all_tasks()
    names = [only] if only else cfg.get("tasks", [])
    opts = cfg.get("task_options", {})
    for name in names:
        try:
            cls = task_pkg.get_task(name)
            cls(bot, opts.get(name, {})).run()
        except FileNotFoundError as e:
            bot_log_warn(f"任务 {name} 缺少模板图: {e}")
        except Exception as e:  # noqa: BLE001 单个任务失败不应中断整体
            bot_log_warn(f"任务 {name} 执行出错: {e}")


def bot_log_warn(msg: str):
    import logging
    logging.getLogger("twa").warning(msg)


def main():
    parser = argparse.ArgumentParser(description="全战觉醒挂机助手")
    parser.add_argument("-c", "--config", default="config.yaml")
    parser.add_argument("--loop", action="store_true", help="循环挂机")
    parser.add_argument("--once", metavar="TASK", help="只执行指定任务")
    parser.add_argument("--shot", metavar="FILE", help="保存一张当前截图")
    parser.add_argument("--devices", action="store_true", help="列出 adb 设备")
    args = parser.parse_args()

    cfg = load_config(args.config)
    log = setup_logger(
        level=cfg.get("log", {}).get("level", "INFO"),
        log_dir=cfg.get("log", {}).get("dir", "logs"),
    )

    try:
        if args.devices:
            import subprocess
            adb_path = cfg.get("device", {}).get("adb_path", "adb")
            try:
                out = subprocess.run([adb_path, "devices"], capture_output=True)
                print(out.stdout.decode())
            except FileNotFoundError:
                log.error("找不到 adb（%s）。请先安装 Android Platform Tools "
                          "并确保 adb 在 PATH 中。", adb_path)
                sys.exit(1)
            return

        bot = build_bot(cfg)

        if args.shot:
            import cv2
            cv2.imwrite(args.shot, bot.screen())
            log.info("已保存截图到 %s（用图片工具裁出按钮放进 templates/）", args.shot)
            return

        if args.loop:
            interval = cfg.get("loop", {}).get("interval", 2.0)
            log.info("进入挂机循环，Ctrl+C 退出")
            while True:
                run_tasks(bot, cfg, only=args.once)
                time.sleep(interval)
        else:
            run_tasks(bot, cfg, only=args.once)

    except ADBError as e:
        log.error("ADB 错误: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("已手动退出")


if __name__ == "__main__":
    main()
