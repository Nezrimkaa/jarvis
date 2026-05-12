import subprocess
import shutil
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("code_editor")


class CodeEditor:
    def __init__(self):
        self._available_editors = self._detect_editors()

    def _detect_editors(self) -> dict:
        editors = {}
        if shutil.which("code"):
            editors["code"] = "code"
        if shutil.which("notepad"):
            editors["notepad"] = "notepad"
        return editors

    def open_file(self, filename: str, path: str | None = None, editor: str = "code") -> bool:
        try:
            if editor not in self._available_editors:
                editor = next(iter(self._available_editors), None)
            if editor is None:
                logger.error("No editor available")
                return False

            full_path = str(Path(path or ".") / filename) if path else filename
            if editor == "code":
                subprocess.Popen(["code", full_path])
            else:
                subprocess.Popen([editor, full_path])
            logger.info(f"Opened {full_path} in {editor}")
            return True
        except Exception as e:
            logger.error(f"Failed to open {filename}: {e}")
            return False
