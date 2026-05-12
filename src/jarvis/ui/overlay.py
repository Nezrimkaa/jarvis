"""
Overlay window for Jarvis status display.
Uses Windows toast notifications + optional tkinter window in separate process.
"""

import subprocess
import tempfile
import json
import os
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("overlay")


class OverlayWindow:
    def __init__(self, width: int = 400, height: int = 300, opacity: float = 0.9):
        self.width = width
        self.height = height
        self.opacity = opacity
        self._process = None
        self._status_file = Path(tempfile.gettempdir()) / "jarvis_status.json"
        self._init_status_file()

    def _init_status_file(self):
        self._write_status({"status": "initialized", "history": []})

    def _write_status(self, data: dict):
        try:
            self._status_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def show(self):
        self._start_gui_process()

    def hide(self):
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
        self._write_status({"status": "hidden", "history": []})

    def _start_gui_process(self):
        if self._process and self._process.poll() is None:
            return

        gui_script = Path(__file__).parent / "_gui_window.py"
        try:
            self._process = subprocess.Popen(
                ["python", str(gui_script), str(self._status_file)],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:
            logger.error(f"Failed to start GUI process: {e}")

    def update_status(self, text: str):
        self._notify_windows(text)
        try:
            data = json.loads(self._status_file.read_text(encoding="utf-8"))
            data["status"] = text
            self._write_status(data)
        except Exception:
            self._write_status({"status": text, "history": []})

    def add_to_history(self, text: str):
        try:
            data = json.loads(self._status_file.read_text(encoding="utf-8"))
            history = data.get("history", [])
            history.append(text)
            if len(history) > 50:
                history = history[-50:]
            data["history"] = history
            self._write_status(data)
        except Exception:
            pass

    def _notify_windows(self, text: str):
        try:
            subprocess.Popen(
                ["powershell", "-Command",
                 f'''
                 [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                 $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                 $textNodes = $template.GetElementsByTagName("text")
                 $textNodes.Item(0).AppendChild($template.CreateTextNode("Jarvis")) | Out-Null
                 $textNodes.Item(1).AppendChild($template.CreateTextNode("{text}")) | Out-Null
                 $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                 [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Jarvis").Show($toast)
                 '''.replace("'", "''")],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:
            logger.debug(f"Toast notification failed: {e}")

    def close(self):
        self.hide()
