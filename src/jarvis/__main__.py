"""
Jarvis Assistant — точка входа.
Запускает чат-окно (tkinter) в главном потоке.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jarvis.core.main import JarvisAssistant
from jarvis.ui.chat import ChatWindow


def main():
    assistant = JarvisAssistant()
    chat = ChatWindow(assistant=assistant)
    chat.run()


if __name__ == "__main__":
    main()
