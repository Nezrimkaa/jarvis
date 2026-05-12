import threading
from jarvis.utils.logger import get_logger

logger = get_logger("tray")


class TrayIcon:
    def __init__(self, tooltip: str = "Jarvis Assistant", on_quit=None, on_activate=None):
        self.tooltip = tooltip
        self.on_quit = on_quit
        self.on_activate = on_activate
        self._icon = None
        self._thread = None

    def start(self):
        try:
            import pystray
            from PIL import Image, ImageDraw

            image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill=(0, 120, 255, 255))
            draw.ellipse([20, 20, 44, 44], fill=(255, 255, 255, 200))

            menu = pystray.Menu(
                pystray.MenuItem("Активировать", lambda: self._on_activate() if self.on_activate else None),
                pystray.MenuItem("Выход", lambda: self._on_quit() if self.on_quit else None),
            )

            self._icon = pystray.Icon("jarvis", image, self.tooltip, menu)
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
            logger.info("Tray icon started")
        except Exception as e:
            logger.error(f"Failed to start tray icon: {e}")

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
                logger.info("Tray icon stopped")
            except Exception:
                pass

    def _on_quit(self):
        if self.on_quit:
            self.on_quit()
        self.stop()

    def _on_activate(self):
        if self.on_activate:
            self.on_activate()
