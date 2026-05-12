import os
import shutil
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("file_ops")


class FileOperator:
    def create_file(self, path: str, content: str = "") -> bool:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            logger.info(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create file {path}: {e}")
            return False

    def delete_file(self, path: str) -> bool:
        try:
            p = Path(path)
            if p.exists() and p.is_file():
                p.unlink()
                logger.info(f"Deleted file: {path}")
                return True
            logger.warning(f"File not found: {path}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {e}")
            return False

    def move_file(self, source: str, dest: str) -> bool:
        try:
            shutil.move(source, dest)
            logger.info(f"Moved {source} -> {dest}")
            return True
        except Exception as e:
            logger.error(f"Failed to move {source}: {e}")
            return False

    def create_folder(self, path: str) -> bool:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create folder {path}: {e}")
            return False

    def delete_folder(self, path: str) -> bool:
        try:
            shutil.rmtree(path, ignore_errors=True)
            logger.info(f"Deleted folder: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete folder {path}: {e}")
            return False

    def find_files(self, name: str, search_path: str = ".") -> list[str]:
        try:
            matches = []
            for root, dirs, files in os.walk(search_path):
                for f in files:
                    if name.lower() in f.lower():
                        matches.append(str(Path(root) / f))
            return matches
        except Exception as e:
            logger.error(f"Failed to find files: {e}")
            return []
