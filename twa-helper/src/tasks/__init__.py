"""任务注册表。

每个任务模块用 @register("名字") 装饰一个 Task 子类即可被主程序按
config.yaml 里的 tasks 列表加载。
"""
import importlib
import logging
import pkgutil
from typing import Dict, Type

log = logging.getLogger("twa")

_REGISTRY: Dict[str, Type["Task"]] = {}


def register(name: str):
    def deco(cls):
        _REGISTRY[name] = cls
        cls.task_name = name
        return cls
    return deco


class Task:
    """所有任务的基类。"""
    task_name: str = "base"

    def __init__(self, bot, options: dict):
        self.bot = bot
        self.options = options or {}

    def run(self) -> bool:
        """执行任务，返回是否成功。子类必须实现。"""
        raise NotImplementedError


def load_all_tasks() -> None:
    """导入 tasks 包下所有模块，触发 @register。"""
    import src.tasks as pkg
    for _, modname, _ in pkgutil.iter_modules(pkg.__path__):
        if modname.startswith("_"):
            continue
        importlib.import_module(f"src.tasks.{modname}")


def get_task(name: str) -> Type[Task]:
    if name not in _REGISTRY:
        raise KeyError(
            f"未知任务 '{name}'。已注册任务: {list(_REGISTRY)}"
        )
    return _REGISTRY[name]
