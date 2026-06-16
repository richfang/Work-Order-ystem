"""消息推送：挂机卡死/出错时通知你（企业微信/钉钉机器人 或 Server酱）。

无人值守挂机时很实用。不配置则静默忽略。
"""
import json
import logging
import urllib.request

log = logging.getLogger("twa")


class Notifier:
    def __init__(self, cfg: dict):
        cfg = cfg or {}
        self.enabled = cfg.get("enabled", False)
        self.type = cfg.get("type", "webhook")
        self.url = cfg.get("url", "")
        self.events = set(cfg.get("on", ["stuck", "error"]))

    def send(self, event: str, text: str) -> None:
        if not self.enabled or not self.url or event not in self.events:
            return
        try:
            if self.type == "serverchan":
                self._post_form(self.url, {"title": "挂机助手", "desp": text})
            else:  # webhook: 企业微信/钉钉 机器人通用的 text 格式
                self._post_json(self.url, {"msgtype": "text", "text": {"content": text}})
            log.debug("已推送通知[%s]: %s", event, text)
        except Exception as e:  # noqa: BLE001 通知失败不能影响主流程
            log.warning("推送通知失败: %s", e)

    @staticmethod
    def _post_json(url: str, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10).read()

    @staticmethod
    def _post_form(url: str, payload: dict) -> None:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        urllib.request.urlopen(url, data=data, timeout=10).read()


# urllib.parse 延迟导入，避免顶部未使用告警
import urllib.parse  # noqa: E402
