"""Main chat window for Jarvis Assistant."""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import asyncio
from pathlib import Path
from jarvis.utils.logger import get_logger

logger = get_logger("chat")


class ChatWindow:
    def __init__(self, assistant=None):
        self.assistant = assistant
        self._voice_button = None
        self._build_ui()

    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Jarvis Assistant")
        self.root.geometry("520x600")
        self.root.configure(bg="#1e1e1e")
        self.root.minsize(400, 400)

        # Title bar
        title_frame = tk.Frame(self.root, bg="#2d2d2d", height=40)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame, text="  Jarvis Assistant", bg="#2d2d2d", fg="#ffffff",
            font=("Segoe UI", 12, "bold"), anchor="w",
        ).pack(side="left", padx=10, pady=5)

        status_btn = tk.Label(
            title_frame, text="●", bg="#2d2d2d", fg="#4ec94e",
            font=("Segoe UI", 14),
        )
        status_btn.pack(side="right", padx=(0, 10))

        # Chat history
        chat_frame = tk.Frame(self.root, bg="#1e1e1e")
        chat_frame.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        self.chat_display = tk.Text(
            chat_frame, bg="#252526", fg="#d4d4d4",
            font=("Segoe UI", 10), wrap="word", relief="flat",
            bd=0, padx=10, pady=10, cursor="arrow",
            state="disabled",
        )
        self.chat_display.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_display.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_display.configure(yscrollcommand=scrollbar.set)

        # Input area
        input_frame = tk.Frame(self.root, bg="#2d2d2d", height=60)
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)

        self.input_field = tk.Entry(
            input_frame, bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff",
            font=("Segoe UI", 11), relief="flat", bd=8,
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=10)
        self.input_field.bind("<Return>", self._on_send)

        send_btn = tk.Button(
            input_frame, text="➤", bg="#0e639c", fg="#ffffff",
            font=("Segoe UI", 12, "bold"), relief="flat", bd=0,
            activebackground="#1177bb", cursor="hand2",
            command=self._on_send, width=3,
        )
        send_btn.pack(side="right", padx=(0, 4), pady=10)

        self._voice_button = tk.Button(
            input_frame, text="🎤", bg="#2d2d2d", fg="#cccccc",
            font=("Segoe UI", 12), relief="flat", bd=0,
            activebackground="#3c3c3c", cursor="hand2",
            command=self._on_voice, width=3,
        )
        self._voice_button.pack(side="right", padx=(0, 2), pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._add_message("system", "🤖 Jarvis запущен. Напиши команду или нажми 🎤 для голоса.")

    def _add_message(self, role: str, text: str):
        if not text:
            return
        self.chat_display.config(state="normal")
        tag = "user" if role == "user" else ("assistant" if role == "assistant" else "system")

        prefix = {"user": "👤 Вы: ", "assistant": "🤖 Jarvis: ", "system": ""}
        p = prefix.get(role, "")

        self.chat_display.insert("end", p + text + "\n\n", tag)
        self.chat_display.tag_config("user", foreground="#4fc1ff", font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="#d4d4d4", font=("Segoe UI", 10))
        self.chat_display.tag_config("system", foreground="#888888", font=("Segoe UI", 9, "italic"))
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")

    def _on_send(self, event=None):
        text = self.input_field.get().strip()
        if not text:
            return
        self.input_field.delete(0, "end")
        self._add_message("user", text)
        self._process_text(text)

    def _on_voice(self):
        self._voice_button.config(text="🔴", state="disabled")
        self._add_message("system", "🎤 Слушаю...")
        threading.Thread(target=self._voice_thread, daemon=True).start()

    def _voice_thread(self):
        try:
            from jarvis.audio.stt import SpeechRecognizer
            stt = SpeechRecognizer()
            if stt.is_available:
                text = stt.transcribe(duration=5.0)
                if text:
                    self.root.after(0, lambda: self._on_voice_result(text))
                else:
                    self.root.after(0, lambda: self._add_message("system", "❌ Не удалось распознать речь"))
            else:
                self.root.after(0, lambda: self._add_message("system", "⚠️ Модель STT не загружена"))
        except Exception as e:
            self.root.after(0, lambda: self._add_message("system", f"❌ Ошибка: {e}"))
        finally:
            self.root.after(0, self._reset_voice_button)

    def _on_voice_result(self, text: str):
        self._add_message("user", f"[голос] {text}")
        self._process_text(text)

    def _reset_voice_button(self):
        self._voice_button.config(text="🎤", state="normal")

    def _process_text(self, text: str):
        self._add_message("system", "⏳ Обработка...")
        threading.Thread(target=self._process_thread, args=(text,), daemon=True).start()

    def _process_thread(self, text: str):
        try:
            if self.assistant:
                response = self.assistant.process_text(text)
                self.root.after(0, lambda: self._handle_response(response))
            else:
                self.root.after(0, lambda: self._add_message("system", "❌ Ассистент не инициализирован"))
        except Exception as e:
            logger.error(f"Process error: {e}")
            self.root.after(0, lambda: self._add_message("system", f"❌ Ошибка: {e}"))

    def _handle_response(self, response: str):
        # Remove "processing..." message
        self._remove_last_system()
        if response:
            self._add_message("assistant", response)
        else:
            self._add_message("system", "✅ Выполнено")

    def _remove_last_system(self):
        self.chat_display.config(state="normal")
        lines = self.chat_display.get("1.0", "end-2c").split("\n")
        if lines and "Обработка..." in lines[-2] if len(lines) >= 2 else False:
            self.chat_display.delete("end-2l", "end-1c")
        self.chat_display.config(state="disabled")

    def _on_close(self):
        if self.assistant:
            self.assistant.shutdown()
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
