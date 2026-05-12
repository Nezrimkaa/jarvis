import subprocess
from jarvis.utils.logger import get_logger

logger = get_logger("system_cmd")


class SystemCmd:
    def run(self, command: str, timeout: int = 30, admin: bool = False) -> dict:
        try:
            if admin:
                logger.warning("Admin command requested (not implemented for safety)")
                return {"success": False, "stdout": "", "stderr": "Admin mode not supported in MVP"}

            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Command timed out"}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}

    def run_powershell(self, command: str, timeout: int = 30) -> dict:
        return self.run(f"powershell -Command \"{command}\"", timeout=timeout)
