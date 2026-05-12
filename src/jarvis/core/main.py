"""
Jarvis Assistant — контекстно-зависимый движок.
LLM получает историю диалога + контекст и сама решает что делать.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.utils.logger import setup_logger, get_logger
from jarvis.core.config import load_config
from jarvis.core.session import Session
from jarvis.nlu.llm_client import LLMClient, LLMError
from jarvis.nlu.intent_parser import IntentParser
from jarvis.actions.dispatcher import ActionDispatcher
from jarvis.actions.os_control import OSController
from jarvis.actions.file_ops import FileOperator
from jarvis.actions.browser import BrowserController
from jarvis.actions.git_ops import GitOperator, GitHubOperator
from jarvis.actions.code_editor import CodeEditor
from jarvis.actions.system_cmd import SystemCmd
from jarvis.utils.security import get_deepseek_key, get_github_token

logger = get_logger("jarvis")


class JarvisAssistant:
    def __init__(self):
        self.config = load_config()
        self.session = Session(max_dialog=self.config.session.history_size)
        self.dispatcher = ActionDispatcher()
        self.os_ctrl = OSController()
        self.file_ops = FileOperator()
        self.browser = BrowserController()
        self.git_op = GitOperator()
        self.code_editor = CodeEditor()
        self.sys_cmd = SystemCmd()
        self.llm_client: LLMClient | None = None
        self.intent_parser: IntentParser | None = None
        self.gh_operator: GitHubOperator | None = None

        self._init_logging()
        self._init_llm()
        self._init_github()
        self._register_handlers()

    def _init_logging(self):
        setup_logger(
            name="jarvis",
            level=self.config.logging.level,
            file_path=self.config.logging.file,
        )

    def _init_llm(self):
        provider = self.config.llm.provider
        if provider == "github":
            api_key = get_github_token()
            endpoint = self.config.llm.github_endpoint
            model = self.config.llm.github_model
        else:
            api_key = get_deepseek_key()
            endpoint = self.config.llm.deepseek_endpoint
            model = self.config.llm.deepseek_model
        if not api_key:
            logger.error(f"API key for '{provider}' not found")
            return
        try:
            self.llm_client = LLMClient(
                api_key=api_key, model=model, endpoint=endpoint,
                provider=provider, temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens,
            )
            self.intent_parser = IntentParser(llm_client=self.llm_client)
            logger.info(f"{provider} | {model}")
        except LLMError as e:
            logger.error(f"LLM init failed: {e}")

    def _init_github(self):
        token = get_github_token()
        if token:
            self.gh_operator = GitHubOperator(token=token)
            logger.info("GitHub OK")

    def _register_handlers(self):
        handlers = {
            "file.create": self._handle_file_create,
            "file.delete": self._handle_file_delete,
            "file.move": self._handle_file_move,
            "file.find": self._handle_file_find,
            "folder.create": self._handle_folder_create,
            "folder.delete": self._handle_folder_delete,
            "os.app.open": self._handle_os_app_open,
            "os.app.close": self._handle_os_app_close,
            "os.volume": self._handle_os_volume,
            "os.shutdown": self._handle_os_shutdown,
            "os.restart": self._handle_os_restart,
            "os.sleep": self._handle_os_sleep,
            "os.lock": self._handle_os_lock,
            "os.screenshot": self._handle_os_screenshot,
            "browser.open": self._handle_browser_open,
            "browser.search": self._handle_browser_search,
            "browser.scrape": self._handle_browser_scrape,
            "browser.screenshot": self._handle_browser_screenshot,
            "git.commit": self._handle_git_commit,
            "git.push": self._handle_git_push,
            "git.pull": self._handle_git_pull,
            "git.branch": self._handle_git_branch,
            "git.pr": self._handle_git_pr,
            "code.open": self._handle_code_open,
            "code.write": self._handle_code_write,
            "shell.run": self._handle_shell_run,
            "assistant.status": self._handle_status,
            "assistant.help": self._handle_help,
        }
        self.dispatcher.register_all(handlers)
        logger.info(f"Registered {len(handlers)} handlers")

    def process_text(self, text: str) -> str:
        if not text:
            return ""

        self.session.add_message("user", text)
        session_ctx = self.session.get_context_prompt()
        dialog_hist = self.session.get_dialog_prompt()

        nlu = self._run_async(
            self.intent_parser.parse(text, session_context=session_ctx, dialog_history=dialog_hist)
        )
        logger.debug(f"NLU: actions={nlu.actions}, text={nlu.text[:100] if nlu.text else ''}")

        if nlu.actions:
            results = self.dispatcher.execute_plan(nlu.actions, self.session)
            combined = "\n".join(results)
            response = combined
            self.session.update_context("last_command", nlu.actions[0]["name"])
            self.session.update_context("last_result", combined[:200])
        elif nlu.text:
            response = nlu.text
        else:
            response = "✅ Выполнено"

        self.session.add_message("assistant", response)
        return response

    def _run_async(self, coro):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def shutdown(self):
        logger.info("Shutdown...")
        self._run_async(self._cleanup())

    async def _cleanup(self):
        if self.llm_client:
            await self.llm_client.close()

    def _resolve_path(self, path: str | None) -> str:
        if path and Path(path).is_absolute():
            return path
        base = path or self.session.context.get("current_dir", ".")
        return str(Path(self.session.context.get("current_dir", ".")) / (path or ""))

    def _handle_file_create(self, intent, entities, session):
        filename = entities.get("filename", "untitled.txt")
        path = entities.get("path") or entities.get("content")
        content = entities.get("content", "")
        full = str(Path(self._resolve_path(None)) / filename) if not entities.get("path") else self._resolve_path(entities.get("path", ""))
        if entities.get("path"):
            full = str(Path(entities["path"]) / filename) if not Path(entities["path"]).suffix else entities["path"]
        if content and not Path(full).suffix:
            full = full + ".txt"
        ok = self.file_ops.create_file(full, content)
        if ok:
            self.session.update_context("last_file", full)
            return f"✅ Файл {Path(full).name} создан"
        return f"❌ Не удалось создать {filename}"

    def _handle_file_delete(self, intent, entities, session):
        filename = entities.get("filename", "")
        path = entities.get("path", ".")
        if not filename:
            return "❌ Укажите имя файла"
        full = self._resolve_path(path) if path != "." else str(Path(self._resolve_path(None)) / filename)
        ok = self.file_ops.delete_file(full)
        return f"✅ {filename} удалён" if ok else f"❌ {filename} не найден"

    def _handle_file_move(self, intent, entities, session):
        src = entities.get("source", "")
        dst = entities.get("destination", "")
        ok = self.file_ops.move_file(src, dst)
        return f"✅ Перемещено" if ok else f"❌ Не удалось переместить"

    def _handle_file_find(self, intent, entities, session):
        name = entities.get("name", "")
        path = entities.get("path", ".")
        results = self.file_ops.find_files(name, path)
        if results:
            return f"🔍 Найдено {len(results)}:\n" + "\n".join(results[:10])
        return "❌ Файлы не найдены"

    def _handle_folder_create(self, intent, entities, session):
        name = entities.get("foldername", "new_folder")
        path = entities.get("path", self._resolve_path(None))
        full = str(Path(path) / name)
        ok = self.file_ops.create_folder(full)
        return f"✅ Папка {name} создана" if ok else f"❌ Не удалось создать папку"

    def _handle_folder_delete(self, intent, entities, session):
        name = entities.get("foldername", "")
        path = entities.get("path", ".")
        full = str(Path(path) / name)
        ok = self.file_ops.delete_folder(full)
        return f"✅ Папка удалена" if ok else f"❌ Не удалось удалить"

    def _handle_os_app_open(self, intent, entities, session):
        app = entities.get("app_name", "")
        if not app:
            return "❌ Укажите имя приложения"
        self.os_ctrl.open_app(app)
        return f"🚀 Открываю {app}"

    def _handle_os_app_close(self, intent, entities, session):
        app = entities.get("app_name", "")
        ok = self.os_ctrl.close_app(app)
        return f"✅ {app} закрыт" if ok else f"❌ {app} не найден"

    def _handle_os_volume(self, intent, entities, session):
        level = entities.get("level")
        if level is not None:
            self.os_ctrl.set_volume(int(level))
            return f"🔊 Громкость: {level}%"
        return f"🔊 Громкость: {self.os_ctrl.get_volume()}%"

    def _handle_os_shutdown(self, intent, entities, session):
        delay = int(entities.get("delay_minutes", 0))
        self.os_ctrl.shutdown(delay)
        return f"⏻ Выключение через {delay} мин" if delay else "⏻ Выключаюсь"

    def _handle_os_restart(self, intent, entities, session):
        delay = int(entities.get("delay_minutes", 0))
        self.os_ctrl.restart(delay)
        return f"🔄 Перезагрузка через {delay} мин" if delay else "🔄 Перезагружаюсь"

    def _handle_os_sleep(self, intent, entities, session):
        self.os_ctrl.sleep()
        return "💤 Спящий режим"

    def _handle_os_lock(self, intent, entities, session):
        self.os_ctrl.lock()
        return "🔒 Заблокировано"

    def _handle_os_screenshot(self, intent, entities, session):
        path = entities.get("path")
        result = self.os_ctrl.take_screenshot(path)
        return f"📸 Скриншот: {result}" if result else "❌ Не удалось сделать скриншот"

    def _handle_browser_open(self, intent, entities, session):
        url = entities.get("url", "")
        if not url:
            return "❌ Укажите URL"
        self._run_async(self.browser.open_url(url))
        return f"🌐 Открываю {url}"

    def _handle_browser_search(self, intent, entities, session):
        query = entities.get("query", "")
        engine = entities.get("engine", "google")
        self._run_async(self.browser.search(query, engine))
        return f"🔍 Ищу: {query}"

    def _handle_browser_scrape(self, intent, entities, session):
        url = entities.get("url", "")
        self._run_async(self.browser.scrape(url))
        return f"📄 Парсю {url}"

    def _handle_browser_screenshot(self, intent, entities, session):
        url = entities.get("url", "")
        path = entities.get("path")
        self._run_async(self.browser.screenshot(url, path))
        return f"📸 Скриншот {url}"

    def _handle_git_commit(self, intent, entities, session):
        msg = entities.get("message", "Jarvis auto-commit")
        result = self.git_op.commit(message=msg)
        return f"✅ Коммит: {result['stdout']}" if result['success'] else f"❌ {result['stderr']}"

    def _handle_git_push(self, intent, entities, session):
        branch = entities.get("branch")
        result = self.git_op.push(branch=branch)
        return f"✅ Push: {result['stdout']}" if result['success'] else f"❌ {result['stderr']}"

    def _handle_git_pull(self, intent, entities, session):
        branch = entities.get("branch")
        result = self.git_op.pull(branch=branch)
        return f"✅ Pull: {result['stdout']}" if result['success'] else f"❌ {result['stderr']}"

    def _handle_git_branch(self, intent, entities, session):
        name = entities.get("name", "")
        action = entities.get("action", "create")
        result = self.git_op.branch(name, action)
        return f"✅ Ветка: {result['stdout']}" if result['success'] else f"❌ {result['stderr']}"

    def _handle_git_pr(self, intent, entities, session):
        if not self.gh_operator:
            return "❌ GitHub не настроен"
        result = self.gh_operator.create_pr(
            title=entities.get("title", "PR"), body=entities.get("body", ""),
            head=entities.get("head", ""), base=entities.get("base", "main"),
        )
        return f"✅ PR: {result.get('url', '')}" if result['success'] else f"❌ {result.get('error', '')}"

    def _handle_code_open(self, intent, entities, session):
        filename = entities.get("filename", "")
        path = entities.get("path")
        ok = self.code_editor.open_file(filename, path)
        return f"📝 Открываю {filename}" if ok else f"❌ Не удалось открыть"

    def _handle_code_write(self, intent, entities, session):
        task = entities.get("task", "")
        filename = entities.get("filename", "output")
        lang = entities.get("language", "")
        return f"✍️ Генерация {filename}..."

    def _handle_shell_run(self, intent, entities, session):
        cmd = entities.get("command", "")
        admin = entities.get("admin", False)
        result = self.sys_cmd.run(cmd, admin=admin)
        return f"💻 {result['stdout'][:500]}" if result['success'] else f"❌ {result['stderr'][:500]}"

    def _handle_status(self, intent, entities, session):
        return "✅ Jarvis работает. Напиши что нужно сделать — я пойму."

    def _handle_help(self, intent, entities, session):
        return (
            "🤖 **Jarvis Assistant** — контекстный ассистент для Windows\n\n"
            "Говори что угодно, я пойму:\n"
            "• \"создай файл test.txt\"\n"
            "• \"открой github.com\"\n"
            "• \"сделай коммит\"\n"
            "• \"выключи ПК через 5 мин\"\n"
            "• \"напиши функцию на python\"\n"
            "• \"создай проект на десктопе и открой его\"\n\n"
            "🎤 Кнопка микрофона — голосовой ввод"
        )
