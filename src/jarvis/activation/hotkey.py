from jarvis.utils.logger import get_logger

logger = get_logger("hotkey")


class HotkeyListener:
    def __init__(self, hotkey: str = "ctrl+win+z"):
        self.hotkey = hotkey
        self._callback = None
        self._hook = None

    def register(self, callback):
        self._callback = callback
        try:
            import keyboard
            keyboard.add_hotkey(self.hotkey, self._on_trigger)
            logger.info(f"Hotkey registered: {self.hotkey}")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def _on_trigger(self):
        if self._callback:
            try:
                self._callback()
            except Exception as e:
                logger.error(f"Hotkey callback error: {e}")

    def unregister(self):
        if self._hook:
            try:
                import keyboard
                keyboard.remove_hotkey(self.hotkey)
                logger.info("Hotkey unregistered")
            except Exception as e:
                logger.error(f"Failed to unregister hotkey: {e}")
