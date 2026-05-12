"""
Agentic NLU — LLM получает контекст + историю диалога и сама решает что делать.
Ответ: либо текст, либо [ACTION: name] param=val
"""

import re
from dataclasses import dataclass, field
from jarvis.utils.logger import get_logger

logger = get_logger("nlu")


@dataclass
class NLUResponse:
    text: str = ""
    actions: list[dict] = field(default_factory=list)
    is_action: bool = False
    raw: str = ""


JARVIS_SYSTEM_PROMPT = """Ты — Jarvis, интеллектуальный ассистент для Windows.

У тебя есть инструменты (actions). Если пользователь просит что-то сделать — 
используй их. Если просто разговор — отвечай текстом.

=== ИНСТРУМЕНТЫ ===
file.create — создать файл. Параметры: filename, path, content
file.delete — удалить файл. Параметры: filename, path
file.move — переместить файл. Параметры: source, destination
file.find — найти файл. Параметры: name, path
folder.create — создать папку. Параметры: foldername, path
folder.delete — удалить папку. Параметры: foldername, path
os.app.open — открыть приложение. Параметры: app_name
os.app.close — закрыть приложение. Параметры: app_name
os.volume — изменить громкость. Параметры: level (0-100)
os.shutdown — выключить ПК. Параметры: delay_minutes
os.restart — перезагрузить. Параметры: delay_minutes
os.sleep — спящий режим. Параметры: нет
os.lock — заблокировать экран. Параметры: нет
os.screenshot — скриншот экрана. Параметры: path
browser.open — открыть URL. Параметры: url
browser.search — поиск в интернете. Параметры: query, engine
browser.scrape — спарсить страницу. Параметры: url, selector
browser.screenshot — скриншот страницы. Параметры: url, path
git.commit — коммит. Параметры: message
git.push — пуш. Параметры: branch, remote
git.pull — пул. Параметры: branch, remote
git.branch — работа с ветками. Параметры: name, action (create/switch/delete)
git.pr — создать PR. Параметры: title, body, head, base
code.open — открыть файл в редакторе. Параметры: filename, path
code.write — сгенерировать код. Параметры: language, task, filename
shell.run — выполнить команду. Параметры: command

=== ПРАВИЛА ===
1. Если пользователь просит действие — используй [ACTION: имя] параметры
2. Если просит несколько действий — сделай несколько [ACTION: ...] строк подряд
3. Если просто разговор или вопрос — отвечай текстом
4. Поддерживай контекст: "открой его" может означать предыдущий файл
5. Не уверен — уточни
6. Для file.create/content указывай небольшие примеры кода, если просят
7. Отвечай на том же языке, что и пользователь

=== КОНТЕКСТ СЕССИИ ===
{session_context}

=== ИСТОРИЯ ДИАЛОГА ===
{dialog_history}

=== ТЕКУЩИЙ ЗАПРОС ===
{user_message}

=== ТВОЙ ОТВЕТ (текст или action-блоки) ===
"""


class IntentParser:
    def __init__(self, llm_client=None):
        self._llm = llm_client

    def build_prompt(self, user_message: str, session_context: str, dialog_history: str) -> str:
        return JARVIS_SYSTEM_PROMPT.format(
            user_message=user_message,
            session_context=session_context or "нет данных",
            dialog_history=dialog_history or "начало диалога",
        )

    def parse_response(self, raw: str) -> NLUResponse:
        action_lines = []
        other_lines = []
        for line in raw.split('\n'):
            stripped = line.strip()
            match = re.match(r'\[ACTION:\s*(\w+(?:\.\w+)*)\]\s*(.*)', stripped)
            if match:
                action_lines.append(match.groups())
            else:
                other_lines.append(line)

        if not action_lines:
            return NLUResponse(text=raw.strip(), raw=raw)

        actions = []
        for name, params_str in action_lines:
            params = {}
            if params_str.strip():
                for pair in re.findall(r'(\w[\w.]*)\s*=\s*("(?:\\.|[^"])*"|[^\s,]+)', params_str):
                    key, val = pair
                    val = val.strip('"')
                    params[key] = val
            actions.append({"name": name.strip(), "params": params})

        text = '\n'.join(other_lines).strip()
        return NLUResponse(text=text, actions=actions, is_action=True, raw=raw)

    async def parse(self, user_message: str, session_context: str = "", dialog_history: str = "") -> NLUResponse:
        if not self._llm:
            logger.error("LLM not configured")
            return NLUResponse(text="Ошибка: LLM не настроен")

        if not user_message:
            return NLUResponse(text="")

        prompt = self.build_prompt(user_message, session_context, dialog_history)

        try:
            response = await self._llm.chat(message=prompt)
            logger.debug(f"LLM raw: {response[:300]}")
            return self.parse_response(response)
        except Exception as e:
            logger.error(f"NLU failed: {e}")
            return NLUResponse(text=f"❌ Ошибка: {e}")
