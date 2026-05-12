from collections.abc import Callable
from jarvis.utils.logger import get_logger

logger = get_logger("dispatcher")

Handler = Callable[[str, dict, object | None], str | None]


class ActionDispatcher:
    def __init__(self):
        self._handlers: dict[str, Handler] = {}

    def register(self, intent: str, handler: Handler):
        self._handlers[intent] = handler
        logger.debug(f"Registered handler for '{intent}'")

    def execute(self, intent: str, entities: dict, session=None) -> str | None:
        handler = self._handlers.get(intent)
        if handler is None:
            logger.warning(f"No handler for '{intent}'")
            return None
        try:
            result = handler(intent, entities, session)
            logger.info(f"'{intent}' → {result}")
            return result
        except Exception as e:
            logger.error(f"Handler '{intent}' failed: {e}")
            return f"❌ Ошибка при {intent}: {e}"

    def execute_plan(self, actions: list[dict], session=None) -> list[str]:
        results = []
        for action in actions:
            name = action.get("name", "")
            params = action.get("params", {})
            if not name:
                results.append("⚠️ Пустое действие")
                continue
            result = self.execute(name, params, session)
            results.append(result or f"✅ {name} выполнен")
        return results

    def register_all(self, handlers: dict[str, Handler]):
        for intent, handler in handlers.items():
            self.register(intent, handler)

    @property
    def handlers(self) -> dict:
        return dict(self._handlers)
