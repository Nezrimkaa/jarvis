import os
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    dialog: list = field(default_factory=list)
    context: dict = field(default_factory=lambda: {
        "state": "idle",
        "current_dir": str(Path.home()),
        "desktop": str(Path.home() / "Desktop"),
        "username": os.environ.get("USERNAME", "unknown"),
        "last_command": None,
        "last_result": None,
    })
    max_dialog: int = 100
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_message(self, role: str, text: str):
        self.dialog.append({
            "role": role,
            "text": text,
            "time": datetime.now().isoformat(),
        })
        if len(self.dialog) > self.max_dialog:
            self.dialog = self.dialog[-self.max_dialog:]

    def update_context(self, key: str, value):
        self.context[key] = value

    def get_context_prompt(self) -> str:
        lines = [
            f"Текущая директория: {self.context.get('current_dir', 'неизвестно')}",
            f"Рабочий стол: {self.context.get('desktop', 'неизвестно')}",
            f"Пользователь: {self.context.get('username', 'unknown')}",
        ]
        if self.context.get("last_command"):
            lines.append(f"Последняя команда: {self.context['last_command']}")
        if self.context.get("last_result"):
            lines.append(f"Последний результат: {self.context['last_result']}")
        return "\n".join(lines)

    def get_dialog_prompt(self, max_entries: int = 20) -> str:
        entries = self.dialog[-max_entries:] if len(self.dialog) > max_entries else self.dialog
        if not entries:
            return "История диалога пуста."
        lines = []
        for e in entries:
            prefix = "Пользователь" if e["role"] == "user" else "Ассистент"
            lines.append(f"{prefix}: {e['text']}")
        return "\n".join(lines)

    def reset(self):
        self.dialog = []
        self.context["state"] = "idle"
        self.context["last_command"] = None
        self.context["last_result"] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "dialog": self.dialog[-10:],
            "context": dict(self.context),
            "created_at": self.created_at,
        }
