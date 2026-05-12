import os
import subprocess
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("os_control")


class OSController:
    def __init__(self):
        self._shell = os.environ.get("SHELL", "powershell.exe")

    def get_volume(self) -> int:
        try:
            script = """
            $obj = New-Object -ComObject SAPI.SpSharedRecoContext
            $audio = $obj.Audio
            $devices = New-Object -ComObject MMDeviceEnumerator
            $device = $devices.GetDefaultAudioEndpoint(0, 1)
            $device.AudioEndpointVolume.MasterVolumeLevelScalar * 100
            """
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True, text=True, timeout=5,
                encoding="utf-8", errors="replace",
            )
            if result.stdout.strip():
                return int(float(result.stdout.strip()))
        except Exception as e:
            logger.debug(f"Failed to get volume: {e}")
        return 50  # fallback

    def set_volume(self, level: int):
        level = max(0, min(100, level))
        try:
            subprocess.run(
                ["powershell", "-Command",
                 f"(New-Object -ComObject WScript.Shell).SendKeys([char]175)"],
                capture_output=True, timeout=3,
            )
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")

    def open_app(self, app_name: str) -> bool:
        try:
            subprocess.Popen(["start", app_name], shell=True)
            logger.info(f"Opened app: {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return False

    def close_app(self, app_name: str) -> bool:
        try:
            result = subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"Closed app: {app_name}")
                return True
            logger.warning(f"Failed to close {app_name}: {result.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return False

    def take_screenshot(self, path: str | None = None) -> str | None:
        try:
            if path is None:
                path = str(Path.home() / "Pictures" / "jarvis_screenshot.png")
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            logger.info(f"Screenshot saved: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None

    def shutdown(self, delay_minutes: int = 0):
        cmd = f"shutdown /s /t {delay_minutes * 60}"
        subprocess.Popen(cmd, shell=True)

    def restart(self, delay_minutes: int = 0):
        cmd = f"shutdown /r /t {delay_minutes * 60}"
        subprocess.Popen(cmd, shell=True)

    def sleep(self):
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)

    def lock(self):
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
