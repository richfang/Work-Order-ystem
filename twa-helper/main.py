#!/usr/bin/env python3
"""小程序游戏挂机助手 入口（支持多游戏 profile）。

用法:
    python main.py                       # 跑当前游戏(active_game)的所有任务一轮
    python main.py --game 奇光霸业        # 指定游戏
    python main.py --loop                # 循环挂机，Ctrl+C 退出
    python main.py --once daily_login    # 只跑某个任务
    python main.py --serial 127.0.0.1:5555   # 指定设备(多开时按台跑)
    python main.py --shot a.png          # 抓当前画面，方便裁模板图
    python main.py doctor                 # 体检：检查 adb/设备/截图/模板
    python main.py --devices             # 列出 adb 设备

注意：仅做 UI 自动化(模拟人手点击)，不破解/不抓包/不连第三方服务器。
请知悉游戏与微信协议、封号风险，使用可承受损失的账号。
"""
import argparse
import os
import sys
import time

import yaml

from src.logger import setup_logger
from src.adb import ADB, ADBError
from src.vision import Vision
from src.bot import Bot
from src.notify import Notifier
from src import tasks as task_pkg


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_game(cfg: dict, game: str = None) -> tuple:
    """返回 (游戏名, 该游戏的 profile dict)。"""
    name = game or cfg.get("active_game")
    games = cfg.get("games", {})
    if name not in games:
        raise KeyError(f"未配置游戏 '{name}'。已配置: {list(games)}")
    return name, games[name] or {}


def build_bot(cfg: dict, game_name: str, serial: str = None) -> Bot:
    dev = cfg.get("device", {})
    adb = ADB(
        adb_path=dev.get("adb_path", "adb"),
        serial=serial if serial is not None else dev.get("serial", ""),
    )

    vcfg = cfg.get("vision", {})
    lcfg = cfg.get("log", {})
    template_dir = os.path.join(vcfg.get("template_root", "templates"), game_name)
    vision = Vision(
        template_dir=template_dir,
        threshold=vcfg.get("threshold", 0.85),
        save_debug_shots=lcfg.get("save_debug_shots", False),
    )
    notifier = Notifier(cfg.get("notify", {}))
    return Bot(adb, vision, cfg, notifier)


def run_tasks(bot: Bot, profile: dict, only: str = None) -> None:
    task_pkg.load_all_tasks()
    names = [only] if only else profile.get("tasks", [])
    opts = profile.get("task_options", {})
    for name in names:
        try:
            cls = task_pkg.get_task(name)
            cls(bot, opts.get(name, {})).run()
        except FileNotFoundError as e:
            log_warn(f"任务 {name} 缺少模板图: {e}")
        except Exception as e:  # noqa: BLE001 单任务失败不应中断整体
            log_warn(f"任务 {name} 执行出错: {e}")
            bot.notify("error", f"任务 {name} 出错: {e}")


def log_warn(msg: str):
    import logging
    logging.getLogger("twa").warning(msg)


def cmd_doctor(cfg: dict, game_name: str, serial: str) -> None:
    import logging
    log = logging.getLogger("twa")
    ok = True

    print("== 挂机助手体检 ==")
    # 1. adb 是否可用 + 设备
    try:
        adb = ADB(
            adb_path=cfg.get("device", {}).get("adb_path", "adb"),
            serial=serial if serial is not None else cfg.get("device", {}).get("serial", ""),
        )
        print(f"[OK] ADB 设备: {adb.serial}")
    except ADBError as e:
        print(f"[FAIL] ADB/设备: {e}")
        return

    # 2. 截图是否正常
    try:
        img = adb.screenshot()
        print(f"[OK] 截图正常, 分辨率 {img.shape[1]}x{img.shape[0]}")
    except ADBError as e:
        print(f"[FAIL] 截图: {e}")
        ok = False

    # 3. 模板目录与数量
    tdir = os.path.join(cfg.get("vision", {}).get("template_root", "templates"), game_name)
    if os.path.isdir(tdir):
        pngs = [f for f in os.listdir(tdir) if f.lower().endswith(".png")]
        if pngs:
            print(f"[OK] 模板目录 {tdir}: {len(pngs)} 张")
        else:
            print(f"[WARN] 模板目录 {tdir} 还没有任何 .png 模板，先去裁图")
            ok = False
    else:
        print(f"[WARN] 模板目录不存在: {tdir}（运行后会自动认这个路径）")
        ok = False

    print("== 体检完成: " + ("一切就绪 ✅" if ok else "有项目需要处理 ⚠️") + " ==")


def main():
    parser = argparse.ArgumentParser(description="小程序游戏挂机助手")
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "doctor"], help="run(默认) / doctor 体检")
    parser.add_argument("-c", "--config", default="config.yaml")
    parser.add_argument("--game", help="指定游戏(覆盖 active_game)")
    parser.add_argument("--serial", help="指定 adb 设备(多开按台跑)")
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
                print(subprocess.run([adb_path, "devices"], capture_output=True).stdout.decode())
            except FileNotFoundError:
                log.error("找不到 adb（%s）。请先安装 Android Platform Tools 并加入 PATH。", adb_path)
                sys.exit(1)
            return

        game_name, profile = resolve_game(cfg, args.game)
        log.info("当前游戏: %s", game_name)

        if args.command == "doctor":
            cmd_doctor(cfg, game_name, args.serial)
            return

        bot = build_bot(cfg, game_name, args.serial)

        if args.shot:
            import cv2
            cv2.imwrite(args.shot, bot.screen())
            log.info("已保存截图到 %s（裁出按钮放进 templates/%s/）", args.shot, game_name)
            return

        if args.loop:
            interval = cfg.get("loop", {}).get("interval", 2.0)
            log.info("进入挂机循环（%s），Ctrl+C 退出", game_name)
            while True:
                run_tasks(bot, profile, only=args.once)
                time.sleep(interval)
        else:
            run_tasks(bot, profile, only=args.once)

    except (ADBError, KeyError) as e:
        log.error("%s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        log.info("已手动退出")


if __name__ == "__main__":
    main()
