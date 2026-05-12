import os
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("git_ops")


class GitOperator:
    def __init__(self, repo_path: str | None = None):
        self.repo_path = repo_path or os.getcwd()

    def _run_git(self, *args: str) -> dict:
        import subprocess
        try:
            result = subprocess.run(
                ["git"] + list(args),
                capture_output=True, text=True, timeout=30,
                cwd=self.repo_path, encoding="utf-8", errors="replace",
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}

    def commit(self, message: str = "Jarvis auto-commit") -> dict:
        self._run_git("add", "-A")
        return self._run_git("commit", "-m", message)

    def push(self, remote: str = "origin", branch: str | None = None) -> dict:
        if branch:
            return self._run_git("push", remote, branch)
        return self._run_git("push", remote)

    def pull(self, remote: str = "origin", branch: str | None = None) -> dict:
        if branch:
            return self._run_git("pull", remote, branch)
        return self._run_git("pull", remote)

    def branch(self, name: str, action: str = "create") -> dict:
        if action == "create":
            return self._run_git("branch", name)
        elif action == "switch":
            return self._run_git("checkout", name)
        elif action == "delete":
            return self._run_git("branch", "-d", name)
        return {"success": False, "stdout": "", "stderr": f"Unknown action: {action}"}

    def status(self) -> dict:
        return self._run_git("status")


class GitHubOperator:
    def __init__(self, token: str):
        self.token = token

    def create_pr(self, title: str, body: str = "", head: str = "", base: str = "main", repo: str = "") -> dict:
        try:
            from github import Github
            g = Github(self.token)
            if repo:
                gh_repo = g.get_repo(repo)
            else:
                user = g.get_user()
                gh_repo = user.get_repo(Path(os.getcwd()).name)

            if not head:
                head = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()

            pr = gh_repo.create_pull(title=title, body=body, head=head, base=base)
            logger.info(f"Created PR: {pr.html_url}")
            return {"success": True, "url": pr.html_url}
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return {"success": False, "error": str(e)}
