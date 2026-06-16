"""收资源 / 领产出。

示例：在主城界面点亮的资源图标(金币/粮食等)逐个收取。
需要的模板：
  - resource_collect.png   可收取的资源气泡/图标
"""
import logging

from . import Task, register

log = logging.getLogger("twa")


@register("collect_resource")
class CollectResource(Task):
    def run(self) -> bool:
        if not self.options.get("enabled", True):
            log.info("[collect_resource] 已在配置中禁用，跳过")
            return False

        log.info("[collect_resource] 开始收资源")
        # 资源图标可能有多个，反复点直到没有可收取的为止
        self.bot.tap_until_gone("resource_collect", max_taps=15, interval=0.5)
        log.info("[collect_resource] 完成")
        return True
